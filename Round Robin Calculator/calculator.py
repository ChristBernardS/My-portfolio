import customtkinter as ctk
from PIL import Image
from tkinter import ttk
import tkinter as tk
from settings import *
from RoundRobin import *
import markdown
import sys
import os

ctk.set_appearance_mode("system")

class App(ctk.CTk):
    width = 1000
    height = 600

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("")

        # icon
        iconPath = self.resource_path("BLANK_ICON.ico")
        self.iconbitmap(iconPath)


        # window size
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(False, False)


        # data
        self.BurstTime = ctk.StringVar(value='2 4 6 8')
        self.quantumVar = ctk.IntVar(value=3)
        self.column = ctk.StringVar()
        self.avgWaitTime = ctk.StringVar()

        # background
        self.bg_image = ctk.CTkImage(Image.open(self.resource_path("pattern.png")),
                                               size=(self.width, self.height))
        self.bg_image_label = ctk.CTkLabel(self,
                                           image=self.bg_image,
                                           text='')
        self.bg_image_label.grid(row=0, column=0, columnspan=5)

        # input frame
        self.inputFrame = ctk.CTkFrame(master=self,
                                       fg_color=WHITE)
        self.inputFrame.grid(column=0, row=0, columnspan=2, padx= 30, pady= 30, sticky='nswe')

        self.inputLabel = ctk.CTkLabel(master=self.inputFrame,
                                       text='Input',
                                       font=(FONT, MAIN_TEXT_SIZE),
                                       text_color=BLACK)
        self.inputLabel.grid(column=0, row=0, sticky='nw', padx=20, pady=20)

        self.burstTimeLabel = ctk.CTkLabel(master=self.inputFrame,
                                           text='burst time: e.g. 2 4 6 8',
                                           font=(FONT, SWITCH_FONT_SIZE),
                                           text_color=BLACK)
        self.burstTimeLabel.grid(column=0, row=1, sticky='nw', padx=20, pady=10)
        self.inputBurstTime = ctk.CTkEntry(master=self.inputFrame,
                                           textvariable=self.BurstTime,
                                           width=270)
        self.inputBurstTime.grid(column=0, row=2, sticky='new', padx=20, pady=10)


        self.quantumLabel = ctk.CTkLabel(master=self.inputFrame,
                                           text='quantum time: e.g. 3',
                                           font=(FONT, SWITCH_FONT_SIZE),
                                           text_color=BLACK)
        self.quantumLabel.grid(column=0, row=3, sticky='nw', padx=20, pady=10)
        self.inputQuantum = ctk.CTkEntry(master=self.inputFrame,
                                           textvariable=self.quantumVar,
                                           width=270)
        self.inputQuantum.grid(column=0, row=4, sticky='new', padx=20, pady=10)

        self.convertBtn = ctk.CTkButton(master=self.inputFrame,
                                        command=self.createProcessRow,
                                        fg_color=GRAY,
                                        hover_color=BLACK,
                                        text='=')
        self.convertBtn.grid(column=0, row=5, sticky='sw', padx=20, pady=30)

        # Result frame
        self.resultFrame = ctk.CTkFrame(master=self,
                                        fg_color=LIGHT_BLACK)
        self.resultFrame.grid(column=2, row=0, columnspan=5, padx= 30, pady= 30, sticky='nsew')

        self.outputLabel = ctk.CTkLabel(master=self.resultFrame,
                                       text='Output',
                                       font=(FONT, MAIN_TEXT_SIZE),
                                       text_color=WHITE)
        self.outputLabel.grid(column=0, row=0, sticky='nw', padx=20, pady=20)

        # table frame
        self.tableFrame = ctk.CTkFrame(master=self.resultFrame,
                                       fg_color=LIGHT_GRAY)
        self.tableFrame.grid(column=0, row=1, padx=20, pady=20, sticky='nsew')

        # table style
        self.style = ttk.Style()
    
        self.style.theme_use("default")

        self.style.configure("Treeview",
                        background="#2a2d2e",
                        foreground="white",
                        rowheight=25,
                        fieldbackground="#343638",
                        bordercolor="#343638",
                        borderwidth=0)
        self.style.map('Treeview', background=[('selected', BLUE)])

        self.style.configure("Treeview.Heading",
                        background="#565b5e",
                        foreground="white",
                        relief="flat")
        self.style.map("Treeview.Heading",
                background=[('active', '#3484F0')])

        # table
        self.heading = ('Id Process', 'Burst Time', 'Waiting Time', 'Turn-arround Time')

        self.table = ttk.Treeview(master=self.tableFrame,
                                  show='headings',
                                  height=12,
                                  columns=self.heading)
        self.table.heading('Id Process', text='Id Process')
        self.table.column('Id Process', minwidth=110, width=110, anchor='center')
        self.table.heading('Burst Time', text='Burst Time')
        self.table.column('Burst Time', minwidth=110, width=110, anchor='center')
        self.table.heading('Waiting Time', text='Waiting Time')
        self.table.column('Waiting Time', minwidth=110, width=110, anchor='center')
        self.table.heading('Turn-arround Time', text='Turn-arround Time')
        self.table.column('Turn-arround Time', minwidth=110, width=110, anchor='center')

        self.table.grid(column=0, row=0, sticky='new', padx=20, pady=20)

        # scrollbar
        self.scrollbar = ctk.CTkScrollbar(master=self.tableFrame,
                                          command=self.table.yview,
                                          button_color=BLACK,
                                          button_hover_color=GRAY)
        self.scrollbar.grid(column=1, row=0, sticky='ns')
        self.table.configure(yscrollcommand=self.scrollbar.set)

        # average waiting time
        self.avgWaitTimeLabel = ctk.CTkLabel(master=self.resultFrame,
                                             textvariable=self.avgWaitTime,
                                             font=(FONT, SWITCH_FONT_SIZE),
                                             text_color=WHITE)
        self.avgWaitTimeLabel.grid(column=0, row=2, sticky='nw', padx=20, pady=10)

        self.createProcessRow()

        self.mainloop()

    def createProcessRow(self):
        self.clearRow()
        burstTime = self.BurstTime.get().split(' ')
        for i in range(len(burstTime)):
            burstTime[i] = int(burstTime[i])
        qt = int(self.quantumVar.get())
        idProcess = [1] * len(burstTime)
        for i in range(len(idProcess)):
            idProcess[i] = i+1
        waitTime = [0] * len(idProcess)
        tatTime = [0] * len(idProcess)

        findWaitingTime(idProcess, len(idProcess), burstTime, waitTime, qt)
        findTurnAroundTime(idProcess, len(idProcess), burstTime, waitTime, tatTime)

        totalWt = 0
        totalTat = 0
        for i in range(len(idProcess)):
            totalWt += waitTime[i]
            totalTat+= tatTime[i]
            self.updateRow(self.table, (idProcess[i], burstTime[i], waitTime[i], tatTime[i]))
        self.avgWaitTime.set(f"Average waiting time = {round(totalWt /len(idProcess), 2)}")

    def clearRow(self):
        for row in self.table.get_children():
            self.table.delete(row)
        
    def updateRow(self, theTable, val):
        theTable.insert('', tk.END, values=val)
    
    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

        




if __name__ == '__main__':
    App()