#!/bin/sh

radardirec=${1}

for file in ${radardirec}*;
do
	radarpath=$(basename -- "$file")
	radarid=${radarpath:0:4}
	fullradarpath=${radardirec}${radarpath}
	screen -dm -S $radarid bash -c "python radar_time_series.py $fullradarpath; exec sh";
done