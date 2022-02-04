import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import mplcursors

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

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
root.wm_title("Vizualizacija mjerenja u Kvarnerskom zaljevu: salinitet, temperatura i E. Coli")

# sidebar
sidebar = tk.Frame(root, width=350, height=500, relief='sunken', borderwidth=2)
sidebar.pack(expand=False, fill='both', side='left', anchor='nw')
# main content area - visualization
mainarea = tk.Frame(root, bg='#CCC', width=500, height=500)
mainarea.pack(expand=True, fill='both', side='right')


all_beaches = list(data["Ime plaze"].unique())
selected_beaches = set(data["Ime plaze"].unique())
dates = list(data["Datum"].unique()) # assumption: data rows are sorted chronologically

SALINITY = 0
TEMPERATURE = 1
ECOLI = 2

# visualization parameters
size_variable = tk.IntVar(value=SALINITY)
color_variable = tk.IntVar(value=ECOLI)
start_date = tk.StringVar()
end_date = tk.StringVar()
beach_vars = [tk.IntVar(value=1) for i in range(len(all_beaches))] # selected or not

info_label = None

def update_selected_beaches():
    for i, var in enumerate(beach_vars):
        if var.get() == 1:
            selected_beaches.add(all_beaches[i])
        elif var.get() == 0:
            selected_beaches.discard(all_beaches[i])

def check_all_beaches():
    for i, var in enumerate(beach_vars):
        var.set(1)
        selected_beaches.add(all_beaches[i])

def uncheck_all_beaches():
    for i, var in enumerate(beach_vars):
        var.set(0)
        selected_beaches.discard(all_beaches[i])

def visualization_callback():
    """
    This will run when one of the following changes:
     - color variable
     - size variable
     - the range of dates (observations which should be visualized)
     - beaches selected for visualization
    """
    start_idx = dates.index(start_date.get())
    end_idx = dates.index(end_date.get())

    if start_idx > end_idx:
        info_label.config(text="Početni datum ne smije biti kasniji od zadnjeg datuma")
        return
    else:
        info_label.config(text="")

    selected_dates = dates[start_idx:end_idx+1]
    if isinstance(selected_dates, str):
        selected_dates = [selected_dates]

    update_visualization(
        data, selected_dates, color_variable.get(), size_variable.get()
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

    # create dropdown menus for selecting start date and end date
    tk.Label(sidebar, text="Početni datum", font='Helvetica 11 bold').pack(fill='x')
    start_date.set("8/6/2010") # default value
    tk.OptionMenu(sidebar, start_date, *dates).pack()
    tk.Label(sidebar, text="Zadnji datum", font='Helvetica 11 bold').pack(fill='x')
    end_date.set("8/6/2010") # default value
    tk.OptionMenu(sidebar, end_date, *dates).pack()

    ttk.Separator(sidebar, orient='horizontal').pack(fill='x')

    # add checkboxes for selecting beaches
    tk.Label(sidebar, text="Odabir plaža", font='Helvetica 11 bold').pack(fill='x')
    scrollabe_area = ScrolledText(sidebar, width=38, height=12)
    scrollabe_area.pack()
    for i, beach in enumerate(all_beaches):
        checkbox = tk.Checkbutton(
            scrollabe_area, text=beach, variable=beach_vars[i], onvalue=1, anchor=tk.W,
            command=update_selected_beaches, bg="white"
        )
        scrollabe_area.window_create('end', window=checkbox)
        scrollabe_area.insert('end', '\n')
    scrollabe_area['state'] = 'disabled'
    tk.Button(sidebar, text='Check all', command=check_all_beaches).pack()
    tk.Button(sidebar, text='Uncheck all', command=uncheck_all_beaches).pack()

    ttk.Separator(sidebar, orient='horizontal').pack(fill='x')

    tk.Button(sidebar, text='Update visualization', command=visualization_callback).pack()

    global info_label
    info_label = tk.Label(sidebar, text="", font='Helvetica 9 bold',fg='#ff0000')
    info_label.pack(fill='x')

    quit_button = tk.Button(master=sidebar, text="Quit", command=quit_callback)
    quit_button.pack(side=tk.BOTTOM)

add_widgets_to_sidebar(sidebar)

img = mpimg.imread("kvarnerski-zaljev.png")

# canvas for the map
fig = Figure(figsize=(5, 4), dpi=95)
canvas = FigureCanvasTkAgg(fig, master=mainarea)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
toolbar = NavigationToolbar2Tk(canvas, mainarea)
toolbar.update()

# canvas for the scatterplots
fig2 = Figure(figsize=(5, 2), dpi=95)
canvas2 = FigureCanvasTkAgg(fig2, master=mainarea)
canvas2.draw()
canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

def update_scatterplots(observations, selected_dates):
    """
    Draw scatterplots (variable pairs). Display correlation coefficient values.
    """
    fig2.clf() # clear figure
    if len(selected_dates) > 1:
        dates_str = selected_dates[0] + " do " + selected_dates[-1]
    else:
        dates_str = selected_dates[0]

    if (len(observations) == 0):
        fig2.suptitle("0 mjerenja odabrano")
        return
    else:
        fig2.suptitle("Parovi opažanja i korelacijski koeficijenti: " + dates_str)

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


def update_visualization(data, selected_dates, color_variable, size_variable):
    fig.clf() # clear figure content
    ax = fig.gca()
    ax.imshow(img)
    ax.set_title(
        "Vizualizacija mjerenja u Kvarnerskom zaljevu: "
        "salinitet, temperatura i E. Coli"
    )

    observations = data[
        (data["Datum"].isin(selected_dates)) & (data["Ime plaze"].isin(selected_beaches))
    ]

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

    MIN_SIZE = 100
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
    update_scatterplots(observations, selected_dates)
    canvas2.draw()

# visualize with initial settings
update_visualization(data, ["8/6/2010"], color_variable.get(), size_variable.get())

# set to fullscreen
root.attributes('-zoomed', True)

tk.mainloop()
# If you put root.destroy() here, it will cause an error if the window is
# closed with the window manager.