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
size_variable = tk.IntVar()
color_variable = tk.IntVar()

selected_date = tk.StringVar()

def visualization_callback():
    """
    This will run when one of the following changes:
     - color variable
     - size variable
     - the date of observations which should be visualized
    """
    update_visualization(
        data, selected_date.get(), color_variable.get(), size_variable.get()
    )

def quit_callback():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

def add_widgets_to_sidebar(sidebar):
    values = (SALINITY, TEMPERATURE, ECOLI)
    variable_names = ("Salinitet", "Temperatura", "E. Coli")

    # create radio buttons for selecting the variable which should be used
    # to determine point size
    tk.Label(sidebar, text="Veličina kruga", font='Helvetica 11 bold').pack(fill='x')
    for val, var_name in zip(values, variable_names):
        tk.Radiobutton(
            sidebar, text=var_name, variable=size_variable, value=val,
            command=visualization_callback, width=35
        ).pack(anchor=tk.W)
 
    ttk.Separator(sidebar, orient='horizontal').pack(fill='x')

    # create radio buttons for selecting the variable which should be used
    # to determine point color
    tk.Label(sidebar, text="Boja kruga", font='Helvetica 11 bold').pack(fill='x')
    for val, var_name in zip(values, variable_names):
        tk.Radiobutton(
            sidebar, text=var_name, variable=color_variable, value=val,
            command=visualization_callback, width=35
        ).pack(anchor=tk.W)

    ttk.Separator(sidebar, orient='horizontal').pack(fill='x')

    # create dropdown menu for selecting date
    tk.Label(sidebar, text="Datum opažanja", font='Helvetica 11 bold').pack(fill='x')
    dates = list(data["Datum"].unique())
    dates.append("all dates")
    selected_date.set(dates[0]) # default value
    tk.OptionMenu(sidebar, selected_date, *dates).pack()

    submit_button = tk.Button(
        sidebar, text='Update', command=visualization_callback
    )
    submit_button.pack()

    quit_button = tk.Button(master=sidebar, text="Quit", command=quit_callback)
    quit_button.pack(side=tk.BOTTOM)

add_widgets_to_sidebar(sidebar)

img = mpimg.imread("kvarnerski-zaljev.png")
fig = Figure(figsize=(5, 4), dpi=95)

# canvas for the map
canvas = FigureCanvasTkAgg(fig, master=mainarea)  # A tk.DrawingArea.
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

toolbar = NavigationToolbar2Tk(canvas, mainarea)
toolbar.update()

fig2 = Figure(figsize=(7, 1), dpi=95)

# canvas for the scatterplots
canvas2 = FigureCanvasTkAgg(fig2, master=mainarea)  # A tk.DrawingArea.
canvas2.draw()
canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

def update_scatterplots(observations, date):
    """
    Draw scatterplots (variable pairs). Display correlation coefficient values.
    """
    fig2.clf() # clear
    fig2.suptitle("Parovi opažanja i korelacijski koeficijenti: " + date)
    
    ax1 = fig2.add_subplot(131)
    ax1.set_xlabel("Slanost")
    ax1.set_ylabel("E. Coli")
    ax1.set_title(
        "Pearsonov koeficijent korelacije: {:.2f}".format( 
            np.corrcoef(observations["Slanost"], observations["EC"])[0, 1]),
        fontsize=10
    )
    ax1.scatter(observations["Slanost"], observations["EC"])
    
    ax2 = fig2.add_subplot(132)
    ax2.set_xlabel("Slanost")
    ax2.set_ylabel("Temperatura mora")
    ax2.set_title(
        "Pearsonov koeficijent korelacije: {:.2f}".format( 
            np.corrcoef(observations["Slanost"], observations["Temperatura mora"])[0, 1]),
        fontsize=10
    )
    ax2.scatter(observations["Slanost"], observations["Temperatura mora"])
    
    ax3 = fig2.add_subplot(133)
    ax3.set_xlabel("E. Coli")
    ax3.set_ylabel("Temperatura mora")
    ax3.set_title(
        "Pearsonov koeficijent korelacije: {:.2f}".format( 
            np.corrcoef(observations["EC"], observations["Temperatura mora"])[0, 1]),
        fontsize=10
    )
    ax3.scatter(observations["EC"], observations["Temperatura mora"])


def update_visualization(data, date, color_variable, size_variable):
    fig.clf() # clear figure content
    ax = fig.gca()
    ax.imshow(img)
    ax.set_title(
        "Vizualizacija mjerenja u kvarnerskom zaljevu: "
        "salinitet, temperatura i E. Coli"
    )

    if date == "all dates":
        observations = data
    else:
        observations = data[data["Datum"] == date]

    column_names = ("Slanost", "Temperatura mora", "EC")
    min_values = (
        observations["Slanost"].min(),
        observations["Temperatura mora"].min(),
        observations["EC"].min()
    )
    max_values = (
        observations["Slanost"].max(),
        observations["Temperatura mora"].max(),
        observations["EC"].max()
    )

    MIN_SIZE = 200
    MAX_SIZE = 600
    def get_circle_size(size_variable, value):
        """
        Select circle size between MIN_SIZE and MAX_SIZE
        depending on the given variable value.
        """
        value_range = max_values[size_variable] - min_values[size_variable]
        ratio = (value - min_values[size_variable]) / value_range
        circle_size = MIN_SIZE + ratio * (MAX_SIZE - MIN_SIZE)
        return circle_size

    def create_cirle_size_legend():
        min_size = ax.scatter([],[], s=MIN_SIZE, marker='o', color='#555555')
        max_size = ax.scatter([],[], s=MAX_SIZE, marker='o', color='#555555')
        fig.legend(
            (min_size, max_size),
            (str(min_values[size_variable]), str(max_values[size_variable])),
            scatterpoints=1, loc='lower right', ncol=1,
            fontsize=8, borderpad=1.5, labelspacing=2, title=column_names[size_variable]
        )

    x = []
    y = []
    sizes = []
    colors = []
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

    canvas.draw()

    # draw scatterplots (variable pairs) and display correlation coefficient values
    update_scatterplots(observations, date)
    canvas2.draw()

update_visualization(data, "13/05/2009", ECOLI, TEMPERATURE)

def on_key_press(event):
    #print("you pressed {}".format(event.key))
    key_press_handler(event, canvas, toolbar)

canvas.mpl_connect("key_press_event", on_key_press)

tk.mainloop()
# If you put root.destroy() here, it will cause an error if the window is
# closed with the window manager.