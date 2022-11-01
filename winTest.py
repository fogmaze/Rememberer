import os
from time import sleep
import win
import tester

if __name__ == "__main__":
    win.pullFile('highSchool.db')
    win.pullFile('tester_default.json')
    try:
        tester.test()
    finally:
        win.pushFile('highSchool.db')
        win.pushFile('tester_default.json')
        while True:
            try:
                os.remove('highSchool.db')
            except:
                print('cannot remove db file')
                sleep(1)
            else:
                break
        pass
