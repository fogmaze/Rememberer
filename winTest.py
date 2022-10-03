import os
import win
import tester

if __name__ == "__main__":
    win.checkPhoneReady()
    win.pullFile('highSchool.db')
    win.pullFile('records/')
    win.pullFile('tester_default.json')
    try:
        tester.test()
    finally:
        win.pushFile('highSchool.db')
        win.pushFile('records/')
        os.remove('highSchool.db')

