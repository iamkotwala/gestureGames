#Importing necessary libraries
import mediapipe as mp
import cv2
import random
import os

# Class of Finer Recognition
class FingerRecognition:

    def __init__(self):
        self.mp_hands = mp.solutions.hands   #Initializing mediapipe hands class
        
        self.mp_drawing = mp.solutions.drawing_utils  #Initializing mediapipe drawing class

        #Setting up hand functions for video
        self.hands_video = self.mp_hands.Hands(static_image_mode = False, max_num_hands = 1, 
                                                min_detection_confidence = 0.8, min_tracking_confidence = 0.8)

    
    def detectHandLandmarks(self, img, draw = False, display = True):
        output = img.copy()    # Image Copy for output
        
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) #Converting from BGR to RGB format
        
        results = self.hands_video.process(imgRGB)    #Image Processing
        
        #If hands are found draw handlandmarks on copy of input image
        
        if results.multi_hand_landmarks and draw:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(image = output, landmark_list = hand_landmarks,
                                        connections =self. mp_hands.HAND_CONNECTIONS,
                                        landmark_drawing_spec = self.mp_drawing.DrawingSpec(color = (255,255,255), thickness = 2, circle_radius = 2),
                                        connection_drawing_spec = self.mp_drawing.DrawingSpec(color = (0,255,0), thickness = 2, circle_radius = 2))
        return(output, results)    #Returning the output image

    def countFingers(self, img, results, computer, start, replay, draw = True, display = True):
    
        height, width, _ = img.shape    
        output = img.copy()

        finger_count = 0
        thumbs_down = False

        #Obtaining the finger Tip Id's and finger Mcp Id's

        finger_tips_ids = [self.mp_hands.HandLandmark.INDEX_FINGER_TIP, self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                        self.mp_hands.HandLandmark.RING_FINGER_TIP, self.mp_hands.HandLandmark.PINKY_TIP]   

        finger_mcp_ids = [self.mp_hands.HandLandmark.INDEX_FINGER_MCP, self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP,
                        self.mp_hands.HandLandmark.RING_FINGER_MCP]     

        #Setting finger status to false, and changing it to true when finger opens.
        finger_status = {'THUMB' : False, 'INDEX' : False, 'MIDDLE' : False, 'RING' : False, 'PINKY' : False}


        for hand_index, hand_info in enumerate(results.multi_handedness):
            hand_label = hand_info.classification[0].label
            hand_landmarks = results.multi_hand_landmarks[hand_index]

            #Function to obtain the difference between the mcp values of fingers.

            '''
            Note : If fingers are open in vertical direction, then the difference of y coordinates between the mcp values of the 
            fingers will be less than or equal to 0.02, and difference between x coordinates will be greater than 0.02. 
            It will be vice versa if the fingers are open in horizontal direction.
            Hence to check the direction of the fingers, the below steps are performed.

            '''
            def diff(lists):     
                diff_list = []
                for i in range(1,len(lists)):
                    diff_list.append(abs(round(lists[i] - lists[i-1],2)))
                return diff_list

            mcp_x_values, mcp_y_values = [], []

            for mcp_index in finger_mcp_ids:
                mcp_x_values.append(round(hand_landmarks.landmark[mcp_index].x,2))
                mcp_y_values.append(round(hand_landmarks.landmark[mcp_index].y,2))

            from statistics import mean   
            x = mean(diff(mcp_x_values))
            y = mean(diff(mcp_y_values))


            '''
            Note: x coordinate values are greater in the right and lesser in left. 
                y coordinate values are greater at the bottom and lesser at the top.
            '''

            if x <= 0.02:    # If fingers are in horizontal direction
                for tip_index in finger_tips_ids:

                    wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST].x

                    finger_name = tip_index.name.split('_')[0]


                    if ((wrist > hand_landmarks.landmark[tip_index].x) and (hand_landmarks.landmark[tip_index].x < hand_landmarks.landmark[tip_index - 2].x)) or ((wrist < hand_landmarks.landmark[tip_index].x) and (hand_landmarks.landmark[tip_index].x > hand_landmarks.landmark[tip_index - 2].x)):
                        finger_status[finger_name] = True
                        finger_count += 1

                thumb_tip_x = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP].y
                thumb_mcp_x = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP - 2].y      


                if (thumb_tip_x < thumb_mcp_x):
                    finger_status['THUMB'] = True
                    finger_count += 1

            else:
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

        # Obtaining only necessary finger counts
        
        fingers = []
        count = finger_count
        
        for finger,flag in finger_status.items():   #Finding fingers that are open
            if finger_status[finger] == True:
                fingers.append(finger)
        
        if x <= 0.02:    # If fingers are in horizontal direction
            if count == 1 and fingers == ['THUMB']:
                final_count = 6
            else:
                final_count = None
        else:             # If fingers are in vertical direction
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

        folderPath = "resources"
        my_list = os.listdir(folderPath)
        overlay = []

        for impath in my_list:
            image = cv2.imread(f'{folderPath}/{impath}')
            overlay.append(image)

        pic = overlay[computer - 1]  
        # pic = f'{folderPath}/{computer}.jpg'
        # pic = ImageProcessing.convertImage(pic)

        if final_count !=  None:
        
            if start == False and replay == False:
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
            elif start == True or replay == True:
                cv2.putText(output, "",(430, 180), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,0), 2)

        return output, finger_count, final_count

