#!/usr/bin/env python

'''
Lucas-Kanade tracker
====================

Lucas-Kanade sparse optical flow demo. Uses goodFeaturesToTrack
for track initialization and back-tracking for match verification
between frames.

Usage
-----
lk_track.py [<video_source>]


Keys
----
ESC - exit
'''
import socket   #for sockets
import sys  #for exit
import numpy as np
import cv2
import video
from common import anorm2, draw_str
from time import clock
from time import sleep
import ultrasonic_poller

lk_params = dict( winSize  = (15, 15),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

feature_params = dict( maxCorners = 500,
                       qualityLevel = 0.3,
                       minDistance = 7,
                       blockSize = 7 )

class App:
    def __init__(self, video_src, s, host, port):
        # create the threads
        self.ultrasonics = ultrasonic_poller.UltrasonicPoller() 
        self.ultrasonics.start()
        self.track_len = 10 # length of tracks
        self.detect_interval = 5 # detect features every 5 frames
        self.cam = video.create_capture(video_src)
        self.frame_idx = 0 # frame number
        self.left_tracks = []
        self.right_tracks = []
        self.left_mag = 0
        self.right_mag = 0
        self.max_tracks = 100
        self.s = s
        self.host = host 
        self.port = port

    def annotate_image(self, frame):
        height, width, channels = frame.shape
        mid_bottom = (width/2, 0) 
        mid_top = (width/2, height)
        
        cv2.line(frame, mid_bottom, mid_top,(0, 0, 255), 2)

        text_right = "Right"
        text_left = "Left"
        font_face = cv2.FONT_HERSHEY_PLAIN
        font_scale = 2
        thickness = 2
        baseline = 0

        text_size_right, baseline = cv2.getTextSize(text_right, font_face,
                                  font_scale, thickness) #, baseline)
        text_size_left, baseline = cv2.getTextSize(text_left, font_face,
                                  font_scale, thickness) #, baseline)
        baseline = baseline + thickness      

        # center the text
        p1 = (5, (width + text_size_left[1])/10)
        p2 = ((width - text_size_right[0] - 5), (width + text_size_left[1])/10)

        # then put the text itself
        cv2.putText(frame, text_left, p1, font_face, font_scale,
              (255, 255, 255), thickness, 8)
        cv2.putText(frame, text_right, p2, font_face, font_scale,
                (255, 255, 255), thickness, 8)
        return frame

    def run(self):
        try:
            while True:
                ret, frame = self.cam.read() # read .. ret == boolean
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # convert to grayscale
                vis = frame.copy() # frame to print

                if len(self.left_tracks) > 0:
                    if len(self.left_tracks) > self.max_tracks:
                        for i in range(0, 10):
                            del self.left_tracks[i]
                    img0, img1 = self.prev_gray, frame_gray

                    p0 = np.float32([tr[-1] for tr in self.left_tracks]).reshape(-1, 1, 2) # for each track in self.tracks get last element + reshape       
                    p1, st, err = cv2.calcOpticalFlowPyrLK(img0, img1, p0, None, **lk_params) # .. new tracks here
                    p0r, st, err = cv2.calcOpticalFlowPyrLK(img1, img0, p1, None, **lk_params)
                    d = abs(p0-p0r).reshape(-1, 2).max(-1) # fancy reshape.. one for each track
                    good = d < 1 # converts to boolean array len(self.tracks)
                    new_tracks = []
                    for tr, (x, y), good_flag in zip(self.left_tracks, p1.reshape(-1, 2), good):
                        if not good_flag:
                            continue
                        tr.append((x, y))
                        if len(tr) > self.track_len:
                            del tr[0]
                        new_tracks.append(tr) # our new tracks array
                        cv2.circle(vis, (x, y), 2, (0, 255, 0), -1) # draw circle  on vis
                    self.left_tracks = new_tracks
                    cv2.polylines(vis, [np.int32(tr) for tr in self.left_tracks], False, (0, 255, 0)) # nice polylines   
                
                if len(self.right_tracks) > 0:
                    if len(self.right_tracks) > self.max_tracks:
                        for i in range(0, 10):
                            del self.right_tracks[i]
                    img0, img1 = self.prev_gray, frame_gray

                    p0 = np.float32([tr[-1] for tr in self.right_tracks]).reshape(-1, 1, 2) # for each track in self.tracks get last element + reshape       
                    p1, st, err = cv2.calcOpticalFlowPyrLK(img0, img1, p0, None, **lk_params) # .. new tracks here
                    p0r, st, err = cv2.calcOpticalFlowPyrLK(img1, img0, p1, None, **lk_params)
                    d = abs(p0-p0r).reshape(-1, 2).max(-1) # fancy reshape.. one for each track
                    good = d < 1 # converts to boolean array len(self.tracks)
                    new_tracks = []
                    for tr, (x, y), good_flag in zip(self.right_tracks, p1.reshape(-1, 2), good):
                        if not good_flag:
                            continue
                        tr.append((x, y))
                        if len(tr) > self.track_len:
                            del tr[0]
                        new_tracks.append(tr) # our new tracks array
                        cv2.circle(vis, (x, y), 2, (255, 0, 0), -1) # draw circle  on vis
                    self.right_tracks = new_tracks
                    cv2.polylines(vis, [np.int32(tr) for tr in self.right_tracks], False, (255, 0, 0)) # nice polylines

                if self.frame_idx % self.detect_interval == 0:
                    print "left: ", len(self.left_tracks)
                    print "right: ", len(self.right_tracks)
                    
                    try :
                        #Set the whole string
                        if int(self.left_mag) or int(self.right_mag):
                            self.s.sendto("distance " + str(int(self.ultrasonics.distance)) + " left " + str(int(self.left_mag)) + " right " + str(int(self.right_mag)), (self.host, self.port))
                        else:
                            self.s.sendto("distane " + str(int(self.ultrasonics.distance)), (self.host, self.port))
                        # receive data from client (data, addr)
                        # d = self.s.recvfrom(1024)
                        # reply = d[0]
                        # addr = d[1]
                        # print 'Server reply : ' + reply
                    except socket.error, msg:
                        print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
                        #sys.exit()

                    if len(self.left_tracks) > 0:
                        self.left_mag = 0
                        for tr in self.left_tracks:
                            x = [x[0] for x in tr]
                            y = [y[1] for y in tr]
                            self.left_mag = self.left_mag + abs(max(x) - min(x)) + abs(max(y) - min(y))
                        self.left_mag = self.left_mag / len(self.left_tracks)
                        
                    if len(self.right_tracks) > 0:
                        self.right_mag = 0
                        for tr in self.right_tracks:
                            x = [x[0] for x in tr]
                            y = [y[1] for y in tr]
                            self.right_mag = self.right_mag + abs(max(x) - min(x)) + abs(max(y) - min(y))
                        self.right_mag = self.right_mag / len(self.right_tracks)
                    
                    mask = np.zeros_like(frame_gray) # mask == array of zeros with the same shape and type as 'frame_gray'
                    mask[:] = 255 # set every value to 255
                    for x, y in [np.int32(tr[-1]) for tr in self.left_tracks]:
                        cv2.circle(mask, (x, y), 5, 0, -1)
                    for x, y in [np.int32(tr[-1]) for tr in self.right_tracks]:
                        cv2.circle(mask, (x, y), 5, 0, -1)
                    p = cv2.goodFeaturesToTrack(frame_gray, mask = mask, **feature_params)
                    if p is not None:
                        for x, y in np.float32(p).reshape(-1, 2): # fancy reshape
                            if x < 320.0:
                                self.left_tracks.append([(x, y)]) # append features to track
                            else:
                                self.right_tracks.append([(x, y)]) # append features to track

                self.frame_idx += 1 # increment
                self.prev_gray = frame_gray # set prev_gray for next iteration
                # vis = self.annotate_image(vis)
                # draw_str(vis, (20, 100), 'ultrasonic reading: %d cm' % self.ultrasonics.distance) # give count 
                # draw_str(vis, (20, 20), 'left count: %d' % self.left_mag) # give count      
                # draw_str(vis, (500, 20), 'right count: %d' % self.right_mag) # give count 
                # cv2.imshow('lk_track', vis) # show copy of frame 'vis'

                ch = 0xFF & cv2.waitKey(1)
                if ch == 27:
                    break

        except (KeyboardInterrupt):#, SystemExit): #when you press ctrl+c
            print "Exiting.."
            self.ultrasonics.stop()

def main():
    import sys
    try: 
        video_src = sys.argv[1]
    except: 
        video_src = 0

    print __doc__

    # create dgram udp socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        print 'Failed to create socket'
        sys.exit()

    host = '127.0.0.1'
    port = 8888;

    App(video_src, s, host, port).run()
    # cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
