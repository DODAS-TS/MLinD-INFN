#!/bin/bash

# Configure oidc-agent for user token management
echo "eval \`oidc-keychain\`" >> ~/.bashrc
eval `oidc-keychain`
oidc-gen dodas --issuer $IAM_SERVER \
               --client-id $IAM_CLIENT_ID \
               --client-secret $IAM_CLIENT_SECRET \
               --rt $REFRESH_TOKEN \
               --confirm-yes \
               --scope "openid profile email" \
               --redirect-uri  http://dummy:8843 \
               --pw-cmd "echo \"DUMMY PWD\""

# Mount S3 user buckets
cd /tf/
kill `ps faux | grep "sts-wire ${USERNAME}" | awk '{ print $2 }'`
kill `ps faux | grep ".${USERNAME}" | awk '{ print $2 }'`
kill `ps faux | grep "sts-wire scratch" | awk '{ print $2 }'`
kill `ps faux | grep ".scratch" | awk '{ print $2 }'`
mkdir -p s3/${USERNAME}
mkdir -p s3/scratch
cd .init/
./sts-wire ${USERNAME} https://131.154.97.112:9000/ /${USERNAME} ../s3/${USERNAME} > .mount_log_${USERNAME}.txt &
./sts-wire scratch https://131.154.97.112:9000/ /scratch ../s3/scratch > .mount_log_scratch.txt &

