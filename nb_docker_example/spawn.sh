#!/bin/bash
mkdir -p s3/${USERNAME} && cd .init/ && ./sts-wire ${USERNAME} https://131.154.97.112:9000/ /${USERNAME} ../s3/${USERNAME} > .mount_log_${USERNAME}.txt &
mkdir -p s3/scratch && cd .init/ && ./sts-wire scratch https://131.154.97.112:9000/ /scratch ../s3/scratch > .mount_log_scratch.txt &
