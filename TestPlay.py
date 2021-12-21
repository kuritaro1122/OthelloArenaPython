import OthelloAction
import OthelloLogic
import copy

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
while(True):
	if(player == -1): #2p
		action = OthelloAction.getAction(OthelloLogic.getReverseboard(board),moves)
	else: #1p
		action = OthelloAction.getAction2(board,moves)
	if(not (action in moves)):
		print(board)
		print('合法手ではない手が打たれました' + action)
		exit()
	board = OthelloLogic.execute(board,action,player,size)
	_board = copy.deepcopy(board)
	#if player == -1:
	#	_board = OthelloLogic.getReverseboard(_board)
	OthelloLogic.printBoard(_board)
	print('player', player)
	print('現在の合法手一覧')
	print(moves)
	moves = OthelloLogic.getMoves(board,player*-1,size)
	if(len(moves) == 0):
		moves = OthelloLogic.getMoves(board,player,size)
		if(len(moves) == 0):
			break
	else:
		player = player * -1

print('正常に終了しました。')

# ゲームリザルトの表示
n = 0
for b1 in board:
	for b2 in b1:
		n += b2
print('1p - 2p:',n)
if n > 0:
	print('1p(black) win')
elif n < 0:
	print('2p(white), win')
else:
	print('draw')