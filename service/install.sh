#!/bin/bash
SERVICE="/etc/systemd/system/nixflix.service"
BASEDIR=$(dirname $0)

# copy the systemd service template
cp "$BASEDIR/nixflix.service" /etc/systemd/system/nixflix.service

# relace the python script location
NF=$(readlink -e "$BASEDIR/../nixflix.py")
echo $NF
sed -i "s:nixflix.py:$NF:" $SERVICE

# set perms
sudo chmod 644 $SERVICE

systemctl enable nixflix.service
systemctl status nixflix.service
