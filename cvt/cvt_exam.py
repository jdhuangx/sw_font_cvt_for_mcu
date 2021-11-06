import tkinter as tk
import threading
from PIL import Image, ImageFont, ImageDraw,ImageTk
from  queue import Queue
import struct

#free font
#https://www.pkstep.com/archives/5693
#https://mrmad.com.tw/free-chinese-font
#https://fonts.google.com/noto

class Tester:
    def __init__(self,win,canvas,lib_path):
        self.window=win
        self.canvas=canvas
        self.lib_path=lib_path
        self.disp_interval_in_ms=10
        self.thd=None
        self.idx=0
        self.char_cnt=0
        self.char_list=[]
        self.char_bin_map={}
        self.parse_lib()

        self.buf_img=Image.new(mode="RGB", size=(200,200), color = (255, 255, 255))
        self.cvt_image = ImageTk.PhotoImage(self.buf_img)
        self.tk_img = canvas.create_image(100,100,image=self.cvt_image,anchor="center")
        self.draw = ImageDraw.Draw(self.buf_img)  
        canvas.itemconfig(self.tk_img,image=self.cvt_image)

    def parse_lib(self):
        #meta data
        #[format version: uint8_t][char cnt: uint32_t][font height: uint16_t][index offset: uint32_t][font library offset: uint32_t][desc: char x n]
        with open(self.lib_path,'rb') as f:
            meta_main_len=1+4+2+4+4
            meta_main_ba=f.read(meta_main_len)
            ver,char_cnt,font_height,idx_offset,bin_offset=struct.unpack('<BIHII',meta_main_ba)
            print('version: %d'%(ver))
            print('char count: %d'%(char_cnt))
            print('font total height: %d'%(font_height))
            print('index offset: %d'%(idx_offset))
            print('binary offset: %d'%(bin_offset))
            desc_len=idx_offset-meta_main_len
            desc=f.read(desc_len)
            print('desc: '+desc.decode())

            self.char_cnt=char_cnt
            self.font_total_height=font_height

            #read idx
            idx_bin_len=bin_offset-idx_offset
            idx_bin=f.read(idx_bin_len)

            #read font bin
            font_bin=f.read()

            #parse info
            idx_offset=0
            for i in range(char_cnt):
                word_idx_ba=idx_bin[idx_offset:(idx_offset+4)]
                word_offset_ba=idx_bin[(idx_offset+4):(idx_offset+8)]
                idx_offset+=8
                word_offset=struct.unpack('<I',word_offset_ba)[0]
                
                rm_cnt=0
                for i in range(0,4):
                    if(word_idx_ba[i]==0x00):
                        rm_cnt+=1
                
                word_idx_ba=word_idx_ba[:(4-rm_cnt)]
                word_idx_ba=bytearray(word_idx_ba)
                word_idx_ba.reverse()
                word=word_idx_ba.decode('utf-8')

                word_width,word_height,word_y_offset,word_byte_len=struct.unpack('<BBBH',font_bin[word_offset:(word_offset+5)])
                word_ba=font_bin[(word_offset+5):(word_offset+5+word_byte_len)]
                
                print("%s,%d,%d,%d,%d"%(word,word_width,word_height,word_y_offset,word_byte_len))
                self.char_list.append(word)
                self.char_bin_map[word]=(word_width,word_height,word_y_offset,word_ba)

    def update_screen(self):
        if(self.flag.is_set()==False or self.char_cnt<=self.idx):
            self.window.destroy()
            return

        word=self.char_list[self.idx]
        word_width,word_height,word_y_offset,word_ba=self.char_bin_map[word]


        self.draw.rectangle((0,0,200,200),fill=(255,255,255))
        x_draw_offset=5

        for y in range(word_height):
            for x in range(word_width):
                gray=255-word_ba[word_width*y+x]
                if(gray==255):
                    self.buf_img.putpixel((x+x_draw_offset,y+word_y_offset),(0,gray,0))
                else:
                    self.buf_img.putpixel((x+x_draw_offset,y+word_y_offset),(gray,gray,gray))

        self.cvt_image = ImageTk.PhotoImage(self.buf_img)
        canvas.itemconfig(self.tk_img,image=self.cvt_image)
        self.idx+=1


        self.window.after(self.disp_interval_in_ms, self.update_screen)

    def start(self):
        self.flag=threading.Event()
        self.flag.set()
        self.update_screen()

    def stop(self):
        if(self.flag is not None):
            self.flag.clear()

if __name__ == '__main__':
    lib_path='font_lib.bin'

    window = tk.Tk()
    window.title('window')
    window.geometry('200x200')
    canvas=tk.Canvas(window, width=200, height=200)
    canvas.pack()

    tester=Tester(window,canvas,lib_path)
    tester.start()

    window.mainloop()
    
    tester.stop()