class Game:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)    #access webcam 
        self.run = []
        self.target = 0
        self.current = 0
        self.innings = 1
        self.status = ""
        self.win_status = ""
        self.replay = False
        self.thumbs_down = False
        self.thumbs_up = False
        self.start = True
    
    def play(self):
        delay = 0
        text = ""
        computer = random.randint(1, 6)
        finger = FingerRecognition()

        while True:
            ret, img = self.cap.read()     # read the image
        
            img = cv2.flip(img, 1)    #Flipping the image
 
            icon = cv2.imread('1-6.jpg')
            icon = cv2.resize(icon, (640,120))
            img[0:120, 0:] = icon

            font_style = cv2.FONT_HERSHEY_PLAIN
            user = None
                    
            if delay >= 0 and delay <= 20:
                text = "Ready?"
            elif delay < 40:
                text = "Set!"
            elif delay < 85:
                text = "Show your run now!"
                img, results = finger.detectHandLandmarks(img, draw = False, display = True)  #Detecting hand landmarks

                if results.multi_hand_landmarks:   #Counting the fingers
                    img, finger_count, final_count = finger.countFingers(img, results, computer, start = self.start, replay = self.replay, draw = True, display = True) 

                    if final_count != None:
                        text = ""
                        user = final_count
                        if computer == final_count:
                            txt = "stop"
                        else: 
                            txt = 'playing'
                        self.run = [final_count, computer, txt]
            
            elif delay < 100:
                if user == None:
                    text = "You missed it...Try again!!"
            
            delay = (delay + 1) % 100     

            if self.win_status == '':
                if self.start == True:
                    text = "   "
                    cv2.rectangle(img, (0, 0), (640,150), (220,220,220), cv2.FILLED)
                    cv2.putText(img, "Gesture Cricket",(50, 70), fontFace = 4, fontScale = 2, color = (106,51,170), thickness = 3)
                    cv2.putText(img, "Do you choose Batting or Bowling?",(30, 110), fontFace = 1, fontScale = 2, color = (106,51,170), thickness = 1)
                    cv2.putText(img, "Batting (Show 1)",(60, 140), fontFace = 1, fontScale = 1, color = (106,51,170), thickness = 1)
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
                cv2.putText(img, f"{self.win_status}",(70, 80), fontFace = 4, fontScale = 3, color = (128,0,128), thickness = 3)
                cv2.putText(img, "Try Again (Show Thumbs Up)",(60, 120), fontFace = 1, fontScale = 1, color = (128,0,128), thickness = 1)
                cv2.putText(img, "Exit (Show Five)",(380, 120), fontFace = 1, fontScale = 1, color = (128,0,128), thickness = 1)
                    
            if  user == computer and self.replay == False and self.start == False:
                cv2.rectangle(img, (0, 190), (640,400), (220,220,220), cv2.FILLED)
                cv2.putText(img, "OUT!!",(230, 280), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 3)

                if self.innings == 1:
                    cv2.putText(img, "INNINGS 2",(170, 380), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 3)
                elif self.innings == 2:
                    cv2.rectangle(img, (0, 400), (640,480), (220,220,220), cv2.FILLED)
                    cv2.putText(img, "GAME OVER",(170, 380), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 3)

            cv2.imshow('Hand Cricket', img)

            temp = 0
            while(temp < 10000 and user == computer):
                temp += 1
                text = " "
            
            if delay == 80 and self.run != []:
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):          #Closing web cam if key q is pressed.
                self.cap.release()
                break

    def game_main(self):

        def HandCricket(batting, innings, target):
                current = 0
                self.current= current
                
                if innings == 1:  
                    print("\nINNINGS 1 : \n")
                    print("CURRENT SCORE : ", current, "\n")
                    self.play()

                    if self.run != []:
                        runs = self.run
                        self.run = []

                        while(runs[2] != "stop"):
                            print("Your Run : ", runs[0], "\t\tOpponents Run : ", runs[1], "\n")

                            if batting != "COMPUTER":
                                current += runs[0]
                                self.current= current
                            else: 
                                current += runs[1]
                                self.current= current
                            print("CURRENT SCORE : ", current, "\n")
                            self.play()
                            if self.run != []:
                                runs = self.run
                                self.run = []
                            
                        if runs[2] == 'stop':
                            print("Your Run : ", runs[0], "\t\tOpponents Run : ", runs[1], "\n")
                            print("\nOUT!!")
                        return(current)

                elif innings == 2:
                    print("\nINNINGS 2 : \n")
                    print("\nTARGET SCORE : ", target, "\t\t", "CURRENT SCORE : ", current, "\n")

                    if batting != "COMPUTER":
                        while(current < target):
                            self.play()
                            if self.run != []:
                                runs = self.run
                                self.run = []

                                print("Your Run : ", runs[0], "\t\tOpponents Run : ", runs[1], "\n")

                                if runs[2] == "stop":
                                    print("\nOUT!!")
                                    return(current)

                                current += runs[0]
                                self.current= current
                                print("TARGET SCORE : ", target, "\t\t", "CURRENT SCORE : ", current, "\n")
                        return(current)
                    else:
                        while(current < target):
                            self.play()
                            if self.run != []:
                                runs = self.run
                                self.run = []
                                print("Your Run : ", runs[0], "\t\tOpponents Run : ", runs[1], "\n")

                                if runs[2] == "stop":
                                    print("\nOUT!!")
                                    return(current)

                                current += runs[1]
                                self.current= current
                                print("TARGET SCORE : ", target, "\t\t", "CURRENT SCORE : ", current, "\n")
                        return(current)
    
        flag = True

        while flag:
            self.win_status = ""
            self.replay = False

            ch = 0
            while(ch == 0):
                self.play()
                if self.run[0] == 1:
                    ch = 1
                    break
                elif self.run[0] == 2:
                    ch = 2
                    break
                else:
                    pass

            self.run = []
            self.start = False
            player = 'SELF'
        
            innings = 1
            target = 0

            if ch == 1:
                self.status = "You Bat"
                print("\nYou Bat!!")
                user_score = HandCricket(player, innings, target)
                target = user_score + 1
                innings += 1
                self.innings = innings
                self.status = "You Bowl"
                self.target = target
                comp_score = HandCricket("COMPUTER", innings, target)

                print("GAME OVER!!!")   
                if comp_score >= target:
                    txt = 'You Lose!'
                    print("\nYou Lose.")
                elif comp_score == user_score:
                    txt = 'Match is a Tie'
                    print("\nMatch is a Tie.")
                else:
                    txt = 'You Win!!'
                    print("\nYou Win!!")
                self.win_status = txt
                
            elif ch == 2:
                self.status = "You Bowl"
                print("\nYou Bowl!!")
                comp_score = HandCricket("COMPUTER", innings, target)
                target = comp_score + 1
                innings += 1
                self.innings = innings
                self.status = "You Bat"
                self.target = target
                user_score = HandCricket(player, innings, target)

                print("GAME OVER!!!") 
                if user_score >= target:
                    txt = 'You Win!!'
                    print("\nYou Win!!")
                elif comp_score == user_score:
                    txt = 'Match is a Tie'
                    print("\nMatch is a Tie.")
                else:
                    txt = 'You Lose!'
                    print("\nYou Lose.")
                self.win_status = txt

            self.replay = True

            ch = 0
            while(ch == 0):
                self.play()
                if self.run[0] == 5:
                    ch = 1
                    flag = False
                    self.cap.release()
                    break
                elif self.run[0] == 6:
                    ch = 2
                    self.win_status = ''
                    self.start = True
                    self.run = []
                    self.target = 0
                    self.current = 0
                    self.innings = 1
                    self.replay = False

        cv2.destroyAllWindows()
        
if __name__ == "__main__":
    game = Game()
    game.game_main()
    