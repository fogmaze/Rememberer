from time import sleep
import os
import win
import writer

if __name__ == "__main__":
    while os.path.isfile("highSchool.db"):
        print("Warn: database file already exists")
        sleep(1)
    win.pullFile('highSchool.db')
    try:
        writer.operate()
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
