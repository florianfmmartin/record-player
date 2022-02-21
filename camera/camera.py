import cv2
import numpy as np
import RPi.GPIO as GPIO
import time

def take_photo():
    img = cv2.imread("photo.jpg")
    rows, cols, ch = img.shape
    f_s = 720

    print(rows, cols)

    pts1 = np.float32([[0, rows/2], [cols, rows/2], [0, rows], [cols, rows]])
    pts2 = np.float32([[0, 0], [f_s, 0], [0, f_s], [f_s, f_s]])

    M = cv2.getPerspectiveTransform(pts1, pts2)

    dst = cv2.warpPerspective(img, M, (f_s, f_s))

    cv2.imwrite("photo_transformed.jpg", dst)

def button_callback(channel):
    global last_time
    now = time.time()
    if (now - last_time) > 2:
        take_photo()
        last_time = now

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

last_time = time.time()

GPIO.add_event_detect(10, GPIO.RISING, callback=button_callback)

message = input("Press enter to quit\n\n")
GPIO.cleanup()

