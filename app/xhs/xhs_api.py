"""Xiaohongshu API client implementation."""

import asyncio
import json
import time
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from urllib.parse import urlencode, urlparse, parse_qs
import csv
from datetime import datetime
from mimetypes import guess_extension
import math
import random
from curl_cffi import requests
from loguru import logger
from .xhs_utils.xhs_util import splice_str, generate_request_params, generate_x_b3_traceid, get_common_headers,convert_discovery_to_explore_url

class XhsAPI:
    """小红书API类，封装了获取评论、搜索笔记等功能"""
    
    def __init__(self):
        """初始化XhsAPI类"""
        self.note_list = []

    def extract_url_params(self, url: str) -> Dict[str, str]:
        """从URL中提取参数
        
        Args:
            url (str): 小红书笔记URL
            
        Returns:
            dict: 包含note_id、xsec_token、xsec_source的字典
        """
        parsed = urlparse(url)
        # 提取 note_id
        path_segments = parsed.path.strip("/").split("/")
        note_id = path_segments[1] if len(path_segments) >= 2 and path_segments[0] == "explore" else None
        
        # 提取查询参数
        query_params = parse_qs(parsed.query)
        params = {
            "note_id": note_id,
            "xsec_token": query_params.get("xsec_token", [""])[0],
            "xsec_source": query_params.get("xsec_source", [""])[0]
        }
        return params

    def get_comments(self, cookies_str: str, ori_url: str, cursor: str = '', comments_list: List[Dict] = [], max_comments: Optional[int] = None) -> List[Dict]:
        """获取小红书笔记下的评论
        
        Args:
            cookies_str (str): Cookie字符串
            ori_url (str): 笔记URL
            cursor (str): 分页游标，默认为空
            comments_list (list): 评论列表
            max_comments (int, optional): 最大评论数量
            
        Returns:
            list: 评论列表
        """
        if comments_list is None:
            comments_list = []
            
        # 转换discovery URL为explore URL
        if "discovery" in ori_url:
            ori_url = convert_discovery_to_explore_url(ori_url)
            logger.info(f"Converted URL: {ori_url}")
        
        note_params = self.extract_url_params(ori_url)
        uri = "/api/sns/web/v2/comment/page"
        params = {
            "note_id": note_params['note_id'],
            "cursor": cursor,
            "top_comment_id": "",
            "image_formats": "jpg,webp,avif",
            "xsec_token": note_params['xsec_token'],
        }
        
        # 生成请求头和cookies
        headers, cookies, data = generate_request_params(cookies_str, uri, params)
        url = "https://edith.xiaohongshu.com/api/sns/web/v2/comment/page"
        
        try:
            response = requests.get(url, headers=headers, cookies=cookies, params=params, impersonate="chrome110")
            response_data = response.json()
                
            if not response_data or not isinstance(response_data, dict) or 'data' not in response_data:
                logger.warning("API响应数据异常，返回当前评论列表")
                return comments_list
                
            comments = response_data.get('data', {}).get('comments', [])
        except Exception as e:
            logger.error(f"获取评论时发生异常: {e}，返回当前评论列表")
            return comments_list
        
        logger.info(f"成功获取{len(comments)}条评论")
        
        for comment in comments:
            # 检查是否已达到最大评论数量
            if max_comments and len(comments_list) >= max_comments:
                return comments_list
                
            format_dict = {
                'note_id': note_params['note_id'],
                'content': comment.get('content', ''),
                'like_count': comment.get('like_count', 0),
                'nickname': comment.get('user_info', {}).get('nickname', ''),
                'comment_id': comment.get('id', ''),
                'comment_location': comment.get('ip_location', ''),
                'note_time': datetime.fromtimestamp(
                    int(int(comment.get('create_time', '0'))/1000)
                ).strftime("%Y-%m-%d %H:%M:%S")
            }
            comments_list.append(format_dict)
            
            # 检查是否已达到最大评论数量
            if max_comments and len(comments_list) >= max_comments:
                return comments_list
            
            # 处理子评论
            for sub_comment in comment.get('sub_comments', []):
                if max_comments and len(comments_list) >= max_comments:
                    return comments_list
                    
                sub_format_dict = {
                    'note_id': note_params['note_id'],
                    'content': sub_comment.get('content', ''),
                    'like_count': sub_comment.get('like_count', 0),
                    'nickname': sub_comment.get('user_info', {}).get('nickname', ''),
                    'comment_id': sub_comment.get('id', ''),
                    'comment_location': sub_comment.get('ip_location', ''),
                    'note_time': datetime.fromtimestamp(
                        int(int(sub_comment.get('create_time', '0'))/1000)
                    ).strftime("%Y-%m-%d %H:%M:%S")
                }
                comments_list.append(sub_format_dict)
            
            # 获取更多子评论
            if comment.get('sub_comment_has_more') == True:
                if max_comments and len(comments_list) >= max_comments:
                    return comments_list
                    
                time.sleep(2)
                self.get_sub_comments(
                    cookies_str,
                    comment.get('note_id', note_params['note_id']),
                    comment.get('id', ''),
                    comment.get('sub_comment_cursor', ''),
                    note_params['xsec_token'],
                    comments_list,
                    max_comments
                )
        
        # 检查是否有下一页
        if response_data.get('data', {}).get('has_more') == True:
            if max_comments and len(comments_list) >= max_comments:
                return comments_list
                
            new_cursor = response_data.get('data', {}).get('cursor', '')
            self.get_comments(cookies_str, ori_url, new_cursor, comments_list, max_comments)
        
        return comments_list
    
    def get_sub_comments(self,cookies_str: str,note_id: str,root_comment_id: str,cursor: str,xsec_token: str,comments_list: List[Dict],max_comments: Optional[int] = None) -> None:
        """获取子评论
        
        Args:
            cookies_str (str): Cookie字符串
            note_id (str): 笔记ID
            root_comment_id (str): 根评论ID
            cursor (str): 分页游标
            xsec_token (str): xsec_token
            comments_list (list): 评论列表
            max_comments (int, optional): 最大评论数量
        """
        uri = "/api/sns/web/v2/comment/sub/page"
        params = {
            "note_id": note_id,
            "root_comment_id": root_comment_id,
            "num": 30,
            "cursor": cursor,
            "image_formats": "jpg,webp,avif",
            "xsec_token": xsec_token,
        }
        splice_api = splice_str(uri, params)
        try:
            # 生成请求头和cookies
            headers, cookies, data = generate_request_params(cookies_str, splice_api)
            url = "https://edith.xiaohongshu.com/api/sns/web/v2/comment/sub/page"
            
            response = requests.get(url, headers=headers, cookies=cookies, params=params, impersonate="chrome110")
            response_data = response.json()
                
            if not response_data or not isinstance(response_data, dict) or 'data' not in response_data:
                logger.warning("子评论API响应数据异常")
                return
                
            sub_comments = response_data.get('data', {}).get('comments', [])
            logger.info(f"成功获取{len(sub_comments)}条子评论")
            
            for sub_comment in sub_comments:
                # 检查是否已达到最大评论数量
                if max_comments and len(comments_list) >= max_comments:
                    return
                    
                sub_format_dict = {
                    'note_id': note_id,
                    'content': sub_comment.get('content', ''),
                    'like_count': sub_comment.get('like_count', 0),
                    'nickname': sub_comment.get('user_info', {}).get('nickname', ''),
                    'comment_id': sub_comment.get('id', ''),
                    'comment_location': sub_comment.get('ip_location', ''),
                    'note_time': datetime.fromtimestamp(
                        int(int(sub_comment.get('create_time', '0'))/1000)
                    ).strftime("%Y-%m-%d %H:%M:%S")
                }
                comments_list.append(sub_format_dict)
            
            # 检查是否还有更多子评论
            if response_data.get('data', {}).get('has_more') == True:
                if max_comments and len(comments_list) >= max_comments:
                    return
                    
                new_cursor = response_data.get('data', {}).get('cursor', '')
                time.sleep(1)  # 避免请求过快
                self.get_sub_comments(
                    cookies_str,
                    note_id,
                    root_comment_id,
                    new_cursor,
                    xsec_token,
                    comments_list,
                    max_comments
                )
                
        except Exception as e:
            logger.error(f"获取子评论时发生异常: {e}")

    def download_image_with_date(self, url, save_dir="images", date_format="%Y%m%d_%H%M%S", 
                                include_original_name=False, avoid_overwrite=True):
        """下载图片并按日期命名
        
        Args:
            url (str): 图片URL
            save_dir (str): 保存目录
            date_format (str): 日期格式
            include_original_name (bool): 是否包含原文件名
            avoid_overwrite (bool): 是否避免覆盖同名文件
            
        Returns:
            bool: 下载是否成功
        """
        try:
            os.makedirs(save_dir, exist_ok=True)
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()

            # 生成基础日期部分
            timestamp = datetime.now().strftime(date_format)

            # 处理原始文件名（可选）
            original_name = ""
            if include_original_name:
                original_name = os.path.splitext(os.path.basename(url))[0]  # 去扩展名
                original_name = f"_{original_name}" if original_name else ""

            # 确定扩展名
            content_type = response.headers.get("Content-Type", "")
            ext = guess_extension(content_type.split(";")[0].strip()) or ".jpg"

            # 组合基础文件名
            base_filename = f"{timestamp}{original_name}{ext}"
            save_path = os.path.join(save_dir, base_filename)

            # 防止文件覆盖（可选）
            if avoid_overwrite:
                counter = 1
                while os.path.exists(save_path):
                    name, extension = os.path.splitext(base_filename)
                    save_path = os.path.join(save_dir, f"{name}_{counter}{extension}")
                    counter += 1

            # 保存文件
            with open(save_path, "wb") as f:
                for chunk in response.iter_content():
                    if chunk:
                        f.write(chunk)

            print(f"保存成功: {save_path}")
            return True

        except Exception as e:
            print(f"错误: {str(e)}")
            return False

    def search_notes_by_keyword(self, cookies_str, keyword, num):
        """根据关键词搜索的笔记下面的评论
        
        Args:
            keyword (str): 搜索关键词
            num (int): 搜索数量
        """
        for p in range(1000):
            uri = "/api/sns/web/v1/search/notes"
            params = {
                "keyword": keyword,
                "page": p,
                "page_size": 20,
                "search_id": generate_x_b3_traceid(21),
                "sort": "general",
                "note_type": 0,
                "ext_flags": [],
                "filters": [
                    {
                        "tags": [
                            "general"
                        ],
                        "type": "sort_type"
                    },
                    {
                        "tags": [
                            "不限"
                        ],
                        "type": "filter_note_type"
                    },
                    {
                        "tags": [
                            "不限"
                        ],
                        "type": "filter_note_time"
                    },
                    {
                        "tags": [
                            "不限"
                        ],
                        "type": "filter_note_range"
                    },
                    {
                        "tags": [
                            "不限"
                        ],
                        "type": "filter_pos_distance"
                    }
                ],
                "geo": "",
                "image_formats": [
                    "jpg",
                    "webp",
                    "avif"
                ]
            }
            
            # 这里需要实现具体的搜索逻辑
            # 暂时使用硬编码的cookies字符串
            headers, cookies, data = generate_request_params(cookies_str, uri, params)
            url = "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"
            try:
                response_obj = requests.post(url, headers=headers, cookies=cookies, data=data.encode('utf-8'))
                response = response_obj.json()
                print(f"API响应状态码: {response_obj.status_code}")
                print(f"API响应内容: {response}")
            except Exception as e:
                print(f"API请求失败: {e}")
                continue
                
            if not response or not isinstance(response, dict):
                print("API响应为空或格式错误")
                continue
                
            for item in response.get('data', {}).get('items', []):
                note_id = item.get('id')
                xsec_token = item.get('xsec_token')
                if item.get('note_card'):
                    format_dict = {
                        'title': item.get('note_card').get('display_title'),
                        'note_id': note_id,
                        'xsec_token': xsec_token,
                        'url': f'https://www.xiaohongshu.com/explore/{note_id}?xsec_token={xsec_token}&xsec_source=pc_feed'
                    }
                    print(format_dict)
                    self.note_list.append({'title': format_dict['title'], 'url': format_dict['url']})
                    if len(self.note_list) >= num:
                        return self.note_list
    
    def search_comments_by_keyword(self, cookies_str, keyword, num, comments_list: list = []):
        """根据关键词搜索的笔记下面的评论
        
        Args:
            keyword (str): 搜索关键词
            num (int): 搜索的评论数量
        """
    
        for p in range(1000):
            uri = "/api/sns/web/v1/search/notes"
            params = {
                "keyword": keyword,
                "page": 1,
                "page_size": 20,
                "search_id": generate_x_b3_traceid(21),
                "sort": "general",
                "note_type": 0,
                "ext_flags": [],
                "filters": [
                    {
                        "tags": [
                            "general"
                        ],
                        "type": "sort_type"
                    },
                    {
                        "tags": [
                            "不限"
                        ],
                        "type": "filter_note_type"
                    },
                    {
                        "tags": [
                            "不限"
                        ],
                        "type": "filter_note_time"
                    },
                    {
                        "tags": [
                            "不限"
                        ],
                        "type": "filter_note_range"
                    },
                    {
                        "tags": [
                            "不限"
                        ],
                        "type": "filter_pos_distance"
                    }
                ],
                "geo": "",
                "image_formats": [
                    "jpg",
                    "webp",
                    "avif"
                ]
            }
            
            # 将params字典转换为查询字符串
            from urllib.parse import urlencode
            query_string = urlencode(params, doseq=True)
            final_uri = f"{uri}?{query_string}"
            print(final_uri)
            
            # 这里需要实现具体的搜索逻辑
            # 暂时使用硬编码的cookies字符串
            headers, cookies, data = generate_request_params(cookies_str, uri, params)
            url = "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"
            try:
                response = requests.post(url, headers=headers, cookies=cookies, data=data.encode('utf-8')).json()
                if not response or not isinstance(response, dict) or 'data' not in response:
                    print("搜索笔记API响应数据异常，返回当前评论列表")
                    return comments_list
            except Exception as e:
                print(f"搜索笔记时发生异常: {e}，返回当前评论列表")
                return comments_list
            for item in response.get('data', {}).get('items', []):
                note_id = item.get('id')
                xsec_token = item.get('xsec_token')
                if item.get('note_card'):
                    format_dict = {
                        'title': item.get('note_card').get('display_title'),
                        'note_id': note_id,
                        'xsec_token': xsec_token,
                        'url': f'https://www.xiaohongshu.com/explore/{note_id}?xsec_token={xsec_token}&xsec_source=pc_feed'
                    }
                    print(format_dict)
                    
                    # 每爬一篇笔记，就立即爬取该笔记下的评论
                    # 计算还需要多少条评论
                    # remaining_comments = num - len(comments_list)
                    self.get_comments(cookies_str, format_dict['url'], '', comments_list, max_comments=num)
                    
                    # 如果评论列表长度超过num，就返回评论列表
                    if len(comments_list) >= num:
                        return comments_list
        
        # 如果循环结束仍未收集到足够的评论，返回已收集到的评论
        return comments_list

    def merge_note_info_with_comments(self, note_info, comments_list,userInfo,kerword):
        """将笔记信息与评论列表合并
        
        Args:
            note_info (dict): get_note_info函数返回的笔记信息字典
            comments_list (list): get_comments函数返回的评论列表
            userInfo (str): 客户标识
            
        Returns:
            list: 合并后的数据列表，每个元素包含笔记信息和单条评论信息
        """
        merged_data = []
        
        for comment in comments_list:
            # 创建合并后的数据字典
            merged_item = {
                # 笔记信息
                'keyword':kerword,
                'title': note_info.get('title', ''),
                'note_author': note_info.get('author', ''),
                'userInfo': userInfo,  # 客户标识
                'content': comment.get('content', ''),
                'likes': note_info.get('like_count', 0),
                'collects': note_info.get('collected_count', 0),
                'comments': note_info.get('comment_count', 0),
                'note_url': note_info.get('note_url', ''),
                'collect_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # 收藏时间
                'note_time': note_info.get('note_time', ''),  # 笔记创建时间
                'note_location': note_info.get('location', ''),
                'note_type': note_info.get('note_type', ''),
                
                # 评论信息
                'comment_location': comment.get('comment_location', ''),
                'comment_id': comment.get('comment_id', ''),
                'commenter_nickname': comment.get('nickname', ''),
                
                
                
            }
            merged_data.append(merged_item)
            
        return merged_data

    def get_note_info(self, cookies_str, url):
        """获取小红书笔记信息
        Args:
            cookies_str (str): Cookies字符串
            note_id (str): 笔记ID
            xsec_token (str): 安全令牌
        """
        if "discovery" in  url:
            url=convert_discovery_to_explore_url(url)
        note_params = self.extract_url_params(url)
        uri = "/api/sns/web/v1/feed"
        params = {
            "source_note_id": note_params['note_id'],
            "xsec_token": note_params['xsec_token'],
            "xsec_source": note_params['xsec_source'],
            "image_formats": [
                "jpg",
                "webp",
                "avif"
            ],
            "extra": {
                "need_body_topic": "1"
            }
        }
        # splice_api = splice_str(uri, params)
        headers, cookies, data = generate_request_params(cookies_str, uri, params)
        response = requests.post("https://edith.xiaohongshu.com"+uri, headers=headers, cookies=cookies, data=data.encode('utf-8')).json()
        
        if response.get('code') == 0 :
            info_data={
                'note_type': response.get('data', {}).get('items', {})[0].get('model_type', {}),#笔记类型
                'note_id': response.get('data', {}).get('items', {})[0].get('note_card').get('note_id', ''),  # 笔记ID
                'title': response.get('data', {}).get('items', {})[0].get('note_card').get('title', ''),  # 笔记标题
                'like_count': response.get('data', {}).get('items', {})[0].get('note_card').get('interact_info').get('liked_count', 0),  # 点赞数
                'collected_count': response.get('data', {}).get('items', {})[0].get('note_card').get('interact_info').get('collected_count', 0),  # 收藏数
                'comment_count': response.get('data', {}).get('items', {})[0].get('note_card').get('interact_info').get('comment_count', 0),  # 评论数
                'note_url': url,  # 笔记URL
                'xsec_token': note_params['xsec_token'],  # 安全令牌
                'location': response.get('data', {}).get('items', {})[0].get('note_card').get('ip_location', ''),  # 位置
                'author': response.get('data', {}).get('items', {})[0].get('note_card', {}).get('user', '').get('nickname'),  # 作者昵称
            }
            print(f"获取笔记信息成功: {info_data}")
            return info_data
        else:
            print(f"获取笔记信息失败: {response.get('message', '未知错误')}")
            return None
        print(response)
    
    def monitor_comments(self, cookies_str, note_url,userInfo,keyword, interval=60):
        """监控笔记评论变化
        Args:
            cookies_str (str): Cookies字符串
            note_url (str): 笔记URL
            userInfo (str): 客户标识
            keyword (str): 关键词
            interval (int): 检查间隔时间（秒）
        """
        #笔记基本信息
        note_info=self.get_note_info(cookies_str,note_url)
        # if note_info.get('comment_count', 0) != xxx: 如果笔记的评论数和上一次获取的评论数不同，才监控
        
          
        #笔记的评论内容
        comments_list = []
        comments_list = self.get_comments(cookies_str, note_url, comments_list=comments_list)
        print(f'一共收集到{len(comments_list)}条评论')
        merge_info = self.merge_note_info_with_comments(note_info, comments_list,userInfo,keyword)
        
        print(merge_info)
        if not comments_list:
            print("没有获取到评论")
            return None
        return merge_info
    
    def reply_comment(self,cookies_str, note_id, comment_id, content):
        """回复评论
        
        Args:
            cookies_str (str): Cookies字符串
            note_id (str): 笔记ID
            comment_id (str): 评论ID
            content (str): 回复内容
        """
        uri = "/api/sns/web/v1/comment/post"
        params = {
            "note_id": note_id,
            "target_comment_id": comment_id,
            "content": content,
            "at_users": []
        }
        
        headers, cookies, data = generate_request_params(cookies_str, uri, params)
        url = "https://edith.xiaohongshu.com/api/sns/web/v1/comment/post"
        
        response = requests.post(url, headers=headers, cookies=cookies, data=data.encode('utf-8')).json()
        print(f"回复评论请求: {response}")
        if response.get('code') == 0:
            print("回复成功")
        else:
            print(f"回复失败: {response.get('message', '未知错误')}")


    
