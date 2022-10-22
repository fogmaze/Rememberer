import time
import os
import sys
import posixpath
import parse
import subprocess

def checkPhoneReady():
    print('checking adb')
    if sys.platform == 'linux':
        global adb_path,root_dir
        root_dir = './'
        adb_path = 'adb'
    elif sys.platform != 'win32':
        print(sys.platform)
        raise Exception("OS error")
    while True:
        ret = subprocess.run(adb_path + " devices", shell=True,encoding='utf-8',stdout=subprocess.PIPE)
        res = ret.stdout
        try:
            ret.check_returncode()
        except Exception as e:
            print('adb error:')
            print(ret.stdout)

        device_parse = parse.parse('List of devices attached\n{}',res)
        if device_parse == None:
            raise Exception("adb not found")
        device_name = device_parse.fixed[0]
        device_len = len(device_name.split('\n'))-2

        if device_len == 1:
            if 'device' in device_name:
                global last_adb_check
                last_adb_check = time.time()
                print('adb ready!!!')
                break
            elif 'unauthorized' in device_name:
                print("unauthorized device")
            elif 'offline' in device_name:
                print('android device is offline')
            else:
                raise Exception("err")
        elif device_len == 0:
            print("no device found")
        else :
            print("device more than one")
        time.sleep(1)

def pullFile(src_from_project,dst_to_local=''):
    checkADBifNeccesary()
    if dst_to_local == '':
        dst_to_local = root_dir
    cmd = adb_path + " pull {} {}".format(posixpath.join(phone_project_path,src_from_project), dst_to_local)
    print('pulling file: ' + src_from_project)
    res = subprocess.run(cmd, shell=True, encoding='utf-8', stdout=subprocess.PIPE)
    try:
        res.check_returncode()
    except Exception as e:
        print('pull error')
        print(res.stdout)
        raise e

last_adb_check = 0
def checkADBifNeccesary():
    if time.time() - last_adb_check > 5:
        checkPhoneReady()


def pushFile(src_local,dst_to_project=''):
    checkADBifNeccesary()
    if not os.path.isfile(src_local) and not os.path.isdir(src_local):
        print('file not found:' + src_local)
        return
    cmd = adb_path + " push {} {}".format(src_local, posixpath.join(phone_project_path,dst_to_project) )
    print('pushing file: ' + src_local)
    res = subprocess.run(cmd, shell=True, encoding='utf-8', stdout=subprocess.PIPE)
    try:
        res.check_returncode()
    except Exception as e:
        print('push error')
        print(res.stdout)
        raise e

def uploadCode():
    files = [
        'core.py','operator_default.json','tester_default.json','tester.py','writer.py'
    ]
    for filename in files:
        pushFile(filename)

#constants
adb_path = 'platform-tools\\adb.exe'
phone_project_path = '/storage/emulated/0/qpython/projects3/rememberer'
root_dir = '.\\'

if __name__ == "__main__":
    checkPhoneReady()
    uploadCode()
    pass