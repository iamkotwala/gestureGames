# libs
import random
import cv2
import mediapipe as mp

class VideoCamera4(object):
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.mainobj = game()
    def __del__(self):
        self.cap.release()
    def get_frame(self):
        ret, frame = self.cap.read()
        processed_frame = self.mainobj.mainLoop(frame)
        ret, frame = cv2.imencode('.jpg', processed_frame)
        return frame.tobytes()

class game():
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.box_size = 300
        self.width = int(640)
        self.total_attempts = 5
        self.opp_choice_name= ""
        self.computer_score = 0
        self.user_score = 0
        self.rect_color = (255, 0, 0)
        self.user_move_name=""
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.delayCounter = 0 

    def condition_rock(self,ip,it,mp,mt,rp,rt,pp,pt):
        if (ip<it) and (mp<mt) and (rp<rt) and (pp<pt):
            return True
        return False

    def condition_paper(self,ip,it,mp,mt,rp,rt,pp,pt):
        if (ip>it) and (mp>mt) and (rp>rt) and (pp>pt):
            return True
        return False

    def condition_scissors(self,ip,it,mp,mt,rp,rt,pp,pt):
        if (ip>it) and (mp>mt) and (rp<rt) and (pp<pt):
            return True
        return False

    def calculate_winner(self,move1, move2):
        if move1 == move2:
            return "Tie"
        if move1 == "rock":
            if move2 == "scissors":
                return "User"
            if move2 == "paper":
                return "Computer"

        if move1 == "paper":
            if move2 == "rock":
                return "User"
            if move2 == "scissors":
                return "Computer"

        if move1 == "scissors":
            if move2 == "paper":
                return "User"
            if move2 == "rock":
                return "Computer"
    
    def display_computer_move(self, frame):
    
        #icon = cv2.imread( "G:/internship/rockgame{}.png".format(opp_choice_name), 1)
        #path = r""
        icon = cv2.imread( "gestureGames/static/{}.png".format(self.opp_choice_name), 1)
        icon = cv2.resize(icon, (224,224))
        
        # This is the portion which we are going to replace with the icon image
        roi = frame[0:224, 0:224]

        # Get binary mask from the transparent image, 4th channel is the alpha channel 
        mask = icon[:,:,-1] 

        # Making the mask completely binary (black & white)
        mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)[1]

        # Store the normal bgr image
        icon_bgr = icon[:,:,:3] 
        
        # Now combine the foreground of the icon with background of ROI 
        
        img1_bg = cv2.bitwise_and(roi, roi, mask = cv2.bitwise_not(mask))

        img2_fg = cv2.bitwise_and(icon_bgr, icon_bgr, mask = mask)

        combined = cv2.add(img1_bg, img2_fg)

        frame[0:224, 0:224] = combined

        return frame
    
    def user_move(self,roi):
        results = self.hands.process(cv2.cvtColor(self.roi,cv2.COLOR_BGR2RGB))
        self.user_move_name=""
        
            # checks if gesture is detected.
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:  
                hn = results.multi_hand_landmarks[0]
                
                ip = hn.landmark[6].y 
                it = hn.landmark[8].y 
                    
                mp = hn.landmark[10].y 
                mt = hn.landmark[12].y 
                    
                rp = hn.landmark[14].y 
                rt = hn.landmark[16].y 
                    
                pp = hn.landmark[18].y 
                pt = hn.landmark[20].y 
                    
                if(self.condition_rock(ip,it,mp,mt,rp,rt,pp,pt)):
                    self.user_move_name="rock"
                elif(self.condition_paper(ip,it,mp,mt,rp,rt,pp,pt)):
                    self.user_move_name="paper"
                elif(self.condition_scissors(ip,it,mp,mt,rp,rt,pp,pt)):
                    self.user_move_name="scissors"
                else:
                    self.user_move_name = "  "
        return self.user_move_name
    
    def display_details(self,frame,mode,user_score,computer_score):
        font = cv2.FONT_HERSHEY_SIMPLEX
        tmp = self.total_attempts
        
        cv2.putText(frame, "Your Score: " + str(user_score),(380, 325), font, 0.7, (250, 250, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, "Computer Score: " + str(computer_score),(2, 325), font, 0.7, (250,250, 0), 2, cv2.LINE_AA)
        
        if mode == 1:
            tmp = 0
            if user_score > computer_score:
                cv2.putText(frame,"Result: User won!!",(200, 400), font, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
            elif user_score < computer_score:
                cv2.putText(frame,"Result: Computer won!!",(200, 400), font, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
            else:
                cv2.putText(frame,"Result: Oops!!Tie",(200, 400), font, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
        if tmp>0:
            cv2.putText(frame, "Attempts left: {}".format(tmp), (190, 450), font, 0.7,(100, 2, 200), 2, cv2.LINE_AA)
        return frame
    
    def mainLoop(self,frame):
        # Main Loop
        with self.mp_hands.Hands(static_image_mode = True,max_num_hands=1,min_detection_confidence=0.5) as self.hands:
            #while(cap.isOpened()):
            #ret,frame=cap.read()
            frame = cv2.flip(frame, 1)
            # rectangle for user to play
            cv2.rectangle(frame, (self.width - self.box_size, 0), (self.width, self.box_size), self.rect_color, 2)
            
            # extract the region of image within the user rectangle

            self.roi = frame[5: self.box_size-5 , self.width-self.box_size + 5: self.width -5]

            #cv2.rectangle(roi, (400, 0), (700, 300), rect_color, 2)
            cv2.namedWindow("Rock Paper Scissors", cv2.WINDOW_NORMAL)
            self.user_move_name=self.user_move(self.roi)
            # Performs computer moves and tracks scores
            if self.delayCounter == 0 and (self.user_move_name =="rock" or self.user_move_name =="paper" or self.user_move_name =="scissors"):
                if self.total_attempts>0:  
                    self.delayCounter = 12
                    # Display the computer's move
                    opp_choice = random.randint(1, 3)
                    if opp_choice == 1:
                        self.opp_choice_name = 'rock'
                    elif opp_choice == 2:
                        self.opp_choice_name = 'paper'
                    elif opp_choice == 3:
                        self.opp_choice_name = 'scissors'
                
                    self.winner=self.calculate_winner(self.user_move_name, self.opp_choice_name)
                    # At each iteration we will decrease the total_attempts value by 1
                    # Subtract one attempt
                    self.total_attempts -= 1
                    # If winner is computer then it gets two points and vice versa.
                    # We're also changing the color of rectangle based on who wins the round.
                    #display_computer_move(opp_choice_name, frame)

                    if self.winner == "Computer":
                        self.computer_score +=2
                        self.rect_color = (0, 0, 255)
                    elif self.winner == "User":
                        self.user_score += 2
                        self.rect_color = (0, 250, 0)                
                    elif self.winner == "Tie":
                        self.computer_score += 1
                        self.user_score += 1
                        self.rect_color = (255, 250, 255)
                    

            # Skips frames so that user has time to change gesture. 
            if self.delayCounter != 0:
                self.delayCounter -= 1
                
                if 15>self.delayCounter>1:
                    self.display_computer_move(frame)
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    self.user_move_name=self.user_move(self.roi)
                    cv2.putText(frame, "Your Move: " + self.user_move_name,(380, 270),font, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(frame, "Computer's Move: " + self.opp_choice_name,(2, 270), font, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
                    
                if self.total_attempts>=0:
                    cv2.putText(frame, "Winner: " + self.winner,(200, 350), self.font, 0.8, (0, 0, 255), 2, cv2.LINE_AA)

                if self.delayCounter <1:
                   self.delayCounter = 0

            if self.total_attempts>0 and self.delayCounter==0:
                cv2.putText(frame, "Show Your move : ",(350, 100), self.font, 0.7, (250, 0, 0), 2, cv2.LINE_AA)

            # display game information  
            if self.total_attempts>0:

                frame=self.display_details(frame,0,self.user_score,self.computer_score)    
            else:
                frame=self.display_details(frame,1,self.user_score,self.computer_score)
                cv2.putText(frame, "Do you want to play again(y/n) : ",(90, 450), self.font, 1, (0, 0, 250), 2, cv2.LINE_AA)

            
            #cv2.imshow("Rock Paper Scissors", frame)
            if cv2.waitKey(2) & 0xFF == ord('y'):
                self.total_attempts=5
                self.computer_score=0
                self.user_score=0
            #elif cv2.waitKey(2) & 0xFF == (ord('q') or ord('n')):
                #break
                #cap.release()
            return frame
