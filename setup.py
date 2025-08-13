from setuptools import setup, find_packages

setup(
    name="halal-inventory-system",
    version="1.0.0",
    description="Halal Inventory Management System",
    packages=find_packages(),
    python_requires=">=3.9,<3.13",
    install_requires=[
        "Django>=4.2.16,<5.0",
        "djangorestframework>=3.15.2",
        "django-cors-headers>=4.4.0",
        "Pillow>=10.4.0",
        "python-barcode[images]>=0.15.1",
        "qrcode[pil]>=7.4.2",
        "requests>=2.32.3",
        "python-decouple>=3.8",
        "django-crontab>=0.7.1",
        "reportlab>=4.2.5",
        "gunicorn>=23.0.0",
        "psycopg2-binary>=2.9.9",
    ],
)