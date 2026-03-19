"""
导师学术关系图谱接口
根据coops集合中的members数据构建以导师为中心的关系网络
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from typing import List, Dict, Any, Optional, Set

from app.models import User
from app.api.v1.auth.login import get_current_user
from app.utils import (
    success_response,
    error_response,
    business_error_response,
    api_logger
)
from app.db.mongo import get_db

router = APIRouter(
    prefix="/tutor",
    tags=["tutor", "network"]
)


def _normalize_name(name: str) -> str:
    """标准化姓名用于匹配（去除空格、统一格式）"""
    if not name:
        return ""
    return name.strip()


def _name_matches(a: str, b: str) -> bool:
    """判断两个姓名是否匹配"""
    na = _normalize_name(a)
    nb = _normalize_name(b)
    if not na or not nb:
        return False
    return na == nb


async def _find_collaborators_from_coops(db, center_tutor_id: str, center_name: str) -> Dict[str, Dict]:
    """
    从coops集合中提取合作导师（通过members字段）
    返回: {tutor_id: {count, coops: [title, ...]}}
    """
    collaborators: Dict[str, Dict[str, Any]] = {}
    
    # 获取所有包含members的coops（论文和项目）
    coops_cursor = db.coops.find({"members": {"$exists": True, "$ne": []}})
    coops = await coops_cursor.to_list(length=500)
    
    # 获取所有导师ID到导师信息的映射
    all_tutors = await db.tutors.find({}).to_list(length=5000)
    id_to_tutors: Dict[str, Dict] = {}
    name_to_tutors: Dict[str, List[Dict]] = {}
    
    for t in all_tutors:
        tid = t.get("id")
        if tid:
            id_to_tutors[tid] = t
        n = _normalize_name(t.get("name", ""))
        if n and tid != center_tutor_id:
            if n not in name_to_tutors:
                name_to_tutors[n] = []
            name_to_tutors[n].append(t)
    
    for coop in coops:
        members = coop.get("members") or []
        if not isinstance(members, list):
            continue
        
        # 检查中心导师是否在该coop的members中
        center_in_coop = False
        for m in members:
            if isinstance(m, dict):
                member_id = m.get("id", "")
                member_name = m.get("name", "")
                if member_id == center_tutor_id or _name_matches(member_name, center_name):
                    center_in_coop = True
                    break
        
        if not center_in_coop:
            continue
        
        # 该中心导师参与了此coop，找出其他合作者
        for m in members:
            if not isinstance(m, dict):
                continue
            
            member_id = m.get("id", "")
            member_name = m.get("name", "")
            
            # 跳过中心导师自己
            if member_id == center_tutor_id or _name_matches(member_name, center_name):
                continue
            
            # 通过ID或姓名匹配到导师
            collab_tutor = None
            if member_id and member_id in id_to_tutors:
                collab_tutor = id_to_tutors[member_id]
            elif member_name:
                norm = _normalize_name(member_name)
                if norm in name_to_tutors:
                    collab_tutor = name_to_tutors[norm][0]
            
            if not collab_tutor:
                continue
            
            tid = collab_tutor.get("id")
            if not tid:
                continue
            
            if tid not in collaborators:
                collaborators[tid] = {"count": 0, "coops": [], "name": collab_tutor.get("name"), "tutor": collab_tutor}
            
            collaborators[tid]["count"] += 1
            coop_title = coop.get("title") or coop.get("name", "")
            if coop_title and coop_title not in collaborators[tid]["coops"]:
                collaborators[tid]["coops"].append(coop_title[:50])
    
    return collaborators


@router.get(
    "/network/{tutor_id}",
    summary="导师学术关系图谱",
    description="获取以指定导师为中心的学术合作关系网络数据，从coops集合中分析members关系",
)
async def get_tutor_network(
    request: Request,
    tutor_id: str,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    返回图谱数据，格式：
    nodes: [{ id, name, type: 'center'|'collaborator', school, department, avatar }]
    edges: [{ source, target, type: 'coop', label? }]
    """
    try:
        db = get_db()
        
        # 获取中心导师信息 - 使用id字段查询
        tutor = await db.tutors.find_one({
            "id": tutor_id
        })
        
        if not tutor:
            raise HTTPException(
                status_code=404,
                detail=business_error_response(
                    code="TUTOR_NOT_FOUND",
                    message="导师不存在或已被删除"
                )
            )
        
        center_name = tutor.get("name", "")
        
        # 从coops集合获取合作者
        collaborators = await _find_collaborators_from_coops(db, tutor_id, center_name)
        
        # 构建节点
        nodes = [
            {
                "id": tutor_id,
                "name": center_name,
                "type": "center",
                "school": tutor.get("school", ""),
                "department": tutor.get("department", ""),
                "avatar": tutor.get("avatar"),
                "title": tutor.get("jobname", "")
            }
        ]
        
        for tid, collab_data in collaborators.items():
            collab_tutor = collab_data.get("tutor", {})
            nodes.append({
                "id": tid,
                "name": collab_tutor.get("name", collab_data.get("name", "")),
                "type": "collaborator",
                "school": collab_tutor.get("school", ""),
                "department": collab_tutor.get("department", ""),
                "avatar": collab_tutor.get("avatar"),
                "title": collab_tutor.get("jobname", "")
            })
        
        # 构建边
        edges = []
        for tid, collab_data in collaborators.items():
            edges.append({
                "source": tutor_id,
                "target": tid,
                "type": "coop",
                "label": f"共同合作 {collab_data['count']}项"
            })
        
        result = {
            "nodes": nodes,
            "edges": edges,
            "center": {
                "id": tutor_id,
                "name": center_name
            }
        }
        
        api_logger.info(
            f"获取导师关系图谱成功: {tutor_id} - {center_name}, "
            f"节点数: {len(nodes)}, 边数: {len(edges)}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return success_response(
            data=result,
            message="获取学术关系图谱成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(
            f"获取导师关系图谱失败: {str(e)}\n"
            f"Tutor ID: {tutor_id}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="获取学术关系图谱失败",
                error={"request_id": getattr(request.state, "request_id", "")}
            )
        )
