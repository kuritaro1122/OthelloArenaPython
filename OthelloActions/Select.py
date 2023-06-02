#def getAction(board,moves):
#    for i, m in enumerate(moves):
#        print('{0} : {1}'.format(i, m))
#    index = -1
#    while index < 0 or index >= len(moves):
#        message = input('手を選んでください({0}~{1}) : '.format(0, len(moves)))
#        if message.isdecimal:
#            index = int(message)
#    return moves[index]