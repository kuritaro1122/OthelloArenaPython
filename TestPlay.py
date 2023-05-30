import OthelloAction
import OthelloLogic
from OthelloRecord.OthelloRecoder import Recoder
import sys

#sizeを変更することでテストプレイする盤面の大きさを変更できます。
#size = 4
#size = 6
size = 8
board = [[0 for i in range(size)] for j in range(size)]

board[int(size/2)-1][int(size/2)-1] = 1;
board[int(size/2)][int(size/2)-1]=-1;
board[int(size/2)-1][int(size/2)]=-1;
board[int(size/2)][int(size/2)]=1;

player = -1
moves = OthelloLogic.getMoves(board,player,size)

p1_name, p2_name = None, None
recoder = Recoder()
if len(sys.argv) >= 3:
	OthelloAction.setPlayer(int(sys.argv[1]), int(sys.argv[2]))
else:
	p1_name, p2_name = OthelloAction.selectPlayer(playerNum=2)
recoder.setMatchInfo(0,'TestPlay',0,p1_name,1,p2_name)

while(True):
	if(player == -1):
		action = OthelloAction.getAction1(OthelloLogic.getReverseboard(board),moves)
	else:
		action = OthelloAction.getAction2(board,moves)
	if(not (action in moves)):
		print(board)
		print('合法手ではない手が打たれました' + action)
		exit()
	board = OthelloLogic.execute(board,action,player,size)
	OthelloLogic.printBoard(board)
	score = OthelloLogic.countBoard(board, player=1)
	recoder.updateMatch(action[1], action[0], score, score)
	print('現在の合法手一覧')
	print(moves)
	moves = OthelloLogic.getMoves(board,player*-1,size)
	if(len(moves) == 0):
		moves = OthelloLogic.getMoves(board,player,size)
		if(len(moves) == 0):
			break
	else:
		player = player * -1

recoder.exportMatchResult()
print('正常に終了しました。')		
