import OthelloAction
import OthelloLogic
import pyxel
import asyncio
import random
import time
import copy

# SCREEN
SCREEN_WIDTH = 200
SCREEN_HEIGHT = 130

class OthelloApp:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, caption="OthelloGUI", fps=60)
        pyxel.load("othelloGUI.pyxres")
        pyxel.mouse(True)
        self.size = 8
        self.othelloBoard = OthelloBoard(x=0,y=0,size=self.size)
        self.SCENE_TITLE = 0
        self.SCENE_PLAY = 1
        self.scene = self.SCENE_TITLE
        self.players = [0, 3] # 0:human, 1:randomAI, 2:KuriTaroAI
        self.players_list = ["player", "randomAI", "simpleAI", "KuriTaroAI"]
        #self.player1_com = False #1
        #self.player2_com = True #-1
        self.playing = False
        self.wait_input = True
        self.turn = 1 #1 or -1
        pyxel.run(self.update, self.draw)
        self.skip = [False, False]
        self.reset()
        
    def reset(self):
        self.playing = False
        self.wait_input = True
        self.turn = 1
        self.othelloBoard.reset()
        self.skip = [False, False]

    def update(self):
        if self.scene == self.SCENE_TITLE:
            if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
                self.scene = self.SCENE_PLAY
        elif self.scene == self.SCENE_PLAY:
            if self.playing == False:
                if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
                    self.startGame()
                if pyxel.btnp(pyxel.KEY_UP):
                    self.players[0] = (self.players[0] + 1) % len(self.players_list)
                if pyxel.btnp(pyxel.KEY_DOWN):
                    self.players[0] = (self.players[0] - 1) % len(self.players_list)
                if pyxel.btnp(pyxel.KEY_RIGHT):
                    self.players[1] = (self.players[1] + 1) % len(self.players_list)
                if pyxel.btnp(pyxel.KEY_LEFT):
                    self.players[1] = (self.players[1] - 1) % len(self.players_list)
            else:
                self.game()
            if pyxel.btnp(pyxel.KEY_Q):
                self.reset()
                self.scene = self.SCENE_TITLE
                
    
    def startGame(self):
        self.reset()
        self.wait_input = True
        self.turn = 1
        self.playing = True
    def game(self):
        if self.wait_input == False:
                self.wait_input = True
                self.turn *= -1
        if len(self.othelloBoard.getMoves(self.turn)) == 0:
            if True == self.skip[0] == self.skip[1]:
                self.playing = False
            if self.turn > 0:
                self.skip[0] = True
            elif self.turn < 0:
                self.skip[1] = True

            self.wait_input = False
            return
        else:
            self.passNum = 0
        #if self.player1_com if self.turn > 0 else self.player2_com == True:
        p = self.players[0] if self.turn > 0 else self.players[1]
        if p > 0:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.gather(self.action_AI(player=self.turn, AI_ID=p-1)))
            
        else:  
            self.action_Human(player=self.turn)

    def action_Human(self,player):
        if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
            input = self.othelloBoard.input(mouse_x=pyxel.mouse_x,mouse_y=pyxel.mouse_y,player=player)
            if input:
                self.wait_input = False
    async def action_AI(self,player,AI_ID):
        loop = asyncio.get_event_loop()
        moves = self.othelloBoard.getMoves(player=player)
        #index = random.randint(0,len(moves))
        _board = copy.deepcopy(self.othelloBoard.board)
        if self.turn < 0:
            _board = OthelloLogic.getReverseboard(_board)
        if AI_ID == 0:
            move = OthelloAction.getAction2(board=_board,moves=moves)
        elif AI_ID == 1:
            move = OthelloAction.getAction3(board=_board,moves=moves)
        elif AI_ID == 2:
            move = OthelloAction.getAction(board=_board,moves=moves)
        else:
            move=moves[0]
            print("Error")
        self.othelloBoard.execute(action=move,player=player)
        self.wait_input = False

    def draw(self):
        if self.scene == self.SCENE_TITLE:
            title = "Othello Arena GUI!"
            pyxel.cls(pyxel.COLOR_BLACK)
            pyxel.text(int(SCREEN_WIDTH - 4 * len(title)) / 2, SCREEN_HEIGHT / 2, title, pyxel.frame_count % 16)
        elif self.scene == self.SCENE_PLAY:
            pyxel.cls(pyxel.COLOR_DARKBLUE)
            self.othelloBoard.drawBoard(player=self.turn if self.playing and self.wait_input else 0)
            if self.playing == False:
                message = "Space to Play"
                pyxel.text(int(SCREEN_WIDTH - 4 * len(message)) / 2, SCREEN_HEIGHT / 2, message, pyxel.frame_count % 16)
            count = self.othelloBoard.count()
            x = SCREEN_WIDTH-65
            pyxel.text(x=x,y=10,s="black:{}\nscore:{}".format(self.players_list[self.players[0]],count[0]),col=pyxel.frame_count%16 if count[0]>count[1] else pyxel.COLOR_BLACK)
            pyxel.text(x=x,y=30,s="white:{}\nscore:{}".format(self.players_list[self.players[1]],count[1]),col=pyxel.frame_count % 16 if count[1] > count[0] else pyxel.COLOR_BLACK)
            pyxel.text(x=x,y=50,s="space:{}".format(self.othelloBoard.space()),col=pyxel.COLOR_BLACK)
            pyxel.text(x=SCREEN_WIDTH-30,y=SCREEN_HEIGHT-10,s="(Q)uit",col=pyxel.COLOR_BLACK)

