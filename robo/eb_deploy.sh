#!/bin/bash

echo 'Compile grunt (js-minify)...'
grunt compile
echo 'Add angular bin folder to git...'
git add angular/bin -f
git commit -m '(Deploy) Auto commit: added angular bin folder'

./eb_quick_deploy.sh