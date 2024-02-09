# import necessary libs
import mediapipe as mp
import cv2
import numpy as np
import keyboard
import webbrowser 

#webbrowser.open_new_tab("https://chromedino.com/")

class VideoCamera2(object):
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.mainobj = trex()
    def __del__(self):
        self.cap.release()
    def get_frame(self):
        ret, frame = self.cap.read()
        processed_frame = self.mainobj.game(frame)
        ret, frame = cv2.imencode('.jpg', processed_frame)
        return frame.tobytes()

# to find distance between fingers
def euclidean(pt1, pt2):
    d = np.sqrt((pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2)
    return d


class trex:
    def __init__(self):
        self.cam = cv2.VideoCapture(0)
        self.fsize = (520, 720)
        #webbrowser.open_new_tab("https://chromedino.com/")
        self.last_event = None
        self.check_cnt = 0
        self.check_every = 3
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=True,max_num_hands = 1,min_detection_confidence=0.6)



    def game(self,frame):
        with self.mp_hands.Hands(static_image_mode=True,max_num_hands = 1,min_detection_confidence=0.6) as hands:   
        #while cam.isOpened():
            #ret, frame = cam.read()
            
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (self.fsize[1], self.fsize[0]))
            
            h, w,_ = frame.shape
            
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False
            
            res = hands.process(rgb)
            #cv2.imshow("roi", roi)
            rgb.flags.writeable = True
            
            #cv2.putText(rgb,"hello",(210,190),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),3)
            if res.multi_hand_landmarks:

                for hand_landmarks in res.multi_hand_landmarks:
    
                    index_tip = self.mp_drawing._normalized_to_pixel_coordinates(
                        hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].x, 
                        hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y, 
                        w, h)
                
                    thumb_tip = self.mp_drawing._normalized_to_pixel_coordinates(
                        hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP].x, 
                        hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP].y, 
                        w, h)
                    
                    middle_tip = self.mp_drawing._normalized_to_pixel_coordinates(
                        hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x, 
                        hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y, 
                        w, h)
                    
                    if index_tip is not None:
                        if self.check_cnt==self.check_every:
                            if index_tip is not None and middle_tip is not None:

                                
                                if euclidean(index_tip, middle_tip)<65: # 60 should be relative to the height of frame
                                    self.last_event = "jump"
                                else:
                                    if self.last_event=="jump":
                                        self.last_event=None
                            
                            if thumb_tip is not None and index_tip is not None:
                                #print(euclidean(index_tip, middle_tip))
                                if euclidean(thumb_tip, index_tip) < 60:
                                    self.last_event="duck"
                                else:
                                    if self.last_event == "duck":
                                        self.last_event = None
                            self.check_cnt=0
                    
                    if self.check_cnt==0:
                        if self.last_event=="jump":
                            keyboard.press_and_release("space")
                        elif self.last_event=="duck":
                            keyboard.press("down")
                        else:
                            keyboard.release("down")
                        #print(last_event)

                    self.check_cnt+=1

                    self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                    self.mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=2),
                
                    )
                    
            #cv2.imshow("Press Q to exit", frame)
            return frame
            
            
    