from docx import Document
import os
import re
import csv
import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from RadarLocations import radars
from RadarProximity import count_GLM_min, read_radar_coords

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

    return dates, statuses

def write_csv(radar_path, data_path):

    print('Getting radar statuses...')
    dates, statuses = get_status(radar_path)
    print('Radar status completed')

    with open(os.path.splitext(radar_path)[0] + '.csv', 'w', newline='') as f:
        fieldnames = ['radar id', 'date', 'hr', 'min', 'yes/no lightning', 'flash count', 'radar status']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        #Months
        for i in range(5,8):
            monthday = calendar.monthrange(int(year),i)[1]
            #Days
            for j in range(1, monthday + 1):
                print(f'Processing Day {j}...')
                #Determine to use G16 or G17 based on radar location
                sat = '17' if port_lon < -103 else '16'
                os.system(f'./copyday.sh {str(year)}{str(i).zfill(2)}{str(j).zfill(2)} {sat}')
                date = year + '-' + str(i).zfill(2) + '-' + str(j).zfill(2)
                #Hours
                for k in range(0,24):
                    #Minutes
                    for l in range(0,60):
                        ltg_count = count_GLM_min(data_path, radar_id, (k, l))
                        ltg_count = 'N/A' if ltg_count is None else ltg_count
                        if ltg_count == 0:
                            ynl = 0
                        elif ltg_count > 0:
                            ynl = 1
                        else:
                            ynl = 'N/A'

                        #Iterating through cells to find status for each minute
                        for ts, status in zip(dates, statuses):
                            if ts < (datetime(int(year), i, j, k, l) + timedelta(0, 60)):
                                min_status = status
                                break
                        writer.writerow({'radar id' : radar_id, 'date' : date, 'hr' : str(k).zfill(2), 'min' : str(l).zfill(2),
                                         'yes/no lightning' : ynl, 'flash count' : ltg_count,'radar status' : min_status})
    print('Finished creating CSV')

if __name__ == '__main__':

    radar_path = '/var/www/html/projects/airports/Radar/KENX_MJJ_2020.docx'
    data_path = '/var/www/html/projects/airports/Radar/Data/'
    filename = os.path.basename(os.path.splitext(radar_path)[0])
    radar_id, months, year = filename.split('_')
    port_lon, port_lat = read_radar_coords(radar_id)
    write_csv(radar_path, data_path)
