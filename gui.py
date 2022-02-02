import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import mplcursors

import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure


data = pd.read_csv("mjerenja.csv")

# latitude and longitude of image corners
map_coords = {
    "top_left": (45.3769, 14.2833),
    "bottom_right": (45.2763, 14.5420)
}

# latitude and longitude for each beach
beach_coords = {
    "Bivio - Dom umirovljenika": (45.34310004762417, 14.362826355545845),
    "Bivio - Kostanj-plaža za invalide": (45.349817422153514, 14.341178663651757),
    "Bivio - Rekreacijski centar": (45.34873220445173, 14.343477903105173),
    "Bivio plaža": (45.34539336568614, 14.35513659565956),
    "Bivio skalete": (45.34556065748801, 14.352212850179917),
    "Glavanovo istok": (45.31542601555457, 14.46919349547311),
    "Glavanovo zapad": (45.315667986612766, 14.468036940382321),
    "Grcevo": (45.31216083191336, 14.473306879055146),
    "Kantrida - Djecja bolnica": (45.34088176714463, 14.368092523722112),
    "Kantrida - Rekreacijski centar 3. Maj": (45.337117180882984, 14.388154179323333),
    "Kantrida - Vila Nora": (45.339976761585895, 14.373881690432423),
    "Kantrida - bazen istok": (45.34017637489077, 14.372109913644168),
    "Kantrida - bazen zapad": (45.34113087976162, 14.369909847974812),
    "Kantrida - istok": (45.33793474173825, 14.38275949051625),
    "Kantrida - zapad": (45.3381305661761, 14.378580700268692),
    "Kostrena - Ronilacki klub": (45.3029149388772, 14.487858038752638),
    "Kostrena - Stara voda": (45.29323815918468, 14.504907232982019),
    "Kostrena - uvala Svežanj": (45.29797028722772, 14.49536956059997),
    "Kostrena - Žurkovo": (45.30685134104617, 14.488179282983163),
    "Kupalište Hotela Jadran": (45.31864387178061, 14.464244281274247),
    "Preluk - istok": (45.3517806319324, 14.336806589079975),
    "Preluk - sredina": (45.35223744282661, 14.332358499015088),
    "Preluk - zapad": (45.354606274497414, 14.332014909588365),
    "Ružicevo": (45.31299927673528, 14.471526711868467),
    "Sablicevo": (45.31816305990945, 14.465758565898556)
}

def map_coords_to_img_coords(img, lat, lon):
    """
    Find pixel coordinates for given geographical coordinates (lat, lon).
    """
    height = img.shape[0]
    width = img.shape[1]

    lat_diff = map_coords["top_left"][0] - map_coords["bottom_right"][0]
    lon_diff = map_coords["bottom_right"][1] - map_coords["top_left"][1]
    x = (lon - map_coords["top_left"][1]) / lon_diff * width
    y = (map_coords["top_left"][0] - lat) / lat_diff * height
    return x, y

root = tk.Tk()
root.wm_title("Vizualizacija mjerenja u kvarnerskom zaljevu: salinitet, temperatura i E. Coli")

# sidebar
sidebar = tk.Frame(root, width=350, height=500, relief='sunken', borderwidth=2)
sidebar.pack(expand=False, fill='both', side='left', anchor='nw')
# main content area - visualization
mainarea = tk.Frame(root, bg='#CCC', width=500, height=500)
mainarea.pack(expand=True, fill='both', side='right')

SALINITY = 0
TEMPERATURE = 1
ECOLI = 2
def select_color_variable():
    pass
    #selection = "You selected the option " + str(var.get())
    #label.config(text = selection)

def select_size_variable():
    pass
    #selection = "You selected the option " + str(var.get())
    #label.config(text = selection)

def add_widgets_to_sidebar(sidebar):
    values = (SALINITY, TEMPERATURE, ECOLI)
    variable_names = ("Salinitet", "Temperatura", "E. Coli")

    # create radio buttons for selecting the variable which should be used
    # to determine point size
    tk.Label(sidebar, text="Veličina kruga", font='Helvetica 11 bold').pack(fill='x')
    size_variable = tk.IntVar()
    for val, var_name in zip(values, variable_names):
        tk.Radiobutton(
            sidebar, text=var_name, variable=size_variable, value=val,
            command=select_size_variable, width=35
        ).pack(anchor=tk.W)
    
    separator3 = ttk.Separator(sidebar, orient='horizontal')
    separator3.pack(fill='x')

    # create radio buttons for selecting the variable which should be used
    # to determine point color
    tk.Label(sidebar, text="Boja kruga", font='Helvetica 11 bold').pack(fill='x')
    color_variable = tk.IntVar()
    for val, var_name in zip(values, variable_names):
        tk.Radiobutton(
            sidebar, text=var_name, variable=color_variable, value=val,
            command=select_color_variable, width=35
        ).pack(anchor=tk.W)

    separator2 = ttk.Separator(sidebar, orient='horizontal')
    separator2.pack(fill='x')
    tk.Label(sidebar, text="Datum opažanja", font='Helvetica 11 bold').pack(fill='x')
    
    dates = list(data["Datum"].unique())
    
    variable = tk.StringVar(sidebar)
    variable.set(dates[0]) # default value
    
    w = tk.OptionMenu(sidebar, variable, *dates)
    w.pack()

