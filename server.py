import asyncio
import os
import socket

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

def splitCMD(cmd):
    inStr = False
    cmdList = [""]
    for s in cmd:
        if s == '"':
            inStr = not inStr
            continue
        if s == " " and not inStr:
            cmdList.append("")
            continue
        cmdList[-1] += s
    return cmdList

#get "filename"

async def handle_callback(reader, writer):
    reciever = DataReciever(reader)
    sender = DataSender(writer)

    cmd = (await reciever.recieve()).decode()

    if cmd == "bye":
        return 0
    if "get" in cmd:
        filename = splitCMD(cmd)[1]
        if os.path.isfile(filename):
            sender.send("file found".encode())

            with open(filename,"rb") as f:
                sender.send(f.read())
        elif os.path.isdir(filename):
            sender.send("dir found".encode())

            for root,dirs,files in os.walk(filename):
                for file in files:
                    with open(os.path.join(root,file),"rb") as f:
                        sender.send('{}'.format(os.path.join(root,file)).encode())
                        if os.path.getsize(os.path.join(root,file)) == 0:
                            continue
                        sender.send(f.read())
            sender.send("dir end".encode())
        else:
            print("file not found {}".format(filename))
            sender.send("file not found".encode())
    if "put" in cmd:
        if "file" in cmd:
            filename = splitCMD(cmd)[2]
            with open(filename,"wb") as f:
                f.write(await reciever.recieve())
        if "dir" in cmd:
            dirname = splitCMD(cmd)[2]
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            while True:
                filename = (await reciever.recieve()).decode()
                if filename == "dir end":
                    break
                with open(os.path.join(dirname,filename),"wb") as f:
                    f.write(await reciever.recieve())
        return 1
    else:
        return 1

def getIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


async def main():
    port = 3506
    ip = getIp()

    server = await asyncio.start_server(handle_callback, host=ip,port=port)
    print("Server started at %s" % ip)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    print(len(b"hello"))
    asyncio.run(main(),debug=True)