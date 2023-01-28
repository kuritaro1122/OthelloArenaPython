from concurrent.futures import process
from multiprocessing.connection import wait
from telnetlib import STATUS
from typing import overload
import OthelloAction
import OthelloLogic
import pyxel
import copy
import PyxelButton as pb
import numpy as np
import PyxelSceneManager as pcm
import time
#import requests
import json
import AuthCheck
from AsyncFunction import AsyncFunctionManager as afm

# SCREEN
SCREEN_WIDTH = 200
SCREEN_HEIGHT = 130 #130*3
SCENE_TITLE = 0
SCENE_PLAY = 1

class Scenes:
    SCENE_TITLE = 0
    SCENE_LOCALPLAY = 1
    #SCENE_OTHELLOARENA = 2
    #SCENE_LEAGUE = 3
    #SCENE_HISTORY = 4
    SCENE_LEAGUE = 2
    SCENE_HISTORY = 3

class App(pcm.BaseSceneManager):
    def __init__(self):
        pyxel.init(width=SCREEN_WIDTH,height=SCREEN_HEIGHT,title="Othello GUI",fps=60)
        pyxel.load("othelloGUI.pyxres")
        pyxel.mouse(True)
        #super().__init__(scenes=[Scene_Title(),Scene_LocalPlay(),Scene_OthelloArena(),Scene_League(),Scene_History()],beginIndex=0)
        super().__init__(scenes=[Scene_Title(),Scene_LocalPlay(),Scene_League(),Scene_History()],beginIndex=0)
        pyxel.run(super().update, super().draw)

class Scene_Title(pcm.BaseScene):
    def start(self):
        pass
    def update(self):
        if pyxel.btnr(pyxel.KEY_SPACE) or pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
            self.loadScene(Scenes.SCENE_LOCALPLAY)
        #if pyxel.btnr(pyxel.KEY_2):
        #    self.loadScene(Scenes.SCENE_OTHELLOARENA)
    def draw(self):
        title = "Othello Arena GUI!"
        pyxel.cls(pyxel.COLOR_BLACK)
        pyxel.text(int(SCREEN_WIDTH - 4 * len(title)) / 2, SCREEN_HEIGHT / 2, title, pyxel.frame_count % 16)

