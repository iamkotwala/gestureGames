# import necessary libs
import cv2
from cvzone.HandTrackingModule import HandDetector


class VideoCamera(object):
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.mainobj = main(1)
        self.gameOn = True
    def __del__(self):
        self.cap.release()
    def get_frame(self):
        ret, frame = self.cap.read()
        processed_frame = cv2.flip(frame, 1)
        if self.gameOn == True:
            processed_frame = self.mainobj.mainLoop(processed_frame)
        if processed_frame == 'over':
            self.gameOn = False
            ret, frame = cv2.imencode('.jpg', frame)
            return frame.tobytes()

        if self.gameOn == False:
            #img = processed_frame
            cv2.rectangle(processed_frame, (0, 0), (640,480), (255,255,255), cv2.FILLED)
            #cv2.rectangle(processed_frame, (150, 80),(500, 150),(255, 255, 255), cv2.FILLED)
            cv2.rectangle(processed_frame, (150, 80),(500, 150),(50, 50, 50), 3)
            cv2.putText(processed_frame, "Game Over !!", (160, 120), cv2.FONT_HERSHEY_PLAIN,3, (50, 50, 50), 3)
            #processed_frame = img
        ret, frame = cv2.imencode('.jpg', processed_frame)
        return frame.tobytes()




'''
Improvements 
1. Tweek the game so that player has a chance to win. 
'''

# Note the function uses cvzone lib which in turn uses media pipe. 
# cvzone is used mainly to reduce the loc.

# Condition List 
# -1 -- Default condition 
#  0 -- Draw
#  1 -- Bot wins
#  2 -- Player wins

# Self.choice special variable.
#  0 -- Normal mode
#  1 -- Start a new Round.
#  2 -- Start a new game 
# Used to restart the game after each round and start a new game when start again button is clicked.


