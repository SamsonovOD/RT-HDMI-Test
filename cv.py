import os
import os.path
import time
import numpy as np
import cv2
import threading
import ffmpeg

try:
	from PIL import Image
except ImportError:
	import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class VideoCaptureAsync:
    def __init__(self, src=0):
        self.src = src
        self.cap = cv2.VideoCapture(self.src)
        self.grabbed, self.frame = self.cap.read()
        self.started = False
        self.read_lock = threading.Lock()

    def set(self, var1, var2):
        self.cap.set(var1, var2)

    def start(self):
        if self.started:
            print('[!] Asynchroneous video capturing has already been started.')
            return None
        self.started = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()
        return self

    def isOpened(self):
        return self.cap.isOpened()

    def update(self):
        while self.started:
            grabbed, frame = self.cap.read()
            with self.read_lock:
                self.grabbed = grabbed
                self.frame = frame

    def read(self):
        with self.read_lock:
            frame = self.frame.copy()
            grabbed = self.grabbed
        return grabbed, frame

    def stop(self):
        self.started = False
        self.thread.join()

    def __exit__(self, exec_type, exc_value, traceback):
        self.cap.release()

def SaveCap(time, img):
		if os.path.exists("log.txt"):
			append_write = 'a'
		else:
			append_write = 'w'
		file = open("log.txt",append_write)
		method = cv2.TM_SQDIFF_NORMED
		large_image = img
		height, width = large_image.shape[:2]
		file.write("=CAP: "+str(time)+"==\n")

		small_image = large_image[int(height*(1/32)):int(height*(3/32)),int(width*(5/6)):int(width*(6/6))]
		ret, img_binarized = cv2.threshold(small_image, 126, 255, cv2.THRESH_BINARY)
		pil_img = Image.fromarray(img_binarized)
		text = pytesseract.image_to_string(small_image, lang="rus")
		file.write(text + "\n")

		small_image = large_image[int(height*(14/32)):int(height*(17/32)),int(width*(1/6)):int(width*(5/6))]
		ret, img_binarized = cv2.threshold(small_image, 126, 255, cv2.THRESH_BINARY)
		pil_img = Image.fromarray(img_binarized)
		text = pytesseract.image_to_string(small_image, lang="rus+eng")
		file.write(text + "\n")
		file.close()

class Main(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        cap = VideoCaptureAsync("udp://127.0.0.1:2000")
        #cap = VideoCaptureAsync("example.mp4")
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.start()
        
        fourcc = cv2.VideoWriter_fourcc(*'DIVX')
        out = cv2.VideoWriter('output.mpeg',fourcc, 20.0, (1080,1920))
        i = 0
        while True:
            _, frame = cap.read()
            cv2.imshow('Capture', frame)
            out.write(frame)
            k = cv2.waitKey(1) & 0xFF
            if k == ord('q'):
                cv2.destroyWindow('Capture')
            elif k == ord('c'):
                thread = threading.Thread(target=SaveCap, args=(i, frame))
                thread.start()
            if cv2.getWindowProperty('Capture', 4) < 1:
                break
            #cv2.imshow("cycle"+str(i), blank_image)
            i += 1
        cap.stop()
        out.release()
        cv2.destroyAllWindows()
	
if __name__ == '__main__':
    Main().start()