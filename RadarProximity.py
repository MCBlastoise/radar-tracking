import os
import xarray as xr
import geopy.distance
from RadarLocations import radars

def read_radar_coords(code):
    return (float(radars[code]['longitude']), float(radars[code]['latitude']))

def calc_GLM_index(hr, mt):
    return hr * 180 + mt * 3

def extract_GLM(file):
    glm = xr.open_dataset(file)

    try:
        flon = glm['flash_lon'].values
        flat = glm['flash_lat'].values
    except ValueError:
        flon = ()
        flat = ()
        print('File empty')

    return zip(flon, flat)

def count_GLM_min(data_direc, code, time, radius=100):
    port_lon, port_lat = read_radar_coords(code)
    direc_iter = os.listdir(data_direc)

    ltg_count = 0
    start = calc_GLM_index(time[0], time[1])

    for x in range(start, start + 3):
        path = data_direc + direc_iter[x]
        for lon, lat in extract_GLM(path):
            dist = geopy.distance.great_circle((port_lat, port_lon), (lat, lon)).kilometers
            if dist <= radius:
                ltg_count += 1

    return ltg_count
