import os
import shutil
import math
import pandas as pd
import plotly.figure_factory as ff
import dataframe_image as dfi
from radar_locations import radars

# Separates the 143+ CSVs into folders, state-by-state
# csv_dir is the directory where the CSVs live, state_dir is the directory where state-separated directories should live, ending in \ (or / if Linux)
def state_separate(csv_dir, state_dir):
    if not os.path.exists(state_dir):
        os.mkdir(state_dir)
    direc_iter = sorted(os.listdir(csv_dir))
    
    # Iterates through CSVs, checks if state directory already exists and creates if not, then copies file to state direc
    for file in direc_iter:
        code = file.split('_')[0]
        state = radars[code]['stname'].split(', ')[-1]
        if not os.path.exists(f'{state_dir}{state}{os.sep}'):
            os.mkdir(f'{state_dir}{state}{os.sep}')
        shutil.copyfile(f'{csv_dir}{file}', f'{state_dir}{state}{os.sep}{file}')

# Somewhat pretty table formatting with plotly, although column width is fixed which means a lot of empty space / small font
def save_table(df, output_file, table_width=2500, table_height=1000, colorscale=[[0, '#961500'],[.5, '#ffd3cc'],[1, '#ffffff']], font_size=14):
    fig = ff.create_table(df, index=True, colorscale=colorscale)
    fig.update_layout(
        autosize=False,
        width=table_width,
        height=table_height,
    )
    for i in range(len(fig.layout.annotations)):
        fig.layout.annotations[i].font.size = font_size
    
    fig.write_image(output_file)

# Not so pretty table formatting with the dataframe_image module, although it is much more compact / readable
def save_table2(df, output_file, fontsize=32):
    dfi.export(df, output_file, fontsize)

# Produces a statistics CSV and summary statistics in table format
def make_stats(csv_dir, conus_file, output_file):
    csv_lst = sorted(os.listdir(csv_dir))
    conus_df = pd.read_csv(conus_file)
    csv_df_lst = [pd.read_csv(csv_dir + f) for f in csv_lst]
    
    # *Note*: The CONUS flash ct in proximity is a summation of flashes in proximity to each radar, meaning that it may contain duplicates if a flash is incident to multiple radars simultaneously; similarly, this is why I chose not to include a not-in-prox statistic, there is not an accurate way to quantify it without being able to distinguish duplicates
    out_dict = {
        'timestamp': list(conus_df['timestamp']), # Copied from CONUS CSV
        'total flash ct': list(conus_df['total flash count']), # Copied from CONUS CSV
        'CONUS flash ct': list(conus_df['CONUS flash count']), # Copied from CONUS CSV
        'CONUS flash ct in prox': [], # Flashes within 100km of CONUS and in proximity to any of the radars
        'Nonoperational radar ct': [], # Radars that are either in error status or nonoperational status
        'Nonoperational radar ct with flashes': [], # Radars that are either in error status or nonoperational status that also had at least one flash in proximity
        'Nonoperational flash ct': [] # Flashes in proximity to error/nonoperational radars
    }
    
    # Iterate through rows of CONUS file, so minute-by-minute
    for i in conus_df.index:
        conus_radar_flash_ct = 0
        nonop_radar_ct = 0
        nonop_radar_with_flash_ct = 0
        nonop_flash_ct = 0
        
        # Iterate through all CSVs in folder to sum up the various statistics across them for each minute
        for df in csv_df_lst:
            rad_ct = df.at[i, 'radar flash count']
            if not math.isnan(rad_ct):
                conus_radar_flash_ct += rad_ct
                # Check if radar status is not fully operational (green / status code 2)
                if df.at[i, 'radar status'] != 2:
                    nonop_radar_ct += 1
                    if rad_ct > 0:
                        nonop_radar_with_flash_ct += 1
                        nonop_flash_ct += rad_ct
        
        if math.isnan(out_dict['CONUS flash ct'][i]):
            out_dict['CONUS flash ct in prox'].append(math.nan)
        else:
            out_dict['CONUS flash ct in prox'].append(conus_radar_flash_ct)
        
        out_dict['Nonoperational radar ct'].append(nonop_radar_ct)
        out_dict['Nonoperational radar ct with flashes'].append(nonop_radar_with_flash_ct)
        out_dict['Nonoperational flash ct'].append(nonop_flash_ct)
    
    out_df = pd.DataFrame(out_dict)
    out_df.set_index('timestamp', inplace=True)
    out_df[list(out_dict)[1:]] = out_df[list(out_dict)[1:]].astype('Int64') # Convert all non-timestamp columns into integer form
    out_df.to_csv(output_file) # Save df into final CSV
    
    summ_stat = out_df.describe().drop('count').round(3) # Compute summary statistics
    corr_stat = out_df.corr().round(3) # Compute correlation coefficients between different statistics
    
    path_wo_ext = os.path.splitext(output_file)[0] # Extract path name without file extension
    save_table(summ_stat, f'{path_wo_ext} - Summary Stats.png')
    save_table(corr_stat, f'{path_wo_ext} - Correlations.png')

# Declaring paths to important directories / files
all_radars_dir = 'Radar/Products/AllRadars/' # Where the raw collected data CSVs on each radar are
states_dir = 'Radar/Products/States/' # Where you want the state-by-state data to be
stats_dir = 'Radar/Products/Stats/' # Where you want the statistics to live, must create beforehand
conus_file = 'Radar/Products/CONUS_MJJ_2020.csv' # Path to collected data on CONUS

# Create statistics for all radars in the dataset
if 'AllRadars' not in os.listdir(stats_dir):
    os.mkdir(f'{stats_dir}AllRadars{os.sep}')
make_stats(all_radars_dir, conus_file, f'{stats_dir}AllRadars{os.sep}AllRadars.csv')

state_separate(all_radars_dir, states_dir) # Create directory of state-separated collected data
# Create statistics for each state's radars
for state in os.listdir(states_dir):
    if state not in os.listdir(stats_dir):
        os.mkdir(f'{stats_dir}{state}{os.sep}')
    make_stats(f'{states_dir}{state}{os.sep}', conus_file, f'{stats_dir}{state}{os.sep}{state}.csv')

