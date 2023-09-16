#!/bin/sh

# python3
sudo apt install python-pip
python2 -m pip install virtualenv
python2 -m virtualenv venv
source venv/bin/activate

# requirements for selenium
sudo apt-get install python-setuptools
sudo apt install xvfb

pip install -r requirements.txt

# tflearn
sudo apt-get -y install python-h5py
sudo apt-get -y install python-scipy
sudo apt install python-tk

# apache
sudo apt install apache2
sudo ufw allow 'Apache'
sudo ufw enable
sudo mkdir -p /var/www/html
sudo cp -r video_server/* /var/www/html
echo hostname -I

# go to http://<local-ip>/myindex_BB.html