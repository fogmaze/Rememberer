import socket

PORT = 2060
def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    ip = s.getsockname()[0]
    s.close()
    return ip

if __name__ == "__main__":
    try:
        ip = getIP()
        print("start server by ip: {}".format(ip))
        HOST = ip
    except :
        print('cannot get ip')
        ip = socket.gethostbyname(socket.gethostname())
        print("start server by ip:", ip)
        HOST = ip

    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind((HOST,PORT))
    s.listen(1)
    while True:
        conn,addr = s.accept()
        print("connect by: {}".format(addr))
        b_filename = conn.recv(128)
        filename = b_filename.decode("utf-8")


    