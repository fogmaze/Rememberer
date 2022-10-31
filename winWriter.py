import os
import win
import writer

if __name__ == "__main__":
    win.pullFile('operator_default.json')
    win.pullFile('highSchool.db')
    try:
        writer.operate()
    finally:
        win.pushFile('operator_default.json')
        win.pushFile('highSchool.db')
        while True:
            try:
                os.remove('highSchool.db')
            except:
                print('cannot remove db file')
            else:
                break
