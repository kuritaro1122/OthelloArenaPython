import datetime
import csv
import re

LABEL = {
    'tournamentId' : 0,
    'tournamentName' : 1,
    'blackPlayerId' : 2,
    'blackPlayerName' : 3,
    'whitePlayerId' : 4,
    'whitePlayerName' : 5,
    'blackScore' : 6,
    'blackTheoreticalScore' : 7,
    'transcript' : 8,

    'date' : 9,
}
LOG_FILE = 'OthelloRecord/export/wthor.csv'

class Recoder:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.tId = 0
        self.tName = 0
        self.bId = 0
        self.bName = 'black'
        self.wId = 1
        self.wName = 'white'
        self.transcript = []
        self.bScore = 0
        self.bTScore = 0
        #self.date = datetime.datetime.min

    def setMatchInfo(self, tId=0, tName='None', bId=0, bName='black', wId=1, wName='white'):
        self.tId = tId # tournament
        self.tName = tName
        self.bId = bId # black
        self.bName = bName
        self.wId = wId # white
        self.wName = wName
        self.date = datetime.datetime.now()
    
    def updateMatch(self, column:int, row:int, bScore:int, bTScore:int=None):
        self.transcript.append('{0}{1}'.format(chr(97+column), row))
        self.bScore = bScore
        self.bTScore = bTScore
    
    def exportMatchResult(self):
        with open(LOG_FILE, 'a') as f:
            #headerLabel = str.join([l for l in LABEL])
            #header = f.readlines()[0].replace('\n', '').replace(' ', '')
            #print(headerLabel, header)
            date = datetime.datetime.now()
            line = '\n' + self.__str__()
            f.write(line)

    def loadLogs(self):
        lines = []
        with open(LOG_FILE, 'r') as f:
            reader = csv.reader(f)
            for r in reader:
                if r[LABEL['tournamentId']].isdecimal():
                    lines.append(r)
        return lines
    def load(self, index:int):
        line = self.loadLogs()[index]
        self.tId = line[LABEL['tournamentId']]
        self.tName = line[LABEL['tournamentName']]
        self.bId = line[LABEL['blackPlayerId']]
        self.bName = line[LABEL['blackPlayerName']]
        self.wId = line[LABEL['whitePlayerId']]
        self.wName = line[LABEL['whitePlayerName']]
        self.date = datetime.datetime.strptime(line[LABEL['date']], '%Y-%m-%d %H:%M:%S')
        self.transcript = re.split('(..)', line[LABEL['transcript']])[1::2]
        self.bScore = line[LABEL['blackScore']]
        self.bTScore = line[LABEL['blackTheoreticalScore']]
    
    def __str__(self):
        return ','.join([str(self.tId), str(self.tName), str(self.bId), str(self.bName), str(self.wId), str(self.wName), str(self.bScore), str(self.bTScore), ''.join(self.transcript), self.date.strftime('%Y-%m-%d %H:%M:%S')])