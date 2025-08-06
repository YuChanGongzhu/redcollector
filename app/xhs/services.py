"""XHS service layer for business logic and background tasks."""

import asyncio
from typing import List, Dict, Any
from loguru import logger
from datetime import datetime

from .schemas import CommentRequest, SearchRequest
from .xhs_api import XhsAPI


class XhsService:
    """XHS业务服务类"""
    
    def __init__(self):
        self.api = XhsAPI()
    
    async def process_batch_comments(self, requests: List[CommentRequest]) -> List[Dict[str, Any]]:
        """批量处理评论获取任务
        
        Args:
            requests: 评论请求列表
            
        Returns:
            List[Dict]: 处理结果列表
        """
        results = []
        
        for i, request in enumerate(requests):
            try:
                logger.info(f"处理第{i+1}/{len(requests)}个评论任务: {request.note_url}")
                
                comments = self.api.get_comments(
                    cookies_str=request.cookies,
                    ori_url=request.note_url,
                    cursor=request.cursor or "",
                    max_comments=request.max_comments
                )
                
                result = {
                    "task_id": i + 1,
                    "note_url": request.note_url,
                    "status": "success",
                    "comments_count": len(comments),
                    "comments": comments,
                    "processed_at": datetime.now().isoformat()
                }
                
                logger.info(f"任务{i+1}完成，获取{len(comments)}条评论")
                
            except Exception as e:
                logger.error(f"任务{i+1}失败: {e}")
                result = {
                    "task_id": i + 1,
                    "note_url": request.note_url,
                    "status": "failed",
                    "error": str(e),
                    "processed_at": datetime.now().isoformat()
                }
            
            results.append(result)
            
            # 添加延迟避免请求过于频繁
            if i < len(requests) - 1:
                await asyncio.sleep(2)
        
        return results
    
    async def process_batch_search(self, requests: List[SearchRequest]) -> List[Dict[str, Any]]:
        """批量处理搜索任务
        
        Args:
            requests: 搜索请求列表
            
        Returns:
            List[Dict]: 处理结果列表
        """
        results = []
        
        for i, request in enumerate(requests):
            try:
                logger.info(f"处理第{i+1}/{len(requests)}个搜索任务: {request.keyword}")
                
                notes = self.api.search_notes_by_keyword(
                    cookies_str=request.cookies,
                    keyword=request.keyword,
                    num=request.num
                )
                
                result = {
                    "task_id": i + 1,
                    "keyword": request.keyword,
                    "status": "success",
                    "notes_count": len(notes),
                    "notes": notes,
                    "processed_at": datetime.now().isoformat()
                }
                
                logger.info(f"搜索任务{i+1}完成，找到{len(notes)}条笔记")
                
            except Exception as e:
                logger.error(f"搜索任务{i+1}失败: {e}")
                result = {
                    "task_id": i + 1,
                    "keyword": request.keyword,
                    "status": "failed",
                    "error": str(e),
                    "processed_at": datetime.now().isoformat()
                }
            
            results.append(result)
            
            # 添加延迟避免请求过于频繁
            if i < len(requests) - 1:
                await asyncio.sleep(2)
        
        return results
    
    async def get_note_info(self, cookies_str: str, note_url: str) -> Dict[str, Any]:
        """获取笔记基本信息
        
        Args:
            cookies_str: Cookie字符串
            note_url: 笔记URL
            
        Returns:
            Dict: 笔记信息
        """
        try:
            # 提取URL参数
            params = self.api.extract_url_params(note_url)
            
            # 这里可以扩展获取笔记详细信息的逻辑
            note_info = {
                "note_id": params.get("note_id"),
                "xsec_token": params.get("xsec_token"),
                "xsec_source": params.get("xsec_source"),
                "note_url": note_url,
                "extracted_at": datetime.now().isoformat()
            }
            
            return note_info
            
        except Exception as e:
            logger.error(f"获取笔记信息失败: {e}")
            raise
    
    async def validate_cookies(self, cookies_str: str) -> bool:
        """验证cookies是否有效
        
        Args:
            cookies_str: Cookie字符串
            
        Returns:
            bool: cookies是否有效
        """
        try:
            # 尝试进行一个简单的搜索来验证cookies
            notes = self.api.search_notes_by_keyword(
                cookies_str=cookies_str,
                keyword="测试",
                num=1
            )
            
            # 如果能够成功获取结果，说明cookies有效
            return True
            
        except Exception as e:
            logger.warning(f"Cookies验证失败: {e}")
            return False
    
    async def export_comments_to_csv(self, comments: List[Dict], filename: str = None) -> str:
        """将评论导出为CSV文件
        
        Args:
            comments: 评论列表
            filename: 文件名，如果不提供则自动生成
            
        Returns:
            str: 导出的文件路径
        """
        import csv
        import os
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"xhs_comments_{timestamp}.csv"
        
        # 确保导出目录存在
        export_dir = "exports"
        os.makedirs(export_dir, exist_ok=True)
        filepath = os.path.join(export_dir, filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                if comments:
                    fieldnames = comments[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(comments)
            
            logger.info(f"评论已导出到: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"导出CSV失败: {e}")
            raise
    
