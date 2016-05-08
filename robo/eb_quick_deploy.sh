#!/bin/bash

echo 'Add environment variables to git...'
git add .ebextensions/02_env.config -f
git commit -m '(Deploy) Auto commit: added eb environment variables'
echo 'Deploying on eb, environment bolt-dev...'
eb deploy bolt-dev
echo 'Reverting last commit - env variables should not be in repository'
git reset HEAD~1
echo 'Done!'