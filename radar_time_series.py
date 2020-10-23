from docx import Document
import os
import sys
import random
import re
import csv
import calendar
from datetime import datetime
from dateutil.relativedelta import relativedelta
from radar_proximity import count_GLM_min, read_radar_coords
from time import perf_counter as pf

def get_status(radar_path):
    filename = os.path.basename(os.path.splitext(radar_path)[0])
    radar_id, months, year = filename.split('_')
    
    document = Document(radar_path)
    table = document.tables[0]
    dates = []
    statuses = []
    #Assign radar status based on font color (2-operational, 1-error, 0-down)
    value = {
        'FF0000' : 0,
        'FFFF33' : 1,
        '338800' : 2
        }
    for row in table.rows:
        for cell in row.cells:
            try:
                xml_string = str(cell._tc.xml)
                
                color = re.compile('<w:color w:val=\"\\w\\w\\w\\w\\w\\w\"/>').search(xml_string).group().split('"')[1]
                text = re.compile('<w:t>.*</w:t>').search(xml_string).group().split('</w:t>')[0].split('<w:t>')[1]
            except AttributeError:
                continue
            dates.append(datetime.strptime(text, '%m/%d %H:%M:%SZ') + relativedelta(years=int(year)-1900))
            statuses.append(value[color])

    return list(reversed(dates)), list(reversed(statuses)) #Ascending dates

def write_csv(radar_path, data_direc):
    filename = os.path.basename(os.path.splitext(radar_path)[0])
    radar_id, months, year = filename.split('_')
    port_lon, port_lat = read_radar_coords(radar_id)

    csv_path = current_direc + filename + '.csv'
    if os.path.exists(csv_path):
        print('CSV already exists')
        print('Terminating run')
        return None
    
    print('Obtaining radar statuses...')
    dates, statuses = get_status(radar_path)
    print('Radar statuses completed')

    with open(csv_path, 'w', newline='') as f:
        fieldnames = ['timestamp', 'yes/no lightning', 'radar flash count', 'radar status']
        writer1 = csv.DictWriter(f, fieldnames=fieldnames)
        writer1.writeheader()

        #Months
        for i in range(5,8):
            monthday = calendar.monthrange(int(year),i)[1]
            #Days
            for j in range(1, monthday + 1):
                print(f'Processing day {j}...')
                #Determine to use G16 or G17 based on radar location
                sat = '17' if port_lon < -103 else '16'
                os.system(f'./copyday.sh {str(year)}{str(i).zfill(2)}{str(j).zfill(2)} {sat} {data_direc}')
                if not len(os.listdir(data_direc)):
                    day_missing = True
                    print(f'Data for date {str(i).zfill(2)}/{str(j).zfill(2)} missing')
                else:
                    day_missing = False
                date = year + '-' + str(i).zfill(2) + '-' + str(j).zfill(2)
                #Hours
                for k in range(0,24):
                    #Minutes
                    for l in range(0,60):
                        if day_missing:
                            radar_count = ynl = 'N/A'
                        else:
                            radar_count = count_GLM_min(data_direc, radar_id, (k, l))
                            if radar_count is None:
                                radar_count = ynl = 'N/A'
                                print(f'Data for minute {str(l).zfill(2)} of hour {str(k).zfill(2)} on date {str(i).zfill(2)}/{str(j).zfill(2)} missing')
                            else:
                                if radar_count == 0:
                                    ynl = 0
                                elif radar_count > 0:
                                    ynl = 1
                        #Iterating through cells to find status for each minute
                        min_status = None
                        for ts, status in zip(dates, statuses):
                            if ts >= datetime(int(year), i, j, k, l, 0):
                                min_status = status
                                break
                        if min_status is None:
                            min_status = statuses[-1]
                        writer1.writerow({'timestamp' : f'{date} {str(k).zfill(2)}:{str(l).zfill(2)}',
                                          'yes/no lightning' : ynl,
                                          'radar flash count' : radar_count,
                                          'radar status' : min_status,
                                         })
                if not day_missing:
                    os.system(f'./deletedata.sh {data_direc}')
    print('Finished creating CSV')

if __name__ == '__main__':
    t0 = pf()
    current_direc = '/home/ayyub/Radar/'
    
    radar_path = sys.argv[1]
    
    data_direc = current_direc + 'Data_' + (os.path.basename(os.path.splitext(radar_path)[0]).split('_')[0]) + '_' + str(random.randint(100000, 999999)) + '/'
    while(os.path.exists(data_direc) and os.path.isdir(data_direc)):
        data_direc = current_direc + 'Data_' + str(random.randint(100000, 999999)) + '/'
    os.mkdir(data_direc)
    print(f'Temporary data directory for this run is {data_direc}')
    
    write_csv(radar_path, data_direc)
    try:
        os.rmdir(data_direc)
        print('Temporary data directory has been deleted')
    except:
        print('There was an issue with deleting the temporary data directory')
    t1 = pf()

    print(f'Elapsed time: {t1 - t0}')
