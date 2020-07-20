# Usage: ./create_positions.sh <case id of superuser> [run]
# if run is specified in the second argument, then the server will start after the
# superuser has been created

read -p "Are you sure you want to delete the database? " -n 1 -r
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Exiting since database is not being reset"
    echo "Edit the script if you want to not delete the database"
    exit 1
fi

rm db.sqlite3
python manage.py migrate

echo "Creating positions..."

# so this is kinda hacky, but basically the shell command opens a
# python shell so we're putting the python commands to call the
# python code that does all the initial setup to create the positions
# into stdin of the python shell, causing it to execute the code
#
# any changes to how the superuser is built should be made in create_positions.py
# and this should only change if the call interface changes
echo "
import create_positions
create_positions.build_superuser(\"$1\")
" | python manage.py shell

echo "Done creating positions"

if [[ $2 = "run" ]]
then
    echo "Starting server..."
    python manage.py runserver
else
    echo "run command not specified, so exiting"
fi
