from setuptools import setup

config = {
    'name':'php-wsgi',
    'author':'Kyle Roux',
    'author_email':'kyle@level2designs.com',
    'version':'0.0.10',
    'description':'run php from python',
    'packages':['php_wsgi'],
    'install_requires':['flask']
}

setup(**config)
