import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import rgb2hex, Normalize
from matplotlib.colorbar import ColorbarBase
from matplotlib.patches import Polygon

CSV_DATA_PATH = os.getcwd() + '/data/zipcode_data_clean.csv'
STATE_NAMES = [
    "Alaska", "Alabama", "Arkansas", "American Samoa", "Arizona", "California", "Colorado",
    "Connecticut", "District of Columbia", "Delaware", "Florida", "Georgia", "Guam", "Hawaii",
    "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana",
    "Massachusetts", "Maryland", "Maine",  "Michigan", "Minnesota", "Missouri", "Mississippi",
    "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico",
    "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico",
    "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virginia",
    "Virgin Islands", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"
]
ZIPCODES_PER_STATE_MAP_TITLE = "U.S. Zip Code density by state/region"
REPS_PER_STATE_MAP_TITLE = "U.S. Representative density by state/region"


# Lambert Conformal map of lower 48 states.
states_bm_0 = Basemap(llcrnrlon=-119, llcrnrlat=22, urcrnrlon=-64, urcrnrlat=49,
                      projection='lcc', lat_1=33, lat_2=45, lon_0=-95)
# Mercator projection, for Alaska and Hawaii
states_bm_1 = Basemap(llcrnrlon=-190, llcrnrlat=20, urcrnrlon=-143, urcrnrlat=46,
                      projection='merc', lat_ts=20)  # do not change these numbers
# data from U.S Census Bureau
# http://www.census.gov/geo/www/cob/st2000.html
shp_info = states_bm_0.readshapefile('st99_d00', 'states', drawbounds=True,
                                     linewidth=0.45, color='gray')
shp_info_ = states_bm_1.readshapefile(
    'st99_d00', 'states', drawbounds=False)
# use 'reversed hot' colormap
colormap = plt.cm.hot_r
vmin = 0
vmax = 450  # set range.
norm = Normalize(vmin=vmin, vmax=vmax)
fig0, ax0 = plt.subplots()
fig1, ax1 = plt.subplots()
# tzcps = total zip codes per state
# trps = total representatives per state
map_data_dict = {
    "tzcps": {},
    "trps": {}
}
colors_for_map = {
    "tzcps": {},
    "trps": {}
}


def populate_map_data_dict():
    with open(CSV_DATA_PATH, 'r') as csv_data:
        reader = csv.reader(csv_data, skipinitialspace=True)
        print("populating map...")
        for row in reader:
            zip_code = row[0]
            state = row[2]
            rep = row[3]
            if state not in map_data_dict["tzcps"]:
                map_data_dict["tzcps"][state] = set()
            if state not in map_data_dict["trps"]:
                map_data_dict["trps"][state] = set()
            map_data_dict["tzcps"][state].add(zip_code)
            map_data_dict["trps"][state].add(rep)


def get_colors_based_on_density():
    for state in STATE_NAMES:
        tzcps = len(map_data_dict["tzcps"][state])
        trps = len(map_data_dict["trps"][state])
        # Calling colormap with value between 0 and 1 returns
        # rgba value.  Invert color range (hot colors are high
        # population), take sqrt root to spread out colors more.
        colors_for_map["tzcps"][state] = colormap(
            np.sqrt((tzcps-vmin)/(vmax-vmin)))[:3]
        colors_for_map["trps"][state] = colormap(
            np.sqrt((trps-vmin)/(vmax-vmin)))[:3]


def color_each_state_on_map_zero():
    # Color, create, and add polygons to maps
    for index, segment in enumerate(states_bm_0):
        state = STATE_NAMES[index]
        tzcps_color = rgb2hex(colors_for_map["tzcps"][state])
        print(f"tzcps_color for State {state}: {tzcps_color}")
        tzcps_map_polygon = Polygon(
            segment, color=tzcps_color, edgecolor=tzcps_color)
        ax0.add_patch(tzcps_map_polygon)
    for index, segment in enumerate(states_bm_1):
        state = STATE_NAMES[index]
        trps_color = rgb2hex(colors_for_map["trps"][state])
        print(f"trps_color for State {state}: {trps_color}")
        trps_map_polygon = Polygon(
            segment, color=trps_color, edgecolor=trps_color)
        ax1.add_patch(trps_map_polygon)

    # Set Titles for Maps
    ax0.set_title(ZIPCODES_PER_STATE_MAP_TITLE)
    ax1.set_title(REPS_PER_STATE_MAP_TITLE)

# populate_map_data_dict()
# for state in STATE_NAMES:
#     print(f"STATE: {state}")
#     print(
#         f'tzcps: {len(map_data_dict["tzcps"][state])}, trps: {len(map_data_dict["trps"][state])}')
