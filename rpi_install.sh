#!/bin/bash

# Install script for Raspberry Pi running Raspbian Buster
# Note that this is only tested/supported on Buster

raspbian_version=$(cat /etc/os-release |grep VERSION_CODENAME |cut -d = -f 2)

if [ $raspbian_version != 'buster' ]; then
  echo 'This install script is only tested/supported in Raspbian Buster.'
  exit
fi

# Update
apt-get -y update
apt-get -y upgrade

# Install requirements
apt-get -y install python3-pip python3-numpy libopenjp2-7-dev graphviz

# Install MechWolf
pip3 install mechwolf

# Configure Jupyter
su pi -c "mkdir /home/pi/.jupyter"
su pi -c "echo c.NotebookApp.open_browser = False >> /home/pi/.jupyter/jupyter_notebook_config.py"
su pi -c "echo c.NotebookApp.allow_remote_access = True >> /home/pi/.jupyter/jupyter_notebook_config.py"
su pi -c "echo c.NotebookApp.ip = \'0.0.0.0\' >> /home/pi/.jupyter/jupyter_notebook_config.py"

echo "Please set a safe password for your Jupyter server."
su pi -c "jupyter notebook password"

# Install Jupyter Service
echo "[Unit]
Description=Jupyter Notebook

[Service]
Type=simple
PIDFile=/run/jupyter.pid
ExecStart=/usr/local/bin/jupyter notebook --config=/home/pi/.jupyter/jupyter_notebook_config.py
User=pi
WorkingDirectory=/home/pi
Restart=always
RestartSec=10
#KillMode=mixed

[Install]
WantedBy=multi-user.target
" > /etc/systemd/system/jupyter.service

systemctl enable jupyter
systemctl start jupyter

echo "MechWolf install complete."
