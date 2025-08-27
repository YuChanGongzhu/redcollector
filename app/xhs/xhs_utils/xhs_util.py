import json
import math
import random
import execjs
import requests
from loguru import logger
import os
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode

# 获取当前文件的目录
current_dir = Path(__file__).parent
static_dir = current_dir.parent / 'static'
xhs_dir = current_dir.parent  # app/xhs 目录，包含 node_modules

# 配置 execjs 使用 Node.js
os.environ['EXECJS_RUNTIME'] = 'Node'

# 加载JavaScript文件
try:
    js_file_path = static_dir / 'xhs_xs_xsc_56.js'
    logger.info(f"Loading JavaScript file: {js_file_path}")
    
    # 保存当前工作目录
    original_cwd = os.getcwd()
    try:
        # 切换到包含 node_modules 的目录
        os.chdir(str(xhs_dir))
        logger.info(f"Changed working directory to: {xhs_dir}")
        
        with open(js_file_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
            js = execjs.compile(js_content)
        logger.info("Successfully loaded xhs_xs_xsc_56.js")
    finally:
        # 恢复原始工作目录
        os.chdir(original_cwd)
except Exception as e:
    logger.error(f"Failed to load xhs_xs_xsc_56.js: {e}")
    js = None

try:
    xray_file_path = static_dir / 'xhs_xray.js'
    logger.info(f"Loading JavaScript file: {xray_file_path}")
    
    # 保存当前工作目录
    original_cwd = os.getcwd()
    try:
        # 切换到包含 node_modules 的目录
        os.chdir(str(xhs_dir))
        
        with open(xray_file_path, 'r', encoding='utf-8') as f:
            xray_content = f.read()
            xray_js = execjs.compile(xray_content)
        logger.info("Successfully loaded xhs_xray.js")
    finally:
        # 恢复原始工作目录
        os.chdir(original_cwd)
except Exception as e:
    logger.error(f"Failed to load xhs_xray.js: {e}")
    xray_js = None

def generate_x_b3_traceid(len=16):
    x_b3_traceid = ""
    for t in range(len):
        x_b3_traceid += "abcdef0123456789"[math.floor(16 * random.random())]
    return x_b3_traceid

def generate_xs_xs_common(a1, api, data=''):
    original_cwd = os.getcwd()
    try:
        os.chdir(str(xhs_dir))
        ret = js.call('get_request_headers_params', api, data, a1)
        xs, xt, xs_common = ret['xs'], ret['xt'], ret['xs_common']
        return xs, xt, xs_common
    finally:
        os.chdir(original_cwd)

def generate_xs(a1, api, data=''):
    original_cwd = os.getcwd()
    try:
        os.chdir(str(xhs_dir))
        ret = js.call('get_xs', api, data, a1)
        xs, xt = ret['X-s'], ret['X-t']
        return xs, xt
    finally:
        os.chdir(original_cwd)

def generate_xray_traceid():
    original_cwd = os.getcwd()
    try:
        os.chdir(str(xhs_dir))
        return xray_js.call('traceId')
    finally:
        os.chdir(original_cwd)
def get_common_headers():
    return {
        "authority": "www.xiaohongshu.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": "https://www.xiaohongshu.com/",
        "sec-ch-ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Google Chrome\";v=\"122\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
def get_request_headers_template():
    return {
        "authority": "edith.xiaohongshu.com",
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cache-control": "no-cache",
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://www.xiaohongshu.com",
        "pragma": "no-cache",
        "referer": "https://www.xiaohongshu.com/",
        "sec-ch-ua": "\"Not A(Brand\";v=\"99\", \"Microsoft Edge\";v=\"121\", \"Chromium\";v=\"121\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
        "x-b3-traceid": "",
        "x-mns": "unload",
        "x-s": "",
        "x-s-common": "",
        "x-t": "",
        "x-xray-traceid": generate_xray_traceid()
    }

def generate_headers(a1, api, data=''):
    xs, xt, xs_common = generate_xs_xs_common(a1, api, data)
    x_b3_traceid = generate_x_b3_traceid()
    headers = get_request_headers_template()
    headers['x-s'] = xs
    headers['x-t'] = str(xt)
    headers['x-s-common'] = xs_common
    headers['x-b3-traceid'] = x_b3_traceid
    if data:
        data = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    return headers, data

def generate_request_params(cookies_str, api, data=''):
    """生成请求参数，包括headers、cookies和data"""
    if js is None:
        raise Exception("JavaScript engine not available")
    
    cookies = trans_cookies(cookies_str)
    print(f'Cookies: {cookies}')
    logger.info(f'Cookies: {cookies}')
    a1 = cookies.get('a1')
    if not a1:
        raise Exception("Missing a1 cookie")
    
    headers, data = generate_headers(a1, api, data)
    return headers, cookies, data

def splice_str(api, params):
    url = api + '?'
    for key, value in params.items():
        if value is None:
            value = ''
        url += key + '=' + str(value) + '&'
    return url[:-1]

def trans_cookies(cookies_str):
    if '; ' in cookies_str:
        ck = {i.split('=')[0]: '='.join(i.split('=')[1:]) for i in cookies_str.split('; ')}
    else:
        ck = {i.split('=')[0]: '='.join(i.split('=')[1:]) for i in cookies_str.split(';')}
    return ck


def convert_discovery_to_explore_url(discovery_url):
    """将discovery格式的URL转换为explore格式
    
    Args:
        discovery_url (str): discovery格式的小红书链接
        
    Returns:
        str: explore格式的小红书链接，只保留xsec_source、type、xsec_token参数
        
    Example:
        输入: https://www.xiaohongshu.com/discovery/item/6851829e000000002102cb05?app_platform=android&xsec_source=app_share&type=normal&xsec_token=CBdXOVVtUIw-vYe_hwvxF7T9SFM2KAdwiE2MWDtPM_1kM%3D&author_share=1
        输出: https://www.xiaohongshu.com/explore/6851829e000000002102cb05?xsec_source=app_share&type=normal&xsec_token=CBdXOVVtUIw-vYe_hwvxF7T9SFM2KAdwiE2MWDtPM_1kM%3D
    """
    try:
        parsed = urlparse(discovery_url)
        
        # 提取note_id
        path_segments = parsed.path.strip("/").split("/")
        if len(path_segments) >= 3 and path_segments[0] == "discovery" and path_segments[1] == "item":
            note_id = path_segments[2]
        else:
            raise ValueError("无效的discovery URL格式")
        
        # 解析查询参数
        query_params = parse_qs(parsed.query)
        
        # 只保留需要的参数
        filtered_params = {}
        for param in ['xsec_source', 'type', 'xsec_token']:
            if param in query_params:
                filtered_params[param] = query_params[param][0]  # 取第一个值
        
        # 构建新的explore URL
        explore_url = f"https://www.xiaohongshu.com/explore/{note_id}"
        if filtered_params:
            explore_url += "?" + urlencode(filtered_params)
        
        return explore_url
        
    except Exception as e:
        print(f"URL转换失败: {e}")
        return None

if __name__ == "__main__":
    url = "https://edith.xiaohongshu.com/api/sns/web/v2/comment/sub/page"
    
    uri = "/api/sns/web/v2/comment/sub/page"
    params = {
        "note_id": "68a82bc8000000001c03088f",
        "root_comment_id": "68ae445e00000000020163fe",
        "num": "10",
        "cursor": "68ae521a000000003001ef81",
        "image_formats": "jpg,webp,avif",
        "top_comment_id": "",
        "xsec_token": "ABWmWAhF3QlQxwg9n6BrMOf4O2bepBjy_pcl3gq5hDVhM="
    }
    splice_api = splice_str(uri, params)
    print(splice_api)
    # 生成请求头和cookies
    headers, cookies, data = generate_request_params("abRequestId=a134c493-a50b-5252-8195-a01326efae1d; xsecappid=xhs-pc-web; a1=198e57d295fg07uahm6bp5xp5nt6lcmtu186wsvk450000118915; webId=5a190424236156d2c3ae27aff8b1b745; gid=yjYd2WdyyK74yjYd2WfJjyMh2ik8W70x6KDUYT42CU2I9K28K1S69E888yyYjy284WyDWydY; webBuild=4.77.0; web_session=040069b9593484798b5f72219b3a4b14702e02; unread={%22ub%22:%2268ad8992000000001d004807%22%2C%22ue%22:%2268ae668b000000001c03c6aa%22%2C%22uc%22:29}; loadts=1756260885388; acw_tc=0ad5826817562627015413651e8fa04cee7cbc2b83e28db562747196fbad80; websectiga=cffd9dcea65962b05ab048ac76962acee933d26157113bb213105a116241fa6c; sec_poison_id=ecbbbe4f-f0a1-492f-8238-117888366b69", splice_api)
    url = "https://edith.xiaohongshu.com/api/sns/web/v2/comment/sub/page"
    print(headers)
    final_uri = f"{uri}?" f"{urlencode(params)}"
    response = requests.get(url=f"https://edith.xiaohongshu.com{splice_api}", cookies=cookies, headers=headers)
    print(f"https://edith.xiaohongshu.com{splice_api}")
    response_data = response.json()


    print(response.text)
    print(response)