class Scene_LocalPlay(pcm.BaseScene):
    def __init__(self):
        self.othelloBoard = OthelloBoard(x=0,y=0,size=8)
        self.players = [0, 3]
        self.players_list = ["player", "randomAI", "simpleAI", "KuriTaroAI"]
        self.reset()
        button_quit:pb.BaseButton = pb.TextButton(x=SCREEN_WIDTH-30,y=SCREEN_HEIGHT-10,s="(Q)uit",col=pyxel.COLOR_BLACK,func=lambda:self.loadScene(Scenes.SCENE_TITLE))
        def count():
            return self.othelloBoard.count()
        button_black:pb.BaseButton = pb.TextButtonPro(x=SCREEN_WIDTH-65,y=1,s=lambda:"black:{}".format(self.players_list[self.players[0]]),col=lambda:pyxel.frame_count%16 if count()[0]>count()[1] else pyxel.COLOR_BLACK,func=lambda:self.changeBlack())
        button_white:pb.BaseButton = pb.TextButtonPro(x=SCREEN_WIDTH-65,y=21,s=lambda:"white:{}".format(self.players_list[self.players[1]]),col=lambda:pyxel.frame_count%16 if count()[0]<count()[1] else pyxel.COLOR_BLACK,func=lambda:self.changeWhite())
        self.buttonManager = pb.ButtonManager(buttons=[[button_quit,lambda:True,[pyxel.KEY_Q]],[button_black,lambda:self.playing==False,[]],[button_white,lambda:self.playing==False,[]]])
    def start(self):
        self.reset()
    def update(self):
        if self.playing == False:
            if pyxel.btnp(pyxel.KEY_UP):
                self.changeBlack(add=1)
            if pyxel.btnp(pyxel.KEY_DOWN):
                self.changeBlack(add=-1)
            if pyxel.btnp(pyxel.KEY_RIGHT):
                self.changeWhite(add=1)
            if pyxel.btnp(pyxel.KEY_LEFT):
                self.changeWhite(add=-1)
            boardEndPos = self.othelloBoard.size*self.othelloBoard.IMG_SIZE
            if pyxel.btnp(pyxel.KEY_SPACE) or (pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and (0<pyxel.mouse_x<boardEndPos and 0<pyxel.mouse_y<boardEndPos)):
                self.startGame()
        else:
            self.game()
        self.buttonManager.update()
    def draw(self):
        pyxel.cls(pyxel.COLOR_DARK_BLUE)
        self.othelloBoard.drawBoard(player=self.turn,showPut=self.playing and self.players[0 if self.turn == 1 else 1] == self.players_list.index("player"))
        self.othelloBoard_historys.drawBoard(index=1,num=1,x=SCREEN_WIDTH-8*8,y=SCREEN_HEIGHT-8*8-15,offset=-1)
        x = SCREEN_WIDTH-65
        count =  self.othelloBoard.count()
        if self.playing:
            pyxel.text(x=SCREEN_WIDTH-65,y=1,s="black:{}".format(self.players_list[self.players[0]]),col=pyxel.frame_count%16 if count[0]>count[1] else pyxel.COLOR_BLACK)
            pyxel.text(x=SCREEN_WIDTH-65,y=21,s="white:{}".format(self.players_list[self.players[1]]),col=pyxel.frame_count%16 if count[0]<count[1] else pyxel.COLOR_BLACK)
        pyxel.text(x=x,y=7,s="score:{}".format(count[0]),col=pyxel.frame_count%16 if count[0]>count[1] else pyxel.COLOR_BLACK)
        pyxel.text(x=x,y=27,s="score:{}".format(count[1]),col=pyxel.frame_count % 16 if count[1] > count[0] else pyxel.COLOR_BLACK)
        pyxel.text(x=x,y=41,s="space:{}".format(self.othelloBoard.space()),col=pyxel.COLOR_BLACK)
        if self.playing == False:
            pyxel.text(x=int(SCREEN_WIDTH-4*len("Click to Play"))/2,y=SCREEN_HEIGHT/2,s="Click to Play",col=pyxel.frame_count%16)
        self.buttonManager.draw()
    def reset(self):
        self.STEP_BEFORE = 0
        self.STEP_DURING = 1
        self.STEP_AFTER = 2
        self.playing = False
        self.wait_input = True
        self.step = self.STEP_BEFORE
        self.turn = 1
        self.othelloBoard.reset()
        self.othelloBoard_historys = BoardHistoryList(size=3)
        self.skip = [False, False]
    def startGame(self):
        self.reset()
        self.playing = True
    def game(self):
        if self.step == self.STEP_AFTER:
                self.step = self.STEP_BEFORE
                self.turn *= -1
                self.othelloBoard_historys.push(self.othelloBoard.board, self.othelloBoard.lastPut)
        if len(self.othelloBoard.getMoves(self.turn)) == 0:
            if True == self.skip[0] == self.skip[1]:
                self.playing = False
            if self.turn > 0:
                self.skip[0] = True
            elif self.turn < 0:
                self.skip[1] = True
            self.step = self.STEP_AFTER
            return
        else:
            self.skip[0] = self.skip[1] = False
        p = self.players[0] if self.turn > 0 else self.players[1]
        if p > 0:
            if self.step == self.STEP_BEFORE:
                self.step = self.STEP_DURING
                #print("AI")
                func = lambda : self.action_AI(player=self.turn,AI_ID=p-1)
                afm().createAsyncFunc(func=func)
        else:
            if self.step == self.STEP_BEFORE:
                self.action_Human(player=self.turn)
    def action_Human(self,player):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            input = self.othelloBoard.input(mouse_x=pyxel.mouse_x,mouse_y=pyxel.mouse_y,player=player)
            if input:
                self.step = self.STEP_AFTER

    def action_AI(self,player,AI_ID): #重たい処理
        #print("AI begin")
        moves = self.othelloBoard.getMoves(player=player)
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
        #time.sleep(4)
        move = moves[0]
        self.othelloBoard.execute(action=move,player=player)
        self.step = self.STEP_AFTER
        #print("AI end")

    def changeBlack(self, add:int = 1):
        self.players[0] = (self.players[0] + add) % len(self.players_list)
    def changeWhite(self, add:int = 1):
        self.players[1] = (self.players[1] + add) % len(self.players_list)

