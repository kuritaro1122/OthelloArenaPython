import random
#import pandas as pd
import OthelloLogic
import copy
#import OthelloAction_old

"""
引数について

board:現在の盤面の状態
moves:現在の合法手の一覧

詳しい説明はサイトのHomeページをご覧ください。

"""

EVA_FUNC = [[30,-12,0,-1,-1,0,-12,30],[-12,-15,-3,-3,-3,-3,-15,-12],[0,-3,0,-1,-1,0,-3,0],[-1,-3,-1,-1,-1,-1,-3,-1],[-1,-3,-1,-1,-1,-1,-3,-1],[0,-3,0,-1,-1,0,-3,0],[-12,-15,-3,-3,-3,-3,-15,-12],[30,-12,0,-1,-1,0,-12,30]]
OUTPUT = False

def print_wrap(value:str):
	if OUTPUT:
	    print(value)

def getAction(board,moves): #movesは2次配列
	print_wrap("=== action start ===")
	index = getActionIndex(board, moves)
	for p in [1, -1]:
		print_wrap('player:{} 確定石=>{}'.format(p,definiteStones(board=board,player=p)))
	print_wrap('確定石=>{}'.format(definiteStones(board=board)))
	print_wrap('残り=>{}'.format(countSpace(board)))
	print_wrap("=== action end ===")
	return moves[index]

#不正な手を出した時の再試行回数
tryNum = 5
tryCount = tryNum
def getActionIndex(board, moves):
	#space = countSpace(board)
	index = negaMaxSearch(limit=3,board=board,moves=moves,player=1,eva_func=EVA_FUNC)
	#不正な手を防止
	global tryNum
	global tryCount
	if index < 0 or index > len(moves) - 1:
		tryCount -= 1
		if tryCount > 0:
			index = getActionIndex(board=board,moves=moves)
			print_wrap("try again")
		else: 
			index = random.randrange(len(moves))
			print_wrap("random", index)
	tryCount = tryNum
	return index

def simpleSearch(moves, eva_func):
	score = -999
	index = 0
	for i in range(len(moves)):
		_score = eva_func[moves[i][1]][moves[i][0]]
		if _score > score:
			index = i
			score = _score
			print_wrap("スコア更新", score)
	return index
#石を置いた後の盤面を返す.
def simulateBoard(board, action, player):
	_board = copy.deepcopy(board)
	moves = getMoves(_board, player)
	check = False
	for m in moves:
		if action[1] == m[1] and action[0] == m[0]:
			check = True
			break
	if (check == False): 
		return _board,False
	_board[action[1]][action[0]] = player
	offset = [-1, 0, 1]
	for o1 in offset: #各方向の石をひっくり返す
		for o2 in offset:
			if (o1 == 0 and o2 == 0): 
				continue
			_board = turnOnDirection(board=_board,action=action,player=player,direction=[o1, o2])
	return _board,True
def turnOnDirection(board, action, player, direction):
	num = turnNum(board, action, player, direction)
	for i in range(num):
		board[action[1] + i * direction[1]][action[0] + i * direction[0]] = player
	return board
def turnNum(board, action, player, direction):
	distance = 1
	size = len(board)
	while True:
		x = action[1] + distance * direction[1]
		y = action[0] + distance * direction[0]
		if 0 <= x and x < size and 0 <= y and y < size:
			if board[x][y] == player * -1:
				distance += 1
			elif board[x][y] == player:
				return distance
			elif board[x][y] == 0:
				return 0
			else:
				print("Error", board[y][x])
				return 0
		else:
			return 0
def getMoves(board, player):
	l = len(board[0])
	return OthelloLogic.getMoves(board=board,player=player,size=l)
def countSpace(board):
	space = 0
	for b1 in board:
		for b2 in b1:
			if b2 == 0:
				space += 1
	return space

