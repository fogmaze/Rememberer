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

    ret = subprocess.run(adb_path + " devices", shell=True,encoding='utf-8',stdout=subprocess.PIPE)
    res = ret.stdout
    try:
        ret.check_returncode()
    except Exception as e:
        print(ret.stdout)
        raise e

    device_parse = parse.parse('List of devices attached\n{}',res)
    if device_parse == None:
        raise Exception("adb not found")
    device_name = device_parse.fixed[0]
    device_len = len(device_name.split('\n'))-2

    if device_len == 1:
        if 'device' in device_name:
            global phone_checked
            phone_checked = True
            print('adb ready!!!')
        elif 'unauthorized' in device_name:
            raise Exception("unauthorized device")
        else:
            raise Exception("err")
    elif device_len == 0:
        raise Exception("no device found")
    else :
        raise Exception("device more than one")

def pullFile(src_from_project,dst_to_local=''):
    if not phone_checked:
        raise Exception("please check first")
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


def pushFile(src_local,dst_to_project=''):
    if not phone_checked:
        raise Exception("please check first")
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
phone_checked = False
root_dir = '.\\'

if __name__ == "__main__":
    checkPhoneReady()
    uploadCode()
    pass