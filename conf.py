import os, json

conf_folder = os.path.join(os.getcwd(),'m3u8_conf').replace('\\', '/')
conf_file = os.path.join(conf_folder,'download.cfg').replace('\\', '/')
langs_file = os.path.join(conf_folder,'langs.json').replace('\\', '/')
default_cfg = {
    'dfolder':os.getcwd(),
    'max_thread':20,
    'remove_ts':True,
    'headers':{'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',},
    'downloading':{},
    'lang':'English'
}
default_langs = {
    'Русский':{
        'lang':'ru-ru',
        'master_title':'m3u8 Скачиватель',
        'frame_url':'1. Укажите файл m3u8',
        'label_urlpath':'Веб-адрес / URL-адрес m3u8 / Локальный путь к файлу m3u8',
        'button_local_file':'m3u8 файл',
        'button_analyze':'Анализ',
        'label_url2':'Выберите m3u8: нажмите, отредактировать / дважды щелкните, загрузить напрямую (сначала заполните Скачать настройки)',
        'frame_edit':'2. Отредактируйте m3u8 (необязательно)',
        'button_goto_time':'Перейти ко времени',
        'button_prefix':'Добавить доменное',
        'button_remove_ad':'Удалить рекламу',
        'button_reedit':'Перезагрузить',
        'button_confirm_edit':'Сохранять',
        'frame_dconfig':'3. Скачать настройки',
        'label_thread':'Макс потоков',
        'label_note_thread':'* Большое количество НЕ рекомендуется',
        'check_keepfile':'Хранить временные файлы',
        'button_vname':'Файл видео',
        'button_reset_all':'Сбросить',
        'button_download':'Скачать',
        '':'',
    },
    'English':{
        'lang':'en-us',
        'master_title':'m3u8 Downloader',
        'frame_url':'1. Specify m3u8 File',
        'label_urlpath':'Web address / URL of m3u8 / Local path to m3u8 file',
        'button_local_file':'Local file',
        'button_analyze':'Analyze',
        'label_url2':'Select the m3u8 file: Click to edit / Double click to download directly (make sure to complete the download settings)',
        'frame_edit':'2. Edit m3u8 (optional)',
        'button_goto_time':'Jump to time',
        'button_prefix':'Add prefix/domain',
        'button_remove_ad':'Remove ads',
        'button_reedit':'Reset edit',
        'button_confirm_edit':'Save',
        'frame_dconfig':'3. Download Settings',
        'label_thread':'Max threads',
        'label_note_thread':'* Large number is NOT recommended',
        'check_keepfile':'Keep temporary files',
        'button_vname':'Video name',
        'button_reset_all':'Reset all',
        'button_download':'Download',
        '':'',
    },
    '中文':{
        'lang':'zh-cn',
        'master_title':'m3u8 下载器',
        'frame_url':'1. 指定 m3u8 文件',
        'label_urlpath':'输入网址/m3u8文件URL/本地m3u8文件路径',
        'button_local_file':'本地m3u8文件',
        'button_analyze':'分析',
        'label_url2':'选择 m3u8 文件： 单击可编辑 / 双击直接下载（先确保完成下载设置）',
        'frame_edit':'2. 编辑 m3u8 内容（可选）',
        'button_goto_time':'跳到指定时间',
        'button_prefix':'增加前缀/域名',
        'button_remove_ad':'去除外站广告',
        'button_reedit':'重置',
        'button_confirm_edit':'确认修改',
        'frame_dconfig':'3. 下载设置',
        'label_thread':'最大线程数',
        'label_note_thread':'* 线程数不建议设太大',
        'check_keepfile':'合并后保留临时文件',
        'button_vname':'视频名称',
        'button_reset_all':'全部重置',
        'button_download':'下载视频',
        '':'',
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