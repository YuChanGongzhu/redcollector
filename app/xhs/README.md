# XHS API 模块

这个模块集成了小红书（Xiaohongshu）API功能，提供了获取评论、搜索笔记等接口。

## 功能特性

- 🔍 **搜索笔记**: 根据关键词搜索小红书笔记
- 💬 **获取评论**: 获取指定笔记的评论列表（包括子评论）
- 🔄 **URL转换**: 支持discovery和explore URL格式转换
- 📊 **批量处理**: 支持批量获取评论和搜索
- 📁 **数据导出**: 支持将评论数据导出为CSV格式
- ⚡ **异步处理**: 全异步实现，支持高并发

## API 接口

### 1. 获取评论

**POST** `/xhs/comments`

```json
{
  "cookies": "your_cookies_string",
  "note_url": "https://www.xiaohongshu.com/explore/note_id",
  "max_comments": 100,
  "cursor": ""
}
```

### 2. 搜索笔记

**POST** `/xhs/search`

```json
{
  "cookies": "your_cookies_string",
  "keyword": "搜索关键词",
  "num": 20
}
```

### 3. URL转换

**POST** `/xhs/convert-url`

```json
{
  "url": "https://www.xiaohongshu.com/discovery/item/note_id"
}
```

### 4. 批量获取评论

**POST** `/xhs/comments/batch`

```json
[
  {
    "cookies": "your_cookies_string",
    "note_url": "https://www.xiaohongshu.com/explore/note_id_1",
    "max_comments": 50
  },
  {
    "cookies": "your_cookies_string",
    "note_url": "https://www.xiaohongshu.com/explore/note_id_2",
    "max_comments": 50
  }
]
```

### 5. 批量搜索

**POST** `/xhs/search/batch`

```json
[
  {
    "cookies": "your_cookies_string",
    "keyword": "关键词1",
    "num": 20
  },
  {
    "cookies": "your_cookies_string",
    "keyword": "关键词2",
    "num": 20
  }
]
```

### 6. 健康检查

**GET** `/xhs/health`

## 使用示例

### Python 客户端示例

```python
import httpx
import asyncio

async def get_comments_example():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/xhs/comments",
            json={
                "cookies": "your_cookies_here",
                "note_url": "https://www.xiaohongshu.com/explore/64f8a1b2000000001e00c123",
                "max_comments": 50
            }
        )
        result = response.json()
        print(f"获取到 {len(result['data'])} 条评论")
        return result

async def search_notes_example():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/xhs/search",
            json={
                "cookies": "your_cookies_here",
                "keyword": "美食",
                "num": 10
            }
        )
        result = response.json()
        print(f"搜索到 {len(result['data'])} 条笔记")
        return result

# 运行示例
asyncio.run(get_comments_example())
asyncio.run(search_notes_example())
```

### cURL 示例

```bash
# 获取评论
curl -X POST "http://localhost:8000/xhs/comments" \
  -H "Content-Type: application/json" \
  -d '{
    "cookies": "your_cookies_here",
    "note_url": "https://www.xiaohongshu.com/explore/64f8a1b2000000001e00c123",
    "max_comments": 50
  }'

# 搜索笔记
curl -X POST "http://localhost:8000/xhs/search" \
  -H "Content-Type: application/json" \
  -d '{
    "cookies": "your_cookies_here",
    "keyword": "美食",
    "num": 10
  }'
```

## 响应格式

### 成功响应

```json
{
  "success": true,
  "message": "操作成功",
  "data": [
    {
      "content": "评论内容",
      "like_count": 10,
      "nickname": "用户昵称",
      "comment_id": "comment_123",
      "comment_location": "北京",
      "note_time": "2024-01-01 12:00:00"
    }
  ]
}
```

### 错误响应

```json
{
  "detail": "错误信息描述"
}
```

## 注意事项

1. **Cookies获取**: 需要从浏览器中获取有效的小红书cookies
2. **请求频率**: 建议控制请求频率，避免被限制
3. **数据合规**: 请遵守小红书的使用条款和数据使用规范
4. **错误处理**: API会返回详细的错误信息，请根据错误信息进行调试

## 依赖包

- `httpx`: HTTP客户端
- `loguru`: 日志记录
- `pydantic`: 数据验证
- `fastapi`: Web框架

## 测试

运行测试脚本：

```python
from app.xhs.test_xhs import *

# 测试URL参数提取
await test_url_extraction()

# 测试请求参数生成
await test_request_params_generation()

# 测试服务层功能
await test_service_functions()
```

## 扩展功能

模块设计支持以下扩展：

- 添加更多小红书API接口
- 实现数据持久化存储
- 添加数据分析功能
- 集成机器学习模型
- 支持实时数据流处理