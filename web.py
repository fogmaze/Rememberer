import socket

def sendFileData(filename:str,context:bytes):
    conn = connect()
    conn.sendall("send_file")
    conn.sendall(filename.encode("utf-8"))
    conn.sendall(context)

def pullFile(filename:str):
    with open(filename,)
    conn = connect()
    conn.sendall(b"require_file")
    conn.sendall(filename.encode("utf-8"))
    recv  = conn.recv(1024).decode("utf-8")
    if recv == "OK":
        while True:
            data = conn.recv(1024)
            if not data:
                break
            
    else:
        print(recv)
        raise


def connect():
    conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    conn.connect(ADDRESS)
    return conn
def pushFile(src_local:str,dst_to_project=""):
    with open(src_local,'rb') as f:
        conn = connect()
        conn.sendall(src_local.encode("utf-8"))
        conn.sendall(f.read())
def pullFile(src_from_project,dst_to_local=''):
    
    with open(,'wb') as f:
        conn = connect()
        conn.sendall(src_local.encode("utf-8"))
        conn.sendall(f.read())

def getAddress():
    return ("192.168.66.23", 2060)
ADDRESS = getAddress()
