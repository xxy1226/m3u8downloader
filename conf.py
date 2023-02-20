import os, json

conf_folder = os.path.join(os.getcwd(),'m3u8下载器设置').replace('\\', '/')
conf_file = os.path.join(conf_folder,'download.cfg').replace('\\', '/')
langs_file = os.path.join(conf_folder,'langs.json').replace('\\', '/')
default_cfg = {
    'dfolder':os.getcwd(),
    'max_thread':10,
    'remove_ts':True,
    'headers':{'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',},
    'downloading':{},
    'lang':'en-us'
}
default_langs = {
    'en-us':{
        'lang':'English',
        'master_title':'m3u8 Downloader',
        'frame_url':'1. Specify m3u8 File',
    },
    'zh-cn':{
        'lang':'中文',
        'master_title':'m3u8 下载器',
        'frame_url':'1. 指定 m3u8 文件',
    },
}

def write_conf(data: dict) -> None:
    '''将设置数据写入文件
    
    :param data: dict 格式的设置数据
    '''
    with open(conf_file, 'w') as f:
        json.dump(data, f)
    
def get_conf() -> json:
    '''读取设置文件，并将缺失的设置文件补全
    
    :return: json 格式的设置数据
    '''
    rewrite = False
    with open(conf_file, 'r') as f:
        data = json.load(f)
        if 'dfolder' not in data:
            data['dfolder'] = default_cfg['dfolder']
            rewrite = True
        if 'max_thread' not in data:
            data['max_thread'] = 10
            rewrite = True
        else:
            try:
                max_thread = int(data['max_thread'])
            except ValueError:
                data['max_thread'] = default_cfg['max_thread']
                rewrite = True
            else:
                if max_thread <= 0:
                    data['max_thread'] = default_cfg['max_thread']
                    rewrite = True
        if 'remove_ts' not in data:
            data['remove_ts'] = default_cfg['remove_ts']
            rewrite = True
        if 'headers' not in data:
            data['headers'] = default_cfg['headers']
            rewrite = True
        if 'downloading' not in data:
            data['downloading'] = default_cfg['downloading']
            rewrite = True
        if 'lang' not in data:
            data['lang'] = default_cfg['lang']
            rewrite = True
    if rewrite:
        write_conf(data)
    return data

def write_langs(langs: dict = default_langs) -> None:
    '''写入语言文件
    
    :parram langs: dict
    '''
    with open(langs_file, 'w') as f:
        json.dump(langs, f)

def get_langs() -> json:
    '''返回语言数据
    
    :return: json 格式的语言数据
    '''
    with open(langs_file, 'r') as f:
        langs = json.load(f)
    return langs


def check_config_folder():
    '''检查当前文件夹中是否存在存放设置文件的文件夹
    如果不存在就创建该文件夹
    检查设置文件夹中是否有设置文件
    如果不存在就创建该文件    
    '''
    if not os.path.isdir(conf_folder):
        os.mkdir(conf_folder)
    if not os.path.isfile(conf_file):
        write_conf(default_cfg)
    if not os.path.isfile(langs_file):
        write_langs(default_langs)

check_config_folder()

if __name__ == '__main__':
    pass