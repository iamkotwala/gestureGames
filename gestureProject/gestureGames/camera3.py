import mediapipe as mp      # For hand detection
import cv2                  # For computer vision tasks
import random               # To obtain random numbers
import os                   # to fetch contents from a directory

class VideoCamera3(object):

    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.mainobj = Game()

    def __del__(self):
        self.cap.release()

    def get_frame(self):
        ret, frame = self.cap.read()
        processed_frame = self.mainobj.play(frame)
        ret, frame = cv2.imencode('.jpg', processed_frame)
        return frame.tobytes()


# Class to detect hands and for finger recognition
class FingerRecognition:

    def __init__(self):
        self.mp_hands = mp.solutions.hands                                                          # Initializing mediapipe hands class 
        self.mp_drawing = mp.solutions.drawing_utils                                                # Initializing mediapipe drawing class to draw hand landmarks
        self.hands_video = self.mp_hands.Hands(static_image_mode = False, max_num_hands = 1, 
                                min_detection_confidence = 0.8, min_tracking_confidence = 0.8)      # Setting up function for detecting hand during video streaming

    # Function to detect hand, draw hand landmarks and return the results if hand is detected
    
    def detectHandLandmarks(self, img, draw = False, display = True):

        output = img.copy()                             # Image Copy for output
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)   # Converting from BGR to RGB format
        results = self.hands_video.process(imgRGB)      # Image Processing
        
        # If hands are found drawing handlandmarks on image
        
        if results.multi_hand_landmarks and draw:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(image = output, landmark_list = hand_landmarks,connections =self. mp_hands.HAND_CONNECTIONS,
                                        landmark_drawing_spec = self.mp_drawing.DrawingSpec(color = (255,255,255), thickness = 2, circle_radius = 2),
                                        connection_drawing_spec = self.mp_drawing.DrawingSpec(color = (0,255,0), thickness = 2, circle_radius = 2))
        
        return(output, results)  

    # Function to return the count of fingers that are open
    
    def countFingers(self, img, results, start, replay, draw = True, display = True):
    
        height, width, _ = img.shape        
        output = img.copy()                
        finger_count = 0                    # Initializing number of fingers open to 0
        
        # Obtaining the finger tip Id's and finger mcp Id's 

        finger_tips_ids = [self.mp_hands.HandLandmark.INDEX_FINGER_TIP, self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                        self.mp_hands.HandLandmark.RING_FINGER_TIP, self.mp_hands.HandLandmark.PINKY_TIP]                
        finger_mcp_ids = [self.mp_hands.HandLandmark.INDEX_FINGER_MCP, self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP,
                        self.mp_hands.HandLandmark.RING_FINGER_MCP]                                                   

        # Setting finger status to false, and changing it to true when finger opens.

        finger_status = {'THUMB' : False, 'INDEX' : False, 'MIDDLE' : False, 'RING' : False, 'PINKY' : False}

        for hand_index, hand_info in enumerate(results.multi_handedness):
            hand_label = hand_info.classification[0].label
            hand_landmarks = results.multi_hand_landmarks[hand_index]

            '''
            Note : If fingers are open in vertical direction, then the difference of y coordinates between the mcp values of the fingers will be less than 
            or equal to 0.02, and difference between x coordinates will be greater than 0.02. It will be vice versa if the fingers are open in horizontal direction. 
            Hence to check the direction of the fingers, the below steps are performed.
            '''
            # Function to obtain the difference between coordinates of fingers.

            def diff(lists):     
                diff_list = []
                for i in range(1,len(lists)):
                    diff_list.append(abs(round(lists[i] - lists[i-1],2)))
                return diff_list

            # Obtaining difference between coordinates of finger mcp values to check if fingers are open in horizontal or vertical direction.

            mcp_x_values, mcp_y_values = [], []

            for mcp_index in finger_mcp_ids:
                mcp_x_values.append(round(hand_landmarks.landmark[mcp_index].x,2))
                mcp_y_values.append(round(hand_landmarks.landmark[mcp_index].y,2))

            from statistics import mean   
            x = mean(diff(mcp_x_values))
            y = mean(diff(mcp_y_values))

            '''
            Note: x coordinate values are greater in the right and lesser in left. y coordinate values are greater at the bottom and lesser at the top.
            '''

            if x <= 0.02:                                       # If fingers are open in horizontal direction
                for tip_index in finger_tips_ids:               # Counting fingers that are open except thumb

                    wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST].x

                    finger_name = tip_index.name.split('_')[0]

                    if ((wrist > hand_landmarks.landmark[tip_index].x) and (hand_landmarks.landmark[tip_index].x < hand_landmarks.landmark[tip_index - 2].x)) or ((wrist < hand_landmarks.landmark[tip_index].x) and (hand_landmarks.landmark[tip_index].x > hand_landmarks.landmark[tip_index - 2].x)):
                        finger_status[finger_name] = True
                        finger_count += 1

                # Checking if thumb is open

                thumb_tip_x = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP].y
                thumb_mcp_x = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP - 2].y      

                if (thumb_tip_x < thumb_mcp_x):
                    finger_status['THUMB'] = True
                    finger_count += 1

            else:                                               # If fingers are open in vertical direction
                for tip_index in finger_tips_ids:
                    finger_name = tip_index.name.split('_')[0]

                    if (hand_landmarks.landmark[tip_index].y < hand_landmarks.landmark[tip_index - 2].y):
                        finger_status[finger_name] = True
                        finger_count += 1

                thumb_tip_x = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP].x
                thumb_mcp_x = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP - 2].x
                pinky_tip_x = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP].x


                if ((thumb_tip_x < pinky_tip_x) and (thumb_tip_x < thumb_mcp_x)) or ((thumb_tip_x > pinky_tip_x)and (thumb_tip_x > thumb_mcp_x)):
                    finger_status['THUMB'] = True
                    finger_count += 1

        # Obtaining only necessary finger counts for the game
        
        fingers = []
        count = finger_count
        
        for finger,flag in finger_status.items():           # Finding fingers that are open
            if finger_status[finger] == True:
                fingers.append(finger)
        
        if x <= 0.02:                                      
            if count == 1 and fingers == ['THUMB']:
                final_count = 6
            else:
                final_count = None
        else:                                               
            if count == 1 and fingers == ['INDEX']:
                final_count = 1 
            elif count == 2 and fingers == ['INDEX','MIDDLE']:
                final_count = 2
            elif count == 3 and fingers == ['INDEX','MIDDLE','RING']:
                final_count = 3
            elif count == 4 and fingers == ['INDEX','MIDDLE','RING','PINKY']:
                final_count = 4
            elif count == 5 and fingers == ['THUMB','INDEX','MIDDLE','RING','PINKY']:
                final_count = 5
            else:
                final_count = None

        return output, finger_count, final_count

