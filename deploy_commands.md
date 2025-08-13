# Quick Deploy Fix Commands

## For Render Deployment

### 1. Environment Variables to Set in Render:
```
SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=ims-backend-r3ld.onrender.com,localhost,127.0.0.1
PYTHON_VERSION=3.11.9
```

### 2. Build Command for Render:
```bash
pip install --upgrade pip && pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear
```

### 3. Start Command for Render:
```bash
gunicorn halal_inventory_system.wsgi:application --bind 0.0.0.0:$PORT
```

## Test After Deployment:

1. **Health Check**: `GET https://ims-backend-r3ld.onrender.com/`
2. **API Info**: `GET https://ims-backend-r3ld.onrender.com/api/`  
3. **Admin**: `GET https://ims-backend-r3ld.onrender.com/admin/`

## If Still Having Issues:

### Alternative Build Command:
```bash
pip install --upgrade pip && pip install --no-build-isolation -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear
```

### Create Superuser (One-time):
```bash
python manage.py createsuperuser --noinput --username admin --email admin@example.com
```