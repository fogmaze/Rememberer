import os
from time import sleep
import sync_file
import tester

if __name__ == "__main__":
    syncer = sync_file.WebSync()
    while os.path.isfile("highSchool.db"):
        print("Warn: database file already exists")
        sleep(1)
    sync_file.asyncio.run(syncer.getFromTarget('highSchool.db'))
    try:
        tester.test()
    except Exception as e:
        raise e
    finally:
        sync_file.asyncio.run(syncer.pushToTarget('highSchool.db'))
        while True:
            try:
                os.remove('highSchool.db')
            except:
                print('cannot remove db file')
                sleep(1)
            else:
                break
        pass