class ProcessStatus:
    WAIT = 0
    RUNNING = 1
    FINISH = 2

"""
class Scene_OthelloArena(pcm.BaseScene):
    def __init__(self):
        #self.connected = False
        #self.boardLoaded = False
        #self.action_running = False
        self.flag_connectArena = ProcessStatus.WAIT
        #self.flag_loadBoard = loadStatus.WAIT
        self.flag_action = ProcessStatus.WAIT
        self.size = 8
        self.othelloBoard = OthelloBoard(x=0,y=0,size=self.size)
        self.data = []
        self.roomid = ''
        self.payload = {}
        self.moves = []
        self.action = {}
        self.board_reverse = False
        self.player = -1
        #self.prevBoard = [[0 for i in range(self.size)] for j in range(self.size)]
        #self.prevAction = [-1,-1]
        #self.step

    def start(self):
        #self.connected = False
        pass
    def update(self):
        if self.flag_connectArena == ProcessStatus.WAIT:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.flag_connectArena = ProcessStatus.RUNNING
                afm().createAsyncFunc(func=self.requestArena)
        elif self.flag_connectArena == ProcessStatus.FINISH:
            if self.flag_action == ProcessStatus.WAIT:
                self.flag_action = ProcessStatus.RUNNING
                afm().createAsyncFunc(func=self.loadBoard)
                #self.loadBoard()
        if self.flag_action == ProcessStatus.FINISH:
            self.flag_action = ProcessStatus.WAIT

    def getAction(self, board, moves):
        time.sleep(3)
        return moves[0]

    def loadBoard(self):
        print("打った場所は" + str(self.action), self.player)
        print("")
        r = requests.post(self.base_url + "room/" + self.roomid, data=self.payload,headers=self.headers)
        if(r.status_code == 401):
            print('loadBoard 認証エラーが起きました。')
            self.flag_connectArena = ProcessStatus.WAIT
            self.flag_action = ProcessStatus.WAIT
            return
        if(r.status_code != requests.codes.ok):
            print('loadBoard エラーが発生しました。')
            self.flag_connectArena = ProcessStatus.WAIT
            self.flag_action = ProcessStatus.WAIT
            return
        self.data = r.json()
        try:
            if(self.data['finish_flag']):
                print('loadBoard 処理が終了しました。')
                self.flag_connectArena = ProcessStatus.WAIT
                self.flag_action = ProcessStatus.WAIT
                return
        except KeyError:
            print("KeyError Exception")
            self.flag_connectArena = ProcessStatus.WAIT
            self.flag_action = ProcessStatus.WAIT
            return
        OthelloLogic.printBoard(json.loads(self.data['board']))
        if self.player == -1:
            rev_board = json.loads(self.data['board'])
            board = json.loads(self.data['board'])
            for x in range(len(rev_board)):
                for y in range(len(rev_board)):
                    board[x][y] = rev_board[x][y] * -1
        else:
            board = json.loads(self.data['board'])
        moves = json.loads(self.data['moves'])
        self.othelloBoard.setBoard(board)
        self.action = self.getAction(board,moves=moves)
        action = json.dumps(self.action)
        self.payload = {'action' : action, 'player':self.player}
        
        print("next")
        nextBoard = OthelloLogic.execute(board,self.action,self.player,self.size)
        OthelloLogic.printBoard(nextBoard)
        self.othelloBoard.setBoard(nextBoard)
        self.flag_action = ProcessStatus.FINISH

    def draw(self):
        pyxel.cls(pyxel.COLOR_DARKBLUE)
        self.board_reverse = self.player == 1
        self.othelloBoard.drawBoard(player=0, showPut=False, reverse=self.board_reverse)
        #self.othelloBoard_historys.drawBoard(index=1,num=1,x=SCREEN_WIDTH-8*8,y=SCREEN_HEIGHT-8*8-15,offset=-1)
        x = SCREEN_WIDTH-65
        count =  self.othelloBoard.count()
        #if self.connected:
        pyxel.text(x=SCREEN_WIDTH-65,y=1,s="black:{}",col=pyxel.frame_count%16 if count[0]>count[1] else pyxel.COLOR_BLACK)
        pyxel.text(x=SCREEN_WIDTH-65,y=21,s="white:{}",col=pyxel.frame_count%16 if count[0]<count[1] else pyxel.COLOR_BLACK)
        pyxel.text(x=x,y=7,s="score:{}".format(count[0]),col=pyxel.frame_count%16 if count[0]>count[1] else pyxel.COLOR_BLACK)
        pyxel.text(x=x,y=27,s="score:{}".format(count[1]),col=pyxel.frame_count % 16 if count[1] > count[0] else pyxel.COLOR_BLACK)
        pyxel.text(x=x,y=41,s="space:{}".format(self.othelloBoard.space()),col=pyxel.COLOR_BLACK)
        if self.flag_connectArena == ProcessStatus.WAIT:
            message = "Click to Connect OthelloArena"
            pyxel.text(x=int(SCREEN_WIDTH-4*len(message))/2,y=SCREEN_HEIGHT/2,s=message,col=pyxel.frame_count%16)
        #self.buttonManager.draw()
        pass

    def requestArena(self):
        self.base_url = "http://tdu-othello.xyz/api/"
        self.headers = AuthCheck.auth_check(base_url=self.base_url)
        r = requests.post(url=self.base_url + "where", headers=self.headers)
        if r.status_code == 422:
            message = r.json()
            print(message['message'])
            self.flag_connectArena = ProcessStatus.WAIT
            self.flag_action = ProcessStatus.WAIT
            return
        if r.status_code != requests.codes.ok:
            print('requestArena エラーが発生しました。')
            self.flag_connectArena = ProcessStatus.WAIT
            self.flag_action = ProcessStatus.WAIT
            return
        self.data = r.json()
        self.roomid = self.data['id']
        self.player = self.data['player']
        board = []
        self.payload = {}
        if self.player == 1:
            self.payload = {'player':self.player}
            r = requests.post(self.base_url + "wait_for_player/" + self.roomid, data=self.payload,headers=self.headers)
            self.data = r.json()
            OthelloLogic.printBoard(json.loads(self.data['board']))
            board = json.loads(self.data['board'])
            moves = json.loads(self.data['moves'])
        else:
            OthelloLogic.printBoard(json.loads(self.data['board']))
            rev_board = json.loads(self.data['board'])
            board = json.loads(self.data['board'])
            for x in range(len(rev_board)):
                for y in range(len(rev_board)):
                    board[x][y] = rev_board[x][y] * -1
            moves = json.loads(self.data['moves'])
        self.othelloBoard.setBoard(board)
        self.moves = moves
        self.action = self.getAction(board,moves)
        action_ = json.dumps(self.action)
        self.payload = {'action' : action_,'player':self.player}
        print("next")
        nextBoard = OthelloLogic.execute(board,self.action,self.player,self.size)
        OthelloLogic.printBoard(nextBoard)
        self.othelloBoard.setBoard(nextBoard)
        self.flag_action = ProcessStatus.WAIT
        self.flag_connectArena = ProcessStatus.FINISH
"""

