"""
导师学术关系图谱接口
根据论文合作者、项目成员等数据构建以导师为中心的关系网络
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
    """判断两个姓名是否匹配（支持简繁体、空格等）"""
    na = _normalize_name(a)
    nb = _normalize_name(b)
    if not na or not nb:
        return False
    return na == nb


async def _find_collaborators_from_papers(db, center_tutor_id: str, center_name: str) -> Dict[str, Dict]:
    """
    从论文中提取合作导师（共同作者）
    返回: {tutor_id: {count, papers: [title, ...]}}
    """
    collaborators: Dict[str, Dict[str, Any]] = {}
    
    # 获取中心导师的论文（来自 papers 表或 tutor_details 内嵌）
    papers_cursor = db.papers.find({"tutor_id": center_tutor_id})
    papers = await papers_cursor.to_list(length=500)
    
    tutor_detail = await db.tutor_details.find_one({"tutor_id": center_tutor_id})
    if tutor_detail and tutor_detail.get("papers"):
        papers.extend(tutor_detail["papers"])
    
    # 获取所有导师姓名到ID的映射
    all_tutors = await db.tutors.find({}).to_list(length=5000)
    name_to_tutors: Dict[str, List[Dict]] = {}
    for t in all_tutors:
        n = _normalize_name(t.get("name", ""))
        if n and t.get("id") != center_tutor_id:
            if n not in name_to_tutors:
                name_to_tutors[n] = []
            name_to_tutors[n].append(t)
    
    for paper in papers:
        authors = paper.get("authors") or []
        if not isinstance(authors, list):
            authors = []
        for author_name in authors:
            author_name = author_name.strip() if isinstance(author_name, str) else ""
            if not author_name or _name_matches(author_name, center_name):
                continue
            # 尝试精确匹配
            norm = _normalize_name(author_name)
            if norm in name_to_tutors:
                for t in name_to_tutors[norm]:
                    tid = t["id"]
                    if tid not in collaborators:
                        collaborators[tid] = {"count": 0, "papers": [], "name": t.get("name")}
                    collaborators[tid]["count"] += 1
                    title = paper.get("title") or paper.get("name", "")
                    if title and title not in collaborators[tid]["papers"]:
                        collaborators[tid]["papers"].append(title[:50])
            else:
                # 模糊匹配：部分姓名匹配
                for n, tutors in name_to_tutors.items():
                    if author_name in n or n in author_name:
                        for t in tutors:
                            tid = t["id"]
                            if tid not in collaborators:
                                collaborators[tid] = {"count": 0, "papers": [], "name": t.get("name")}
                            collaborators[tid]["count"] += 1
                            break
    
    return collaborators


async def _find_collaborators_from_projects(db, center_tutor_id: str, center_name: str) -> Dict[str, Dict]:
    """
    从合作项目中提取合作导师（项目成员）
    返回: {tutor_id: {count, projects: [title, ...]}}
    """
    collaborators: Dict[str, Dict[str, Any]] = {}
    
    # 获取所有项目（包括带 members 的合作项目）
    projects_cursor = db.projects.find({"members": {"$exists": True, "$ne": []}})
    projects = await projects_cursor.to_list(length=500)
    
    all_tutors = await db.tutors.find({}).to_list(length=5000)
    name_to_tutors: Dict[str, List[Dict]] = {}
    for t in all_tutors:
        n = _normalize_name(t.get("name", ""))
        if n and t.get("id") != center_tutor_id:
            if n not in name_to_tutors:
                name_to_tutors[n] = []
            name_to_tutors[n].append(t)
    
    for proj in projects:
        members = proj.get("members") or []
        if not isinstance(members, list):
            continue
        member_names = []
        for m in members:
            if isinstance(m, dict):
                member_names.append(m.get("name") or m.get("id", ""))
            elif isinstance(m, str):
                member_names.append(m)
        
        if not _normalize_name(center_name) in [_normalize_name(n) for n in member_names]:
            continue
        
        for m in members:
            name = m.get("name") if isinstance(m, dict) else str(m)
            if not name or _name_matches(name, center_name):
                continue
            norm = _normalize_name(name)
            if norm in name_to_tutors:
                for t in name_to_tutors[norm]:
                    tid = t["id"]
                    if tid not in collaborators:
                        collaborators[tid] = {"count": 0, "projects": [], "name": t.get("name")}
                    collaborators[tid]["count"] += 1
                    title = proj.get("title") or proj.get("name", "")
                    if title and title not in collaborators[tid].get("projects", []):
                        collaborators[tid].setdefault("projects", []).append(title[:50])
    
    return collaborators


@router.get(
    "/network/{tutor_id}",
    summary="导师学术关系图谱",
    description="获取以指定导师为中心的学术合作关系网络数据，包括论文合作者、项目合作伙伴等",
)
async def get_tutor_network(
    request: Request,
    tutor_id: str,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    返回图谱数据，格式：
    nodes: [{ id, name, type: 'center'|'collaborator', school, department, avatar }]
    edges: [{ source, target, type: 'paper'|'project', label? }]
    """
    try:
        db = get_db()
        
        tutor = await db.tutors.find_one({
            "id": tutor_id,
            "$or": [
                {"is_deleted": {"$exists": False}},
                {"is_deleted": False}
            ]
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
        
        # 1. 从论文获取合作者
        paper_collabs = await _find_collaborators_from_papers(db, tutor_id, center_name)
        # 2. 从项目获取合作者
        project_collabs = await _find_collaborators_from_projects(db, tutor_id, center_name)
        
        # 合并合作者
        all_collab_ids: Set[str] = set(paper_collabs.keys()) | set(project_collabs.keys())
        
        # 获取合作者详情
        collab_tutors = []
        if all_collab_ids:
            collab_tutors = await db.tutors.find({"id": {"$in": list(all_collab_ids)}}).to_list(length=100)
        
        # 构建节点
        nodes = [
            {
                "id": tutor_id,
                "name": center_name,
                "type": "center",
                "school": tutor.get("school_name", ""),
                "department": tutor.get("department_name", ""),
                "avatar": tutor.get("avatar_url"),
                "title": tutor.get("title")
            }
        ]
        
        collab_map = {t["id"]: t for t in collab_tutors}
        
        for cid in all_collab_ids:
            t = collab_map.get(cid)
            if not t:
                continue
            nodes.append({
                "id": t["id"],
                "name": t.get("name", ""),
                "type": "collaborator",
                "school": t.get("school_name", ""),
                "department": t.get("department_name", ""),
                "avatar": t.get("avatar_url"),
                "title": t.get("title")
            })
        
        # 构建边
        edges = []
        for cid in all_collab_ids:
            if cid in paper_collabs:
                edges.append({
                    "source": tutor_id,
                    "target": cid,
                    "type": "paper",
                    "label": f"论文合作 {paper_collabs[cid]['count']}篇"
                })
            if cid in project_collabs:
                edges.append({
                    "source": tutor_id,
                    "target": cid,
                    "type": "project",
                    "label": f"项目合作 {project_collabs[cid]['count']}个"
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
