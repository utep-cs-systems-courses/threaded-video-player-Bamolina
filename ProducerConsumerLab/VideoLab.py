#!/usr/bin/env python3
import cv2, threading

VIDEO = "../clip.mp4"
EOF = '\0'

class Queue():

    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()
        self.front = threading.Semaphore(24)
        self.rear = threading.Semaphore(0)

    # front and rear will be used to keep track of the capacity
    def enqueue(self, item):
        self.front.acquire()
        self.lock.acquire()
        self.queue.append(item)
        self.lock.release()
        self.rear.release()

    def dequeue(self):
        self.rear.acquire()
        self.lock.acquire()
        item = self.queue.pop(0)
        self.lock.release()
        self.front.release()

# based on extract frames demo
def extractFrames(fileName, queue):
    # initialize frame count
    count = 0

    # open the video clip
    vid_cap = cv2.VideoCapture(fileName)

    # read one frame
    success, image = vid_cap.read()

    print(f'Reading frame {count} {success}')
    while success:
        # add frame to queue
        queue.enqueue(image)

        success, image = vid_cap.read()
        print(f'Reading frame {count}')
        count += 1
    queue.enqueue(EOF)

# based on convert to grayscale demo
def convertToGrayscale(colorFrames, grayFrames):
    # initialize frame count
    count = 0
    colorFrame = colorFrames.dequeue()

    # Iterate through frames
    while colorFrame is not EOF:
        print(f'Converting frame {count}')

        # Convert the image to grayscale_
        grayFrame = cv2.cvtColor(colorFrame, cv2.COLOR_BGR2GRAY)

        grayFrames.enqueue(grayFrame)

        count += 1

        colorFrame = colorFrames.dequeue()

# based on display frames demo
def displayFrames(frames):
    # initialize frame count
    count = 0
    frame = frames.dequeue()

    # iterate over the entire queue
    while frame is not EOF:
        print(f'Displaying frame {count}')

        # Display the frame in a window called "Video"
        cv2.imshow('Video', frame)
        # Wait for 42 ms and check if the user wants to quit
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break
        count += 1

        # Next frame from the queue
        frame = frames.get()

    print('All frames have been displayed. Imagine animating at 24fps for a living')
    # make sure we cleanup the windows, otherwise we might end up with a mess
    cv2.destroyAllWindows()

if __name__ == "__main__":

    colorFrames = Queue()
    grayFrames = Queue()
    extractionThread = threading.Thread(target = extractFrames, args = (VIDEO, colorFrames))
    convertionThread = threading.Thread(target = convertToGrayscale, args = (colorFrames, grayFrames)) # not sure if convertion is a word
    displayThread = threading.Thread(target = displayFrames, args = (grayFrames,))

    extractionThread.start()
    convertionThread.start()
    displayThread.start()
