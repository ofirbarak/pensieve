#!/bin/sh

# python2
sudo apt install python-pip
python2 -m pip install virtualenv
python2 -m virtualenv venv
source venv/bin/activate

pip install -r requirements.txt

# tflearn
sudo apt-get -y install python-h5py
sudo apt-get -y install python-scipy
sudo apt install python-tk
