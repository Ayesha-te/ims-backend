@echo off
echo ========================================
echo Halal Inventory Management System
echo ========================================
echo.

cd /d %~dp0

echo Installing/Upgrading dependencies...
pip install -r requirements.txt

echo.
echo Setting up database...
python manage.py makemigrations
python manage.py migrate

echo.
echo Setting up initial data...
python manage.py setup_inventory --admin-user admin --with-sample-data

echo.
echo Generating alerts...
python manage.py generate_alerts

echo.
echo Collecting static files...
python manage.py collectstatic --noinput

echo.
echo ========================================
echo System Ready!
echo ========================================
echo Admin Panel: http://localhost:8000/admin/
echo API Root: http://localhost:8000/api/
echo Username: admin
echo Password: admin123
echo ========================================
echo.
echo Starting server...

python manage.py runserver

pause