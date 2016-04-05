#!/bin/bash
# Set up virtualenv and migrate project
export HOME=/home/vagrant
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv -a /home/vagrant/quis -r /home/vagrant/quis/quis/requirements/local.txt quis 
workon quis
python manage.py migrate
