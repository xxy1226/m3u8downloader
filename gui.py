from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox

import os, sys, time
from requests import get
from threading import Thread
from re import compile, S
from shutil import rmtree

from conf import write_conf
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
    previous_analyze = ''


    def __init__(self, master):
        # 初始设置
        master.title(langs[lang]['master_title'])
        master.minsize(800, 600)

        self.style = ttk.Style()
        # self.style.configure('TFrame', background='#e1d8b9')

        # 框架1：用户输入下载地址或本地地址，选择要下载的m3u8文件
        self.frame_url = ttk.LabelFrame(master, text=langs[lang]['frame_url'], padding=5)
        self.frame_url.grid(row=0, column=0, padx=10, pady=10, sticky='we')

        # 框架1.1：用户输入下载地址或本地地址
        self.subframe_url1 = ttk.Frame(self.frame_url)
        self.subframe_url1.pack()
        ttk.Label(self.subframe_url1, text='输入网址/m3u8文件URL/本地m3u8文件路径').grid(row=0, column=0, columnspan=2, sticky='w')
        self.button_lang = ttk.Menubutton(self.subframe_url1, text='English')
        self.button_lang.grid(row=0, column=2, sticky='e')
        self.menu_langs = Menu(self.button_lang)
        ttk.Button(self.subframe_url1, style='Colored.TButton', text='本地m3u8文件', command=self.local_m3u8).grid(row=1, column=0)
        self.entry_urlpath = ttk.Entry(self.subframe_url1, width=100)
        self.entry_urlpath.grid(row=1, column=1)
        self.entry_urlpath.bind('<Return>', lambda e:self.analyze())
        ttk.Button(self.subframe_url1, text='分析', width=10, command=self.analyze).grid(row=1, column=3)
        
        # 框架1.2：分析找到的 m3u8 地址
        self.subframe_url2 = ttk.Frame(self.frame_url)
        self.subframe_url2.pack(pady=5)
        ttk.Label(self.subframe_url2, text='选择 m3u8 文件: 单击可编辑/双击直接下载（先确保下载设置）').grid(row=0, column=0, sticky='w')
        self.found_m3u8 = ttk.Treeview(self.subframe_url2, height=3, show='tree', selectmode=BROWSE)
        self.treeview_list.append(self.found_m3u8)
        self.found_m3u8.column('#0', width=740)
        self.found_m3u8['columns'] = ('content')
        self.found_m3u8['displaycolumns'] = []
        self.found_m3u8.grid(row=1, column=0, rowspan=3, columnspan=2)
        self.found_m3u8.bind('<<TreeviewSelect>>', self.click_found_m3u8)
        self.found_m3u8.bind('<Double-Button-1>', self.double_click_found_m3u8)
        self.found_m3u8_scrollbar = ttk.Scrollbar(self.subframe_url2, orient = VERTICAL, command=self.found_m3u8.yview)
        self.found_m3u8_scrollbar.grid(row=1, column=2, rowspan=3, sticky='ns')
        self.found_m3u8.config(yscrollcommand=self.found_m3u8_scrollbar.set)
        
        # 框架2：编辑 m3u8
        self.frame_edit = ttk.LabelFrame(master, text='2. 编辑 m3u8 内容（可选）', padding=5)
        self.frame_edit.grid(row=1, column=0, padx=10, sticky='we')
        
        # 框架2.1：m3u8 文本内容
        self.subframe_edit1 = ttk.Frame(self.frame_edit)
        self.subframe_edit1.grid(row=0, column=0, sticky='we')
        self.text_m3u8 = Text(self.subframe_edit1, width=70, height=15, font=('Arial', 12))
        self.text_m3u8.grid(row=0, column=0,pady=5)
        self.text_m3u8_vscrollbar = ttk.Scrollbar(self.subframe_edit1, orient = VERTICAL, command=self.text_m3u8.yview)
        self.text_m3u8_vscrollbar.grid(row=0, column=1, sticky='ns')
        self.text_m3u8.config(yscrollcommand=self.text_m3u8_vscrollbar.set)
        self.text_m3u8_hscrollbar = ttk.Scrollbar(self.subframe_edit1, orient = HORIZONTAL, command=self.text_m3u8.xview)
        self.text_m3u8_hscrollbar.grid(row=1, column=0, sticky='we')
        self.text_m3u8.config(xscrollcommand=self.text_m3u8_hscrollbar.set)
        
        # 框架2.2：编辑功能按键
        self.subframe_edit2 = ttk.Frame(self.frame_edit, padding=5)
        self.subframe_edit2.grid(row=0, column=1, sticky='we')

        self.subsubframe_edit2_time = ttk.Frame(self.subframe_edit2)
        self.subsubframe_edit2_time.grid(row=0, column=0, pady=10)
        self.text_time_hour = ttk.Entry(self.subsubframe_edit2_time, width=3)
        self.text_time_hour.grid(row=0, column=0)
        Label(self.subsubframe_edit2_time, text=':').grid(row=0, column=1)
        self.text_time_minute = ttk.Entry(self.subsubframe_edit2_time, width=3)
        self.text_time_minute.grid(row=0, column=2)
        Label(self.subsubframe_edit2_time, text=':').grid(row=0, column=3)
        self.text_time_second = ttk.Entry(self.subsubframe_edit2_time, width=3)
        self.text_time_second.grid(row=0, column=4)
        ttk.Button(self.subsubframe_edit2_time, text='跳到时间', padding=5).grid(row=1, column=0, sticky='wens', columnspan=5)

        ttk.Button(self.subframe_edit2, text='去除外站广告', padding=5).grid(row=2, column=0, pady=10, sticky='wens', columnspan=5)
        ttk.Button(self.subframe_edit2, text='删除选中片段', padding=5).grid(row=3, column=0, pady=10, sticky='wens', columnspan=5)
        ttk.Button(self.subframe_edit2, text='重置', padding=5).grid(row=4, column=0, pady=10, sticky='wens', columnspan=5)
        ttk.Button(self.subframe_edit2, text='确认修改', padding=5).grid(row=5, column=0, pady=10, sticky='wens', columnspan=5)
        
        # 框架3：下载设置
        self.frame_dconfig = ttk.LabelFrame(master, text='3. 下载设置', padding=5)
        self.frame_dconfig.grid(row=2, column=0, padx=10, pady=10, sticky='we')
        
        ttk.Label(self.frame_dconfig, text='最大线程数').grid(row=0, column=0)
        self.entry_thread = ttk.Entry(self.frame_dconfig, width=5)
        self.entry_thread.grid(row=0, column=1, padx=20, sticky='w')
        ttk.Label(self.frame_dconfig, text='* 线程数不建议设太大').grid(row=0, column=2, sticky='w')
        
        self.remove_ts = BooleanVar()
        self.remove_ts.set(remove_ts)
        self.check_clean = ttk.Checkbutton(self.frame_dconfig, text='合并后删除临时文件')
        self.check_clean.config(variable=self.remove_ts)
        self.check_clean.grid(row=0, column=9, padx=10)
        
        self.button_vname = ttk.Button(self.frame_dconfig, text='视频名称')
        self.button_vname.grid(row=1, column=0)
        self.entry_vname = ttk.Entry(self.frame_dconfig, width=84)
        self.entry_vname.grid(row=1, column=1, columnspan=9, padx=20)
        self.button_download = ttk.Button(self.frame_dconfig, text='全部重置', width=10, command=self.clear_all)
        self.button_download.grid(row=0, column=10, rowspan=2, sticky='ens')
        self.button_download = ttk.Button(self.frame_dconfig, text='下载视频', width=10, command=self.download_video)
        self.button_download.grid(row=0, column=11, rowspan=2, sticky='ens')
        self.widget_list.append(self.button_download)

        # 初始化
        self.load_config()
        self.disable_analyze()
    
    # 方法开始

    # 框架1方法：用户输入下载地址或本地地址，选择要下载的m3u8文件
    # 框架1.1方法：用户输入下载地址或本地地址

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
                    self.found_m3u8.insert('', '0', 'm3u8_0', text=urlpath, values=[c])
                    self.found_m3u8.selection_add('m3u8_0')
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
            self.previous_analyze = urlpath
            self.enable_analyze()

    # 框架1.2方法：分析找到的 m3u8 地址

    # 单击：选择 m3u8 文件
    def click_found_m3u8(self, event):
        '''在 已找到的 m3u8 中选择
        '''
        self.text_m3u8.delete('1.0', 'end')
        self.text_m3u8.insert('1.0', ''.join(self.found_m3u8.item(self.found_m3u8.selection())['values']))

    # 双击：选择 m3u8 文件
    def double_click_found_m3u8(self, event):
        '''在 已找到的 m3u8 中双击下载
        '''
        self.download_video(skip_check=True)

    # 框架2方法：编辑 m3u8

    # 框架2.1方法：m3u8 文本内容

    # 框架2.2方法：编辑功能按键

    # 框架3方法：下载设置

    def download_video(self, skip_check: bool = False) -> None:
        '''下载视频
        '''
        # 检查是否有路径 ***
        # 检查内容是否有修改
        if not skip_check and self.text_m3u8.get('1.0', 'end')[:-1] != ''.join(self.found_m3u8.item(self.found_m3u8.selection())['values'][0]):
            if messagebox.askyesno('选择', 'm3u8 文本内容已修改。是否选择使用修改后的版本？'):
                self.found_m3u8.set(self.found_m3u8.selection(), 'content', self.text_m3u8.get('1.0', 'end')[:-1].splitlines(True))
        # 开始下载视频 ***
        messagebox.showinfo(message=''.join(self.found_m3u8.item(self.found_m3u8.selection())['values'][0]))

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
    # print(json.dumps(langs, indent=4))
    main()