# Class containing game logic

class Game:

    def __init__(self):
        self.cap = cv2.VideoCapture(0)    # Access webcam 
        self.finger = FingerRecognition()                            # Finger Recognition Object

        self.run = []
        self.target = 0
        self.current = 0
        self.innings = 1
        self.delay = 0
        self.ch = 0 
        self.computer = 0
        self.status = ""
        self.win_status = ""
        self.start = True
        self.out = False
        self.replay = False
        self.flag_comp = True
        self.end = False
        self.close = False
        
    # To fetch the image of the computer run and placing it in the output frame

    def computer_score(self, img, final_count):
        output = img.copy()

        if self.flag_comp == True:
            computer = random.randint(1, 6)
        else:
            computer = self.computer

        folderPath = "gestureGames/resources"
        my_list = os.listdir(folderPath)
        overlay = []

        for impath in my_list:
            image = cv2.imread(f'{folderPath}/{impath}')
            overlay.append(image)

        pic = overlay[computer - 1]  
        
        if self.start == False and self.replay == False:
            over = output.copy()
            cv2.rectangle(over, (0, 120), (640,190), (220,220,220), cv2.FILLED)
            alpha = 0.3
            img = cv2.addWeighted(over, alpha, img, 1-alpha, 0)
            output[200:400, 30:230] = pic
            cv2.putText(output, "OPPONENT",(20, 160), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,0), 2)
            cv2.putText(output, "RUN",(20, 180), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,0), 2)
            cv2.putText(output, f"{computer}",(200, 180), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,128), 3)
            cv2.putText(output, "YOUR",(430, 160), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,0), 2)
            cv2.putText(output, "RUN",(430, 180), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,0), 2)
            cv2.putText(output, f"{final_count}",(550, 180), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,128), 3)
        elif self.start == True or self.replay == True:
            cv2.putText(output, "",(430, 180), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,0), 2)
        
        return output, computer

    # Main Game loop

    def play(self, frame_new):    
        delay = self.delay              # Delay counter to perform certain tasks at specified time 
        img = frame_new
        img = cv2.flip(img, 1)       
        user = None                     # Initializing the user run to None and then changing it when the finger is recognized  
        self.run = []  
        
        icon = cv2.imread('gestureGames/static/1-6.jpg')            # Header Image in the webscreen
        icon = cv2.resize(icon, (640,120))
        img[0:120, 0:] = icon
        font_style = cv2.FONT_HERSHEY_PLAIN                       
                
        if delay >= 0 and delay <= 20:
            text = "Ready?"
        elif delay < 40:
            text = "Set!"
        elif delay < 70:
            text = "Show your run now!"
            img, results = self.finger.detectHandLandmarks(img, draw = False, display = True)    # Detecting hand landmarks form the image

            if results.multi_hand_landmarks:                                                # Obtaining the finger count
                img, finger_count, final_count = self.finger.countFingers(img, results, start = self.start, replay = self.replay, draw = True, display = True)
                user = final_count
                
            if user != None:
                text = ""
                img, computer = self.computer_score(img, user)

                if self.flag_comp == True:
                    self.computer = computer
                    self.flag_comp = False

                if computer == final_count:                                            
                    txt = "stop"
                else: 
                    txt = 'playing'

                self.run = [user, computer, txt]

        elif delay < 100:
            if self.run == []:
                text = "You missed it...Try again!!"

        delay = (delay + 1) % 100 

        if self.close == True:
            self.cap.release()
            exit()

        if self.replay == True and self.start == False and self.run != []:
            if self.run[0] == 6:
                self.run = []
                self.target = 0
                self.current = 0
                self.innings = 1
                self.ch = 0
                self.start = True
                self.replay = False
                self.win_status = ""
            elif self.run[0] == 5:
                self.close = True
                self.replay = False
                
        if self.start == True:
            if self.run != []:
                if self.run[0] == 1:
                    self.ch = 1
                    self.status = "You Bat"
                elif self.run[0] == 2:
                    self.ch = 2
                    self.status = "You Bowl"

            if self.ch == 1 or self.ch == 2:
                self.start = False
                self.run = []
                delay = 0
        
        if self.start == False and self.replay == False and self.out == True and delay == 50:
            self.out = False
            if self.innings == 1:
                self.innings += 1
            elif self.innings == 2:
                self.end = False
                self.replay = True
            delay = 0

        if self.innings == 2 and self.replay == True:
            if self.ch == 1:
                if self.current >= self.target:
                    txt = 'You Lose!'   
                elif self.current == (self.target - 1):
                    txt = 'Tie!'
                else:
                    txt = 'You Win!!'
            elif self.ch == 2:
                if self.current >= self.target:
                    txt = 'You Win!!'
                elif self.current == (self.target - 1):
                    txt = 'Tie!'
                else:
                    txt = 'You Lose!'
            self.win_status = txt

        if self.start == False and self.replay == False and delay == 65 and self.run != []:
            self.flag_comp = True

            if self.run[-1] == 'stop':
                self.out = True

                if self.innings == 1:
                    if self.ch == 1:
                        self.status = 'You Bowl'
                    elif self.ch == 2:
                        self.status = 'You Bat'
                    self.target = self.current + 1
                    self.current = 0

            if self.innings == 1 and self.out != True:
                if self.ch == 1:
                    self.current += self.run[0]
                elif self.ch == 2:
                    self.current += self.run[1]

            elif self.innings == 2 and self.out != True:
                if self.ch == 1:
                    self.current += self.run[1]
                elif self.ch == 2:
                    self.current += self.run[0]
            
            if self.innings == 2 and self.current >= self.target:
                self.out = True
                self.end = True
    
            delay = 0
            self.run = []            
        
        # Displaying certain messages in the webcam screen

        if self.close == True:
            cv2.rectangle(img, (0, 0), (640,480), (255,255,255), cv2.FILLED)
            cv2.putText(img, "Bye...",(200, 260), fontFace = 4, fontScale = 3, color = (0,0,0), thickness = 3)
            cv2.putText(img, "Catch you later :)",(10, 380), fontFace = 4, fontScale = 2, color = (0,0,0), thickness = 3)
            
        if self.win_status == '':
            if self.start == True:
                text = "   "
                cv2.rectangle(img, (0, 0), (640,150), (220,220,220), cv2.FILLED)
                cv2.putText(img, "Hand Cricket",(100, 70), fontFace = 4, fontScale = 2, color = (106,51,170), thickness = 3)
                cv2.putText(img, "Do you choose Batting or Bowling?",(30, 110), fontFace = 1, fontScale = 2, color = (106,51,170), thickness = 1)
                cv2.putText(img, "Batting (Show 1)",(90, 140), fontFace = 1, fontScale = 1, color = (106,51,170), thickness = 1)
                cv2.putText(img, "Bowling (Show 2)",(380, 140), fontFace = 1, fontScale = 1, color = (106,51,170), thickness = 1)
            else:
                alpha = 0.3
                over = img.copy()
                cv2.rectangle(over, (0, 400), (640,480), (220,220,220), cv2.FILLED)
                img = cv2.addWeighted(over, alpha, img, 1-alpha, 0)
                cv2.putText(img, text, (20, 160), font_style, 2, (0, 255, 255), 2,2)
                cv2.putText(img, 'CURRENT', (100, 420), font_style, 1, (0, 0, 0), 2)
                cv2.putText(img, f'{self.current}', (100, 470), font_style, 4, (0, 0, 128), 3)
                cv2.putText(img, f'INNINGS {self.innings}', (250, 430), font_style, 2, (0, 0, 0), 2)
                cv2.putText(img, f'{self.status}', (250, 470), font_style, 2, (0, 0, 128), 2)
                cv2.putText(img, 'TARGET', (500, 420), font_style, 1, (0, 0, 0), 2)
                cv2.putText(img, f'{self.target}', (500, 470), font_style, 4, (0, 0, 128), 3)

        elif self.win_status != "" and self.replay == True:
            text = "   "
            cv2.rectangle(img, (0, 0), (640,150), (220,220,220), cv2.FILLED)
            if self.win_status == 'Tie!':
                cv2.putText(img, f"{self.win_status}",(200, 80), fontFace = 4, fontScale = 3, color = (128,0,128), thickness = 3)
            else:
                cv2.putText(img, f"{self.win_status}",(70, 80), fontFace = 4, fontScale = 3, color = (128,0,128), thickness = 3)
            cv2.putText(img, "Play Again (Show Thumbs Up)",(70, 120), fontFace = 1, fontScale = 1, color = (128,0,128), thickness = 1)
            cv2.putText(img, "Exit (Show Five)",(400, 120), fontFace = 1, fontScale = 1, color = (128,0,128), thickness = 1)
                
        if self.out == True and self.replay == False and self.start == False:
            cv2.rectangle(img, (0, 120), (640,480), (220,220,220), cv2.FILLED)

            if self.end != True:
                cv2.putText(img, "OUT!!",(200, 260), fontFace = 4, fontScale = 3, color = (0,0,255), thickness = 3)

                if self.innings == 1:
                    cv2.putText(img, "INNINGS 2",(140, 380), fontFace = 4, fontScale = 2, color = (0,0,255), thickness = 3)
                elif self.innings == 2:
                    cv2.putText(img, "GAME OVER",(130, 380), fontFace = 4, fontScale = 2, color = (0,0,255), thickness = 3)

            elif self.end == True:
                cv2.putText(img, "GAME OVER",(30, 350), fontFace = 4, fontScale = 3, color = (0,0,255), thickness = 3)

        self.delay = delay

        return img
                