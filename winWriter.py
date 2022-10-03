import os
import win
import writer

if __name__ == "__main__":
    win.checkPhoneReady()
    win.pullFile('operator_default.json')
    win.pullFile('highSchool.db')
    try:
        writer.operate()
    finally:
        win.pushFile('operator_default.json')
        win.pushFile('highSchool.db')
        os.remove('highSchool.db')
