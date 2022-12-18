import asyncio
from time import sleep
import os
import sync_file
import writer

if __name__ == "__main__":
    syncer = sync_file.WebSync()
    while os.path.isfile("highSchool.db"):
        print("Warn: database file already exists")
        sleep(1)
    asyncio.run(syncer.getFromTarget('highSchool.db'))
    try:
        writer.operate()
    finally:
        asyncio.run(syncer.pushToTarget('highSchool.db'))
        while True:
            try:
                os.remove('highSchool.db')
            except:
                print('cannot remove db file')
                sleep(1)
            else:
                break