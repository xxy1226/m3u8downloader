from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox

import os, sys, time
from requests import get
from threading import Thread
from re import compile, S
from shutil import rmtree

from gui_util import *

# 默认设置
name_replace = ['\\','/','"','<','>','|',':','*','?','『','』']

# 初始化
download_folder, max_thread, remove_ts, headers, downloading, lang = get_config()
langs=load_langs()

class M3u8Downloader:
    
    widget_list = [] # 在分析之前需要禁用的一般组件
    treeview_list = [] # 在分析之前需要禁用的 treeview 组件
    m3u8_analyzed = {} # 包含 m3u8 id(str)、content(list)内容、time(int)累计时间、dfolder(str)曾经的使用的文件夹
    lang_list = {} # 用于切换语言的组件
    previous_analyze = ''
    use_lang = langs[lang]

    def __init__(self, master):
        # 初始设置
        master.title(self.use_lang['master_title'])
        master.minsize(800, 600)

        self.style = ttk.Style()
        # self.style.configure('TFrame', background='#e1d8b9')

        # 框架1：用户输入下载地址或本地地址，选择要下载的m3u8文件
        self.frame_url = ttk.LabelFrame(master, text=self.use_lang['frame_url'], padding=5)
        self.frame_url.grid(row=0, column=0, padx=10, pady=10, sticky='we')
        self.lang_list['frame_url'] = self.frame_url

        # 框架1.1：用户输入下载地址或本地地址
        self.subframe_url1 = ttk.Frame(self.frame_url)
        self.subframe_url1.pack()
        self.label_urlpath = ttk.Label(self.subframe_url1, text=self.use_lang['label_urlpath'])
        self.label_urlpath.grid(row=0, column=0, columnspan=3, sticky='w')
        self.lang_list['label_urlpath'] = self.label_urlpath

        self.button_lang = ttk.Menubutton(self.subframe_url1, text=lang, width=7)
        self.button_lang.grid(row=0, column=3, sticky='e')
        self.menu_langs = Menu(self.button_lang, tearoff=False)
        lang_commands = {}
        for language in langs:
            self.menu_langs.add_command(label=language, command=lambda l=language:self.change_lang(l, master))
        self.button_lang.config(menu=self.menu_langs)

        self.button_local_file = ttk.Button(self.subframe_url1, style='Colored.TButton', text=self.use_lang['button_local_file'], command=self.local_m3u8, width=14)
        self.button_local_file.grid(row=1, column=0)
        self.lang_list['button_local_file'] = self.button_local_file
        self.entry_urlpath = ttk.Entry(self.subframe_url1, width=95)
        self.entry_urlpath.grid(row=1, column=1)
        self.entry_urlpath.bind('<Return>', lambda e:self.analyze())
        self.button_analyze = ttk.Button(self.subframe_url1, text=self.use_lang['button_analyze'], width=11, command=self.analyze)
        self.button_analyze.grid(row=1, column=3)
        self.lang_list['button_analyze'] = self.button_analyze
        
        # 框架1.2：分析找到的 m3u8 地址
        self.subframe_url2 = ttk.Frame(self.frame_url)
        self.subframe_url2.pack(pady=5)
        self.label_url2 = ttk.Label(self.subframe_url2, text=self.use_lang['label_url2'])
        self.label_url2.grid(row=0, column=0, sticky='w')
        self.lang_list['label_url2'] = self.label_url2
        self.found_m3u8 = ttk.Treeview(self.subframe_url2, height=3, show='tree', selectmode=BROWSE)
        self.treeview_list.append(self.found_m3u8)
        self.found_m3u8.column('#0', width=724)
        self.found_m3u8['columns'] = ('content')
        self.found_m3u8['displaycolumns'] = []
        self.found_m3u8.grid(row=1, column=0, rowspan=3, columnspan=2, sticky='e')
        self.found_m3u8.bind('<<TreeviewSelect>>', self.click_found_m3u8)
        self.found_m3u8.bind('<Double-Button-1>', self.double_click_found_m3u8)
        self.found_m3u8_scrollbar = ttk.Scrollbar(self.subframe_url2, orient = VERTICAL, command=self.found_m3u8.yview)
        self.found_m3u8_scrollbar.grid(row=1, column=2, rowspan=3, sticky='ns')
        self.found_m3u8.config(yscrollcommand=self.found_m3u8_scrollbar.set)
        
        # 框架2：编辑 m3u8
        self.frame_edit = ttk.LabelFrame(master, text=self.use_lang['frame_edit'], padding=5)
        self.frame_edit.grid(row=1, column=0, padx=10, sticky='we')
        self.lang_list['frame_edit'] = self.frame_edit
        
        # 框架2.1：m3u8 文本内容
        self.subframe_edit1 = ttk.Frame(self.frame_edit)
        self.subframe_edit1.grid(row=0, column=0, padx=10, pady=5, sticky='wens')
        self.text_m3u8 = Text(self.subframe_edit1, width=63, height=15, font=('Arial', 12), wrap=NONE)
        self.text_m3u8.grid(row=0, column=0)
        self.text_m3u8_vscrollbar = ttk.Scrollbar(self.subframe_edit1, orient = VERTICAL, command=self.text_m3u8.yview)
        self.text_m3u8_vscrollbar.grid(row=0, column=1, sticky='ns')
        self.text_m3u8.config(yscrollcommand=self.text_m3u8_vscrollbar.set)
        self.text_m3u8_hscrollbar = ttk.Scrollbar(self.subframe_edit1, orient = HORIZONTAL, command=self.text_m3u8.xview)
        self.text_m3u8_hscrollbar.grid(row=1, column=0, sticky='we')
        self.text_m3u8.config(xscrollcommand=self.text_m3u8_hscrollbar.set)
        
        # 框架2.2：编辑功能按键
        self.subframe_edit2 = ttk.Frame(self.frame_edit, padding=5)
        self.subframe_edit2.grid(row=0, column=1, sticky='wens')

        self.subsubframe_edit2_time = ttk.Frame(self.subframe_edit2)
        self.subsubframe_edit2_time.grid(row=0, column=0, pady=10, sticky='we')
        self.entry_time_hour = ttk.Entry(self.subsubframe_edit2_time, width=4)
        self.entry_time_hour.grid(row=0, column=0)
        Label(self.subsubframe_edit2_time, text=':').grid(row=0, column=1)
        self.entry_time_minute = ttk.Entry(self.subsubframe_edit2_time, width=4)
        self.entry_time_minute.grid(row=0, column=2)
        Label(self.subsubframe_edit2_time, text=':').grid(row=0, column=3)
        self.entry_time_second = ttk.Entry(self.subsubframe_edit2_time, width=4)
        self.entry_time_second.grid(row=0, column=4)
        self.button_goto_time = ttk.Button(self.subsubframe_edit2_time, text=self.use_lang['button_goto_time'], padding=5, width=18)
        self.button_goto_time.grid(row=1, column=0, columnspan=5)
        self.lang_list['button_goto_time'] = self.button_goto_time
        self.button_goto_time.state([DISABLED])

        self.subsubframe_edit2_prefix = ttk.Frame(self.subframe_edit2)
        self.subsubframe_edit2_prefix.grid(row=2, column=0, pady=10, sticky='wens')
        self.entry_prefix = ttk.Entry(self.subsubframe_edit2_prefix)
        self.entry_prefix.grid(row=0, column=0, sticky='wens')
        self.button_prefix = ttk.Button(self.subsubframe_edit2_prefix, text=self.use_lang['button_prefix'], padding=5)
        self.button_prefix.grid(row=1, column=0, sticky='wens', columnspan=5)
        self.lang_list['button_prefix'] = self.button_prefix
        self.button_prefix.state([DISABLED])

        self.button_remove_ad = ttk.Button(self.subframe_edit2, text=self.use_lang['button_remove_ad'], padding=5)
        self.button_remove_ad.grid(row=3, column=0, pady=5, sticky='wens')
        self.lang_list['button_remove_ad'] = self.button_remove_ad
        self.button_remove_ad.state([DISABLED])

        self.button_reedit = ttk.Button(self.subframe_edit2, text=self.use_lang['button_reedit'], padding=5, command=self.click_found_m3u8)
        self.button_reedit.grid(row=4, column=0, pady=5, sticky='wens')
        self.lang_list['button_reedit'] = self.button_reedit
        self.button_confirm_edit = ttk.Button(self.subframe_edit2, text=self.use_lang['button_confirm_edit'], padding=5)
        self.button_confirm_edit.grid(row=5, column=0, pady=5, sticky='wens')
        self.lang_list['button_confirm_edit'] = self.button_confirm_edit
        
        # 框架3：下载设置
        self.frame_dconfig = ttk.LabelFrame(master, text=self.use_lang['frame_dconfig'], padding=5)
        self.frame_dconfig.grid(row=2, column=0, padx=10, pady=10, sticky='we')
        self.lang_list['frame_dconfig'] = self.frame_dconfig
        
        self.label_thread = ttk.Label(self.frame_dconfig, text=self.use_lang['label_thread'], width=12)
        self.label_thread.grid(row=0, column=0)
        self.lang_list['label_thread'] = self.label_thread
        self.entry_thread = ttk.Entry(self.frame_dconfig, width=5)
        self.entry_thread.grid(row=0, column=1, padx=20, sticky='w')
        self.label_note_thread = ttk.Label(self.frame_dconfig, text=self.use_lang['label_note_thread'])
        self.label_note_thread.grid(row=0, column=2, sticky='w')
        self.lang_list['label_note_thread'] = self.label_note_thread
        
        self.remove_ts = BooleanVar()
        self.remove_ts.set(remove_ts)
        self.check_keepfile = ttk.Checkbutton(self.frame_dconfig, text=self.use_lang['check_keepfile'])
        self.check_keepfile.config(variable=self.remove_ts)
        self.lang_list['check_keepfile'] = self.check_keepfile
        self.check_keepfile.grid(row=0, column=9, padx=10)
        
        self.button_vname = ttk.Button(self.frame_dconfig, text=self.use_lang['button_vname'])
        self.button_vname.grid(row=1, column=0)
        self.lang_list['button_vname'] = self.button_vname
        self.entry_vname = ttk.Entry(self.frame_dconfig, width=84)
        self.entry_vname.grid(row=1, column=1, columnspan=9, padx=20)
        self.button_reset_all = ttk.Button(self.frame_dconfig, text=self.use_lang['button_reset_all'], width=10, command=self.clear_all)
        self.button_reset_all.grid(row=0, column=10, rowspan=2, sticky='ens')
        self.lang_list['button_reset_all'] = self.button_reset_all
        self.button_download = ttk.Button(self.frame_dconfig, text=self.use_lang['button_download'], width=10, command=self.download_video)
        self.button_download.grid(row=0, column=11, rowspan=2, sticky='ens')
        self.lang_list['button_download'] = self.button_download
        self.widget_list.append(self.button_download)

        # 初始化
        self.load_config()
        self.disable_analyze()
    
    # 方法开始

    # 框架1方法：用户输入下载地址或本地地址，选择要下载的m3u8文件
    # 框架1.1方法：用户输入下载地址或本地地址

    # 下拉菜单：选择语言
    def change_lang(self, language, master):
        self.use_lang = langs[language]
        master.title(self.use_lang['master_title'])
        for item in self.lang_list:
            self.lang_list[item].config(text=self.use_lang[item])
        # *** 将默认语言写入默认设置

    # 按钮：本地m3u8文件
    def local_m3u8(self):
        '''用文件选择器选择m3u8文件
        '''
        local_file = filedialog.askopenfilename(title='打开 m3u8 文件', filetypes=[('meu8 文件', '*.m3u8')])
        if local_file:
            self.entry_urlpath.delete(0, 'end')
            self.entry_urlpath.insert(0, local_file)
            self.analyze()

    # 按钮：分析
    def analyze(self):
        '''分析用户输入的地址
        '''
        urlpath = self.entry_urlpath.get()
        # 没有输入
        if len(urlpath) == 0:
            messagebox.showerror('错误', message='没有可分析的内容！')
        # 不是 http 地址 也不是 m3u8 文件
        elif urlpath.find('http') != 0 and urlpath[-5:] != '.m3u8':
            messagebox.showerror('错误', message='不支持的地址！')
        # 用户输入 http 地址 或者 本地 m3u8 文件路径，且不是误触
        elif urlpath != self.previous_analyze:
            found = False
            # 清空列表
            self.found_m3u8.selection_clear()
            self.clear_treeview(self.found_m3u8)
            # 禁用组件
            self.disable_analyze()
            # 清空文本框
            
            if urlpath[-5:]=='.m3u8':
                # 从网上下载 .m3u8 文件用以分析
                if urlpath.find('http') == 0:
                    pass
                else:
                    c = read_m3u8(urlpath)
                if c:
                    self.load_found_m3u8(c, 0, urlpath)
            elif urlpath.find('http') == 0:
                try:
                    r = get(urlpath, headers=headers)
                    if r.ok:
                        r.encoding = 'utf-8'
                        m3u8_list = find_m3u8s(r.text)
                        count = 0
                        if len(m3u8_list) > 0:
                            for item in m3u8_list:
                                self.found_m3u8.insert('', count, 'm3u8_'+str(count), text=item)
                                count += 1
                            self.found_m3u8.selection_add('m3u8_0')
                        else: messagebox.showwarning('错误', '没有找到 m3u8 文件！')
                except Exception as e:
                    messagebox.showerror('错误', '无法打开网页！')
            if not found:
                self.found_m3u8.selection_add('m3u8_0')
            self.previous_analyze = urlpath
            self.enable_analyze()
    
    def load_found_m3u8(self, c: list, id: int, urlpath: str):
        self.found_m3u8.insert('', 'end', 'm3u8_'+str(id), text=urlpath, values=[''.join(c)])
        self.m3u8_analyzed['m3u8_'+str(id)] = analyze_m3u8(c)

    # 框架1.2方法：分析找到的 m3u8 地址

    # 单击：选择 m3u8 文件
    def click_found_m3u8(self, event = None):
        '''在 已找到的 m3u8 中选择
        '''
        self.text_m3u8.delete('1.0', 'end')
        self.text_m3u8.insert('1.0', '\n'.join(self.found_m3u8.item(self.found_m3u8.selection())['values']))

    # 双击：选择 m3u8 文件
    def double_click_found_m3u8(self, event):
        '''在 已找到的 m3u8 中双击下载
        '''
        self.download_video(skip_check=True)

    # 框架2方法：编辑 m3u8

    # 框架2.1方法：m3u8 文本内容
    # def show_m3u8(self, c:list):


    # 框架2.2方法：编辑功能按键
    def save_edit(self, event = None):
        self.found_m3u8.set(self.found_m3u8.selection(), 'content', self.text_m3u8.get('1.0', 'end')[:-1])

    # 框架3方法：下载设置

    def download_video(self, skip_check: bool = False) -> None:
        '''下载视频
        '''
        # 检查是否有路径 ***
        # 检查内容是否有修改
        if not skip_check and self.text_m3u8.get('1.0', 'end')[:-1] != ''.join(self.found_m3u8.item(self.found_m3u8.selection())['values'][0]):
            if messagebox.askyesno('选择', 'm3u8 文本内容已修改。是否选择使用修改后的版本？'):
                self.found_m3u8.set(self.found_m3u8.selection(), 'content', self.text_m3u8.get('1.0', 'end')[:-1])
        # 开始下载视频 ***
        

    # 一般方法
    def load_config(self) -> None:
        '''载入设置文件，自动填入内容
        '''
        self.entry_vname.insert('0', download_folder+'\\video.mp4')
        self.entry_thread.insert('0', max_thread)

    def clear_all(self) -> None:
        '''重置所有选项
        '''
        self.entry_urlpath.delete('0', 'end')
        self.clear_treeview()
        self.text_m3u8.delete('1.0', 'end')
        self.disable_analyze()
        
    def clear_treeview(self, treeview=None) -> None:
        '''清空指定的或所有的 Treeview
        '''
        if not treeview:
            treeview_list=self.treeview_list
        else: treeview_list = [treeview]
        for tv in treeview_list:
            for item in tv.get_children():
                tv.delete(item)
        
    def disable_analyze(self) -> None:
        '''分析前禁用功能
        '''
        for item in self.widget_list:
            item.state([DISABLED])
        for tv in self.treeview_list:
            tv.config(selectmode=NONE)
        
    def enable_analyze(self) -> None:
        '''分析后启用功能
        '''
        for item in self.widget_list:
            item.config(state=NORMAL)
        for tv in self.treeview_list:
            tv.config(selectmode=BROWSE)
            


def main():
    root = Tk()
    main_app = M3u8Downloader(root)
    root.mainloop()

if __name__ == '__main__':
    main()