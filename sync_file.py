import socket
import os
from abc import ABC,abstractclassmethod
import asyncio

class Syncer(ABC):
    @abstractclassmethod
    def getFromTarget(self,filename):
        pass
    @abstractclassmethod
    def pushToTarget(self,filename):
        pass
    
class DataSender:
    def __init__(self,writer:asyncio.StreamWriter):
        self.writer = writer
    def send(self,data:bytes):
        self.writer.write(str(len(data)).encode() + b" " + data)
class DataReciever:
    def __init__(self,reader:asyncio.StreamReader):
        self.reader = reader
    async def recieve(self):
        nextlen = int((await self.reader.readuntil(b' ')).decode())
        return await self.reader.readexactly(nextlen)

class WebSync(Syncer):
    @staticmethod
    def getIp():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    def __init__(self):
        self.HOST = "192.168.66.21"
        print("connect to {}? enter or input address".format(self.HOST))
        r = input()
        if not r == "":
            if r[0:2] == '--':
                self.HOST = "192.168.66." + r[2:]
            if r[0] == '-':
                self.HOST = "192.168.66." + r[1:]
            else:
                self.HOST = r
        self.PORT = 3506
        self.is_connected = False
        
    async def connectToTarget(self):
        if self.is_connected:
            return
        self.reader = None
        self.writer = None
        while not self.is_connected:
            try:
                self.reader, self.writer = await asyncio.open_connection(self.HOST,self.PORT)
                self.reciever = DataReciever(self.reader)
                self.sender = DataSender(self.writer)
                self.is_connected = True
            except ConnectionRefusedError as e:
                print("connection refused")
    
    async def disconnectFromTarget(self):
        if not self.is_connected:
            return
        self.writer.close()
        await self.writer.wait_closed()
        self.reciever = None
        self.sender = None
        self.is_connected = False

    async def getFromTarget(self,filename:str):
        await self.connectToTarget()
        self.sender.send("get {}".format(filename).encode())
        data = await self.reciever.recieve()
        if data == b"file found":
            with open(filename,"wb") as f:
                f.write(await self.reciever.recieve())
        elif data == b"dir found":
            if not os.path.isdir(filename):
                os.makedirs(filename)
            while True:
                rec = await self.reciever.recieve()
                if rec == b"dir end":
                    break
                filename = rec
                with open(filename,"wb") as f:
                    f.write(await self.reciever.recieve())
        elif data == b"file not found":
            print("file not found")
        else:
            print("unknown error")
            print(data)
        await self.disconnectFromTarget()
    
    async def pushToTarget(self,filename:str):
        print('pushing ' + filename)
        await self.connectToTarget()
        if os.path.isfile(filename):
            self.sender.send('put file "{}"'.format(filename).encode())
            with open(filename,"rb") as f:
                self.sender.send(f.read())
        if os.path.isdir(filename):
            self.sender.send('put dir "{}"'.format(filename).encode())
            for root,dirs,files in os.walk(filename):
                for file in files:
                    self.sender.send("{}".format(file).encode())
                    with open(os.path.join(root,file),"rb") as f:
                        self.sender.send(f.read())
            self.sender.send("dir end".encode())
        await self.disconnectFromTarget()

if __name__ == "__main__":
    syncer = WebSync()
    asyncio.run(syncer.pushToTarget("highSchool.db"))