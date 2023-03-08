#!/bin/sh

# python2
python2 -m pip install virtualenv
python2 -m virtualenv venv
source venv/bin/activate

pip install requirements.txt

# tflearn
sudo apt-get -y install python-h5py
sudo apt-get -y install python-scipy
