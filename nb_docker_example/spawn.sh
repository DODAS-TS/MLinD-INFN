#!/bin/bash
cd /tf/
kill `ps faux | grep "sts-wire ${USERNAME}" | awk '{ print $2 }'`
kill `ps faux | grep ".${USERNAME}" | awk '{ print $2 }'`
kill `ps faux | grep "sts-wire scratch-covidstat" | awk '{ print $2 }'`
kill `ps faux | grep ".scratch-covidstat" | awk '{ print $2 }'`
mkdir -p s3/${USERNAME}
mkdir -p s3/scratch-covidstat
cd .init/
./sts-wire ${USERNAME} https://131.154.97.112:9000/ /${USERNAME} ../s3/${USERNAME} > .mount_log_${USERNAME}.txt &
./sts-wire scratch-covidstat https://131.154.97.112:9000/ /scratch-covidstat ../s3/scratch-covidstat > .mount_log_scratch.txt &

