import sys
import os
import copy
import glob
import importlib

FUNCTION_NAME = 'getAction'
IMPORT_TXT = 'OthelloActions/import.txt'

# ディレクトリからモジュールを検索するための関数
__module = None
def __executeOnPath(absPath:str, func:lambda:None):
    current = copy.deepcopy(sys.path)
    sys.path.append(absPath)
    func()
    sys.path = current
def __find_scripts(directory:str):
	script_paths = glob.glob(os.path.join(directory, '*.py'))
	return script_paths
def __find_module_from_path(script_path:str):
	dir_path = os.path.dirname(script_path)
	module_name = os.path.basename(script_path).split('.')[0]
	def func():
		global __module
		__module = importlib.import_module(module_name)
	__executeOnPath(dir_path, func)
	return __module

Client = None
def __importModules():
	global Client
	Client = importlib.import_module('OthelloActionClient').OthelloActionClient
__executeOnPath(os.path.join(os.path.dirname(__file__), 'Server/'), __importModules)

# モジュールを実行して手を取得する
def __exexute_othelloAction(module, board, moves):
	function_name = FUNCTION_NAME
	function = getattr(module, function_name)
	return function(board, moves)

modules = []
player1 = 0
player2 = 0

# OthelloActions/import.txt を参照してOthelloAction用のmoduleをimportする
with open(os.path.join(os.path.dirname(__file__), IMPORT_TXT)) as f:
	for line in f.readlines():
		line = line.replace('\n', '')
		targetAbsDir =  os.path.join(os.path.dirname(__file__), line)
		currentAbsDir = os.getcwd()
		relDirPath = os.path.relpath(targetAbsDir, currentAbsDir)
		_modules = []
		for path in __find_scripts(relDirPath):
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

client = None
tryConnect = True

if tryConnect:
	try:
		client = Client()
	except:
		client = None

# 次の手を取得する
def getAction1(board,moves):
	return getAction(board,moves,player1)

def getAction2(board,moves):
	return getAction(board,moves,player2)

def getAction(board,moves,aiIndex):
	if client != None:
		return client.getAction(aiIndex=aiIndex,board=board,moves=moves)
	return __exexute_othelloAction(modules[aiIndex],board,moves)