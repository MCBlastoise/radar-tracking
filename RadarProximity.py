import os
import xarray as xr
import datetime
import geopy.distance
from RadarLocations import radars

def read_radar_coords(code):
    return (float(radars[code]['longitude']), float(radars[code]['latitude']))

def read_filename(filename):
    ts = filename.split('_')[3]
    tup = (int(ts[8:10]), int(ts[10:12]), int(ts[12:14]))
    return tup

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

def find_file(data_direc, h, m):
    direc_iter = sorted(os.listdir(data_direc))
    
    for x in range(0, len(direc_iter)):
        fh, fm, fs = read_filename(direc_iter[x])
        if datetime.datetime(2020, 6, 15, fh, fm, fs) == datetime.datetime(2020, 6, 15, h, m, 0):
            if read_filename(direc_iter[x + 1]) == (fh, fm, 20):
                if read_filename(direc_iter[x + 2]) == (fh, fm, 40):
                    return x
                else:
                    return None
            else:
                return None
        elif datetime.datetime(2020, 6, 15, fh, fm, fs) > datetime.datetime(2020, 6, 15, h, m, 0):
            return None
        
def count_GLM_min(data_direc, code, time, radius=100):
    port_lon, port_lat = read_radar_coords(code)
    direc_iter = sorted(os.listdir(data_direc))

    ltg_count = 0
    if len(direc_iter) == 4320:
        start = calc_GLM_index(time[0], time[1])
    else:
        start = find_file(data_direc, time[0], time[1])
        if start is None:
            print('Data in minute missing')
            return None

    for x in range(start, start + 3):
        path = data_direc + direc_iter[x]
        for lon, lat in extract_GLM(path):
            dist = geopy.distance.great_circle((port_lat, port_lon), (lat, lon)).kilometers
            if dist <= radius:
                ltg_count += 1

    return ltg_count
