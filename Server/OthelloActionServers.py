import sys
import os
import socket
import copy
import importlib
from Framework.ServerBase import *

# 相対パスから親階層のモジュールをインポート
OthelloAction = None
def __executeOnPath(absPath:str, func:lambda:None):
    current = copy.deepcopy(sys.path)
    sys.path.append(absPath)
    func()
    sys.path = current
def __importModules():
	global OthelloAction
	OthelloAction = importlib.import_module('OthelloAction')
__executeOnPath(os.path.join(os.path.dirname(__file__), '../'), __importModules)

class Command:
     OTHELLO_ACTION = '10'
INFO_TXT = 'info.txt'

def getHostAndPort():
    host, port = '0.0.0.0', 8080
    with open(os.path.join(os.path.dirname(__file__), INFO_TXT)) as f:
        lines = f.readlines()
        host = lines[0].replace('\n', '').replace('host=', '')
        port = int(lines[1].replace('\n', '').replace('port=', ''))
    return (host, port)

def txt2board(txt:str) -> list:
    board = []
    for column in txt.split('.'):
        _column = []
        for cell in column:
            if cell in ['0', '1', '2']:
                # 2だったら-1にする
                _column.append(int('-1' if cell == '2' else cell))
        if len(_column) > 0:
            board.append(_column)
    return board
def board2txt(board:list) -> str:
    txt = ''
    for b in board:
        for cell in b:
            if cell in [0, 1, -1]:
                txt += str(2 if cell == -1 else cell)
        txt += '.'
    return txt
def txt2moves(txt:str) -> list:
    moves = []
    for move in txt.split('.'):
        if len(move) == 2:
            moves.append(txt2move(move))
    return moves
def moves2txt(moves:list) -> str:
    txt = ''
    for move in moves:
        if len(move) == 2:
            txt += move2txt(move) + '.'
    return txt
def txt2move(txt:str) -> list:
    return [int(txt[0]), int(txt[1])]
def move2txt(move:list) -> str:
    return str(move[0]) + str(move[1])

class OthelloActionServer(MultipleServerBase):
    def __init__(self) -> None:
        self.server = getHostAndPort()
        super().__init__(timeout=60*60, buffer=1024)
        #super().__init__(5, self.respond, timeout=60, buffer=1024)
        self.accept(self.server, socket.AF_INET, socket.SOCK_STREAM, 0)
    
    def respond(self, message:str) -> str:
        # command,ai_index,boards,moves
        print('receive -> ', message)
        elements = message.split(',')
        if len(elements) > 2 and elements[0] == Command.OTHELLO_ACTION:
            #command,ai_index,boards,moves
            ai_index = int(elements[1])
            boards = txt2board(elements[2])
            moves = txt2moves(elements[3])
            action = OthelloAction.getAction(boards, moves, ai_index)
            return ','.join([elements[0], move2txt(action)])
        return 'Server accept !!'

if __name__=='__main__':
    OthelloActionServer()