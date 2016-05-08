#!/bin/bash

# Recreate the postgres database
echo 'Recreating postgres databases...'
dropdb bolt_dev || { echo "ERROR: Cannot delete database bolt_dev. Aborted"; exit 1; }
echo '  Deleted database bolt_dev'
createdb -O bolt bolt_dev || { echo "ERROR: Cannot create database bolt_dev. Aborted"; exit 1; }
echo '  Created database bolt_dev for user bolt'
echo 'All databases recreated'

# Make migrations
echo 'Make Migrations....'
python manage.py makemigrations || { echo "ERROR: makemigrations failed. Aborted"; exit 1; }

# Migrate
echo 'Migrate....'
python manage.py migrate || { echo "ERROR: migrate failed. Aborted"; exit 1; }

# Load django fixtures (aka default/initial data: categories, etc.)
echo 'Loading fixtures (categories, publications, etc.) ...'
python manage.py loaddata categories || { echo "ERROR: load categories failed. Aborted"; exit 1; }
python manage.py loaddata publications || { echo "ERROR: load publications failed. Aborted"; exit 1; }

# Initialize some data
echo 'Initialize dabase: create superuser & populate some initial mock data'
echo "execfile('init_db.py')" | python manage.py shell || { echo "ERROR: database initialization failed. Aborted"; exit 1;}

echo 'Done!'