#negaScout法による探索
def negaMaxSearch(limit, board, moves, player, eva_func):
	moves = getMoves(board, player)
	index = 0
	score = 999 * player
	moveIndexs = list(range(len(moves)))
	while True: #追加
		for i in range(len(moves)):
			m = moves[i]
			_board,check = simulateBoard(board=board,action=m,player=player)
			if check == False:
				print('simulateError')
				return 0
			_score = negaMaxLevel(limit=limit-1,board=_board,player=player*-1,eva_func=eva_func,move=m,current_score=-999)
			_score = _score * pow(-1, limit-1)
			#盤面候補の表示
			#print('root, player= {}, action= {}, score= {}'.format(player, m, _score))
			#OthelloLogic.printBoard(_board)
			if player * _score < player * score:
				score = _score
				index = i
				moveIndexs = [i]
				print_wrap('update!! (index, score) = ({}, {})'.format(index,score))
			elif player * _score == player * score:
				moveIndexs.append(i)
		if len(moveIndexs) <= 1 or limit < 1: #追加
			break;
		limit -= 2 #追加
		print_wrap('再試行 limit=>{} moves={}'.format(limit,moveIndexs)) #追加
	print_wrap('★ selected!! (index, score) = ({}, {})'.format(index,score))
	return index
def negaMaxLevel(limit, board, player, eva_func, move, current_score):
	moves = getMoves(board, player)
	if limit <= 0:
		#評価関数を更新（確定石）
		_eva_func = evaFuncDefiniteStone(eva_func=eva_func,board=board)
		#盤面の評価値を計算
		sc = 0
		for y in range(len(board)):
			for x in range(len(board)):
				sc += player * board[y][x] * _eva_func[y][x]
		return sc
	score = 999 * player
	for i in range(len(moves)):
		m = moves[i]
		_board,check = simulateBoard(board, m, player)
		if check == False:
			print('simulateError')
			return
		_score = negaMaxLevel(limit=limit-1,board=_board,player=player*-1,eva_func=eva_func,move=m,current_score=score * player * -1)
		if player * _score < player * score:
			score = _score
		if player * current_score > player * score:
			break
		#盤面候補の表示
		#print('leaf:{}, player= {}, action= {}, score= {}'.format(limit, player, m, _score))
		#OthelloLogic.printBoard(_board)
	return score

definiteStoneScore = 30
#確定石の得点を反映させた評価関数
def evaFuncDefiniteStone(eva_func, board):
	if OUTPUT:
		OthelloLogic.printBoard(board)
	_eva_func = copy.deepcopy(eva_func)
	for s in definiteStones(board):
		_eva_func[s[0]][s[1]] = max(eva_func[s[0]][s[1]], definiteStoneScore)
		print_wrap('definiteStone ({},{}) score:{}=>{}'.format(s[0],s[1],eva_func[s[0]][s[1]],_eva_func[s[0]][s[1]]))
	return _eva_func
#確定石の取得
def definiteStones(board, player=0):
	stones = []
	dire = [0,1]
	for y in range(len(board)):
		for x in range(len(board[y])):
			definite = True
			for dy in dire:
				for dx in dire:
					if dy == 0 and dx == 0:
						continue
					definite = definite and definiteLine(board=board,pos=[y,x],dire=[dy,dx],player=player)
			if definite == True:
				stones.append([y, x])
	return stones
def definiteLine(board, pos, dire, player=0):
	definite = False
	length = len(board)
	if board[pos[0]][pos[1]] == 0 or (player!=0 and board[pos[0]][pos[1]]!=player):
		return False
	if player == 0:
		player = board[pos[0]][pos[1]]
	if dire[0] == 0 and dire[1] == 0:
		print('Error')
		return True
	for foward in [1, -1]:
		step = 1
		while True:
			y = pos[0] + dire[0] * step * foward
			x = pos[1] + dire[1] * step * foward
			if (x < 0 or x >= length) or (y < 0 or y >= length):
				definite = True
				break
			elif board[y][x] != player:
				#definite = False
				break
			step += 1
	for foward in [1, -1]:
		step = 1
		while True:
			y = pos[0] + dire[0] * step * foward
			x = pos[1] + dire[1] * step * foward
			if (x < 0 or x >= length) or (y < 0 or y >= length):
				break
			elif board[y][x] == 0:
				return definite
			step += 1
	return True