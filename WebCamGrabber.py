#!/usr/bin/env python

from threading import Thread, Lock
import cv2
import time
RESOLUTION=(640,480)        ## resolution of input video. this has to be dupported by your camera
FPS=30                      ## FPS of your camera
DEVICE=0                    ## device number of camera. use -1 to disable video

'''
resolutions=[(640,360),(640,480),(800,600),(1280,720),(1280,960),(1920,1080)]
vid = cv2.VideoCapture(0)
vid.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3)
vid.set(cv2.CAP_PROP_FPS, 30)
vid.set(cv2.CAP_PROP_FRAME_WIDTH,resolutions[2][0])
vid.set(cv2.CAP_PROP_FRAME_HEIGHT,resolutions[2][1])
vid.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
t=time.perf_counter()
f=0
while True:
    ret, frame = vid.read()
    cv2.imshow('frame', frame)
    f+=1
    if time.perf_counter()>t+1.0:
        t=time.perf_counter()
        print("fps : ", f)
        f=0
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
vid.release()
cv2.destroyAllWindows()
'''
_USUAL_RESOLUTIONS=[
(160, 120),
(192, 144),
(256, 144),
(240, 160),
(320, 240),
(360, 240),
(384, 240),
(400, 240),
(432, 240),
(480, 320),
(480, 360),
(640, 360),
(600, 480),
(640, 480),
(720, 480),
(768, 480),
(800, 480),
(854, 480),
(960, 480),
(675, 540),
(960, 540),
(720, 576),
(768, 576),
(1024, 576),
(750, 600),
(800, 600),
(800, 800),
(1024, 600),
(960, 640),
(1024, 640),
(1136, 640),
(960, 720),
(1152, 720),
(1280, 720),
(1440, 720),
(960, 768),
(1024, 768),
(1152, 768),
(1280, 768),
(1366, 768),
(1280, 800),
(1152, 864),
(1280, 864),
(1536, 864),
(1200, 900),
(1440, 900),
(1600, 900),
(1280, 960),
(1440, 960),
(1536, 960),
(1280, 1024),
(1600, 1024),
(1400, 1050),
(1680, 1050),
(1440, 1080),
(1920, 1080),
(2160, 1080),
(2280, 1080),
(2560, 1080),
(2048, 1152),
(1500, 1200),
(1600, 1200),
(1920, 1200),
(1920, 1280),
(2048, 1280),
(1920, 1440),
(2160, 1440),
(2304, 1440),
(2560, 1440),
(2880, 1440),
(2960, 1440),
(3040, 1440),
(3120, 1440),
(3200, 1440),
(3440, 1440),
(5120, 1440),
(2048, 1536),
(2400, 1600),
(2560, 1600),
(3840, 1600),
(2880, 1620),
(2880, 1800),
(3200, 1800),
(2560, 1920),
(2880, 1920),
(3072, 1920),
(2560, 2048),
(2732, 2048),
(3200, 2048),
(2880, 2160),
(3240, 2160),
(3840, 2160),
(4320, 2160),
(5120, 2160),
(3200, 2400),
(3840, 2400),
(3840, 2560),
(4096, 2560),
(5120, 2880),
(5760, 2880),
(4096, 3072),
(7680, 4320),
(10240, 4320)
]

def list_cam_resolutions(src):
    cap = cv2.VideoCapture(src)
    res=[]
    for r in _USUAL_RESOLUTIONS:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,r[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT,r[1])
        w=cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        h=cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        if w==r[0] and h==r[1]:
            res.append((w,h))
    cap.release()
    return res

def list_cam_fps(src):
    cap = cv2.VideoCapture(src)
    res=[]
    for fps in [5,15,30,60]:
        cap.set(cv2.CAP_PROP_FPS,fps)
        if fps==cap.get(cv2.CAP_PROP_FPS):
            res.append(fps)
    cap.release()
    return res

class WebcamVideoStream :
    def __init__(self, src = 0, width = 640, height =480) :
        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3)
        self.stream.set(cv2.CAP_PROP_FPS, 30)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH,width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT,height)
        self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        (self.grabbed, self.frame) = self.stream.read()
        self.started = False
        self.t=0
        self.fps=0
        self.framecnt=0
        self.writer=None
        self.recording=False
        self.read_lock = Lock()

    def start(self) :
        if self.started :
            print("already started!!")
            return None
        self.started = True
        self.t=time.perf_counter()
        self.framecnt=0
        self.fps=0
        self.thread = Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self) :
        while self.started :
            grabbed=False
            (grabbed, frame) = self.stream.read()
            ## grabbed, frames are local variables to the thread.
            ## because we will now access / modify members in WebCamVideoStream, 
            ## that can also be modified outside the thread,
            ## we need to lock to be sure no other modification occurs during that time
            self.read_lock.acquire()
            self.framecnt+=1
            if time.perf_counter()>self.t+1:
                self.framecnt=0
                self.fps=self.framecnt
                self.t=time.perf_counter()
            if self.recording and not self.writer is None:
                self.writer.write(frame)
            self.grabbed, self.frame = grabbed, frame
            self.read_lock.release()

    def read(self,cvt=False) :
        self.read_lock.acquire()
        if cvt:
            frame = cv2.cvtColor(self.frame,cv2.COLOR_BGR2RGB)
        else:
            frame=self.frame.copy()
        grabbed=self.grabbed
        self.grabbed=False
        self.read_lock.release()
        return grabbed,frame

    def startrecording(self,filename,fourcc='avc1'):
        self.read_lock.acquire()
        self.writer=cv2.VideoWriter(filename,cv2.CAP_FFMPEG,
                                        cv2.VideoWriter_fourcc(*fourcc),
                                        self.stream.get(cv2.CAP_PROP_FPS),
                                        (int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)),int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        )
        self.recording=True
        self.read_lock.release()

    def stoprecording(self):
        self.read_lock.acquire()
        if self.recording:
            self.recording=False
            self.writer.release()
        self.read_lock.release()

    def stop(self) :
        self.started = False
        self.thread.join()

    def __exit__(self, exc_type, exc_value, traceback) :
        if not self.writer is None:
            self.writer.release()
        self.stream.release()

if __name__ == "__main__" :
    print("Checking supported webcam resolutions...")
    print(list_cam_resolutions(2))
    print(list_cam_fps(2))
    instream = WebcamVideoStream(2).start()
    while True :
        got,frame = instream.read()
        if got:
            cv2.imshow('webcam', frame)
        k=cv2.waitKey(1)
        if k==27:
            break
        elif k==ord(' ') and not instream.recording:
            instream.startrecording("test.mts",fourcc='avc1')
        elif k==ord(' ') and instream.recording:
            instream.stoprecording()

    instream.stop()
    cv2.destroyAllWindows()
