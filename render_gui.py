#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 10:01:12 2020

@author: schorb
"""


from tkinter import *
from tkinter import ttk
import os
import time

def calculate(*args):
    numcpus.set(int(numcpus.get()*2))
def calculate1(*args):
    numcpus.set(int(numcpus.get()/2))



def cluster_fiji(*args):
    timelim = s_t.get()
    memlim = s_mem.get()
    n_cpu = s_cpu.get()

    callcmd = 'srun -N1 --pty --x11 -n'

    callcmd += n_cpu

    callcmd += ' --mem '+memlim+'G '

    callcmd += '-t 0-'+timelim+':00 '

    callcmd += 'bash /g/emcf/schorb/code/cluster/fijicluster.sh\n'

    mainframe.destroy()  
    
    prepcmd = 'cp /g/emcf/software/Fiji/Fiji.app/ImageJ.cfg /g/emcf/software/Fiji/Fiji.app/ImageJ.cfg.orig\n'
    prepcmd += 'echo -Xmx'+memlim+'g > /g/emcf/software/Fiji/Fiji.app/ImageJ.cfg\n'  
    prepcmd += 'cat /g/emcf/software/Fiji/Fiji.app/ImageJ.cfg.orig >> /g/emcf/software/Fiji/Fiji.app/ImageJ.cfg\n'
    
    os.system(prepcmd)
    
    callcmd += 'cp /g/emcf/software/Fiji/Fiji.app/ImageJ.cfg.template /g/emcf/software/Fiji/Fiji.app/ImageJ.cfg'
    callcmd += 'rm /g/emcf/software/Fiji/Fiji.app/ImageJ.cfg.orig'
    
    os.popen(callcmd)

                 
    # Declaration of variables 
    hour=StringVar() 
    minute=StringVar() 
    second=StringVar() 
       
    starttime = str(timelim)
    
    # setting the default value as 0 
    hour.set(starttime) 

    ttk.Label(root, text="This Fiji cluster job will terminate in: ").grid(column=2, row=1, sticky=W)
       
    # Use of Entry class to take input from the user 
    hourEntry= ttk.Label(root, font=("Arial",18,""), 
                     textvariable=hour).grid(column=2, row=2, sticky=W) 

    
    temp = int(hour.get())*3600

    while temp >-1: 
          
        # divmod(firstvalue = temp//60, secondvalue = temp%60) 
        mins,secs = divmod(temp,60)  
        
        # Converting the input entered in mins or secs to hours, 
        # mins ,secs(input = 110 min --> 120*60 = 6600 => 1hr : 
        # 50min: 0sec) 
        hours=0
        if mins >60: 
              
            # divmod(firstvalue = temp//60, secondvalue  
            # = temp%60) 
            hours, mins = divmod(mins, 60) 
            
        
        # using format () method to store the value up to  
        # two decimal places 
        t_str = "{} : {} : {}".format(str(hours),str(mins),str(secs))   
                
        hour.set(t_str) 
        # updating the GUI window after decrementing the 
        # temp value every time 
        root.update() 
        time.sleep(5) 
   
        # when temp value = 0; then a messagebox pop's up 
        # with a message:"Time's up" 
        if (temp == 0): 
            exit() 
          
        # after every one sec the value of temp will be decremented 
        # by one 
        temp -= 5  
    

    exit()







root = Tk()
root.title("Cluster Parameters")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

ttk.Label(mainframe, text="Set Parameters for Cluster Fiji").grid(column=2, row=1, sticky=W)

numcpus = DoubleVar()
numcpus.set(2)
s_cpu = Spinbox(mainframe, from_=1, to=100, textvariable=numcpus)
s_cpu.grid(column=1, row=2, sticky=E)


ttk.Label(mainframe, text="Number of CPUs").grid(column=2, row=2, sticky=W)


mem = DoubleVar()
mem.set(4)
s_mem = Spinbox(mainframe, from_=1, to=128, textvariable=mem)
s_mem.grid(column=1, row=3, sticky=E)


ttk.Label(mainframe, text="Memory (GB)").grid(column=2, row=3, sticky=W)


time_in = DoubleVar()
time_in.set(24)
s_t = Spinbox(mainframe, from_=1, to=240, increment=6, textvariable=time_in)
s_t.grid(column=1, row=4, sticky=E)

ttk.Label(mainframe, text="Job time limit (h)").grid(column=2, row=4, sticky=W)

ttk.Button(mainframe, text="Go",command=cluster_fiji).grid(column=2, row=5, sticky=W)

# ttk.Label(mainframe, text="blabla").grid(column=3, row=2, sticky=W)

for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

root.bind('<Return>', calculate)
root.bind('<minus>', calculate1)

root.mainloop()