# Class which contains game logic.
class Game():

    def __init__(self):
        self.board = {1: ' ', 2: ' ', 3: ' ',
                      4: ' ', 5: ' ', 6: ' ',
                      7: ' ', 8: ' ', 9: ' '}
        self.player = 'O'
        self.bot = 'X'
        self.setCondition = -1
    
    def printBoard(self):
        print(self.board[1] + '|' + self.board[2] + '|' + self.board[3])
        print('-+-+-')
        print(self.board[4] + '|' + self.board[5] + '|' + self.board[6])
        print('-+-+-')
        print(self.board[7] + '|' + self.board[8] + '|' + self.board[9])
        print("\n")

    # Checks if list is empty at the given position
    def spaceIsFree(self,position):
        if self.board[position] == ' ':
            return True
        else:
            return False
    
    # Enter X or O on the board
    # Must connected with the UI Class
    def insertLetter(self,letter, position):
        if self.spaceIsFree(position):
            self.board[position] = letter
            if (self.checkDraw()):
                print("Draw!")
                self.printBoard()
                self.setCondition = 0
            if self.checkForWin():
                if letter == 'X':
                    print("Bot wins!")
                    self.printBoard()
                    self.setCondition = 1
                else:
                    print("Player wins!")
                    self.printBoard()
                    self.setCondition = 2
            return
        
    # All win conditions
    # Returns true if either player or bot wins the round.
    def checkForWin(self):
        if (self.board[1] == self.board[2] and self.board[1] == self.board[3] and self.board[1] != ' '):
            return True
        elif (self.board[4] == self.board[5] and self.board[4] == self.board[6] and self.board[4] != ' '):
            return True
        elif (self.board[7] == self.board[8] and self.board[7] == self.board[9] and self.board[7] != ' '):
            return True
        elif (self.board[1] == self.board[4] and self.board[1] == self.board[7] and self.board[1] != ' '):
            return True
        elif (self.board[2] == self.board[5] and self.board[2] == self.board[8] and self.board[2] != ' '):
            return True
        elif (self.board[3] == self.board[6] and self.board[3] == self.board[9] and self.board[3] != ' '):
            return True
        elif (self.board[1] == self.board[5] and self.board[1] == self.board[9] and self.board[1] != ' '):
            return True
        elif (self.board[7] == self.board[5] and self.board[7] == self.board[3] and self.board[7] != ' '):
            return True
        else:
            return False
    
    # To check if player won or computer
    def checkWhichMarkWon(self,mark):
        if self.board[1] == self.board[2] and self.board[1] == self.board[3] and self.board[1] == mark:
            return True
        elif (self.board[4] == self.board[5] and self.board[4] == self.board[6] and self.board[4] == mark):
            return True
        elif (self.board[7] == self.board[8] and self.board[7] == self.board[9] and self.board[7] == mark):
            return True
        elif (self.board[1] == self.board[4] and self.board[1] == self.board[7] and self.board[1] == mark):
            return True
        elif (self.board[2] == self.board[5] and self.board[2] == self.board[8] and self.board[2] == mark):
            return True
        elif (self.board[3] == self.board[6] and self.board[3] == self.board[9] and self.board[3] == mark):
            return True
        elif (self.board[1] == self.board[5] and self.board[1] == self.board[9] and self.board[1] == mark):
            return True
        elif (self.board[7] == self.board[5] and self.board[7] == self.board[3] and self.board[7] == mark):
            return True
        else:
            return False
    
    def checkDraw(self):
        for key in self.board.keys():
            if (self.board[key] == ' '):
                return False
        return True

    # Connect with Gesture input
    def playerMove(self,pos):
        self.insertLetter(self.player, pos)
        return
    
    def compMove(self):
        bestScore = -800
        bestMove = 0
        for key in self.board.keys():
            if (self.board[key] == ' '):
                self.board[key] = self.bot
                score = self.minimax(self.board, 0, False)
                self.board[key] = ' '
                if (score > bestScore):
                    bestScore = score
                    bestMove = key
        self.insertLetter(self.bot, bestMove)
        return



    # MinMax AI Algo used to find the best move for cmp.
    def minimax(self,board, depth, isMaximizing):
        if (self.checkWhichMarkWon(self.bot)):
            return 1
        elif (self.checkWhichMarkWon(self.player)):
            return -1
        elif (self.checkDraw()):
            return 0

        if (isMaximizing):
            bestScore = -800
            for key in board.keys():
                if (board[key] == ' '):
                    board[key] = self.bot
                    score = self.minimax(board, depth + 1, False)
                    board[key] = ' '
                    if (score > bestScore):
                        bestScore = score
            return bestScore
        else:
            bestScore = 800
            for key in board.keys():
                if (board[key] == ' '):
                    board[key] = self.player
                    score = self.minimax(board, depth + 1, True)
                    board[key] = ' '
                    if (score < bestScore):
                        bestScore = score
            return bestScore
    
# Class to draw board on the image.
class Board:
    def __init__(self, pos, width, height, value):
        self.pos = pos
        self.width = width # img Width
        self.height = height # img Height
        self.value = value # Text Value
    
    # Draws a square when called using the provided values. Also adds X or O as txt.
    def draw(self, img):
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                      (225, 225, 225), cv2.FILLED)
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                      (50, 50, 50), 3)
        cv2.putText(img, self.value, (self.pos[0] + 25, self.pos[1] + 80), cv2.FONT_HERSHEY_PLAIN,
                    5, (50, 50, 50), 5)

    # to check the position of index finger once the distance between middle finger and index finger < 40
    def checkClick(self, img, x, y):
        if self.pos[0] < x < self.pos[0] + self.width and self.pos[1] < y < self.pos[1] + self.height:
            cv2.rectangle(img, (self.pos[0] + 3, self.pos[1] + 3),
                          (self.pos[0] + self.width - 3, self.pos[1] + self.height - 3),
                          (255, 255, 255), cv2.FILLED)
            cv2.putText(img, self.value, (self.pos[0] + 25, self.pos[1] + 80), cv2.FONT_HERSHEY_PLAIN,
                        5, (0, 0, 0), 5)
            cv2.putText(img, "O", (self.pos[0] + 25, self.pos[1] + 80), cv2.FONT_HERSHEY_PLAIN,
                    5, (50, 50, 50), 5)
            return True
        else:
            return False
    
    # Func to avoid multiple entries in the same block.
    def warn(self, img, x, y):
        cv2.rectangle(img, (self.pos[0] + 3, self.pos[1] + 3),
                          (self.pos[0] + self.width - 3, self.pos[1] + self.height - 3),
                          (50, 50, 100), cv2.FILLED)

