"""
智能匹配接口
提供根据用户兴趣匹配导师的功能
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional
import uuid
import json
from datetime import datetime

from app.models import (
    User, MatchRequest, MatchResponse, MatchResult,
    MatchHistory, MatchHistoryResponse
)
from app.api.v1.auth.login import get_current_user
from app.utils import (
    success_response,
    error_response,
    business_error_response,
    api_logger
)
from app.db.mongo import get_db

router = APIRouter(
    prefix="/match",
    tags=["match"]
)


def calculate_match_score(tutor: dict, discipline: str, keywords: List[str]) -> float:
    """
    计算导师与用户需求的匹配度分数
    
    Args:
        tutor: 导师信息
        discipline: 学科方向
        keywords: 研究兴趣关键词列表
    
    Returns:
        float: 匹配度分数 (0-100)
    """
    score = 0.0
    
    # 学科方向匹配 (权重 0.4)
    if tutor.get("research_direction"):
        if discipline.lower() in tutor["research_direction"].lower():
            score += 40.0
    
    # 关键词匹配 (权重 0.6)
    research_text = " ".join([
        str(tutor.get("research_direction", "")),
        str(tutor.get("bio", "")),
        str(tutor.get("achievements_summary", ""))
    ]).lower()
    
    keyword_score = 0.0
    for keyword in keywords:
        if keyword.lower() in research_text:
            keyword_score += 1.0
    
    if keywords:
        keyword_score = (keyword_score / len(keywords)) * 60.0
        score += keyword_score
    
    return round(score, 2)


def generate_match_reason(tutor: dict, discipline: str, keywords: List[str]) -> str:
    """
    生成匹配理由
    
    Args:
        tutor: 导师信息
        discipline: 学科方向
        keywords: 研究兴趣关键词列表
    
    Returns:
        str: 匹配理由
    """
    reasons = []
    
    # 学科方向匹配
    if tutor.get("research_direction"):
        if discipline.lower() in tutor["research_direction"].lower():
            reasons.append(f"研究方向包含您感兴趣的「{discipline}」")
    
    # 关键词匹配
    matched_keywords = []
    research_text = " ".join([
        str(tutor.get("research_direction", "")),
        str(tutor.get("bio", "")),
        str(tutor.get("achievements_summary", ""))
    ]).lower()
    
    for keyword in keywords:
        if keyword.lower() in research_text:
            matched_keywords.append(keyword)
    
    if matched_keywords:
        reasons.append(f"研究内容涵盖您关注的关键词：{', '.join(matched_keywords)}")
    
    # 职称匹配
    if tutor.get("title"):
        title = tutor["title"].lower()
        if any(t in title for t in ["教授", "副教授", "研究员"]):
            reasons.append(f"具有{title}职称，学术经验丰富")
    
    # 如果没有具体理由，给出通用理由
    if not reasons:
        reasons.append("基于您的研究兴趣进行的智能匹配推荐")
    
    return "；".join(reasons) + "。"


@router.post(
    "/submit",
    summary="提交匹配请求",
    description="根据用户输入的学科方向和关键词，推荐匹配度高的导师",
    response_model=MatchResponse
)
async def submit_match_request(
    request: Request,
    match_request: MatchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    提交匹配请求接口
    
    Args:
        request: 请求对象
        match_request: 匹配请求数据
        current_user: 当前登录用户
    
    Returns:
        MatchResponse: 匹配结果
    """
    try:
        db = get_db()
        
        # 解析关键词
        keywords = [k.strip() for k in match_request.keywords.split(",") if k.strip()]
        
        if not keywords:
            raise HTTPException(
                status_code=400,
                detail=business_error_response(
                    code="INVALID_KEYWORDS",
                    message="请输入有效的研究兴趣关键词"
                )
            )
        
        # 获取导师列表
        tutors = db.tutors.find({})
        
        # 计算匹配度
        match_results = []
        for tutor in tutors:
            # 获取导师详细信息
            tutor_detail = db.tutor_details.find_one({"tutor_id": tutor["id"]})
            
            # 合并导师信息
            tutor_info = {
                **tutor,
                "bio": tutor_detail.get("bio") if tutor_detail else None,
                "achievements_summary": tutor_detail.get("achievements_summary") if tutor_detail else None
            }
            
            # 计算匹配分数
            score = calculate_match_score(tutor_info, match_request.discipline, keywords)
            
            # 只保留匹配度大于0的结果
            if score > 0:
                match_result = MatchResult(
                    tutor_id=tutor["id"],
                    match_score=score,
                    match_reason=generate_match_reason(tutor_info, match_request.discipline, keywords),
                    tutor_info={
                        "id": tutor["id"],
                        "name": tutor["name"],
                        "title": tutor.get("title"),
                        "school": tutor.get("school_name", ""),
                        "department": tutor.get("department_name", ""),
                        "avatar": tutor.get("avatar_url"),
                        "research_direction": tutor.get("research_direction")
                    }
                )
                match_results.append(match_result)
        
        # 按匹配度排序
        match_results.sort(key=lambda x: x.match_score, reverse=True)
        
        # 限制结果数量
        match_results = match_results[:20]
        
        # 保存匹配历史
        match_history = {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "discipline": match_request.discipline,
            "keywords": match_request.keywords,
            "preferences": match_request.preferences.model_dump(),
            "result_json": json.dumps([r.model_dump() for r in match_results]),
            "created_at": datetime.now()
        }
        
        db.match_histories.insert_one(match_history)
        
        api_logger.info(
            f"智能匹配成功: {current_user.id} - {match_request.discipline}\n"
            f"关键词: {match_request.keywords}\n"
            f"匹配结果: {len(match_results)} 个导师\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return MatchResponse(
            match_id=match_history["id"],
            results=match_results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(
            f"智能匹配失败: {str(e)}\n"
            f"User: {current_user.id}\n"
            f"Discipline: {match_request.discipline}\n"
            f"Keywords: {match_request.keywords}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="智能匹配失败",
                error={"request_id": request.state.request_id}
            )
        )


