import random
#import csv
import pandas as pd
import OthelloLogic
import copy

boardSize = 8

"""
引数について

board:現在の盤面の状態
moves:現在の合法手の一覧

詳しい説明はサイトのHomeページをご覧ください。

"""

def getAction2(board,moves):
	index = random.randrange(len(moves))
	return moves[index]

def getAction(board,moves): #movesは2次配列
	#print("=== start ===")
	#OthelloLogic.printBoard(board)
	print("=== action ===")
	#渡されたMovesの中からランダムで返り値として返却する。
	#index = random.randrange(len(moves))

	eva_func = pd.read_csv("EvaluationFunction.csv", header=None).values.tolist()

	#index = simpleSearch(moves, eva_func)
	index = negaMaxSearch(3, board, moves, 1, eva_func) #limitを偶数にすると途端に弱くなる。

	print("=== actionEnd ===")
	return moves[index]

def getMoves(board, player):
	l = len(board[0])
	return OthelloLogic.getMoves(board=board,player=player,size=l)


def simpleSearch(moves, eva_func):
	score = -999
	index = 0
	for i in range(len(moves)):
		_score = eva_func[moves[i][1]][moves[i][0]]
		if _score > score:
			index = i
			score = _score
			print("スコア更新", score)
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
			_board = turnOnDirection(_board, action, player, [o1, o2])
	return _board,True
def turnOnDirection(board, action, player, direction):
	num = turnNum(board, action, player, direction)
	for i in range(num):
		board[action[1] + i * direction[1]][action[0] + i * direction[0]] = player
	return board
def turnNum(board, action, player, direction):
	distance = 1
	while True:
		x = action[1] + distance * direction[1]
		y = action[0] + distance * direction[0]
		if 0 <= x and x < 8 and 0 <= y and y < 8:
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

def negaMaxSearch(limit, board, moves, player, eva_func):
	moves = getMoves(board, player)
	index = 0
	score = 999 * player
	for i in range(len(moves)):
		m = moves[i]
		_board,check = simulateBoard(board, m, player) #変化なし？？
		if check == False:
			print('simulateError')
			return
		_score,current = negaMaxLevel(0, limit-1, _board, player * -1, eva_func, m, -999)
		#_score = pow(_score, current%2)
		#_score = _score * pow(-1, current%2)
		
		#盤面候補の表示
		print('root, player= {}, action= {}, score= {}'.format(player, m, _score))
		OthelloLogic.printBoard(_board)
		#print("action", m)

		if player * _score < player * score:
			score = _score
			index = i
			print('update!! (index, score) = ({}, {})'.format(index,score))
	print('★ selected!! (index, score) = ({}, {})'.format(index,score))
	return index
def negaMaxLevel(current, limit, board, player, eva_func, move, current_score):
	moves = getMoves(board, player)
	#limit -= 1
	if limit <= 0:
		sc = 0
		for y in range(len(board)):
			for x in range(len(board)):
				sc += player * board[y][x] * eva_func[y][x]
				#sc += board[y][x] * eva_func[y][x]
		return sc,current
		#return player * sc; #盤面の評価値
	score = 999 * player
	for i in range(len(moves)):
		m = moves[i]
		_board,check = simulateBoard(board, m, player)
		if check == False:
			print('simulateError')
			return
		_score,current = negaMaxLevel(current+1, limit-1, _board, player * -1, eva_func, m, score * player * -1)
		if player * _score < player * score:
			score = _score
		if player * current_score > player * score:
			break
		#盤面候補の表示
		print('leaf:{}, player= {}, action= {}, score= {}'.format(limit, player, m, _score))
		OthelloLogic.printBoard(_board)
	return score,current

"""
def negaMaxSearch(limit, board, moves, player, eva_func):
	moves = getMoves(board, player)
	index = 0
	score = 999 * player
	for i in range(len(moves)):
		m = moves[i]
		_board,check = simulateBoard(board, m, player) #変化なし？？
		if check == False:
			print('simulateError')
			return
		_score = negaMaxLevel(limit-1, _board, player * -1, eva_func, m, -999)

		#盤面候補の表示
		#print('root, player= {}, action= {}, score= {}'.format(player, m, _score))
		#OthelloLogic.printBoard(_board)
		#print("action", m)

		if player * _score < player * score:
			score = _score
			index = i
			#print('update!! (index, score) = ({}, {})'.format(index,score))
	#print('★ selected!! (index, score) = ({}, {})'.format(index,score))
	return index
def negaMaxLevel(limit, board, player, eva_func, move, current_score):
	moves = getMoves(board, player)
	#limit -= 1
	if limit <= 0:
		sc = 0
		for y in range(len(board)):
			for x in range(len(board)):
				#sc += player * board[y][x] * eva_func[y][x]
				sc += board[y][x] * eva_func[y][x]
		#return sc
		return player * sc; #盤面の評価値
	score = 999 * player
	for i in range(len(moves)):
		m = moves[i]
		_board,check = simulateBoard(board, m, player)
		if check == False:
			print('simulateError')
			return
		_score = negaMaxLevel(limit-1, _board, player * -1, eva_func, m, score * player * -1)
		if player * _score < player * score:
		#if _score < score:
			score = _score
		#if player * current_score < player * score:
		#	break
		#盤面候補の表示
		#print('leaf:{}, player= {}, action= {}, score= {}'.format(limit, player, m, _score))
		#OthelloLogic.printBoard(_board)
	return score
"""