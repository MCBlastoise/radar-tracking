#!/bin/sh

date=${1}
sat=${2}

year=${date:0:4}
month=${date:4:2}
day=${date:6:2}

copydir=/var/www/html/projects/airports/Radar/Data/
if [[ "${year}" == "2020" ]]
then
    datadir=/data/srudlosky/share/GLM/
else
    datadir=/data/srudlosky/share/GLM/${year}/
fi

if test -f ${datadir}OR_GLM-L2-LCFA_G${sat}_s${date}.nc.tgz
then
    cp ${datadir}OR_GLM-L2-LCFA_G${sat}_s${date}.nc.tgz ${copydir}
    cd ${copydir}
    echo GLM compressed data copied
    tar -zxf OR_GLM-L2-LCFA_G${sat}_s${date}.nc.tgz
	echo GLM data extracted
    rm OR_GLM-L2-LCFA_G${sat}_s${date}.nc.tgz
	echo Compressed data deleted
	echo Data extraction completed successfully
else
    echo "GLM data not found"
fi