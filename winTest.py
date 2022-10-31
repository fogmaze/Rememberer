import os
import win
import tester

if __name__ == "__main__":
    win.pullFile('highSchool.db')
    win.pullFile('records/')
    win.pullFile('tester_default.json')
    try:
        tester.test()
    finally:
        win.pushFile('highSchool.db')
        win.pushFile('records/')
        win.pushFile('tester_default.json')
        while True:
            try:
                os.remove('highSchool.db')
            except:
                print('cannot remove db file')
            else:
                break
        pass