# Class which runs main loop.
class main():

    def __init__(self, noRounds):
        self.rounds = noRounds # Number of rounds for the game
        self.delayCounter = 0 # Program waits for a few frames if delayCounter is not 0
        self.myValue = -1 # Position of player mark
        self.retBoard = {1: 1, 2: 4, 3: 7,
                         4: 2, 5: 5, 6: 8,
                         7: 3, 8: 6, 9: 9}
        self.choice = 0 # Special variable
        self.cap = cv2.VideoCapture(0)
        self.detector = HandDetector(detectionCon=0.8, maxHands=1)
        self.game = Game()
        self.score = 0 # Increments in case of draw.
        self.botScore = 0 # Increments in case of cmp win.
        self.playerScore = 0 # Increments in case of player win.

    # Tracks score and restarts or begins a new game as needed.
    def restartGame(self):
        if self.game.setCondition == 0:
            self.score +=1
        elif self.game.setCondition == 1:
            self.botScore += 1
        elif self.game.setCondition == 2:
            self.playerScore +=1

        # To Restart game after 3 rounds. 
        # self.choice should be 2 so that score isnt affected.
        if self.choice == 1:
            self.rounds = 2
            self.playerScore = 0
            self.botScore = 0
            self.score = 0 
            game = Game()
            self.choice = 0
            return game
        elif self.choice == 2:
            self.choice = 1
            #game = Game()
            return 
        else:
            game = Game()
            return game
        # Init Board to 0
          
    # Draws UI -> Start Again and Quit Game at the end of 3 rounds.
    def newGame(self,img,txt):
        # Game Over!!
        cv2.rectangle(img, (150, 80),(500, 150),(255, 255, 255), cv2.FILLED)
        cv2.rectangle(img, (150, 80),(500, 150),(50, 50, 50), 3)
        cv2.putText(img, "Game Over !!", (160, 120), cv2.FONT_HERSHEY_PLAIN,3, (50, 50, 50), 3)
        # Who Wins
        cv2.putText(img, txt, (160, 200), cv2.FONT_HERSHEY_PLAIN,3, (255, 0, 0), 3)
        # Start Again
        cv2.rectangle(img, (80, 250),(310, 300),(255, 255, 255), cv2.FILLED)
        cv2.rectangle(img, (80, 250),(310, 300),(50, 50, 50), 3)
        cv2.putText(img, "Start Again", (90, 290), cv2.FONT_HERSHEY_PLAIN,2, (50, 50, 50), 2)
        # Quit Game
        cv2.rectangle(img, (400, 250),(590, 300),(255, 255, 255), cv2.FILLED)
        cv2.rectangle(img, (400, 250),(590, 300),(50, 50, 50), 3)
        cv2.putText(img, "Quit Game", (410, 290), cv2.FONT_HERSHEY_PLAIN,2, (50, 50, 50), 2)       
    
    
    # This loop is what keeps updating the frames.
    def mainLoop(self, img):
        #delayCounter = 0
        #while True:
        # Get image frame
        #success, img = self.cap.read()
        #img = cv2.flip(img, 1)
        hands, img = self.detector.findHands(img,flipType=False)

        # Draws board on each iter    
        cnt = 0
        tmp = [1,4,7,2,5,8,3,6,9]
        Blist = []
        for x in range(3):
            for y in range(3):
                xpos = x * 100 + 150
                ypos = y * 100 + 10
                Blist.append(Board((xpos, ypos), 100, 100, self.game.board[tmp[cnt]]))
                cnt+=1
        
        # loop to draw squares. 
        if not self.game.checkForWin() and self.rounds != -1:
                #print("no of rounds left: ",self.rounds)
                for box in Blist:
                    box.draw(img)

        # Checks for draw after a round.
        # Logic
        if self.delayCounter == 0 and self.game.checkDraw():
            if self.rounds>=1 and self.choice !=1:
                self.rounds -= 1
                self.game = self.restartGame()
                print(f'Your Score: {self.playerScore}\tComputer Score: {self.botScore}')
                self.delayCounter = 1      
            else:
                if self.rounds == 0:
                    self.choice = 2
                    print(f'Your Score: {self.playerScore}\tComputer Score: {self.botScore}')
                    self.restartGame()

                if self.score == 3:
                    txt = "It's a Draw."
                elif self.botScore >= 2:
                    txt = "Bot is a winner"
                elif self.playerScore >= 2:
                    txt = "Player is a winner"
                elif (self.score == 2) and (self.botScore == 1):
                    txt = "Bot is a winner"
                elif (self.score == 2) and (self.playerScore == 1):
                    txt = "Player is a winner"
                else:
                    txt = "It's a Draw!!  "+str(self.playerScore)+str(self.botScore)+str(self.score)
                self.newGame(img,txt)
                self.rounds = -1

        # checks for a win either player or comp after a round. 
        # Logic
        if self.delayCounter == 0 and self.game.checkForWin():
            if self.rounds>=1 and self.choice != 1:
                self.rounds -= 1
                self.game = self.restartGame()
                print(f'Your Score: {self.playerScore}\tComputer Score: {self.botScore}')
                self.delayCounter = 1
            else:
                self.choice = 2
                self.restartGame()
                print(f'Your Score: {self.playerScore}\tComputer Score: {self.botScore}')
                if self.score == 3:
                    txt = "It's a Draw."
                elif self.botScore >= 2:
                    txt = "Bot is a winner"
                elif self.playerScore >= 2:
                    txt = "Player is a winner"
                elif (self.score == 2) and (self.botScore == 1):
                    txt = "Bot is a winner"
                elif (self.score == 2) and (self.playerScore == 1):
                    txt = "Player is a winner"
                else:
                    txt = "It's a Draw!!  "+str(self.playerScore)+str(self.botScore)+str(self.score)
                self.newGame(img,txt)
        
        # Check for Hand
        # Logic
        if self.delayCounter == 0 and hands:
            # Find distance between fingers
            lmList = hands[0]['lmList']
            # finds the distance and also draws the landmarks on finger tips.
            length, _, img = self.detector.findDistance(lmList[8][:2], lmList[12][:2], img) 
            #print(length)
            x, y = lmList[8][:2]

            # If clicked check which button and perform action
            if self.choice == 0:
                if length < 40 and self.delayCounter == 0:
                    for i, box in enumerate(Blist):
                        if box.checkClick(img,x, y):
                            myValue = self.retBoard[i+1]
                            if self.game.board[myValue] == ' ':
                                self.game.playerMove(myValue)
                                self.delayCounter = 1
                                if not self.game.checkDraw():
                                    self.game.compMove()
                            else:
                                box.warn(img, x, y)
                                self.delayCounter = 1
            elif self.choice == 1:
                if length < 40:
                    # Start again
                    if (80 < x <310) and (250 < y < 300):
                        self.game = self.restartGame()
                        delayCounter = 1
                    # Quit
                    elif (400 < x < 590) and (250 < y < 300):
                        self.cap.release()
                        return 'over'
                        
        
        # to avoid multiple clicks
        if self.delayCounter != 0:
            self.delayCounter += 1
            if self.delayCounter > 40:
                self.delayCounter = 0

        # Display Video
        key = cv2.waitKey(1)
        #cv2.imshow("Tic Tac Toe", img)
        return img
        if key == ord('q'):
            self.cap.release()
            