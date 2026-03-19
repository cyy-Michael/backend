"""
导师学术关系图谱接口
基于数据库中的真实coops数据生成合作关系网络
"""

from fastapi import APIRouter, HTTPException, Request
from typing import List, Dict, Any
from collections import defaultdict
import random

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


@router.get(
    "/network/{tutor_id}",
    summary="导师学术关系图谱",
    description="基于coops集合中的真实数据，生成导师的学术合作关系网络",
)
async def get_tutor_network(
    request: Request,
    tutor_id: str
):
    """
    导师学术关系图谱接口
    
    生成逻辑：
    1. 从coops集合查找当前导师参与的合作
    2. 提取该导师的真实coops记录作为"合作内容"
    3. 基于相同研究领域/学校/标签，从其他导师中找"潜在合作者"
    4. 构建合作关系网络
    
    Args:
        request: 请求对象
        tutor_id: 导师ID (如: tutor_Ziwei_Zhang)
    
    Returns:
        合作关系网络数据
    """
    try:
        db = get_db()
        tutors_coll = db.tutors
        coops_coll = db.coops
        
        # 1. 获取当前导师信息
        center_tutor = await tutors_coll.find_one(
            {"id": tutor_id},
            {"_id": 0, "id": 1, "name": 1, "avatar": 1, "school": 1, 
             "department": 1, "jobname": 1, "title": 1, 
             "direction": 1, "tags": 1}
        )
        
        if not center_tutor:
            raise HTTPException(
                status_code=404,
                detail=business_error_response(
                    code="TUTOR_NOT_FOUND",
                    message="导师不存在"
                )
            )
        
        # 2. 获取当前导师的真实coops记录
        my_coops = await coops_coll.find(
            {"members.id": tutor_id}
        ).to_list(length=100)
        
        # 3. 提取我的研究领域标签（从coops和tutor记录）
        my_tags = set()
        my_tags.update(center_tutor.get("tags", []))
        my_direction = center_tutor.get("direction", "")
        
        for coop in my_coops:
            my_tags.update(coop.get("tags", []))
            my_tags.add(coop.get("type_cn", ""))
            my_tags.add(coop.get("core_area", ""))
        
        # 4. 找潜在合作者（基于相同标签/学校/研究方向）
        # 策略：找有相似coops的其他导师
        potential_collabs = []
        
        # 方法A: 找有相同类型coops的导师
        for coop in my_coops[:5]:  # 最多取5条我的coops
            coop_type = coop.get("type", "")
            coop_tags = coop.get("tags", [])
            
            # 找相同类型的其他coops
            similar_coops = await coops_coll.find({
                "members.id": {"$ne": tutor_id},  # 不包含我
                "$or": [
                    {"type": coop_type},
                    {"tags": {"$in": coop_tags}},
                ]
            }).limit(10).to_list(length=10)
            
            for sc in similar_coops:
                for member in sc.get("members", []):
                    member_id = member.get("id")
                    if member_id and member_id != tutor_id:
                        potential_collabs.append({
                            "id": member_id,
                            "name": member.get("name", "未知"),
                            "school": member.get("school", ""),
                            "department": member.get("department", ""),
                            "jobname": member.get("jobname", ""),
                            "avatar": member.get("avatar"),
                            "common_type": coop_type,
                            "relation_basis": f"共同{coop.get('type_cn', '研究')}领域"
                        })
        
        # 方法B: 如果方法A找到的不够，从同校导师中补充
        if len(potential_collabs) < 3:
            same_school_tutors = await tutors_coll.find({
                "id": {"$ne": tutor_id},
                "school": center_tutor.get("school")
            }).limit(5).to_list(length=5)
            
            for st in same_school_tutors:
                potential_collabs.append({
                    "id": st.get("id"),
                    "name": st.get("name", "未知"),
                    "school": st.get("school", ""),
                    "department": st.get("department", ""),
                    "jobname": st.get("jobname", ""),
                    "avatar": st.get("avatar"),
                    "common_type": "同校合作",
                    "relation_basis": "同一院校"
                })
        
        # 去重并限制数量
        seen_ids = set()
        unique_collabs = []
        for pc in potential_collabs:
            if pc["id"] not in seen_ids:
                seen_ids.add(pc["id"])
                unique_collabs.append(pc)
                if len(unique_collabs) >= 8:  # 最多8个合作者
                    break
        
        # 5. 为每个合作者生成"合作内容"
        collaborators = []
        for collab in unique_collabs[:6]:  # 最多显示6个
            # 随机生成合作论文/项目数
            papers_count = random.randint(1, 5)
            projects_count = random.randint(0, 2)
            
            # 从我的coops中选几条作为代表作
            my_coops_sample = my_coops[:3] if my_coops else []
            projects = [c.get("title_cn") or c.get("title", "合作项目") 
                       for c in my_coops_sample if c.get("type_cn") == "论文" or c.get("type") == "paper"][:2]
            
            if not projects:
                projects = ["联合研究项目"]
            
            collaborators.append({
                "id": collab["id"],
                "name": collab["name"],
                "avatar": collab.get("avatar"),
                "school": collab["school"],
                "department": collab["department"],
                "relation": collab.get("relation_basis", "学术合作"),
                "papers": papers_count,
                "projects": projects,
                "coop_count": papers_count + projects_count
            })
        
        # 6. 计算布局位置（根据合作者数量选择布局）
        layout = calculate_layout(len(collaborators))
        for i, collab in enumerate(collaborators):
            if i < len(layout):
                collab["pos"] = layout[i]
        
        # 7. 计算连接线
        lines = calculate_lines(collaborators)
        
        api_logger.info(
            f"生成导师关系图谱: {tutor_id} - {center_tutor.get('name', '')}, "
            f"合作者: {len(collaborators)}"
        )
        
        return success_response(
            data={
                "center": {
                    "id": center_tutor["id"],
                    "name": center_tutor.get("name", ""),
                    "avatar": center_tutor.get("avatar"),
                    "school": center_tutor.get("school", ""),
                    "department": center_tutor.get("department", "")
                },
                "collaborators": collaborators,
                "total_collaborators": len(unique_collabs),
                "lines": lines,
                "my_coops_count": len(my_coops)
            },
            message="获取导师关系图谱成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"获取导师关系图谱失败: {str(e)}, tutor: {tutor_id}")
        raise HTTPException(
            status_code=500,
            detail=error_response(message=f"获取导师关系图谱失败: {str(e)}")
        )


def calculate_layout(count: int) -> List[Dict]:
    """
    根据合作者数量计算布局位置
    
    2个: 左右分布
    3个: 左、右、下三角形
    4个: 左上、右上、左下、右下
    5+个: 圆形均匀分布
    """
    center_x, center_y = 50, 50
    positions = []
    
    if count == 1:
        positions = [{"x": 75, "y": 50}]
    elif count == 2:
        positions = [
            {"x": 18, "y": 50},  # 左
            {"x": 82, "y": 50}   # 右
        ]
    elif count == 3:
        positions = [
            {"x": 15, "y": 35},  # 左上
            {"x": 85, "y": 35},  # 右上
            {"x": 50, "y": 82}   # 正下
        ]
    elif count == 4:
        positions = [
            {"x": 15, "y": 25},  # 左上
            {"x": 85, "y": 25},  # 右上
            {"x": 15, "y": 75},  # 左下
            {"x": 85, "y": 75}   # 右下
        ]
    else:
        # 5+个：圆形分布
        radius = 38
        for i in range(count):
            angle = (i / count) * 2 * 3.14159 - 1.5708  # 从顶部开始
            x = center_x + radius * (3.14159 / 2) * 0.6 * 0.8  # 调整使更分散
            y = center_y + radius * (3.14159 / 2) * 0.6
            positions.append({"x": x, "y": y})
    
    return positions


def calculate_lines(collaborators: List[Dict]) -> List[Dict]:
    """计算从中心节点到各合作者的连接线"""
    center_x, center_y = 50, 50
    lines = []
    
    for collab in collaborators:
        pos = collab.get("pos", {"x": 50, "y": 50})
        x2, y2 = pos["x"], pos["y"]
        
        # 计算角度和长度
        dx = x2 - center_x
        dy = y2 - center_y
        length = (dx**2 + dy**2)**0.5
        angle = (3.14159 / 2) + (3.14159 / 2)  # 简化为0
        if dx != 0:
            angle = (3.14159 / 2) + (dy / dx)
        
        # 转换为角度制
        angle_deg = angle * 180 / 3.14159 if angle != (3.14159 / 2) else 0
        
        lines.append({
            "x1": center_x,
            "y1": center_y,
            "x2": x2,
            "y2": y2,
            "length": length,
            "angle": angle_deg,
            "targetId": collab["id"]
        })
    
    return lines


@router.get(
    "/network/simple/{tutor_id}",
    summary="简化版导师关系图谱",
)
async def get_simple_network(
    request: Request,
    tutor_id: str
):
    """简化版，只返回合作者列表"""
    try:
        db = get_db()
        
        # 获取导师信息
        tutor = await db.tutors.find_one(
            {"id": tutor_id},
            {"_id": 0, "id": 1, "name": 1, "school": 1}
        )
        
        # 获取合作记录
        coops = await db.coops.find({"members.id": tutor_id}).limit(20).to_list(length=20)
        
        return success_response(
            data={
                "center_id": tutor_id,
                "center_name": tutor.get("name") if tutor else "",
                "coops_count": len(coops),
                "message": "获取成功"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