add_widgets_to_sidebar(sidebar)

img = mpimg.imread("kvarnerski-zaljev.png")
fig = Figure(figsize=(5, 4), dpi=100)
#fig.add_subplot(111).imshow(img)
ax = fig.gca()
ax.imshow(img)
## imgplot = plt.imshow(img)

def update_visualization(data, date, color_variable, size_variable):
    observations = data[data["Datum"] == date]
    x = []
    y = []
    sizes = []
    colors = []

    column_names = ["Slanost", "Temperatura mora", "EC"]
    min_values = [
        observations["Slanost"].min(),
        observations["Temperatura mora"].min(),
        observations["EC"].min()
    ]
    max_values = [
        observations["Slanost"].max(),
        observations["Temperatura mora"].max(),
        observations["EC"].max()
    ]

    def get_circle_size(size_variable, value):
        """
        Select circle size between MIN_SIZE and MAX_SIZE
        depending on the given variable value.
        """
        MIN_SIZE = 200
        MAX_SIZE = 500
        value_range = max_values[size_variable] - min_values[size_variable]
        ratio = (value - min_values[size_variable]) / value_range
        circle_size = MIN_SIZE + ratio * (MAX_SIZE - MIN_SIZE)
        return circle_size

    def create_cirle_size_legend():
        min_size = ax.scatter([],[], s=200, marker='o', color='#555555')
        max_size = ax.scatter([],[], s=500, marker='o', color='#555555')
        fig.legend(
            (min_size, max_size),
            (str(min_values[size_variable]), str(max_values[size_variable])),
            scatterpoints=1, loc='lower right', ncol=1,
            fontsize=8, borderpad=1.5, labelspacing=2, title=column_names[size_variable]
        )

    annotations = []
    for idx, row in observations.iterrows():
        lat, lon = beach_coords[row["Ime plaze"]]
        beach_x, beach_y = map_coords_to_img_coords(img, lat, lon)
        x.append(beach_x)
        y.append(beach_y)
        colors.append(row[column_names[color_variable]])
        sizes.append(get_circle_size(size_variable, row[column_names[size_variable]]))

        annotations.append(
            row["Ime plaze"] + "\n" +
            "Slanost: " + str(row["Slanost"]) + "\n" +
            "Temperatura mora: " + str(row["Temperatura mora"]) + "\n" +
            "E. Coli: " + str(row["EC"])
        )
    points = ax.scatter(
        x, y, s=sizes, c=colors, alpha=1,
        vmin=min_values[color_variable], vmax=max_values[color_variable]
    )
    create_cirle_size_legend()

    mplcursors.cursor(points, hover=True).connect(
        "add", lambda sel: sel.annotation.set_text(annotations[sel.index])
    )
    fig.colorbar(points, label=column_names[color_variable])

update_visualization(data, "13/05/2009", ECOLI, TEMPERATURE)
## x = []
## y = []
## sizes = []
## colors = []
## ecoli_min = data["EC"].min()
## ecoli_max = data["EC"].max()
## temp_min = data["Temperatura mora"].min()
## temp_max = data["Temperatura mora"].max()
## salinity_min = data["Slanost"].min()
## salinity_max = data["Slanost"].max()
## 
## beaches = []
## annotations = []
## for idx, row in data.iterrows():
##     lat, lon = beach_coords[row["Ime plaze"]]
##     beach_x, beach_y = map_coords_to_img_coords(img, lat, lon)
##     if row["Ime plaze"] not in beaches:
##         x.append(beach_x)
##         y.append(beach_y)
##         colors.append(row["EC"])
##         sizes.append(200)
##         beaches.append(row["Ime plaze"])
##         annotations.append(
##             row["Ime plaze"] + "\n" +
##             "Slanost: " + str(row["Slanost"]) + "\n" +
##             "Temperatura mora: " + str(row["Temperatura mora"]) + "\n" +
##             "E. Coli: " + str(row["EC"])
##         )
## points = ax.scatter(x, y, s=sizes, c=colors, alpha=1, vmin=ecoli_min, vmax=ecoli_max)
## mplcursors.cursor(points, hover=True).connect(
##     "add", lambda sel: sel.annotation.set_text(annotations[sel.index])
## )
## fig.colorbar(points)
#plt.show()


canvas = FigureCanvasTkAgg(fig, master=mainarea)  # A tk.DrawingArea.
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

toolbar = NavigationToolbar2Tk(canvas, mainarea)
toolbar.update()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


def on_key_press(event):
    print("you pressed {}".format(event.key))
    key_press_handler(event, canvas, toolbar)

canvas.mpl_connect("key_press_event", on_key_press)


def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

button = tk.Button(master=mainarea, text="Quit", command=_quit)
button.pack(side=tk.BOTTOM)

label = tk.Label(sidebar)
label.pack()
tk.mainloop()
# If you put root.destroy() here, it will cause an error if the window is
# closed with the window manager.

