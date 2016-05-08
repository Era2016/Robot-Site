#!/bin/bash

echo 'Clean grunt...'
grunt clean
echo 'Reinstall vendor libraries'
bower install
echo 'Rebuild grunt...'
grunt build

./eb_deploy.sh