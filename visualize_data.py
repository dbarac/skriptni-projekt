import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import mplcursors

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

img = mpimg.imread("kvarnerski-zaljev.png")
imgplot = plt.imshow(img)

x = []
y = []
sizes = []
colors = []
ecoli_min = data["EC"].min()
ecoli_max = data["EC"].max()
temp_min = data["Temperatura mora"].min()
temp_max = data["Temperatura mora"].max()
salinity_min = data["Slanost"].min()
salinity_max = data["Slanost"].max()

beaches = []
annotations = []
for idx, row in data.iterrows():
    lat, lon = beach_coords[row["Ime plaze"]]
    beach_x, beach_y = map_coords_to_img_coords(img, lat, lon)
    if row["Ime plaze"] not in beaches:
        x.append(beach_x)
        y.append(beach_y)
        colors.append(row["EC"])
        sizes.append(200)
        beaches.append(row["Ime plaze"])
        annotations.append(
            row["Ime plaze"] + "\n" +
            "Slanost: " + str(row["Slanost"]) + "\n" +
            "Temperatura mora: " + str(row["Temperatura mora"]) + "\n" +
            "E. Coli: " + str(row["EC"])
        )
points = plt.scatter(x, y, s=sizes, c=colors, alpha=1, vmin=ecoli_min, vmax=ecoli_max)
mplcursors.cursor(points, hover=True).connect(
    "add", lambda sel: sel.annotation.set_text(annotations[sel.index])
)
plt.colorbar()
plt.show()

    


