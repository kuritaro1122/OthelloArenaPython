import sys
import os
import glob
import importlib

FUNCTION_NAME = 'getAction'
IMPORT_TXT = 'OthelloActions/import.txt'

# ディレクトリからモジュールを検索するための関数
def __find_scripts(directory:str):
	script_paths = glob.glob(os.path.join(directory, '*.py'))
	return script_paths

def __find_module_from_path(script_path:str):
	module_name = str.replace(os.path.splitext(script_path)[0], '/', '.')
	module = importlib.import_module(module_name)
	return module

def __exexute_othelloAction(module, board, moves):
	function_name = FUNCTION_NAME
	function = getattr(module, function_name)
	return function(board, moves)

modules = []
player1 = 0
player2 = 0

# OthelloActions/import.txt を参照してOthelloAction用のmoduleをimportする
with open(IMPORT_TXT) as f:
	for line in f.readlines():
		line = line.replace('\n', '')
		_modules = []
		print('line', line)
		for path in __find_scripts(line):
			if os.path.isabs(path):
				print('絶対パスは対応していません')
				raise NotImplementedError()
			_module = __find_module_from_path(path)
			if _module != None and hasattr(_module, FUNCTION_NAME):
				_modules.append(_module)
		modules.extend(_modules)

# player を設定する
def setPlayer(_player1:int=None, _player2:int=None):
	global player1, player2
	if _player1 != None:
		player1 = _player1
	if _player2 != None:
		player2 = _player2

def selectPlayer(playerNum:int=2):
	global player1, player2
	print('OthelloAction 一覧\n>')
	for i, m in enumerate(modules):
		print('{0} : {1}'.format(i, m.__name__))
	print('>')
	print('インデックスを入力してください. ({0}~{1})'.format(0, len(modules) - 1))
	if playerNum > 0:
		player1 = int(input('player1:'))
	if playerNum > 1:
		player2 = int(input('player2:'))
	return modules[player1].__name__, modules[player2].__name__

# 次の手を取得する
def getAction1(board,moves):
	return __exexute_othelloAction(modules[player1],board,moves)

def getAction2(board,moves):
	return __exexute_othelloAction(modules[player2],board,moves)