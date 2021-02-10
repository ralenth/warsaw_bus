from setuptools import setup

setup(
    name='warsawbus',
    version='0.0.1',
    author='Adriana Bukała',
    author_email='bukala.adriana@gmail.com',
    packages=[
        'warsawbus',
        'warsawbus.fetch',
        'warsawbus.statistics',
        'warsawbus.visualize'
    ],
    description='Warsaw public bus transit',
    long_description=open('README.md').read(),
    install_requires=[
        "geopy",
        "pandas",
        "numpy",
        "plotly",
        "pytest",
        "pytest-cov",
    ],
)
