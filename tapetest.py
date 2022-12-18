import os,sys,pathlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox,CheckButtons,Button
import time
try:
    from WebCamGrabber import WebcamVideoStream
    import cv2
    CV2=True
except ImportError:
    print("Could not import opencv or WebCamGrabber")
    CV2=False

plt.rcParams['keymap.save'].remove('s')
plt.rcParams['keymap.quit'].remove('q')
plt.rcParams['keymap.pan'].remove('p')
plt.rcParams["figure.figsize"] = (10,4)

class TapeTest:
    def __init__(self,cfg):
        os.chdir(pathlib.Path(__file__).parent)
        self.starttime=0
        self.leftstart,self.leftstop, self.rightstart,self.rightstop=[],[],[],[]
        self.cfg=cfg
        self.debounce_delay=self.cfg['DEBOUNCE']
        self.camera=self.cfg['CAMERA']
        self.max_time=self.cfg['TIMEOUT']
        self.lastlup=0 # for debouncing up key; last time left control was released
        self.lastrup=0 # for debouncing up key; last time right control was released
        self.saved=True ## prevent any further saving
        self.fig, self.ax = plt.subplots()
        self.ax.set(ylim=[0,3],yticks=[1,2],yticklabels=['left','right'])
        self.ax.grid(True)
        plt.subplots_adjust(bottom=0.4)
        self.text_box = TextBox     (plt.axes([0.1,0.25,0.8,0.075]),
                                        'Save as', 
                                        initial=self.cfg['FILENAMETEMPLATE'])
        self.check_box= CheckButtons(plt.axes([0.1,0.05,0.15,0.15]),
                                        [" left success"," right success"],
                                        [False,False])
        self.btn_box= Button        (plt.axes([0.75,0.05,0.15,0.15]),
                                        "Save")
        self.btn_box.on_clicked(lambda e:self.save() or self.reset())
        self.running=False
        self.xscalewidth=self.cfg['X_SCALE_WIDTH']
        self.timer = self.fig.canvas.new_timer(interval=16.66)
        self.timer.add_callback(self.plotlines, self.ax)
        self.fig.canvas.mpl_connect('key_press_event', self.on_press)
        self.fig.canvas.mpl_connect('key_release_event', self.on_release)
        #self.fig.canvas.mpl_connect('resize_event', self.on_resize)
        plt.suptitle("Press/release a and p key to indicate onset and offset of interactions with left or right leg")
        self.ax.set_title("Paused. Press space to begin regordings")
        if CV2 and self.camera>=0:
            self.cam=WebcamVideoStream(self.camera,width=self.cfg['RESOLUTION'][0],height=self.cfg['RESOLUTION'][1]).start()
            self.fig.canvas.mpl_connect('close_event', self.on_close)
            self.vtimer = self.fig.canvas.new_timer(interval=33.333)
            self.vtimer.add_callback(self.plotvid,self.ax)
            self.vtimer.start()
        plt.show()

    '''
    def on_resize(self,event):
        ## fixes the vertical position and height of buttons, checkboxes and textbox in pixels rather than in figure units
        ## heavy code without any fundamental interest
        vpixel=1/event.height
        hpixel=1/event.width
        p=self.btn_box.ax.get_position()
        self.btn_box.ax.set_position([p.xmin,10*vpixel,p.xmax-p.xmin,30*vpixel])
        p=self.check_box.ax.get_position()
        self.check_box.ax.set_position([p.xmin,10*vpixel,60*hpixel,50*vpixel])
        self.check_box.ax.axis('off')
        p=self.text_box.ax.get_position()
        self.text_box.ax.set_position([p.xmin,55*vpixel,p.xmax-p.xmin,30*vpixel],which='both')
        p=self.ax.get_position()
        self.ax.set_position([p.xmin,120*vpixel,p.xmax-p.xmin,1-200*vpixel])
        #self.fig.canvas.draw()
    '''

    def on_close(self,event):
        if self.camera>=0:
            self.cam.stop()
            cv2.destroyAllWindows()

    def plotvid(self,ax):
        got,frame=self.cam.read()
        if got:
            if self.running:
                if int(time.perf_counter())%2: ## blinking
                    cv2.putText(frame, 'Recording', (10,20), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0,0,255), 1, cv2.LINE_AA)
            else:
                cv2.putText(frame, 'Idle', (10,20), cv2.FONT_HERSHEY_SIMPLEX,0.75, (255,255,255), 1, cv2.LINE_AA)
            cv2.imshow('video',frame)
            cv2.waitKey(1)

    def plotlines(self,ax):
        if time.time()-self.starttime>self.max_time: ## check for timeout
            self.stop()
            if self.camera>=0:
                self.cam.stoprecording()
            return
        ax.cla()
        self.ax.set(ylim=[0,3],
                    yticks=[1,2],
                    yticklabels=['left','right'])
        self.ax.grid(True)
        self.ax.set_title("Recording. press 'space' to stop",color='r')
        if len(self.leftstart)>0:
            ax.hlines([1 for x in self.leftstart],
                            xmin=self.leftstart,
                            xmax=self.leftstop + [time.time()-self.starttime]*(len(self.leftstart)-len(self.leftstop)), 
                            color=self.cfg['LEFTCOLOR'], linewidth=self.cfg['LINEWIDTH'])
        if len(self.rightstart)>0:
            ax.hlines([2 for x in self.rightstart],
                            xmin=self.rightstart,
                            xmax=self.rightstop + [time.time()-self.starttime]*(len(self.rightstart)-len(self.rightstop)), 
                            color=self.cfg['RIGHTCOLOR'], linewidth=self.cfg['LINEWIDTH'])
        self.ax.set_xlim(max(0,time.time()-self.starttime-self.xscalewidth),max(time.time()-self.starttime,self.xscalewidth))
        self.ax.axvline(time.time()-self.starttime,color='k')
        self.fig.canvas.draw()

    def save(self):
        if self.running or self.saved:
            return
        df=pd.DataFrame([pd.Series(self.leftstart).rename("leftstart"),
        pd.Series(self.leftstop).rename("leftstop"),
        pd.Series(self.rightstart).rename("rightstart"),
        pd.Series(self.rightstop).rename("rightstop")]).T
        df['leftdur']=df['leftstop']-df['leftstart']
        df['rightdur']=df['rightstop']-df['rightstart']
        leftr=df['leftstop'].max() if self.check_box.get_status()[0] else np.nan
        rightr=df['rightstop'].max() if self.check_box.get_status()[1] else np.nan
        df['leftremoval']=pd.Series(leftr).rename('leftremoval')
        df['rightremoval']=pd.Series(rightr).rename('rightremoval')
        filename=self.text_box.text.replace('{date}',time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time())))
        df.to_csv(self.cfg['PREFIX']+filename+"_details.csv",sep='\t')
        summary={"left_leg_first_contact":self.leftstart[0] if len(self.leftstart) else np.nan,
                 "left_leg_removal_time":df['leftremoval'].max(),
                 "left_leg_episode_count":len(self.leftstart),
                 "left_leg_episode_duration_avg":np.mean(df["leftdur"]),
                 "left_leg_episode_duration_max":np.max(df["leftdur"]),
                 "left_leg_episode_duration_min":np.min(df["leftdur"]),
                 "left_leg_episode_duration_std":np.std(df["leftdur"]),
                 "right_leg_first_contact":self.rightstart[0] if len(self.rightstart) else np.nan,
                 "right_leg_removal_time":df['rightremoval'].max(),
                 "right_leg_episode_count":len(self.rightstart),
                 "right_leg_episode_duration_avg":np.mean(df["rightdur"]),
                 "right_leg_episode_duration_max":np.max(df["rightdur"]),
                 "right_leg_episode_duration_min":np.min(df["rightdur"]),
                 "right_leg_episode_duration_std":np.std(df["rightdur"]),
        }
        pd.DataFrame(pd.Series(summary).rename("summary")).to_csv(self.cfg['PREFIX']+filename+"_summary.csv",sep='\t')
        if self.camera>=0:
            try:
                os.rename(self.cfg['PREFIX']+"tapetest.mts",self.cfg['PREFIX']+filename+"_video.mts")
            except:
                print("Something weird happened while attempting to save video.")
                print("(or maybe you simply tried to save twice!)")
        self.ax.set_title("Successfully saved results. Press r to reset",color='k')
        self.saved=True

    def reset(self):
        self.ax.cla()
        self.ax.grid(True)
        self.ax.set(ylim=[0,3],yticks=[1,2],yticklabels=['left','right'])
        self.leftstart=[]
        self.leftstop=[]
        self.rightstart=[]
        self.rightstop=[]
        self.running=False
        self.ax.set_title("Paused. Press space to begin regordings",color='k')
        self.starttime=0
        self.fig.canvas.draw()

    def start(self):
        self.starttime=time.time()
        self.timer.start()
        self.running=True
        self.ax.set_title("Recording. press 'space' to stop",color='r')
        self.fig.canvas.draw()

    def stop(self):
        self.timer.stop()
        self.running=False
        self.ax.set_title("Paused. Press 's' to save or 'r' to reset",color='k')
        self.fig.canvas.draw()

    def debounce(self):
        if time.time()-self.lastlup<self.debounce_delay and len(self.leftstop): ## an event occured immediately after a release!
            self.leftstop.pop()
            self.lastlup=time.time()
            return True
        if time.time()-self.lastrup<self.debounce_delay and len(self.rightstop): ## an event occured immediately after a release!
            self.rightstop.pop()
            self.lastrup=time.time()
            return True
        return False

    def on_press(self,event):
        if self.debounce():
            return
        elif event.key == 'escape':
            self.stop()
            self.reset()
        elif event.key == self.cfg['KEYSAVE']:
            self.save()
        elif event.key == self.cfg['KEYLEFT'] and self.running:
            self.leftstart.append(time.time()-self.starttime)
        elif event.key==self.cfg['KEYRIGHT'] and self.running:
            self.rightstart.append(time.time()-self.starttime)
        elif event.key==self.cfg['KEYZOOMIN'] and self.running:
            self.xscalewidth/=2
        elif event.key==self.cfg['KEYZOOMOUT'] and self.running:
            self.xscalewidth*=2
        elif event.key==self.cfg['KEYSTART']:
            if not self.running:
                self.start()
                self.saved=False
                if self.camera>=0:
                    self.cam.startrecording(self.cfg['PREFIX']+"tapetest"+self.cfg['VIDCONTAINER'],
                                                    self.cfg['VIDFOURCC'])
            else:
                self.stop()
                if self.camera>=0:
                    self.cam.stoprecording()

    def on_release(self,event):
        if event.key == self.cfg['KEYLEFT'] and self.running:
            self.leftstop.append(time.time()-self.starttime)
            self.lastlup=time.time()
        elif event.key==self.cfg['KEYRIGHT'] and self.running:
            self.rightstop.append(time.time()-self.starttime)
            self.lastrup=time.time()

if __name__=='__main__':
    import os,sys,re,pathlib
    cfg={}
    if getattr(sys, 'frozen', False):
        cfgpath = pathlib.Path(sys._MEIPASS).parent
        cfg["PREFIX"]=".."+os.sep
    else:
        cfgpath = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
        cfg["PREFIX"]=""
    for l in open(cfgpath/"params.py").readlines():
        if not l.startswith('#'):
            r=re.split('=|#',l)
            cfg[r[0].strip(' ')]=eval(r[1].strip(' '))
    TapeTest(cfg)
