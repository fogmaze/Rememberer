if __name__ == "__main__":
    prompt="""w -> write
s -> start server
else -> test"""
    cmd = input(prompt)
    if cmd == "w":
        import writer
        writer.operate()
    elif cmd == "s":
        import webServer
        webServer.startServer()
    else:
        import tester
        tester.test()
