import requests
from abc import ABC,abstractclassmethod

class Syncer(ABC):
    @abstractclassmethod
    def getFromTarget(self,filename):
        pass
    @abstractclassmethod
    def pushToTarget(self,filename):
        pass
    
class WebSync(Syncer):
    def __init__(self):
        self.HOST = "192.168.66.23"
        r = input("connect to {}? enter or input address".format(self.HOST))
        if not r == "":
            self.HOST = r
    
    def getFromTarget(self,filename:str):
        res = requests.get("http://{}:{}/{}",self.HOST,3520,filename)
        

