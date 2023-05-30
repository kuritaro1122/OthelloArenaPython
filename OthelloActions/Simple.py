"""
引数について

board:現在の盤面の状態
moves:現在の合法手の一覧

詳しい説明はサイトのHomeページをご覧ください。

"""

EVA_FUNC = [[30,-12,0,-1,-1,0,-12,30],[-12,-15,-3,-3,-3,-3,-15,-12],[0,-3,0,-1,-1,0,-3,0],[-1,-3,-1,-1,-1,-1,-3,-1],[-1,-3,-1,-1,-1,-1,-3,-1],[0,-3,0,-1,-1,0,-3,0],[-12,-15,-3,-3,-3,-3,-15,-12],[30,-12,0,-1,-1,0,-12,30]]

def getAction(board,moves):
    index = simpleSearch(moves=moves, eva_func=EVA_FUNC)
    return moves[index]

def simpleSearch(moves, eva_func):
    score = -999
    index = 0
    for i in range(len(moves)):
        _score = eva_func[moves[i][1]][moves[i][0]]
        if _score > score:
            index = i
            score = _score
            #print("スコア更新", score)
    return index