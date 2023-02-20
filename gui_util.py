from re import compile, S
import os, json
from tkinter import messagebox
from conf import get_conf, get_langs

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
    data = get_conf()
    return data['dfolder'], data['max_thread'], data['remove_ts'], data['headers'], data['downloading'], data['lang']

def find_m3u8s(text: str) -> list:
    """在网页中寻找 m3u8 文件
    
    :param text: 网页源码
    """
    tarstr1 = r"<script>.*'(?P<m3u8link>.*?).m3u8'"
    obj1 = compile(tarstr1, S)
    rows1 = obj1.finditer(text)
    tarstr2 = r'<script>.*"(?P<m3u8link>.*?).m3u8"'
    obj2 = compile(tarstr2, S)
    rows2 = obj2.finditer(text)
    whole_list = []
    for it in rows1:
        whole_list.append(it.group("m3u8link")+'.m3u8')
    for it in rows2:
        whole_list.append(it.group("m3u8link")+'.m3u8')
    return whole_list

def read_m3u8(path: str) -> list[str]:
    """读取 m3u8 文件
    
    :param path: 文件路径
    :return: 返回文本内容的列表，以行分割 
    """
    if os.path.isfile(path):
        with open(path, 'r') as f:
            return f.readlines()
    else: return
    
if __name__ == '__main__':
    m3u8 = read_m3u8('index.m3u8')
    if m3u8:
        print(m3u8)
    else:
        print('File not found!')