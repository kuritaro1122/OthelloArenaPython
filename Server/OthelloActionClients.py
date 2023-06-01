
import sys
import os
import copy
import importlib
import socket

# 相対パスから親階層のモジュールをインポート
ClientBase = None
Server = None
def __executeOnPath(absPath:str, func:lambda:None):
    current = copy.deepcopy(sys.path)
    sys.path.append(absPath)
    func()
    sys.path = current
def __importModules_Framework():
	global ClientBase
	ClientBase = importlib.import_module('ClientBase').ClientBase
def __importModules():
    global Server
    Server = importlib.import_module('OthelloActionServers')
__executeOnPath(os.path.join(os.path.dirname(__file__), 'Framework/'), __importModules_Framework)
__executeOnPath(os.path.join(os.path.dirname(__file__), ''), __importModules)

"""
size = 8
board = [[0 for i in range(size)] for j in range(size)]

board[int(size/2)-1][int(size/2)-1] = 1;
board[int(size/2)][int(size/2)-1]=-1;
board[int(size/2)-1][int(size/2)]=-1;
board[int(size/2)][int(size/2)]=1;

moves = [[0,0],[0,1],[0,2]]
"""

#client = None

class OthelloActionClient(ClientBase):
    def __init__(self):
        self.server = Server.getHostAndPort()
        super().__init__(timeout=60, buffer=1024)
        super().connect(self.server, socket.AF_INET, socket.SOCK_STREAM, 0)
        self.isReceived = False
        self.recentlyCmd = ''
    def received(self, message:str):
        print('received ->', message)
        row = message.split(',')
        if row[0] == self.recentlyCmd:
            self.isReceived = True
            self.action = Server.txt2move(row[1])
            print('ok', self.recentlyCmd, message)
        else:
            print('no', self.recentlyCmd, message)
    def getAction(self,board,moves,aiIndex) -> list:
        cmd = '10'
        self.recentlyCmd = cmd
        self.isReceived = False
        msg = ','.join([cmd,str(aiIndex),Server.board2txt(board),Server.moves2txt(moves)])
        self.send2(msg)
        while self.isReceived == False:
            pass
        return self.action

"""
if __name__=='__main__':
    #cli = OthelloActionClient()
    #cmd = '10'#str(OthelloActionServer.Command.OTHELLO_ACTION)
    #message = ','.join([cmd,'1',OthelloActionServer.board2txt(board),OthelloActionServer.moves2txt(moves)])
    #cli.send(message)
    init()
    while True:
        pass
"""