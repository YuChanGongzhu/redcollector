"""Pydantic schemas for XHS API."""

from typing import List, Optional
from pydantic import BaseModel, Field


class CommentResponse(BaseModel):
    """评论响应模型"""
    content: str = Field(..., description="评论内容")
    like_count: int = Field(default=0, description="点赞数")
    nickname: str = Field(..., description="用户昵称")
    comment_id: str = Field(..., description="评论ID")
    comment_location: str = Field(default="", description="IP位置")
    note_time: str = Field(..., description="评论时间")


class NoteResponse(BaseModel):
    """笔记响应模型"""
    title: str = Field(..., description="笔记标题")
    note_id: str = Field(..., description="笔记ID")
    xsec_token: str = Field(..., description="安全令牌")
    user_nickname: str = Field(..., description="用户昵称")
    liked_count: int = Field(default=0, description="点赞数")
    note_url: str = Field(..., description="笔记URL")


class CommentRequest(BaseModel):
    """获取评论请求模型"""
    cookies: str = Field(..., description="Cookie字符串")
    note_url: str = Field(..., description="笔记URL")
    max_comments: Optional[int] = Field(default=None, description="最大评论数量")
    cursor: Optional[str] = Field(default="", description="分页游标")


class SearchRequest(BaseModel):
    """搜索笔记请求模型"""
    cookies: str = Field(..., description="Cookie字符串")
    keyword: str = Field(..., description="搜索关键词")
    num: int = Field(default=20, ge=1, le=100, description="搜索数量")


class ApiResponse(BaseModel):
    """通用API响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[List] = Field(default=None, description="响应数据")


class UrlConvertRequest(BaseModel):
    """URL转换请求模型"""
    url: str = Field(..., description="原始URL")


class UrlConvertResponse(BaseModel):
    """URL转换响应模型"""
    original_url: str = Field(..., description="原始URL")
    converted_url: str = Field(..., description="转换后的URL")
    note_id: Optional[str] = Field(default=None, description="笔记ID")
    xsec_token: Optional[str] = Field(default=None, description="安全令牌")
    xsec_source: Optional[str] = Field(default=None, description="安全来源")


class ReplyCommentRequest(BaseModel):
    """回复评论请求模型"""
    cookies: str = Field(..., description="Cookie字符串")
    note_url: str = Field(..., description="笔记URL")
    comment_id: str = Field(..., description="评论ID")
    content: str = Field(..., description="回复内容")