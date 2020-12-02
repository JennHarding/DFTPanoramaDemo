import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import  FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib import style
from matplotlib import pyplot as plt

import tkinter as tk
from tkinter import ttk

from pandastable import Table, TableModel
# import pandas as pd
from pandas import DataFrame, set_option

from CorpusManagement import corpus_list
from CalculationFunctions import score_to_data
import Visuals as vis

LARGE_FONT = ("Verdana", 16)
NORMAL_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 8)
style.use("ggplot")
score_data = "none"
master_df = "none"


class PanoramaGenerator(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "DFT Panorama Generator")
        
        container = tk.Frame(self)
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        menubar = tk.Menu(container)
        # filemenu = tk.Menu(menubar, tearoff=0)
        # filemenu.add_command(label="Exit", command=quit)
        # menubar.add_cascade(label="File", menu=filemenu)
        
        goto_menu = tk.Menu(menubar, tearoff=1)
        goto_menu.add_command(label="Home", command=lambda: self.show_frame(StartPage))
        goto_menu.add_command(label="Data", command=lambda: self.show_frame(DataPage))
        goto_menu.add_command(label="Master Data Frame", command=lambda: self.show_frame(MasterDataFrame))
        menubar.add_cascade(label="Go To", menu=goto_menu)
        
        tk.Tk.config(self, menu=menubar)
        
        
        self.frames = {}
        
        for F in (StartPage, DataPage, MasterDataFrame):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame(StartPage)
        

    
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        


class StartPage(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="DFT Panorama Generator", font=LARGE_FONT)
        label.grid(row=0, column=0, columnspan=5)

        rep_label = ttk.Label(self, text="Select Repertoire")
        rep_label.grid(row=1, column=0)
        rep = tk.StringVar()
        rep_select = ttk.OptionMenu(self, rep, *corpus_list)
        rep_select.grid(row=1, column=1, columnspan=3, sticky="we", pady=20)
             
        
        def switch():
            if beg_select["state"] == tk.DISABLED:
                beg_select["state"] = tk.NORMAL
                end_select["state"] = tk.NORMAL
            else:
                beg_select["state"] = tk.DISABLED
                end_select["state"] = tk.DISABLED
        
        exc = tk.BooleanVar()
        exc_select = tk.Checkbutton(self, text="Use Excerpt", variable=exc, command=switch)
        exc_select.grid(row=2, column=0)
        
        beg_label = tk.Label(self, text="Begin in Measure:")
        beg_label.grid(row=2, column=1)
        beg = tk.IntVar()
        beg_select = tk.Entry(self, textvariable=beg, state=tk.DISABLED)
        beg_select.grid(row=2, column=2)
        end_label = tk.Label(self, text="End in Measure:")
        end_label.grid(row=3, column=1)
        end = tk.IntVar()
        end_select = tk.Entry(self, textvariable=end, state=tk.DISABLED)
        end_select.grid(row=3, column=2)
                
        window_label = tk.Label(self, text="Window Size:")
        window_label.grid(row=4, column=0)
        win_size = tk.IntVar()
        win_size.set(16)
        win_size_select = tk.Entry(self, textvariable=win_size)
        win_size_select.grid(row=4, column=1, pady=20)
        
        strategy_label = tk.Label(self, text="PC Counting\n Strategy:")
        strategy_label.grid(row=5, column=0)
        strat = tk.StringVar()
        strat.set("Onset")
        strats = ["Onset", "Duration", "Flat"]
        for i, s in enumerate(strats, 1):
            strat_select = ttk.Radiobutton(self, text=s, variable=strat, value=s)
            strat_select.grid(row=5, column=i, sticky="w")
        
        log_label = tk.Label(self, text="Weighting")
        log_label.grid(row=6, column=0)
        log = tk.BooleanVar()
        log.set(True)
        log_select = tk.Checkbutton(self, text="Use Log Weighting \n (Recommended)", variable=log)
        log_select.grid(row=6, column=1, pady=20)
        


        def calculate_dft():
            global master_df
            
            config = {
                "Repertoire": rep.get(),
                "Excerpt Measures": (beg.get(), end.get()),
                "Window Size": win_size.get(),
                "Strategy": strat.get(),
                "Log Weighting": log.get(),
                }
            score_data = score_to_data(config.values())
            master_df = vis.make_dataframes(score_data=score_data)


            
        calculate = ttk.Button(self, text="Calculate", command=calculate_dft)
        calculate.grid(row=8, column=0, columnspan=4, sticky="we")
              
        

class DataPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.make_empty_graph()
        self.make_empty_dataframe()
        self.var = tk.IntVar()
        self.graph_options = []
        
        
        def graph_callback(var, indx, mode):
            print("Graph changed to {}".format(graph.get()))
            self.var = self.graph_options.index(graph.get())
            print("New variable is {}".format(self.var))
            
            
        graph = tk.StringVar()
        self.graph_options = ["Magnitudes"]
        for i in range(1, 12 // 2 + 1):
            self.graph_options.append(f'f{i}')
        graph_menu = tk.OptionMenu(self, variable=graph, value=None)
        graph_menu.grid(row=0, column=1, sticky='w')
        graph.trace_add(mode='write', callback=graph_callback)
        graph.set(self.graph_options[0])
        for g in self.graph_options:
            graph_menu['menu'].add_command(label=g, command=tk._setit(var=graph, value=g))
      
        
    def make_empty_graph(self):
        fig = Figure(figsize=(10,2.5))
        sub = fig.add_subplot(111)
        sub_left = fig.add_subplot(111)
        sub_right = sub_left.twinx()
        sub_left.set_xlabel("X Axis")
        sub_left.set_ylabel("Left Y Axis")
        sub_right.set_ylabel("Right Y Axis")
        fig.tight_layout()
        
        
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget()
        canvas.get_tk_widget().grid(row=4, column=0, sticky="nswe", columnspan=7)
        
        toolbar_frame = tk.Frame(self)
        toolbar_frame.grid(row=3, column=0, sticky="w", columnspan=7)
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.pack()
        
        graph_button = ttk.Button(self, text="Update Graph", command=lambda: self.make_graph(canvas=canvas, sub=sub, left=sub_left, right=sub_right))
        graph_button.grid(row=1, column=0, sticky="w")
        
        
    def make_graph(self, canvas, sub, left, right):
        global master_df
        sub.clear()
        left.clear()
        right.clear()
        
        if self.var == 0:
            for i in range(1, 12 // 2 + 1):
                left.stackplot(range(len(master_df[f'f{i} Magnitude'])), 
                        master_df[f'f{i} Magnitude'], 
                        # color=vis.xkcd_colors[f'f{i}_colors'][0],
                        color=vis.hex_colors[f'f{i}_colors'][0],
                        alpha=0.4,
                        labels=[f'f{i} Magnitude'])
                left.margins(x=0) 

            left.legend(loc="lower center", 
                        bbox_to_anchor=(0.5, 1.02), 
                        borderaxespad=0, 
                        fancybox=True, 
                        shadow=True, 
                        prop={'size': 7}, 
                        ncol=6
                        )
            left.set_ylabel("Magnitude")
            right.grid(b=False)
            right.margins(x=0)
            right.tick_params(axis='y', length=0)
            right.set_yticklabels([])
            left.set_xlabel("Window Number")
            left.set_xticks(ticks=range(0, len(master_df[f'f{i} Phase']), 20))
            
        else:
            i = self.var
            right.stackplot(range(len(master_df[f'f{i} Magnitude'])), 
                    master_df[f'f{i} Magnitude'], 
                    # color=vis.xkcd_colors[f'f{i}_colors'][0],
                    color=vis.hex_colors[f'f{i}_colors'][0],
                    alpha=0.3,
                    labels=[f'f{i} Magnitude']
                    )
            right.grid(b=False)
            right.margins(x=0) 
            right.set_ylabel("Magnitude")
            
            left.plot(range(len(master_df[f'f{i} Phase'])),
                    master_df[f'f{i} Phase'],
                    # color=vis.xkcd_colors[f'f{i}_colors'][1],
                    color=vis.hex_colors[f'f{i}_colors'][1],
                    label=f'f{i} Phase',
                    )
            left.plot(range(len(master_df[f'f{i} Quantized Phase'])),
                    master_df[f'f{i} Quantized Phase'],
                    # color=vis.xkcd_colors[f'f{i}_colors'][2],
                    color=vis.hex_colors[f'f{i}_colors'][2],
                    label=f'f{i} Quantized Phase',
                    )
            left.set_yticks(ticks=range(-180,210,30))
            left.grid(axis='x')
            left.margins(x=0)
            left.set_ylabel("Phase")
            left.set_xlabel("Window Number")
            left.set_xticks(ticks=range(0, len(master_df[f'f{i} Phase']), 20))

            left.legend(loc="lower center", 
                        bbox_to_anchor=(0.5, 1.02), 
                        borderaxespad=0, 
                        fancybox=True, 
                        shadow=True, 
                        prop={'size': 7}, 
                        ncol=2
                        )
        canvas.draw()
            
        
    def make_empty_dataframe(self):
        empty_df = DataFrame({})
        frame = tk.Frame(self)
        frame.grid(row=6, column=0, sticky="we", columnspan=7)
        pt = Table(frame, showtoolbar=True, showstatusbar=True, dataframe=empty_df)
        pt.show()
        
        df_button = ttk.Button(self, text="Update Table", command=lambda: self.make_data(table=pt))
        df_button.grid(row=1, column=1, sticky="w")       
        
        
    def make_data(self, table):
        global master_df
        table.clearTable()
        
        df = table.model.df
        df['Window'] = master_df['Window Number']
        df['Measures'] = master_df['Measure Range']
        df['Array'] = master_df['Original Array']
        if self.var == 0:
            for i in range(0, 12 // 2 + 1):
                df[f'| f{i} |'] = master_df[f'f{i} Magnitude']
            set_option('display.max_colwidth', 40)
            
        else:
            i = self.var
            df[f'| f{i} |'] = master_df[f'f{i} Magnitude']
            df['Phase'] = master_df[f'f{i} Phase']
            df['Quantized Phase'] = master_df[f'f{i} Quantized Phase']
        table.redraw()


        
class MasterDataFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.make_empty_dataframe()
        
    def make_empty_dataframe(self):
        empty_df = DataFrame({})
        frame = tk.Frame(self)
        frame.grid(row=5, column=0, sticky="nswe", columnspan=9)
        pt = Table(frame, showtoolbar=True, showstatusbar=True, dataframe=empty_df)
        pt.show()
        
        df_button = ttk.Button(self, text="Update Table", command=lambda: self.make_data(table=pt))
        df_button.grid(row=1, column=1, sticky="w")   
    
    
    def make_data(self, table):
        global master_df
        table.clearTable()
        
        df = table.model.df = master_df
        
        table.redraw()
    

app = PanoramaGenerator()
# app.geometry("1024x768")
# app.mainloop()



