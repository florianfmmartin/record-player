import asyncio
import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
import os
import glob
import json
from websockets import connect

def calibrate():
    print("Calibrating camera")

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    objp = np.zeros((8*5, 3), np.float32)
    objp[:,:2] = np.mgrid[0:8,0:5].T.reshape(-1,2)

    objpoints = []
    imgpoints = []

    images = glob.glob("check*.jpg")

    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        print("Finding checkboard")
        ret, corners = cv2.findChessboardCorners(gray, (8,5), cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)

        print(fname)
        print(ret)
        print(corners)
        print()

        objpoints.append(objp)
        # corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(corners)

    checkboard = cv2.imread("check-1.jpg")
    shape = (checkboard.shape[1], checkboard.shape[0])

    print("Calibrating camera...")
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, shape,None,None)

    with open("./calibration.json", "w") as f:
        json.dump({ "mtx": mtx, "dist": dist }, f)

async def take_photo():
    # mtx = None
    # dist = None

    # with open("./calibration.json", "r") as f:
    #     data = json.load(f)
    #     mtx = data["mtx"]
    #     dist = data["dist"]

    print("Button pressed...")

    print("Taking photo")
    os.system("raspistill -o photo.jpg -vf -hf -n")

    print("Reading photo")
    img = cv2.imread("photo.jpg")

    # Calibrate
    # print("Undistorting photo")
    # h, w = img.shape[:2]
    # newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
    # tmp = cv2.undistort(img, mtx, dist, None, newcameramtx)

    # tmp
    # cv2.imwrite("distort.jpg", tmp)

    rows, cols, ch = img.shape
    f_s = 1500

    # pts1 = np.float32([[680, 635], [1750, 650], [0, 1820], [2570, 1765]])
    pts1 = np.float32([[384, 153], [2022, 54], [201, 1809], [2301, 1704]])
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

# calibrate -- doesnt work
# calibrate()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

last_click = 0
click = False

while True:
    now = time.time()
    if GPIO.input(10) == GPIO.HIGH and (now - last_click) > 0.4 and not click:
        last_click = now
        click = True
    elif GPIO.input(10) == GPIO.LOW and (now - last_click) < 1 and click:
        click = False
        # asyncio.run(take_photo())
    elif GPIO.input(10) == GPIO.LOW and (now - last_click) > 2 and click:
        click = False
        os.system("spt pb -t")


