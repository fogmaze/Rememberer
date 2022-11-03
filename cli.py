import socket


HOST = "192.168.66.23"
if __name__ == "__main__":
    conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    conn.connect((HOST,2060))
    print("connected")