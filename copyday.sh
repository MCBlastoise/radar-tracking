#!/bin/sh

date=${1}
sat=${2}
copydir=${3}

year=${date:0:4}
month=${date:4:2}
day=${date:6:2}

if [[ "${year}" == "2020" ]]
then
    datadir=/data_lightning/srudlosky/share/GLM/
else
    datadir=/data_lightning/srudlosky/share/GLM/${year}/
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
    if [[ "${year}" == "2020" ]]
    then
        if [[ ${sat} == 17 ]]
        then
            datadir=${datadir}${date}w/
        else
            datadir=${datadir}${date}/
        fi
        
        if test -d ${datadir}
        then
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
        else
            echo "GLM data not found"
        fi
    else
        echo "GLM data not found"
    fi
fi