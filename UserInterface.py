import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import  FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib import style
from matplotlib import pyplot as plt

import tkinter as tk
from tkinter import ttk

from pandastable import Table, TableModel
import pandas as pd

from Corpus import full_corpus
from CalculationFunctions import score_to_data
import visuals as vis

LARGE_FONT = ("Verdana", 16)
NORMAL_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 8)
style.use("ggplot")
score_data = "none"
master_df = "none"
EDO = 12




class PanoramaGenerator(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "DFT Panorama Generator")
        
        container = tk.Frame(self)
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=quit)
        menubar.add_cascade(label="File", menu=filemenu)
        
        goto_menu = tk.Menu(menubar, tearoff=1)
        goto_menu.add_command(label="Home", command=lambda: self.show_frame(StartPage))
        goto_menu.add_command(label="Data", command=lambda: self.show_frame(DataPage))
        goto_menu.add_command(label="Phase Comparison", command=lambda: self.show_frame(PhaseComparisonPage))
        goto_menu.add_command(label="Master Data Frame", command=lambda: self.show_frame(MasterDataFrame))
        menubar.add_cascade(label="Go To", menu=goto_menu)
        
        tk.Tk.config(self, menu=menubar)
        
        
        self.frames = {}
        
        for F in (StartPage, DataPage, PhaseComparisonPage, MasterDataFrame):
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
        rep_select = ttk.OptionMenu(self, rep, *full_corpus)
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
        
        def edo_callback(var, indx, mode):
            global EDO
            print("EDO changed to {}".format(edo.get()))
            EDO = edo.get()
        
        edo_label = tk.Label(self, text="EDO")
        edo_label.grid(row=7, column=0)
        edo = tk.IntVar()
        edo.set(12)
        edo.trace_add(mode='write', callback=edo_callback)
        edo_select = tk.OptionMenu(self, edo, 12, 24)
        edo_select.grid(row=7, column=1)
 

        def calculate_dft():
            global master_df
            global EDO
            
            config = {
                "Repertoire": rep.get(),
                "Excerpt": exc.get(),
                "Excerpt Measures": (beg.get(), end.get()),
                "Window Size": win_size.get(),
                "Strategy": strat.get(),
                "Log Weighting": log.get(),
                "EDO" : EDO
            }
            score_data = score_to_data(config.values())
            master_df = vis.make_dataframes(score_data=score_data, edo=EDO)
            print(f'The EDO in use is {EDO}')

            
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
            
            
        message = ["Update EDO First"]
        graph = tk.StringVar()
        graph.set(message[0])
        graph_menu = tk.OptionMenu(self, graph, *message)
        graph_menu.grid(row=0, column=1, sticky='w')
        graph.trace_add(mode='write', callback=graph_callback)
        
        
        def update_options():
            global EDO
            graph_menu['menu'].delete(0, 'end')
            self.graph_options = ["Magnitudes"]
            for i in range(1, EDO//2 + 1):
                self.graph_options.append(f'f{i}')
            graph.set(self.graph_options[0])
            for g in self.graph_options:
                graph_menu['menu'].add_command(label=g, command=tk._setit(var=graph, value=g))
        
        update_button = ttk.Button(self, text="Update EDO", command=lambda: update_options())
        update_button.grid(row=0, column=0, sticky='w')
      
        
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
        global EDO
        sub.clear()
        left.clear()
        right.clear()
        
        if self.var == 0:
            for i in range(1, EDO//2 +1):
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
        empty_df = pd.DataFrame({})
        frame = tk.Frame(self)
        frame.grid(row=6, column=0, sticky="we", columnspan=7)
        pt = Table(frame, showtoolbar=True, showstatusbar=True, dataframe=empty_df)
        pt.show()
        
        df_button = ttk.Button(self, text="Update Table", command=lambda: self.make_data(table=pt))
        df_button.grid(row=1, column=1, sticky="w")       
        
        
    def make_data(self, table):
        global master_df
        global EDO
        table.clearTable()
        
        df = table.model.df
        df['Window'] = master_df['Window Number']
        df['Measures'] = master_df['Measure Range']
        df['Array'] = master_df['Original Array']
        if self.var == 0:
            for i in range(0, EDO//2 + 1):
                df[f'| f{i} |'] = master_df[f'f{i} Magnitude']
            pd.set_option('display.max_colwidth', 40)
            
        else:
            i = self.var
            df[f'| f{i} |'] = master_df[f'f{i} Magnitude']
            df['Phase'] = master_df[f'f{i} Phase']
            df['Quantized Phase'] = master_df[f'f{i} Quantized Phase']
        table.redraw()



class PhaseComparisonPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.make_empty_graph()
        self.make_empty_dataframe()
        self.varX = tk.IntVar()
        self.varY = tk.IntVar()
        self.varZ = tk.IntVar()
        self.X = tk.StringVar()
        self.Y = tk.StringVar()
        self.Z = tk.StringVar()
        self.graph_options = []
        self.menus = []
        
        var_list = [self.X, self.Y, self.Z]
        self.variables = {"X" : self.varX,
                          "Y" : self.varY,
                          "Z" : self.varZ}
        
        
        def update_options():
            global EDO
            self.graph_options.clear()
            for i in range(1, EDO//2 + 1):
                self.graph_options.append(f'f{i} Phase')
            for v in var_list:
                v.set(self.graph_options[0])
            for idx, m in enumerate(self.menus):
                m['menu'].delete(0, 'end')
                for g in self.graph_options:
                    m['menu'].add_command(label=g, command=tk._setit(var=var_list[idx], value=g))
                    
        
        def graph_callback(var, indx, mode):
            for idx, (k, v) in enumerate(self.variables.items()):
                print("Graph changed to {}".format(var_list[idx].get()))
                v = self.graph_options.index(var_list[idx].get()) + 1
                self.variables[k] = v
                print(f'The variable for {k} is now {v}')
                
                
        message = ["Update EDO First"]
        
        for idx, k in enumerate(self.variables.keys()):
            variable_label = ttk.Label(self, text=k)
            variable_label.grid(row=1, column=idx*2 +2, sticky='w')
            variable_menu = tk.OptionMenu(self, var_list[idx], *message)
            variable_menu.grid(row=2, column=idx*2 +2, sticky='w')
            self.menus.append(variable_menu)
            var_list[idx].trace_add(mode='write', callback=graph_callback)
        
        update_button = ttk.Button(self, text="Update EDO", command=lambda: update_options())
        update_button.grid(row=0, column=0, sticky='w')
        
        plus = ttk.Label(self, text="+")
        plus.grid(row=1, column=3, sticky='we')
        plus.config(font=LARGE_FONT)
        minus = ttk.Label(self, text="-")
        minus.grid(row=1, column=5, sticky='we')
        minus.config(font=LARGE_FONT)
         

    def make_empty_graph(self):
        fig = Figure(figsize=(10,2.5))
        sub_left = fig.add_subplot(111)
        sub_right = sub_left.twinx()
        sub_left.set_xlabel("X Axis")
        sub_left.set_ylabel("Left Y Axis")
        sub_right.set_ylabel("Right Y Axis")
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget()
        canvas.get_tk_widget().grid(row=4, column=0, sticky="we", columnspan=7)
        
        toolbar_frame = tk.Frame(self)
        toolbar_frame.grid(row=3, column=0, sticky="w", columnspan=7)
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.pack()
        
        graph_button = ttk.Button(self, 
                                  text="Update Graph", 
                                  command=lambda: self.make_graph(canvas=canvas, 
                                                                  left=sub_left, 
                                                                  right=sub_right, 
                                                                  x=self.variables["X"], 
                                                                  y=self.variables["Y"], 
                                                                  z=self.variables["Z"]))
        graph_button.grid(row=1, column=0, sticky="w")
        
        
    def make_empty_dataframe(self):
        empty_df = pd.DataFrame({})
        frame = tk.Frame(self)
        frame.grid(row=5, column=0, sticky="we", columnspan=7)
        pt = Table(frame, showtoolbar=True, showstatusbar=True, dataframe=empty_df)
        pt.show()
        
        df_button = ttk.Button(self, 
                               text="Update Table", 
                               command=lambda: self.make_data(table=pt, 
                                                              x=self.variables["X"], 
                                                              y=self.variables["Y"], 
                                                              z=self.variables["Z"]))
        df_button.grid(row=1, column=1, sticky="w")      
        
        
    def fix_index(self, phaseIndex):
            if abs(phaseIndex) <= 180:
                return abs(phaseIndex)
            else:
                return abs(360 - abs(phaseIndex))
            
    
    def make_phase_index_df(self, df, x, y, z):
        phase_index_list = (df[f'f{x} Phase'] + df[f'f{y} Phase'] - df[f'f{z} Phase']).values.tolist()
        normalized_phase_index_list = [self.fix_index(phaseIndex=p_idx) for p_idx in phase_index_list]
        phase_index_df = pd.DataFrame({'Phase Index' : phase_index_list, 'Normalized Index' : normalized_phase_index_list})
        return phase_index_df
            
            
        
    def make_graph(self, canvas, left, right, x, y, z):
        global master_df
        left.clear()
        right.clear()
        
        phase_index_df = self.make_phase_index_df(df=master_df, x=x, y=y, z=z)
        
        for i in [x, y, z]:
            # print(f'X is {x} // Y is {y} // Z is {z}')
            left.plot(range(len(master_df[f'f{i} Phase'])),
                        master_df[f'f{i} Phase'],
                        # color=vis.xkcd_colors[f'f{i}_colors'][1],
                        color=vis.hex_colors[f'f{i}_colors'][1],
                        alpha=0.5,
                        label=f'f{i} Phase',
                        )
        
        left.set_yticks(ticks=range(-180,210,30))
        left.grid(axis='x')
        left.margins(x=0)
        left.set_ylabel("Phase")
        left.set_xlabel("Window Number")
        left.set_xticks(ticks=range(0, len(master_df[f'f{i} Phase']), 20))
        
        # left.legend(loc="upper right", 
        #     bbox_to_anchor=(-0.06, 1), 
        #     borderaxespad=0, 
        #     fancybox=True, 
        #     shadow=True, 
        #     prop={'size': 7}, 
        #     ncol=1
        #     )
        
        left.legend(loc="lower left", 
            bbox_to_anchor=(0, 1.02), 
            borderaxespad=0, 
            fancybox=True, 
            shadow=True, 
            prop={'size': 7}, 
            ncol=3
            )  
        
        right.plot(range(len(master_df[f'f{x} Phase'])), 
                   phase_index_df['Normalized Index'],
                    # [self.fix_index(phaseIndex=p_idx) for p_idx in find_index], 
                    # color=vis.xkcd_colors[f'f{i}_colors'][0],
                    color='black',
                    label='Tonal Index'
                    )
        right.grid(b=False)
        right.margins(x=0) 
        right.set_ylabel("Tonal Index")        
        
        # right.legend(loc="upper left", 
        #              bbox_to_anchor=(1.05, 1),  
        #              borderaxespad=0,  
        #              fancybox=True, 
        #              shadow=True, 
        #              prop={'size': 7}, 
        #              ncol=1
        #              )
        
        right.legend(loc="lower right", 
            bbox_to_anchor=(1, 1.02), 
            borderaxespad=0, 
            fancybox=True, 
            shadow=True, 
            prop={'size': 7}, 
            ncol=2
            )    

        canvas.draw()

    
        
    def make_data(self, table, x, y, z):
        global master_df
        table.clearTable()
        
        phase_index_df = self.make_phase_index_df(df=master_df, x=x, y=y, z=z)
        
        df = table.model.df
        df['Window'] = master_df['Window Number']
        df['Measures'] = master_df['Measure Range']
        df['Array'] = master_df['Original Array']
        df[f'f{x} Phase'] = master_df[f'f{x} Phase']
        df[f'f{y} Phase'] = master_df[f'f{y} Phase']
        df[f'f{z} Phase'] = master_df[f'f{z} Phase']
        df['Phase Index'] = phase_index_df['Phase Index']
        df['Normalized Index'] = phase_index_df['Normalized Index']
        table.redraw()        
        
        
class MasterDataFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.make_empty_dataframe()
        
    def make_empty_dataframe(self):
        empty_df = pd.DataFrame({})
        frame = tk.Frame(self)
        frame.grid(row=5, column=0, sticky="nswe", columnspan=7)
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
app.geometry("1024x768")
app.mainloop()



