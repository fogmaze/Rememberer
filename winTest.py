import os
from time import sleep
import win
import tester

if __name__ == "__main__":
    win.pullFile('highSchool.db')
    try:
        tester.test()
    finally:
        win.pushFile('highSchool.db')
        while True:
            try:
                os.remove('highSchool.db')
            except:
                print('cannot remove db file')
                sleep(1)
            else:
                break
        pass
