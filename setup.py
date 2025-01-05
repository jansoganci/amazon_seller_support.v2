from setuptools import setup, find_packages

setup(
    name="amazon_seller_support",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'sqlalchemy',
        'pytest',
        'python-dateutil',
        'pandas',
        'numpy',
    ],
)
