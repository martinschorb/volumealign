#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ZetCode Tkinter e-book

This script produces a long-running task of calculating 
a large Pi number, while keeping the GUI responsive.

Author: Jan Bodnar
Last modified: January 2016
Website: www.zetcode.com
"""

from tkinter import (Tk, BOTH, Text, E, W, S, N, END, 
    NORMAL, DISABLED, StringVar, RIGHT, BOTH, RAISED)
from tkinter.ttk import Frame, Label, Button, Progressbar, Entry, Style
from tkinter import scrolledtext

from multiprocessing import Queue, Process
import queue 
from decimal import Decimal, getcontext

DELAY1 = 80
DELAY2 = 20

# class Example1(Frame):
  
#     def __init__(self, parent, q):
#         Frame.__init__(self, parent)   
         
#         self.queue = q 
#         self.parent = parent
#         self.initUI()
        
        
#     def initUI(self):
      
#         self.parent.title("Pi computation")
#         self.pack(fill=BOTH, expand=True)
        
#         self.grid_columnconfigure(4, weight=1)
#         self.grid_rowconfigure(3, weight=1)
        
#         lbl1 = Label(self, text="Digits:")
#         lbl1.grid(row=0, column=0, sticky=E, padx=10, pady=10)
        
#         self.ent1 = Entry(self, width=10)
#         self.ent1.insert(END, "4000")
#         self.ent1.grid(row=0, column=1, sticky=W)
        
#         lbl2 = Label(self, text="Accuracy:")
#         lbl2.grid(row=0, column=2, sticky=E, padx=10, pady=10)

#         self.ent2 = Entry(self, width=10)
#         self.ent2.insert(END, "100")
#         self.ent2.grid(row=0, column=3, sticky=W)        
        
#         self.startBtn = Button(self, text="Start", 
#             command=self.onStart)
#         self.startBtn.grid(row=1, column=0, padx=10, pady=5, sticky=W)
        
#         self.pbar = Progressbar(self, mode='indeterminate')        
#         self.pbar.grid(row=1, column=1, columnspan=3, sticky=W+E)     
        
#         self.txt = scrolledtext.ScrolledText(self)  
#         self.txt.grid(row=2, column=0, rowspan=4, padx=10, pady=5,
#             columnspan=5, sticky=E+W+S+N)
       
        
#     def onStart(self):
        
#         self.startBtn.config(state=DISABLED)
#         self.txt.delete("1.0", END)
        
#         self.digits = int(self.ent1.get())
#         self.accuracy = int(self.ent2.get())
        
#         self.p1 = Process(target=self.generatePi, args=(self.queue,))
#         self.p1.start()
#         self.pbar.start(DELAY2)
#         self.after(DELAY1, self.onGetValue)
        
       
#     def onGetValue(self):
        
#         if (self.p1.is_alive()):
            
#             self.after(DELAY1, self.onGetValue)
#             return
#         else:    
        
#             try:
#                 self.txt.insert('end', self.queue.get(0))
#                 self.txt.insert('end', "\n")
#                 self.pbar.stop()
#                 self.startBtn.config(state=NORMAL)
            
#             except queue.Empty:
#                 print("queue is empty")
            
            
#     def generatePi(self, queue):
        
#         getcontext().prec = self.digits
        
#         pi = Decimal(0)
#         k = 0
#         n = self.accuracy
        
#         while k < n:
#             pi += (Decimal(1)/(16**k))*((Decimal(4)/(8*k+1)) - \
#                 (Decimal(2)/(8*k+4)) - (Decimal(1)/(8*k+5))- \
#                 (Decimal(1)/(8*k+6)))
#             k += 1
#             print (self.p1.is_alive())
            
#         queue.put(pi)    
#         print("end")    



class Example(Frame):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):

        self.master.title("Buttons")
        self.style = Style()
        self.style.theme_use("default")
        
        self.columnconfigure(0, pad=3)
        self.columnconfigure(1, pad=3)
        
        self.rowconfigure(0, pad=3)
        self.rowconfigure(1, pad=3)
        self.rowconfigure(2, pad=3)
        self.rowconfigure(3, pad=3)
        self.rowconfigure(4, pad=3)

        frame0 = Frame(self, relief=RAISED, borderwidth=1)
        frame0.grid(column=0, rowspan=4, sticky=W+E)
        # frame.pack(fill=BOTH, expand=True)

        self.pack(fill=BOTH, expand=True)

        self.closeButton = Button(self, text="Close",command=self.cb_CloseButton)
        self.closeButton.grid(column=0, row=4, sticky=W+E)
        # closeButton.pack(side=RIGHT, padx=5, pady=5)
        self.okButton = Button(self, text="OK")
        self.okButton.grid(column=0, row=3, sticky=W+E)
        # okButton.pack(side=RIGHT, padx=5, pady=5)

    def cb_CloseButton(self):
        self.okButton.config(state=DISABLED)



def main():
    
    q = Queue()  
    root = Tk()
    # root.geometry("400x350+300+300")
    # app = Example(root, q)
    # root.mainloop()  
    root.geometry("300x200+300+300")
    app = Example()
    root.mainloop()


if __name__ == '__main__':
    main()  
