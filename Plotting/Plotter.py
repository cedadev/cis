# Plotter.py
# Created by WALDM on 14th Jan 2013
# Copyright TODO
#
# Class for plotting graphs

import iris.plot as iplt
import matplotlib.pyplot as plt
   
def plot_line_graph(data, out_filename = None, *args, **kwargs):    
    iplt.plot(data, *args, **kwargs)   
    show_or_save_plot(out_filename)
    
def plot_scatter_graph(data, out_filename = None, *args, **kwargs):        
    iplt.points(data, *args, **kwargs)   
    show_or_save_plot(out_filename)
    
def plot_heatmap(data, out_filename = None, *args, **kwargs):        
    iplt.pcolormesh(data, *args, **kwargs)   
    show_or_save_plot(out_filename)
     
def show_or_save_plot(out_filename = None):
    if out_filename == None:
        plt.show()
    else:
        # Will overwrite if file already exists
        plt.savefig(out_filename)