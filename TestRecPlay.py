#import OthelloAction
import OthelloLogic
from OthelloRecord.OthelloRecoder import *

size = 8
board = [[0 for i in range(size)] for j in range(size)]

board[int(size/2)-1][int(size/2)-1] = 1;
board[int(size/2)][int(size/2)-1]=-1;
board[int(size/2)-1][int(size/2)]=-1;
board[int(size/2)][int(size/2)]=1;

player = -1
moves = OthelloLogic.getMoves(board,player,size)
recoder = Recoder()

print('再生するログを選んでください')
logs = recoder.loadLogs()
for i, log in enumerate(logs):
    print('{0} : {1}'.format(i, (log[LABEL['date']], log[LABEL['blackPlayerName']], log[LABEL['whitePlayerName']], log[LABEL['blackScore']])))

index = int(input('index({0}~{1}):'.format(0,len(logs)-1)))

recoder.load(index)
print(recoder.__str__())

transcript = recoder.transcript
cnt = 0

def transcript_2_action(transcript:str):
    return [int(transcript[1]), ord(transcript[0]) - 97]

while True:
    if cnt > len(transcript) - 1:
        break;
    action = transcript_2_action(transcript[cnt])
    cnt += 1
    if not (action in moves):
        print(board)
        print('合法手ではない手が打たれました' + action)
        exit()
    board = OthelloLogic.execute(board,action,player,size)
    OthelloLogic.printBoard(board)
    print('現在の合法手一覧')
    print(moves)
    moves = OthelloLogic.getMoves(board,player*-1,size)
    if len(moves) == 0:
        moves = OthelloLogic.getMoves(board,player,size)
        if len(moves) == 0:
            break;
    else:
        player = player * -1

print('正常に終了しました.')