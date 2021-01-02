import os
import csv
import calendar
from radar_proximity import all_count_GLM_min

# Calculate total flash and CONUS-wide flash counts
def write_CONUS_csv(data_path):
    year = '2020' # Hardcoded
    months = 'MJJ' # Hardcoded
    
    # Open new CSV that we will write to with the flash counts
    with open(f'CONUS_{months}_{year}' + '.csv', 'w', newline='') as f:
        fieldnames = ['timestamp', 'total flash count', 'CONUS flash count', '', 'cumulative total flash count', 'cumulative CONUS flash count']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        cumul_total_count = 0
        cumul_conus_count = 0
        
        # i = month
        for i in range(5,8):
            monthday = calendar.monthrange(int(year), i)[1]
            
            # j = day
            for j in range(1, monthday + 1):
                print(f'Processing day {j}...')
                sat = '16' # Hardcoded to GOES-16 for CONUS-wide data
                os.system(f'./copyday.sh {year}{str(i).zfill(2)}{str(j).zfill(2)} {sat} {data_path}') # Run shell script to copy GLM data for that date
                if not len(os.listdir(data_path)):
                    day_missing = True
                    print(f'Data for {i}/{j} missing')
                else:
                    day_missing = False
                date = f'{year}-{str(i).zfill(2)}-{str(j).zfill(2)}'
                
                # k = hour
                for k in range(0,24):
                    # l = minute
                    for l in range(0,60):
                        if day_missing:
                            total_count = conus_count = 'N/A' # If data for that day is missing from the server, set vals to N/A
                        else:
                            total_count, conus_count = all_count_GLM_min(data_path, (k, l)) # Count total flash and CONUS flash counts for that min
                            if total_count is None:
                                total_count = conus_count = 'N/A'
                                print(f'Data in minute {l} missing')
                            else:
                                cumul_total_count += total_count
                                cumul_conus_count += conus_count
                        
                        # Empty string is a separator column
                        writer.writerow({'timestamp' : f'{date} {str(k).zfill(2)}:{str(l).zfill(2)}',
                                          'total flash count' : total_count,
                                          'CONUS flash count' : conus_count,
                                          '' : ' ',
                                          'cumulative total flash count' : cumul_total_count,
                                          'cumulative CONUS flash count' : cumul_conus_count
                                         })
                os.system(f'./deletedata.sh {data_path}') # Run shell script to delete GLM data for that date
    print('Finished creating CSV')

# Executes when the script is run
if __name__ == '__main__':
    # *Note*: This script makes use of a temporary data directory that is created when the script is run - for that instance alone - and deleted at the end.
    
    current_dir = os.getcwd() + os.sep
    data_dir = current_dir + 'Data_CONUS' + os.sep
    if not os.path.exists(data_dir):
        os.mkdir(data_dir) # Make temporary data directory
        write_CONUS_csv(data_dir) # Write out CSV
        try:
            os.rmdir(data_dir) # Attempt to delete temporary data directory
            print('Temporary data directory has been deleted')
        except:
            print('There was an issue with deleting the temporary data directory')
    else:
        print('Data directory already exists, aborting script')