import tkinter as tk
import threading
import time
from PIL import Image, ImageFont, ImageDraw,ImageTk
from  queue import Queue
import math
import struct
import glob
import os

#free font
#https://www.pkstep.com/archives/5693
#https://mrmad.com.tw/free-chinese-font
#https://fonts.google.com/noto

class Converter:
    def __init__(self,win,canvas,output_path='font_lib.bin'):
        self.window=win
        self.canvas=canvas
        self.output_path=output_path
        self.disp_interval_in_ms=1
        self.thd=None
        self.msg_que=Queue(10)
        self.char_vec='1234567890'
        self.char_vec_len=len(self.char_vec)
        self.idx=0

        self.word_info_map={}

        self.set_font("NotoSansTC-Regular.otf",32)

    def set_font(self,font,height):
        self.font_total_height=math.ceil(height*1.5)
        self.font_height=height
        self.fon_path=font
        self.font = ImageFont.truetype(font, height)  

        self.buf_img=Image.new(mode="RGB", size=(200,200), color = (255, 255, 255))
        self.cvt_image = ImageTk.PhotoImage(self.buf_img)
        self.tk_img = canvas.create_image(100,100,image=self.cvt_image,anchor="center")
        self.draw = ImageDraw.Draw(self.buf_img)  
        canvas.itemconfig(self.tk_img,image=self.cvt_image)

    def set_chars(self,chars):
        ascii_list=''.join([a for a in [chr(x) for x in range(128)] if a.isprintable()])
        self.char_vec=chars+ascii_list
        self.char_vec_len=len(self.char_vec)
        

    def output(self):
        #ESP32 & ARM is Little Endian
        
        print('output result')
        idx_list=list(self.word_info_map.keys())
        idx_list.sort()

        #gen meta data
        #[format version: uint8_t][char cnt: uint32_t][font height: uint16_t][index offset: uint32_t][font library offset: uint32_t][desc: char x n]
        
        desc=(self.fon_path+",%d"%(self.font_height)).encode()+bytes(1)
        version=1
        char_cnt=len(idx_list)
        font_height=self.font_total_height
        index_offset=1+4+2+4+4+len(desc)
        index_list_size=char_cnt*(4+4)
        binary_offset=index_offset+index_list_size

        meta_bin=struct.pack('<BIHII',version,char_cnt,font_height,index_offset,binary_offset)+desc

        #gen binary
        #([width: uint8_t][len: uint16_t][pixel: uint8_t x len]) x n
        font_bin=bytes(0)
        bin_base_offset=0
        idx_offset_map={}

        for idx in idx_list:
            word_width,word_bin=self.word_info_map[idx]
            word_len=len(word_bin)
            word_info=struct.pack('<BH',word_width,word_len)+word_bin

            idx_offset_map[idx]=bin_base_offset
            font_bin+=word_info

            bin_base_offset+=len(word_info)

        #gen index
        #([char idx: uint32_t][font offset: uint32_t]) x n
        idx_bin=bytes(0)
        for idx in idx_list:
            idx_info=struct.pack('<II',idx,idx_offset_map[idx])
            idx_bin+=idx_info

        lib_bin=meta_bin+idx_bin+font_bin

        file = open(self.output_path, "wb")
        file.write(lib_bin)
        file.close()

        print('total %d words'%(char_cnt))

    def extra_bin_info(self,word):
        word_idx=int.from_bytes(word.encode(),"big")
        print("%s:\t%d"%(word,word_idx))

        scan_range=self.font_total_height
        left=scan_range
        right=0

        #scan range
        for y in range(scan_range):
            for x in range(scan_range):
                color=self.buf_img.getpixel((x,y))
                if(color[0]!=255):
                    if(x<left):
                        left=x
                    if(x>right):
                        right=x

        if(left>right):#可能遇到無法顯示的文字，預設空白1/4字高
            left=0
            right=math.floor(self.font_height/4)

        #extra bin info
        word_bin=bytearray()
        for y in range(scan_range):
            for x in range(left,right+1):
                color=self.buf_img.getpixel((x,y))
                word_bin.append(255-color[0])

        word_width=right-left+1
        self.word_info_map[word_idx]=(word_width,word_bin)

    def update_screen(self):
        if(self.flag.is_set()==False or self.char_vec_len<=self.idx):
            self.window.destroy()
            return

        c=self.char_vec[self.idx]

        if c not in self.word_info_map:
            #draw txt on pil buffer
            self.draw.rectangle((0,0,200,200),fill=(255,255,255))
            self.draw.text((0,0), c, (0,0,0), font=self.font, anchor=None, spacing=0, align="left")  
            self.extra_bin_info(c)

            self.cvt_image = ImageTk.PhotoImage(self.buf_img)
            canvas.itemconfig(self.tk_img,image=self.cvt_image)
            self.idx+=1

        self.window.after(self.disp_interval_in_ms, self.update_screen)

    def start(self):
        self.flag=threading.Event()
        self.flag.set()
        self.idx=0
        self.update_screen()

    def stop(self):
        if(self.flag is not None):
            self.flag.clear()
        self.output()

def scan_dir_for_words(path):
    file_list=glob.glob(path+'/*')
    word_set=set()

    for fp in file_list:
        fn, ext = os.path.splitext(fp)
        if(ext in ['.c','.cpp','.cc','.h','.hpp']):
            with open(fp,'r',encoding="utf-8") as f:
                cxt = f.read()
                for w in cxt:
                    word_set.add(w)
    return ''.join(list(word_set))

if __name__ == '__main__':
    src_dir='example_src'
    font_path='NotoSansTC-Regular.otf'
    font_size=24

    window = tk.Tk()
    window.title('window')
    window.geometry('200x200')
    canvas=tk.Canvas(window, width=200, height=200)
    canvas.pack()

    words=scan_dir_for_words(src_dir)
    print(words)

    cvt=Converter(window,canvas)
    cvt.set_font(font_path,font_size)
    cvt.set_chars(words)
    cvt.start()

    window.mainloop()
    
    cvt.stop()