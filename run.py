import os
import time

count = 0
while True:
    ts = time.time()
    os.system ( 'Main2.py' )
    te = time.time()
    count += 1
    f = open ( 'score.txt' , 'r' )
    score = f.readline()
    f.close()
    s = 'ROUND: ' + str ( count ) + \
        ', score: ' + str ( score ) + \
        ', time: ' + str ( te - ts )
    print ( s )
    f = open ( 'log.txt' , 'a' )
    f.write ( s )
    f.write ( '\n' )
    f.close()