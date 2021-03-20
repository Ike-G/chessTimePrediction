import re
import numpy as np

def getTC(path: str, desiredTC: tuple) :
    with open(path, 'r') as file, open(f'relGames_{desiredTC[0]}_{desiredTC[1]}', 'a+') as out :
        l = file.readlines()
        tc = l[13::18]
        tcString = f'"{desiredTC[0]*60}\\+{desiredTC[1]}"'
        check = re.compile(tcString)
        for i in range(len(tc)) :
            if check.search(tc[i]) :
                out.writelines(l[(18*i):(18*(i+1))])

getTC("lichess_db_standard_rated_2017-07.pgn/lichess_db_standard_rated_2017-07.pgn", (1,0))
# getTC("lichess_db_standard_rated_2017-04.pgn", (3,2))

def getTimes(path: str, tc: tuple) :
    with open(path, 'r') as file :
        l = file.readlines()
        games = l[16::18]
        move = re.compile(r'(\d+)\..+?k\s(\d+):(\d+):(\d+).+?k\s(\d+):(\d+):(\d+)')
        data = []
        for g in games :
            gData = []
            rPoints = move.findall(g)
            lastW = lastB = tc[0]*60 - tc[1]
            for i in rPoints :
                wP = (int(i[0]), lastW + tc[1] - (int(i[1])*3600+int(i[2])*60+int(i[3])))
                bP = (int(i[0]), lastB + tc[1] - (int(i[4])*3600+int(i[5])*60+int(i[6])))
                lastW = int(i[1])*3600+int(i[2])*60+int(i[3])
                lastB = int(i[4])*3600+int(i[5])*60+int(i[6])
                gData.extend([wP, bP])
            data.extend(gData)
    return data

def timesInFile() :
    t = getTimes('relGames_3_2', (3,2))
    with open('times_3_2', 'w+') as out :
        out.write("Number Time (s)\n")
        out.writelines([f'{i[0]} {i[1]}\n' for i in t])

def parseGames() :
    with open('relGames_3_2', 'r') as t:
        l = t.readlines()
    currGame = []
    gameList = []
    c = 2
    for i in l :
        if re.match(r'\n', i) :
            c -= 1
            if not c :
                c = 2
                gameList.append(currGame)
                currGame = []
        else :
            currGame.append(i)
    return gameList

def getBasicFeatures() :
    # Get move
    # Get current time available
    # Get time used on last move
    # Get opponent's time available
    # Get opponent's time used on last move
    # Get rating
    # Get opponent's rating
    # TODO: run RNN over previous moves within game - When doing this all but current time, opponent time, and rating can be ignored
    games = parseGames()
    clock = re.compile(r'\[%clk\s(\d+):(\d+):(\d+)\]')
    data = []
    for g in games : 
        gData = []
        wElo = 0
        bElo = 0
        for i in range(len(g)-1) : 
            wEloCheck = re.match(r'\[WhiteElo\s"(\d+)"\]', g[i])
            bEloCheck = re.match(r'\[BlackElo\s"(\d+)"\]', g[i])
            if wEloCheck : 
                wElo = int(wEloCheck.groups()[0])
            elif bEloCheck : 
                bElo = int(bEloCheck.groups()[0])
        wBefore = 178 # Defined as the initial control minus the increment
        bBefore = 178
        times = clock.findall(g[-1])
        whiteMoves = times[::2]
        blackMoves = times[1::2]
        wt = [int(i[0])*3600+int(i[1])*60+int(i[2]) for i in whiteMoves]
        bt = [int(i[0])*3600+int(i[1])*60+int(i[2]) for i in blackMoves]
        wd = [] 
        bd = []
        for i in range(len(wt)) : 
            wAfter = wt[i]
            wDiff = wBefore + 2 - wAfter # Including increment
            wBefore = wAfter
            wd.append(wDiff)
        for i in range(len(bt)) : 
            bAfter = bt[i]
            bDiff = bBefore + 2 - bAfter
            bBefore = bAfter
            bd.append(bDiff)
        # Given that lichess doesn't remove time from the first move, this model will not consider move 0
        # Move dependent features: 
        # - Personal Time remaining
        # - Last move time
        # - Opponent time remaining
        # - Opponent last move time
        # - Move number
        for i in range(len(wt)-1) : 
            gData.append((wd[i+1], i+1, wt[i], wd[i], bt[i], bd[i], wElo, bElo))
        for i in range(len(bt)-1) : 
            gData.append((bd[i+1], i+1, bt[i], bd[i], wt[i+1], wd[i+1], bElo, wElo))
        data.extend(gData)
    return data

#with open('basicFeatures_3_2', 'w+') as f : 
#    data = getBasicFeatures()
#    data = [str(i)+'\n' for i in data]
#    f.writelines(data)

