import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import rgb2hex, Normalize
from matplotlib.colorbar import ColorbarBase
from matplotlib.patches import Polygon

CSV_DATA_PATH = os.getcwd() + '/data/zipcode_data_clean.csv'
ZIPCODES_PER_STATE_MAP_TITLE = "U.S. Zip Code Density by State/Region"
REPS_PER_STATE_MAP_TITLE = "U.S. Representative Density by State/Region"
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

# Lambert Conformal map of lower 48 states.
states_bm_0 = Basemap(llcrnrlon=-119, llcrnrlat=20.2, urcrnrlon=-64, urcrnrlat=48.8,
                      projection='lcc', lat_1=33, lat_2=45, lon_0=-95)
# Mercator projection, for Alaska and Hawaii
states_bm_1 = Basemap(llcrnrlon=-190, llcrnrlat=20.2, urcrnrlon=-143, urcrnrlat=45.8,
                      projection='merc', lat_ts=20)
# data from U.S Census Bureau: http://www.census.gov/geo/www/cob/st2000.html
shp_info = states_bm_0.readshapefile('st99_d00', 'states', drawbounds=True,
                                     linewidth=0.45, color='gray')
shp_info_ = states_bm_1.readshapefile(
    'st99_d00', 'states', drawbounds=False)
# 'reversed hot' colormap
colormap = plt.cm.hot_r
# tzcps = total zip codes per state
# trps = total representatives per state
map_data_dict = {"tzcps": {}, "trps": {}}
colors_for_map = {"tzcps": {}, "trps": {}}
state_names = []
fig0, ax0 = plt.subplots()


def populate_map_data_dict():
    with open(CSV_DATA_PATH, 'r') as csv_data:
        reader = csv.reader(csv_data, skipinitialspace=True)
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


def get_max(map_data_type):
    max_count = 0
    for state in STATE_NAMES:
        curr_state_count = len(map_data_dict[map_data_type][state])
        max_count = curr_state_count if curr_state_count > max_count else max_count
    return max_count


def get_colors_based_on_density(vmin, vmax):
    val_range = vmax - vmin
    for shape_dict in states_bm_0.states_info:
        state = shape_dict["NAME"]
        tzcps = len(map_data_dict["tzcps"][state])
        trps = len(map_data_dict["trps"][state])
        # Calling colormap with a value between 0 and 1 returns argba value.
        # Invert color range (hot colors are high population), and take sqrt root
        # to spread out colors even more.
        colors_for_map["tzcps"][state] = colormap(
            np.sqrt((tzcps-vmin)/(val_range)))[:3]
        colors_for_map["trps"][state] = colormap(
            np.sqrt((trps-vmin)/(val_range)))[:3]
        state_names.append(state)


def plot_state_boundaries_to_maps():
    # Color, create, and add polygons to maps
    for index, segment in enumerate(states_bm_0.states):
        state = state_names[index]
        tzcps_color = rgb2hex(colors_for_map["tzcps"][state])
        tzcps_map_polygon = Polygon(
            segment, facecolor=tzcps_color, edgecolor='lightgrey')
        ax0.add_patch(tzcps_map_polygon)
    # for index, segment in enumerate(states_bm_1):
    #     state = STATE_NAMES[index]
    #     trps_color = rgb2hex(colors_for_map["trps"][state])
    #     print(f"trps_color for State {state}: {trps_color}")
    #     trps_map_polygon = Polygon(
    #         segment, color=trps_color, edgecolor=trps_color)
    #     ax1.add_patch(trps_map_polygon)


def plot_boundaries_for_ak_and_hi():
    AREA_1 = 0.005  # exclude small Hawaiian islands that are smaller than AREA_1
    AREA_2 = AREA_1 * 30.0  # exclude Alaskan islands that are smaller than AREA_2
    AK_SCALE = 0.19  # scale down Alaska to show as a map inset
    HI_OFFSET_X = -1900000  # X coordinate offset amount to move Hawaii "beneath" Texas
    HI_OFFSET_Y = 250000    # similar to above: Y offset for Hawaii
    # X offset for Alaska (These four values are obtained
    AK_OFFSET_X = -250000
    # via manual trial and error, thus changing them is not recommended.
    AK_OFFSET_Y = -750000
    # plot Alaska and Hawaii as map insets
    for index, shapedict in enumerate(states_bm_1.states_info):
        if shapedict["NAME"] in ['Alaska', 'Hawaii']:
            state = state_names[index]
            segment = states_bm_1.states[int(shapedict['SHAPENUM'] - 1)]
            if shapedict['NAME'] == 'Hawaii' and float(shapedict['AREA']) > AREA_1:
                segment = [(x + HI_OFFSET_X, y + HI_OFFSET_Y)
                           for x, y in segment]
                tzcps_color = rgb2hex(colors_for_map["tzcps"][state])
            elif shapedict['NAME'] == 'Alaska' and float(shapedict['AREA']) > AREA_2:
                segment = [(x*AK_SCALE + AK_OFFSET_X, y*AK_SCALE + AK_OFFSET_Y)
                           for x, y in segment]
                tzcps_color = rgb2hex(colors_for_map["tzcps"][state])
            tzcps_map_polygon = Polygon(
                segment, facecolor=tzcps_color, edgecolor='gray', linewidth=.45)
            ax0.add_patch(tzcps_map_polygon)


def plot_bounding_boxes_for_ak_and_hi():
    light_gray = [0.8]*3  # define light gray color RGB
    x1, y1 = states_bm_1(
        [-190, -183, -180, -180, -175, -171, -171], [29, 29, 26, 26, 26, 22, 20])
    # these numbers are fine-tuned manually
    x2, y2 = states_bm_1([-180, -180, -177], [26, 23, 20])
    # do not change them drastically
    states_bm_1.plot(x1, y1, color=light_gray, linewidth=0.8)
    states_bm_1.plot(x2, y2, color=light_gray, linewidth=0.8)


def plot_color_bar(norm):
    # starts with x, y coordinates for start and then width and height in % of figure width
    ax_c0 = fig0.add_axes([0.9, 0.1, 0.022, 0.8])
    cb = ColorbarBase(ax_c0, cmap=colormap, norm=norm, orientation='vertical',
                      label=r'[density per $\mathregular{km^2}$]')


def plot_zipcode_density():
    populate_map_data_dict()
    vmin = 0
    vmax = get_max("tzcps")
    get_colors_based_on_density(vmin, vmax)
    plot_state_boundaries_to_maps()
    plot_boundaries_for_ak_and_hi()
    ax0.set_title(ZIPCODES_PER_STATE_MAP_TITLE)
    # ax1.set_title(REPS_PER_STATE_MAP_TITLE)
    plot_bounding_boxes_for_ak_and_hi()
    plot_color_bar(Normalize(vmin=vmin, vmax=vmax))
    plt.show()


if __name__ == "__main__":
    plot_zipcode_density()
