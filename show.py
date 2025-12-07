import queue_class as queue
import cv2

def show_video_run():
    while True:
        frame = queue.show_queue.get()
        #cv2.imshow("Camara", frame)
        #cv2.waitKey(1)