class Scene_League(pcm.BaseScene):
    def start(self):
        pass
    def update(self):
        pass
    def draw(self):
        pass

class Scene_History(pcm.BaseScene):
    def start(self):
        pass
    def update(self):
        pass
    def draw(self):
        pass

class BoardHistoryList:
    def __init__(self, size=3):
        self.historys = [BoardHistory() for i in range(size)]
    def push(self, board, lastPut=[-1,-1]):
        size : int = len(self.historys)
        for i in range(size - 1):
            index = (size - 1) - i
            self.historys[index].setBoard(self.historys[index-1].board, self.historys[index-1].lastPut)
        self.historys[0].setBoard(board=board,lastPut=lastPut)
    def drawBoard(self,index=0,num=-1,x=0,y=0,offset=1):
        i : int = 0
        d : int = 0
        for h in self.historys:
            i += 1
            if i - 1 < index:
                continue
            if i - 1 >= num + index:
                break
            h.drawBoard_m(x=x,y=y+8*h.IMG_Size*offset*d)
            d += 1

class BoardHistory:
    def __init__(self, board=[[0 for i in range(8)] for j in range(8)],lastPut=[-1,-1]):
        self.setBoard(board=board)
        self.IMG_Size = 8
        self.lastPut = lastPut
    def setBoard(self, board, lastPut=[-1,-1]):
        self.board = copy.deepcopy(board)
        self.lastPut = lastPut
    def drawBoard_m(self,x=0,y=0):
        IMG_SIZE = self.IMG_Size
        for u in range(len(self.board)):
            for v in range(len(self.board[u])):
                p = self.board[u][v]
                type : int = 0
                if u == self.lastPut[1] and v == self.lastPut[0]:
                    type = 2
                pyxel.blt(x=IMG_SIZE*u+x,y=IMG_SIZE*v+y,img=0,u=48+IMG_SIZE*(p+1),v=type*IMG_SIZE,w=IMG_SIZE,h=IMG_SIZE)
    def drawBoard_s(self,x=0,y=0):
        IMG_SIZE = 4

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
        self.lastPut = [-1, -1]
    def setBoard(self,board):
        self.board = copy.deepcopy(board)
    def execute(self, action, player):
        moves = self.getMoves(player=player)
        check = False
        for m in moves:
            check = check or (action[0] == m[0] and action[1] == m[1])
        if check == False:
            print("Error")
            return False
        self.board = OthelloLogic.execute(board=self.board,action=action,player=player,size=len(self.board)) 
        self.lastPut = action
        return True
    def getMoves(self, player):
        return OthelloLogic.getMoves(board=self.board,player=player,size=len(self.board))
    def input(self, mouse_x, mouse_y, player):
        IMG_SIZE = self.IMG_SIZE
        for m in self.getMoves(player=player):
            if IMG_SIZE*m[1] <= mouse_x-self.x < IMG_SIZE*(m[1]+1) and IMG_SIZE*m[0] <= mouse_y-self.y < IMG_SIZE*(m[0]+1):
                return self.execute(action=m,player=player)
        return False
    def drawBoard(self, player=0, showPut=True, reverse=False):
        IMG_SIZE = self.IMG_SIZE
        for u in range(len(self.board)):
            for v in range(len(self.board[u])):
                p = self.board[u][v]
                type : int = 0
                if u == self.lastPut[1] and v == self.lastPut[0]:
                    type = 2
                    #print(u,v)
                #pyxel.blt(x=IMG_SIZE*u+self.x,y=IMG_SIZE*v+self.y,img=0,u=IMG_SIZE*(p+1),v=type*IMG_SIZE,w=IMG_SIZE,h=IMG_SIZE)
                p_ = p if reverse == False else -p
                pyxel.blt(x=IMG_SIZE*u+self.x,y=IMG_SIZE*v+self.y,img=0,u=IMG_SIZE*(p+1),v=type*IMG_SIZE,w=IMG_SIZE,h=IMG_SIZE)
        if player == 0 or showPut == False:
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

#OthelloApp()
App()