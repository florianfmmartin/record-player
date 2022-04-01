#!/usr/bin/env bash

export PATH="/home/pi/.config/nvm/versions/node/v16.14.2/bin:/snap/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/games:/usr/games:/snap/bin"

(cd /home/pi/record-player/camera && ./camera/bin/python camera.py) &

(cd /home/pi/record-player/frontend && npm start) &

sleep infinity
