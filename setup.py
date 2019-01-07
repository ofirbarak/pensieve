import os

start_dir = os.getcwd()

# tensorflow
os.system("sudo pip install tensorflow==1.1.0")

# tflearn
os.system("sudo pip install tflearn==0.3.1")
os.system("sudo apt-get -y install python-h5py")
os.system("sudo apt-get -y install python-scipy")
