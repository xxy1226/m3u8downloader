import re
import os, json
from requests import get
from tkinter import messagebox
from conf import get_conf, get_langs

data = get_conf()
# data['dfolder'], data['max_thread'], data['remove_ts'], data['headers'], data['downloading'], data['lang']

def download(url: str, name: str = None) -> str:
    '''从 url 下载内容。
    如果指定文件名则保存至文件，
    否则返回内容。
    
    :return: '[OK]': 内容写入文件
    :return: '[Err]message': 下载不成功
    :return: 下载的内容
    '''
    # 如果文件已下载，则什么也不做
    if name and os.path.isfile(name): return
    code504, retry = 0, 0
    while True:
        try:
            r = get(url, headers=data['headers'], timeout=15)
            if r.ok:
                r.encoding = 'utf-8'
                if name:
                    with open(name, 'wb') as f:
                        f.write(r.content)
                        return '[OK]'
                else:
                    return r.text
            elif r.status_code == 504:
                code504 += 1
                if code504 == 3:
                    return '[Err]err_504'
            elif r.status_code == 404:
                return '[Err]err_404'
            elif retry > 10:
                return '[Err]Error: downloading ' + url
        except:
            retry += 1
    

def load_langs() -> json:
    return get_langs()

def get_config() -> tuple:
    """返回 视频下载文件夹、最大线程数 和 headers
    
    :return dfolder: str 格式下载文件夹路径
    :return max_thread: int 格式最大线程数
    :return remove_ts: bool 格式删除临时文件夹
    :return headers: 字典 格式 HTTP 请求的 headers
    :return downloading: 字典 格式的下载中断的记录
    :return lang: str 选择的语言
    """
    return data['dfolder'], data['max_thread'], data['remove_ts'], data['headers'], data['downloading'], data['lang']

def validate_m3u8(url: str) -> dict[list] | str:
    '''通过 url 获取并验证 m3u8。
    如果没有视频内容，找到 m3u8 信息重新获取并验证 m3u8。
    
    :return: {url: m3u8内容列表，以行分割}
    '''
    content = download(url)
    if content[0] == '[': return content
    if 'ts' not in content:
        uri = False
        for line in content.split():
            if 'm3u8' in line:
                if line.find('http') != 0 and not uri:
                    uri = url[:url.find(line[:6])]
                return validate_m3u8(uri + line)
    value = re.split('(\n)', content)
    print('value', len(value))
    for i in range(len(value)-1, 0, -1):
        print(len(value[i]))
        if len(value[i]) <= 1:
            print('remove', value[i])
            value.pop(i)
    return {url: value}

def find_m3u8s_web(content: str) -> list[dict[list]]:
    """在网页中寻找 m3u8 文件
    
    :param content: 网页源码
    :return: 找到的所有包含视频的 m3u8 的列表
    """
    whole_list = []
    if '.m3u8"' in content or ".m3u8'" in content:
        tarstr1 = r"<script>.*'(?P<m3u8link>.*?).m3u8'"
        obj1 = re.compile(tarstr1, re.S)
        rows1 = obj1.finditer(content)
        tarstr2 = r'<script>.*"(?P<m3u8link>.*?).m3u8"'
        obj2 = re.compile(tarstr2, re.S)
        rows2 = obj2.finditer(content)
        for it in rows1:
            m3u8 = validate_m3u8(it.group("m3u8link")+'.m3u8')
            if isinstance(m3u8, str) and m3u8[0] == '[': return m3u8
            whole_list.append(m3u8)
        for it in rows2:
            m3u8 = validate_m3u8(it.group("m3u8link")+'.m3u8')
            if isinstance(m3u8, str) and m3u8[0] == '[': return m3u8
            whole_list.append(m3u8)
    return whole_list
    
    

def read_m3u8(path: str) -> None | list[str]:
    """读取 m3u8 文件
    
    :param path: 文件路径
    :return: 返回文本内容的列表，以行分割 
    """
    if os.path.isfile(path):
        with open(path, 'r') as f:
            return f.readlines()
    else: return

def analyze_m3u8(content: list) -> dict:
    '''分析 m3u8 内容以得到：
        id(str)
        content(list)内容
        time(int)累计时间
    '''
    d = {}
    d['time'] = []
    for line in content:
        t = 0.0
        if '#EXTINF:' in line:
            t = float(line[line.rfind(':')+1:line.rfind(',')])
        d['time'].append(t if len(d['time']) == 0 else t + d['time'][-1])
    return d


def download_video(m3u8: str, video_folder, video_name, max_thread, headers):
    '''输入 m3u8 内容，下载并合并视频
    
    :param m3u8: str m3u8文件的内容
    :param video_folder: str 目标文件夹路径
    :param video_name: str 目标文件名
    :param max_thread: int 最大线程数
    :param headers: dict HTTP请求头
    '''
    # with open(os.path.join())
    pass

def merge_tss(merge_m3u8: str, filename: str) -> None | str:
    if os.path.isfile(filename):
        os.remove(filename)
    command = 'ffmpeg -allowed_extensions ALL -i "'+ merge_m3u8.replace('\\', '/') + '" -c copy "' + filename.replace('\\', '/') + '.mp4"'
    os.system('cmd /c "'+command+'"')

if __name__ == '__main__':
    m3u8 = read_m3u8('testfiles/short2.m3u8')
    if m3u8:
        print(m3u8)
    else:
        print('File not found!')