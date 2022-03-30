#!/usr/bin/bash

cd /home/pi/record-player/frontend && npm start &

cd /home/pi/record-player/camera && ./camera/bin/python camera.py &
