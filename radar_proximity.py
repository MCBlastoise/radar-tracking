import os
import netCDF4 as nc
import datetime
import geopy.distance
from radar_locations import radars

def read_radar_coords(code):
    return (float(radars[code]['longitude']), float(radars[code]['latitude']))

def read_filename(filename):
    ts = filename.split('_')[3]
    tup = (int(ts[8:10]), int(ts[10:12]), int(ts[12:14]))
    return tup

def calc_GLM_index(hr, mt):
    return hr * 180 + mt * 3

def extract_GLM(file):
    glm = nc.Dataset(file, mode='r')
    flon = glm['flash_lon'][:]
    flat = glm['flash_lat'][:]

    return (flon, flat)

def find_file(data_direc, h, m):
    direc_iter = sorted(os.listdir(data_direc))

    expected_ind = calc_GLM_index(h, m)
    for x in range( expected_ind if expected_ind < (len(direc_iter) - 1) else len(direc_iter) - 1, -1, -1 ):
        fh, fm, fs = read_filename(direc_iter[x])
        #2020, 6, 15 are dummy values
        if datetime.datetime(2020, 6, 15, fh, fm, fs) == datetime.datetime(2020, 6, 15, h, m, 0):
            if x <= len(direc_iter) - 3:
                if read_filename(direc_iter[x + 1]) == (fh, fm, 20):
                    if read_filename(direc_iter[x + 2]) == (fh, fm, 40):
                        return x
                    else:
                        return None
                else:
                    return None
            else:
                return None
        elif datetime.datetime(2020, 6, 15, fh, fm, fs) < datetime.datetime(2020, 6, 15, h, m, 0):
            return None

def count_GLM_min(data_direc, code, time, radius=100):
    port_lon, port_lat = read_radar_coords(code)
    direc_iter = sorted(os.listdir(data_direc))
    radar_count = 0
    if len(direc_iter) == 4320:
        start = calc_GLM_index(time[0], time[1])
    else:
        start = find_file(data_direc, time[0], time[1])
        if start is None:
            return None

    for x in range(start, start + 3):
        path = data_direc + direc_iter[x]
        flon, flat = extract_GLM(path)
        for lon, lat in zip(flon, flat):
            if near_CONUS(lon, lat, radius):
                dist = geopy.distance.great_circle((port_lat, port_lon), (lat, lon)).kilometers
                if dist <= radius:
                    radar_count += 1

    return radar_count

def all_count_GLM_min(data_direc, code, time, radius=100):
    port_lon, port_lat = read_radar_coords(code)
    direc_iter = sorted(os.listdir(data_direc))
    total_count = 0
    conus_count = 0
    radar_count = 0
    if len(direc_iter) == 4320:
        start = calc_GLM_index(time[0], time[1])
    else:
        start = find_file(data_direc, time[0], time[1])
        if start is None:
            return (None, None, None)

    for x in range(start, start + 3):
        path = data_direc + direc_iter[x]
        flon, flat = extract_GLM(path)
        for lon, lat in zip(flon, flat):
            total_count += 1
            if near_CONUS(lon, lat, radius):
                conus_count += 1
                dist = geopy.distance.great_circle((port_lat, port_lon), (lat, lon)).kilometers
                if dist <= radius:
                    radar_count += 1

    return total_count, conus_count, radar_count

def near_CONUS(lon, lat, radius=100):

    #Box defining CONUS
    min_lon = -125
    max_lon = -67
    min_lat = 25
    max_lat = 49

    #Check if lightning is inside CONUS
    if lon >= min_lon:
        if lon <= max_lon:
            if lat >= min_lat:
                if lat <= max_lat:
                    return True

    d = geopy.distance.distance(kilometers=radius)

    #100km box around CONUS
    min_lon_100km = d.destination(point=geopy.Point(0, min_lon), bearing=270).longitude
    max_lon_100km = d.destination(point=geopy.Point(0, max_lon), bearing=90).longitude
    min_lat_100km = d.destination(point=geopy.Point(min_lat, 0), bearing=180).latitude
    max_lat_100km = d.destination(point=geopy.Point(max_lat, 0), bearing=0).latitude

    #Check if lightning is within 100km
    if lon < min_lon:
        if lon > min_lon_100km and (min_lat_100km < lat < max_lat_100km):
            return True
    elif lon > max_lon:
        if lon < max_lon_100km and (min_lat_100km < lat < max_lat_100km):
            return True
    elif lat < min_lat:
        if lat > min_lat_100km and (min_lon_100km < lon < max_lon_100km):
            return True
    elif lat > max_lat:
        if lat < max_lat_100km and (min_lon_100km < lon < max_lon_100km):
            return True
    else:
        return False
