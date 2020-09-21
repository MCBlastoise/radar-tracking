from docx import Document
import os
import re
import csv
import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from radar_locations import radars
from radar_proximity import count_GLM_min, read_radar_coords
from time import perf_counter as pf

def get_status(radar_path):
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
            xml_string = str(cell._tc.xml)
            try:
                color = re.compile('<w:color w:val=\"\\w\\w\\w\\w\\w\\w\"/>').search(xml_string).group().split('"')[1]
                text = re.compile('<w:t>.*</w:t>').search(xml_string).group().split('</w:t>')[0].split('<w:t>')[1]
            except AttributeError:
                continue
            dates.append(datetime.strptime(text, '%m/%d %H:%M:%SZ') + relativedelta(years=int(year)-1900))
            statuses.append(value[color])

    return list(reversed(dates)), list(reversed(statuses)) #Ascending dates

def write_csv(radar_path, data_path):

    print('Getting radar statuses...')
    dates, statuses = get_status(radar_path)
    print('Radar status completed')

    with open(os.path.splitext(radar_path)[0][:-8] + 'MAY_2020' + '.csv', 'w', newline='') as f:
        with open(os.path.splitext(radar_path)[0][:-8] + 'JUN_2020' + '.csv', 'w', newline='') as g:
            with open(os.path.splitext(radar_path)[0][:-8] + 'JUL_2020' + '.csv', 'w', newline='') as h:
                fieldnames = ['timestamp', 'yes/no lightning', 'radar flash count', 'radar status']
                writer1 = csv.DictWriter(f, fieldnames=fieldnames)
                writer2 = csv.DictWriter(g, fieldnames=fieldnames)
                writer3 = csv.DictWriter(h, fieldnames=fieldnames)
                writer1.writeheader()
                writer2.writeheader()
                writer3.writeheader()
        #Months
        for i in range(5,8):
            monthday = calendar.monthrange(int(year),i)[1]
            #Days
            for j in range(1, monthday + 1):
                print(f'Processing day {j}...')
                #Determine to use G16 or G17 based on radar location
                sat = '17' if port_lon < -103 else '16'
                os.system(f'./copyday.sh {str(year)}{str(i).zfill(2)}{str(j).zfill(2)} {sat}')
                if not len(os.listdir(data_path)):
                    day_missing = True
                    print(f'Data for {i}/{j} missing')
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
                            radar_count = count_GLM_min(data_path, radar_id, (k, l))
                            if radar_count is None:
                                radar_count = ynl = 'N/A'
                                print(f'Data in minute {l} missing')
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
                        if i == 5:
                            writer1.writerow({'timestamp' : f'{date} {str(k).zfill(2)}:{str(l).zfill(2)}',
                                             'yes/no lightning' : ynl,
                                             'radar flash count' : radar_count,
                                             'radar status' : min_status,
                                             })
                        elif i == 6:
                            writer2.writerow({'timestamp' : f'{date} {str(k).zfill(2)}:{str(l).zfill(2)}',
                                             'yes/no lightning' : ynl,
                                             'radar flash count' : radar_count,
                                             'radar status' : min_status,
                                             })
                        elif i == 7:
                            writer3.writerow({'timestamp' : f'{date} {str(k).zfill(2)}:{str(l).zfill(2)}',
                                             'yes/no lightning' : ynl,
                                             'radar flash count' : radar_count,
                                             'radar status' : min_status,
                                             })
                os.system(f'./deletedata.sh')
    print('Finished creating CSV')

if __name__ == '__main__':

    t0 = pf()
    radar_path = '/var/www/html/projects/airports/Radar/KOHX_MJJ_2020.docx'
    data_path = '/var/www/html/projects/airports/Radar/Data/'
    filename = os.path.basename(os.path.splitext(radar_path)[0])
    radar_id, months, year = filename.split('_')
    port_lon, port_lat = read_radar_coords(radar_id)
    write_csv(radar_path, data_path)
    t1 = pf()

    print(f'Elapsed time: {t1 - t0}')

#Started 4:00 P.M
