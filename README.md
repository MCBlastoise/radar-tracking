# radar-tracking
The goal of this project is to assess the value of Geostationary Lightning Mapper observations in contrast to ground-based radar, by way of analyzing lightning observations in proximity to various radar across the US during operational and nonoperational periods, during the months of May, June, and July.

## Tools
The project uses Python and Bash, and the directory structure is identical to that of this Github (minus the CSVs / product files already existing). It made use of 4 main Python scripts, 3 Bash scripts for the automation of copying data, deleting data, and automating the analyis process, as well as a reference Python file containing coordinates of radar.

## Initial Analysis
The first step of this project was to create time series (in CSV format) for 147 selected radar around the continental United States and Hawaii that computed the number of flashes within 100km of each radar and the operational status of the radar for each minute. A time series was also constructed to compute total flash and CONUS-proxmity flash information, for use later. The flash data used for these time series were GLM L2 files taken from the NOAA repository (if one wants to perform a similar analysis, these files could be accessed from [this Amazon repository here](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/goes16_download.cgi)). The documents used for the radar statuses were also taken from a NOAA repository and are included in this repository in the 'RadarStatuses' folder. These documents included both timestamps and the associated operational status of the radar indicated by its color (green, yellow, and red indicate operational, in error, and nonoperational, respectively). A file consisting of the coordinates and other auxiliary information for each radar (labeled by their code) was also used for this analysis and is included in this repository, titled 'radar_locations.py'.

## Statistics
Second, these time series were used to compute several statistics for each minute, including the following: number of flashes in proximity to radar, number of radars that were in error or nonoperational, number of radars that were in error or nonoperational and had at least one flash in proximity, number of flashes in proximity to radars in error or nonoperational (total flash and CONUS-proximity data were also appended to these statistic CSVs for comparison purposes). These statistics were created for the entire dataset of radars and also on a state-by-state basis. Summary statistics and correlation coefficients for these statistics were also produced and are stored in the 'Stats' folder under 'Products'.

## Current Developments
This project is currently ongoing, and will continue to work towards assessing and quantifying the value of the GLM.
