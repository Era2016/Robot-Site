#!/bin/bash

# Removed all migration files
echo 'Clearing migration files.....' $file

for file in $(find ./bolt/apps -regex .*migrations/[0-9].*.py.*)
do
rm $file
echo '  Removed' $file
done

echo 'All migrations files deleted'

# Reset database
./reset_db.sh