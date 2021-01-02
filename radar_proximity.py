import os
import netCDF4 as nc
import datetime
import geopy.distance
from radar_locations import radars

# Takes a radar code and returns a pair of coords in (lon, lat) format
def read_radar_coords(code):
    return (float(radars[code]['longitude']), float(radars[code]['latitude']))

# Takes a GLM L2 data filename and returns a triplet timestamp in (h, m, s) format
def read_filename(filename):
    ts = filename.split('_')[3]
    tup = (int(ts[8:10]), int(ts[10:12]), int(ts[12:14]))
    return tup

# Takes a GLM l2 data file path and returns a pair of lists of the lon and lat coords of each flash, respectively
def extract_GLM(file):
    glm = nc.Dataset(file, mode='r')
    flon = glm['flash_lon'][:]
    flat = glm['flash_lat'][:]

    return (flon, flat)

# Takes an hr and min and uses the fact that a full day of GLM L2 data = a directory with 4320 20-sec files to return the index a specific L2 file should be
def calc_GLM_index(hr, mt):
    return hr * 180 + mt * 3

# Takes a directory of one day of L2 data, an hour, and a minute, and returns the index of the first L2 file for that minute
# More intensive function for finding a specific L2 file, to be used when the directory is missing some data (i.e. not 4320 files)
def find_file(data_direc, h, m):
    direc_iter = sorted(os.listdir(data_direc))

    expected_ind = calc_GLM_index(h, m) # Index where the file would normally be
    
    # Starts at the expected index and iterates backwards until the file is found => much more efficient than starting from beginning or end
    for x in range( expected_ind if expected_ind < (len(direc_iter) - 1) else len(direc_iter) - 1, -1, -1 ):
        fh, fm, fs = read_filename(direc_iter[x])
        # Check if (h, m, s) of file match what we're looking for
        if datetime.datetime(2020, 6, 15, fh, fm, fs) == datetime.datetime(2020, 6, 15, h, m, 0): # 2020, 6, 15 are hardcoded dummy values
            # Ensure all three 20s files in the corresponding minute are present, otherwise, consider the whole minute missing
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

# Takes a longitude and latitude (for a flash) and returns whether it is inside / within proximity to CONUS
def near_CONUS(lon, lat, radius=100):
    # For our purposes, CONUS is defined as a close-fitting rectangle. This is much easier to process than to handle it as a conjoined set of complex polygons, as we are tracking not only flashes within CONUS, but in proximity to it. This is clearly a simplification, however the close-fitting nature of the bounding box combined with the large proximity (100km) makes the over-counting minimal.
    
    # Coordinates of the CONUS rectangle
    min_lon = -125
    max_lon = -67
    min_lat = 25
    max_lat = 49

    # First check if lightning is inside CONUS
    if lon >= min_lon:
        if lon <= max_lon:
            if lat >= min_lat:
                if lat <= max_lat:
                    return True

    d = geopy.distance.distance(kilometers=radius)

    # Coordinates of a 100km expanded CONUS rectangle
    min_lon_100km = d.destination(point=geopy.Point(0, min_lon), bearing=270).longitude
    max_lon_100km = d.destination(point=geopy.Point(0, max_lon), bearing=90).longitude
    min_lat_100km = d.destination(point=geopy.Point(min_lat, 0), bearing=180).latitude
    max_lat_100km = d.destination(point=geopy.Point(max_lat, 0), bearing=0).latitude

    # Check if lightning is within 100km of CONUS
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

# Takes a directory of one day of L2 data, a radar code, and a time in (h, m) format, and returns the number of flashes in proximity to that radar for that min
def count_GLM_min(data_direc, code, time, radius=100):
    port_lon, port_lat = read_radar_coords(code)
    direc_iter = sorted(os.listdir(data_direc))
    radar_count = 0
    if len(direc_iter) == 4320:
        start = calc_GLM_index(time[0], time[1]) # Use ideal index calculation if there are no missing files
    else:
        start = find_file(data_direc, time[0], time[1]) # Use alternative function for finding a file in case of missing files
        if start is None:
            return None

    for x in range(start, start + 3):
        path = data_direc + direc_iter[x]
        flon, flat = extract_GLM(path)
        for lon, lat in zip(flon, flat):
            # Preliminary check of whether flash is in proximity to CONUS
            if near_CONUS(lon, lat, radius): 
                # Next check if flash is in proximity to specific radar
                dist = geopy.distance.great_circle((port_lat, port_lon), (lat, lon)).kilometers
                if dist <= radius:
                    radar_count += 1

    return radar_count

# Takes a directory of one day of L2 data and a time in (h, m) format, and returns the total flash count and number of flashes in prox to CONUS for that min
def all_count_GLM_min(data_direc, time, radius=100):
    direc_iter = sorted(os.listdir(data_direc))
    total_count = 0
    conus_count = 0

    if len(direc_iter) == 4320:
        start = calc_GLM_index(time[0], time[1]) # Use ideal index calculation if there are no missing files
    else:
        start = find_file(data_direc, time[0], time[1]) # Use alternative function for finding a file in case of missing files
        if start is None:
            return (None, None)

    for x in range(start, start + 3):
        path = data_direc + direc_iter[x]
        flon, flat = extract_GLM(path)
        for lon, lat in zip(flon, flat):
            total_count += 1
            # Check if flash is in proximity to CONUS
            if near_CONUS(lon, lat, radius):
                conus_count += 1

    return total_count, conus_count