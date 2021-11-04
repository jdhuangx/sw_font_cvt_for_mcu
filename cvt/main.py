import tkinter as tk
import threading
import time
from  queue import Queue

class Converter:
    def __init__(self,win,canvas):
        self.window=win
        self.canvas=canvas
        self.disp_interval_in_ms=1000
        self.thd=None
        self.msg_que=Queue(10)
        self.char_vec='Ag測試123456'
        self.char_vec_len=len(self.char_vec)
        self.idx=0

        self.font_height=12
        self.font_name='Arial'

    def set_font(self,font,height):
        self.font_height=height
        self.font_name=font

    def set_chars(self,chars):
        self.char_vec=chars
        self.char_vec_len=len(self.char_vec)

    def cvt_char(self):
        print('cvt font')
        self.window.after(self.disp_interval_in_ms, self.update_screen)

    def output(self):
        print('output result')

    def update_screen(self):
        if(self.flag.is_set()==False or self.char_vec_len<=self.idx):
            self.window.destroy()
            return

        #lb['text']=self.char_vec[self.idx]
        font_real_height=self.font_height*1.5
        font_width=font_real_height
        self.canvas.delete("all")
        self.canvas.create_text(10, 10, font=(self.font_name, self.font_height), text=self.char_vec[self.idx], anchor='nw')
        self.canvas.create_rectangle(9, 9, 9+2+font_width, 12+font_real_height, outline='red')
        self.idx+=1

        self.window.after(1, self.cvt_char)

    def start(self):
        self.flag=threading.Event()
        self.flag.set()
        self.idx=0
        self.update_screen()

    def stop(self):
        if(self.flag is not None):
            self.flag.clear()
        self.output()

if __name__ == '__main__':
    font_name='Arial'
    #font_name='新細明體'
    font_size=32

    window = tk.Tk()
    window.title('window')
    window.geometry('100x100')
    canvas=tk.Canvas(window, width=100, height=100)
    canvas.pack()

    cvt=Converter(window,canvas)
    cvt.set_font(font_name,font_size)
    cvt.start()

    window.mainloop()
    

    cvt.stop()
