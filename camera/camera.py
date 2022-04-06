import asyncio
import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
import os
import glob
import json
from websockets import connect

async def take_photo():
    print("Button pressed...")

    print("Taking photo")
    os.system("raspistill -o photo.jpg -hf -vf -n")

    print("Reading photo")
    img = cv2.imread("photo.jpg")

    rows, cols, ch = img.shape
    f_s = 1500

    pts1 = np.float32([[600, 165], [1977, 117], [54, 1590], [2565, 1599]])
    pts2 = np.float32([[0, 0], [f_s, 0], [0, f_s], [f_s, f_s]])

    M = cv2.getPerspectiveTransform(pts1, pts2)

    dst = cv2.warpPerspective(img, M, (f_s, f_s))

    print("Photo transformed...")
    cv2.imwrite("photo_transformed.jpg", dst)
    os.system("cp /home/pi/record-player/camera/photo_transformed.jpg /home/pi/record-player/frontend/public/photo/photo_transformed.jpg")
    async with connect("ws://localhost:8000") as ws:
        print("Notifying via ws...")
        await ws.send("new-photo")

    print("Done. Waiting for next button press...\n")

last_click = 0

def photo_callback(channel):
    global last_click
    now = time.time()
    if (now - last_click) > 10:
        last_click = time.time()
        print("photo button")
        asyncio.run(take_photo())

def pause_callback(channel):
    global last_click
    now = time.time()
    if (now - last_click) > 4:
        last_click = time.time()
        print("pause button")
        os.system("spt pb -t")

def next_track_callback(channel):
    global last_click
    now = time.time()
    if (now - last_click) > 4:
        last_click = time.time()
        print("next button")
        os.system("spt pb -n")

def prev_track_callback(channel):
    global last_click
    now = time.time()
    if (now - last_click) > 2:
        last_click = time.time()
        print("prev button")
        os.system("spt pb -p")


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.add_event_detect(11, GPIO.FALLING, callback=photo_callback, bouncetime=1000)
GPIO.add_event_detect(10, GPIO.FALLING, callback=pause_callback, bouncetime=1000)
GPIO.add_event_detect(13, GPIO.FALLING, callback=next_track_callback, bouncetime=1000)
GPIO.add_event_detect(18, GPIO.FALLING, callback=prev_track_callback, bouncetime=1000)

print("camera module ready")

#os.system("spt play --name \"This is The Black Keys\" --playlist")

while True:
    pass

print("camera quit")
GPIO.cleanup()
