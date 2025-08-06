"""XHS API routes."""

import asyncio
from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from loguru import logger

from .schemas import (
    CommentRequest,
    CommentResponse,
    SearchRequest,
    NoteResponse,
    ApiResponse,
    UrlConvertRequest,
    UrlConvertResponse
)
from .xhs_api import XhsAPI
from .services import XhsService

router = APIRouter(prefix="/xhs", tags=["XHS"])
xhs_service = XhsService()


@router.post("/get_comments", response_model=ApiResponse)
async def get_comments(request: CommentRequest):
    """获取小红书笔记评论
    
    Args:
        request: 包含cookies、note_url等参数的请求体
        
    Returns:
        ApiResponse: 包含评论列表的响应
    """
    try:
        api = XhsAPI()
        comments = api.get_comments(
            cookies_str=request.cookies,
            ori_url=request.note_url,
            cursor=request.cursor or "",
            max_comments=request.max_comments
        )

        
        return ApiResponse(
            success=True,
            message=f"成功获取{len(comments)}条评论",
            data=comments
        )
        
    except Exception as e:
        logger.error(f"获取评论失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取评论失败: {str(e)}")


@router.post("/search_notes_by_keyword", response_model=ApiResponse)
async def search_notes_by_keyword(request: SearchRequest):
    """根据关键词搜索小红书笔记
    
    Args:
        request: 包含cookies、keyword、num等参数的请求体
        
    Returns:
        ApiResponse: 包含笔记列表的响应
    """
    try:
        api = XhsAPI()
        notes = api.search_notes_by_keyword(
            cookies_str=request.cookies,
            keyword=request.keyword,
            num=request.num
        )

        
        return ApiResponse(
            success=True,
            message=f"成功搜索到{len(notes)}条笔记",
            data=notes
        )
        
    except Exception as e:
        logger.error(f"搜索笔记失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索笔记失败: {str(e)}")

@router.post("/search_comments_by_keyword", response_model=ApiResponse)
async def search_comments_by_keyword(request: SearchRequest):
    """根据关键词搜索小红书评论

    Args:
        request: 包含cookies、keyword、num等参数的请求体
        
    Returns:
        ApiResponse: 包含笔记列表的响应
    """
    try:
        api = XhsAPI()
        comments_list = api.search_comments_by_keyword(
            cookies_str=request.cookies,
            keyword=request.keyword,
            num=request.num
        )

        
        return ApiResponse(
            success=True,
            message=f"成功搜索到{len(comments_list)}条评论",
            data=comments_list
        )
        
    except Exception as e:
        logger.error(f"搜索评论失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索评论失败: {str(e)}")


@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "xhs-api"}


@router.post("/comments/batch", response_model=ApiResponse)
async def get_comments_batch(requests: List[CommentRequest], background_tasks: BackgroundTasks):
    """批量获取多个笔记的评论
    
    Args:
        requests: 包含多个评论请求的列表
        background_tasks: 后台任务
        
    Returns:
        ApiResponse: 批量处理结果
    """
    try:
        # 添加到后台任务队列
        background_tasks.add_task(xhs_service.process_batch_comments, requests)
        
        return ApiResponse(
            success=True,
            message=f"已提交{len(requests)}个批量任务到后台处理",
            data=[]
        )
        
    except Exception as e:
        logger.error(f"批量处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量处理失败: {str(e)}")


@router.post("/search/batch", response_model=ApiResponse)
async def search_notes_batch(requests: List[SearchRequest], background_tasks: BackgroundTasks):
    """批量搜索多个关键词的笔记
    
    Args:
        requests: 包含多个搜索请求的列表
        background_tasks: 后台任务
        
    Returns:
        ApiResponse: 批量处理结果
    """
    try:
        # 添加到后台任务队列
        background_tasks.add_task(xhs_service.process_batch_search, requests)
        
        return ApiResponse(
            success=True,
            message=f"已提交{len(requests)}个批量搜索任务到后台处理",
            data=[]
        )
        
    except Exception as e:
        logger.error(f"批量搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量搜索失败: {str(e)}")