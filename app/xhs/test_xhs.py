"""Test script for XHS API functionality."""

import asyncio
from .xhs_api import XhsAPI
from .services import XhsService


async def test_url_extraction():
    """测试URL参数提取功能"""
    api = XhsAPI()
    
    # 测试explore URL
    explore_url = "https://www.xiaohongshu.com/explore/64f8a1b2000000001e00c123?xsec_token=ABtest123&xsec_source=pc_search"
    params = api.extract_url_params(explore_url)
    print(f"Explore URL参数: {params}")
    
    # 测试discovery URL转换
    discovery_url = "https://www.xiaohongshu.com/discovery/item/64f8a1b2000000001e00c123?xsec_token=ABtest123"
    converted_url = api._convert_discovery_to_explore_url(discovery_url)
    print(f"转换后的URL: {converted_url}")
    
    converted_params = api.extract_url_params(converted_url)
    print(f"转换后URL参数: {converted_params}")


async def test_request_params_generation():
    """测试请求参数生成功能"""
    api = XhsAPI()
    
    # 模拟cookies字符串
    cookies_str = "sessionid=test123; userid=user456; token=abc789"
    uri = "/api/sns/web/v2/comment/page"
    params = {
        "note_id": "64f8a1b2000000001e00c123",
        "cursor": "",
        "top_comment_id": "",
        "image_formats": "jpg,webp,avif",
        "xsec_token": "ABtest123"
    }
    
    headers, cookies, data = api._generate_request_params(cookies_str, uri, params)
    
    print("生成的请求头:")
    for key, value in headers.items():
        print(f"  {key}: {value}")
    
    print("\n解析的Cookies:")
    for key, value in cookies.items():
        print(f"  {key}: {value}")
    
    print(f"\n请求数据: {data}")


async def test_service_functions():
    """测试服务层功能"""
    service = XhsService()
    
    # 测试笔记信息获取
    note_url = "https://www.xiaohongshu.com/explore/64f8a1b2000000001e00c123?xsec_token=ABtest123&xsec_source=pc_search"
    note_info = await service.get_note_info("test_cookies", note_url)
    print(f"笔记信息: {note_info}")
    
    await service.close()


if __name__ == "__main__":
    print("=== 测试URL参数提取 ===")
    asyncio.run(test_url_extraction())
    
    print("\n=== 测试请求参数生成 ===")
    asyncio.run(test_request_params_generation())
    
    print("\n=== 测试服务层功能 ===")
    asyncio.run(test_service_functions())
    
    print("\n测试完成！")