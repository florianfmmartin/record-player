import asyncio
import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
import os
from websockets import connect

async def take_photo():
    print("Button pressed...")

    os.system("raspistill -o photo.jpg -vf -n -br 42")

    img = cv2.imread("photo.jpg")
    rows, cols, ch = img.shape
    f_s = 720

    pts1 = np.float32([[845, 625], [1700, 635], [180, 1505], [2370, 1535]])
    pts2 = np.float32([[0, 0], [f_s, 0], [0, f_s], [f_s, f_s]])

    M = cv2.getPerspectiveTransform(pts1, pts2)

    dst = cv2.warpPerspective(img, M, (f_s, f_s))

    print("Photo transformed...")
    cv2.imwrite("photo_transformed.jpg", dst)

    async with connect("ws://localhost:8000") as ws:
        print("Notifying via ws...")
        await ws.send("new-photo")

    print("Done. Waiting for next button press...\n")

print("Press `e` to exit")

while (True):
    message = input()
    if (message == "e"):
        exit()
    elif (message == ""):
        asyncio.run(take_photo())