class OthelloBoard:
    def __init__(self, x=0, y=0, size=8):
        self.x = x
        self.y = y
        self.size = size
        self.reset()
        self.IMG_SIZE = 16
    def reset(self):
        self.board = [[0 for i in range(self.size)] for j in range(self.size)]
        self.board[int(self.size/2)-1][int(self.size/2)-1] = 1
        self.board[int(self.size/2)][int(self.size/2)-1]=-1
        self.board[int(self.size/2)-1][int(self.size/2)]=-1
        self.board[int(self.size/2)][int(self.size/2)]=1
    def execute(self, action, player):
        moves = self.getMoves(player=player)
        check = False
        for m in moves:
            check = check or (action[0] == m[0] and action[1] == m[1])
        if check == False:
            print("Error")
            return False
        self.board = OthelloLogic.execute(board=self.board,action=action,player=player,size=len(self.board)) 
        return True
    def getMoves(self, player):
        return OthelloLogic.getMoves(board=self.board,player=player,size=len(self.board))
    def input(self, mouse_x, mouse_y, player):
        IMG_SIZE = self.IMG_SIZE
        for m in self.getMoves(player=player):
            if IMG_SIZE*m[1] <= mouse_x-self.x < IMG_SIZE*(m[1]+1) and IMG_SIZE*m[0] <= mouse_y-self.y < IMG_SIZE*(m[0]+1):
                return self.execute(action=m,player=player)
        return False
    def drawBoard(self, player=0):
        IMG_SIZE = self.IMG_SIZE
        for u in range(len(self.board)):
            for v in range(len(self.board[u])):
                p = self.board[u][v]
                pyxel.blt(x=IMG_SIZE*u+self.x,y=IMG_SIZE*v+self.y,img=0,u=IMG_SIZE*(p+1),v=0,w=IMG_SIZE,h=IMG_SIZE)
        if player == 0:
            return
        for m in OthelloLogic.getMoves(board=self.board,player=player,size=len(self.board)):
            p = self.board[m[1]][m[0]]
            pyxel.blt(x=IMG_SIZE*m[1]+self.x,y=IMG_SIZE*m[0]+self.y,img=0,u=IMG_SIZE*(p+1),v=IMG_SIZE,w=IMG_SIZE,h=IMG_SIZE)
    def count(self):
        c = [0, 0, 0]
        playerId = [1, -1]
        for p in range(2):
            for b1 in self.board:
                for b2 in b1:
                    c[2] += 1
                    if (b2 == playerId[p]):
                        c[p] += 1
        return c
    def space(self):
        s = 0
        for b1 in self.board:
            for b2 in b1:
                if b2 == 0:
                    s += 1
        return s

OthelloApp()