@router.get(
    "/history",
    summary="获取匹配历史",
    description="获取用户的历史匹配记录"
)
async def get_match_history(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_user)
):
    """
    获取匹配历史接口
    
    Args:
        request: 请求对象
        page: 页码
        page_size: 每页数量
        current_user: 当前登录用户
    
    Returns:
        匹配历史列表
    """
    try:
        db = get_db()
        
        # 计算分页
        skip = (page - 1) * page_size
        
        # 获取总数
        total = db.match_histories.count_documents({"user_id": current_user.id})
        
        # 获取历史记录
        histories = db.match_histories.find(
            {"user_id": current_user.id}
        ).sort("created_at", -1).skip(skip).limit(page_size)
        
        history_list = []
        for history in histories:
            # 解析结果
            result_data = json.loads(history["result_json"])
            
            history_response = MatchHistoryResponse(
                id=history["id"],
                discipline=history["discipline"],
                keywords=history["keywords"],
                preferences=history["preferences"],
                created_at=history["created_at"],
                result_count=len(result_data)
            )
            history_list.append(history_response)
        
        return success_response(
            data={
                "list": history_list,
                "total": total,
                "page": page,
                "pageSize": page_size
            },
            message="获取匹配历史成功"
        )
        
    except Exception as e:
        api_logger.error(
            f"获取匹配历史失败: {str(e)}\n"
            f"User: {current_user.id}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="获取匹配历史失败",
                error={"request_id": request.state.request_id}
            )
        )


@router.get(
    "/history/{history_id}",
    summary="获取匹配历史详情",
    description="获取指定匹配历史的详细结果"
)
async def get_match_history_detail(
    request: Request,
    history_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    获取匹配历史详情接口
    
    Args:
        request: 请求对象
        history_id: 历史记录ID
        current_user: 当前登录用户
    
    Returns:
        匹配历史详情
    """
    try:
        db = get_db()
        
        # 获取历史记录
        history = db.match_histories.find_one({
            "id": history_id,
            "user_id": current_user.id
        })
        
        if not history:
            raise HTTPException(
                status_code=404,
                detail=business_error_response(
                    code="HISTORY_NOT_FOUND",
                    message="匹配历史不存在"
                )
            )
        
        # 解析结果
        result_data = json.loads(history["result_json"])
        results = [MatchResult(**r) for r in result_data]
        
        return success_response(
            data={
                "match_id": history["id"],
                "discipline": history["discipline"],
                "keywords": history["keywords"],
                "preferences": history["preferences"],
                "created_at": history["created_at"],
                "results": results
            },
            message="获取匹配历史详情成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(
            f"获取匹配历史详情失败: {str(e)}\n"
            f"User: {current_user.id}\n"
            f"History ID: {history_id}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="获取匹配历史详情失败",
                error={"request_id": request.state.request_id}
            )
        )