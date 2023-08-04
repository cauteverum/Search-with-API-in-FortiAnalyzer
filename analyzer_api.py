import requests
import urllib3
import json 
from getpass import getpass
from time import sleep 

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class API: 
    def __init__(self): 
        self.uname = input("Username: ")
        self.passwd = getpass()
        self.url = "https://x.x.x.x/jsonrpc"
        self.sid:str
        self.tid:int
        self.response:json
        self.filter = input('Type any filter or leave blank (Example: srcip="192.168.1.9" AND service="HTTPS"): ')
        self.stime = input("Type start time or leave blank: (Example: 2023-06-09T17:16:35): ")
        self.etime = input("Type end time: or leave blank (Example: 2023-08-04T17:16:35 ): ")
        self.login()
        self.log_search()
        self.get_log()
        self.logout()
        self.writeIntoJsonFile()


    def login(self):
        req = {"id": 1, 
            "method": "exec",
            "params": [{"data": {"passwd": self.passwd, "user": self.uname}, 
                        "url": "/sys/login/user"}]}
        r = requests.post(url=self.url, json=req, verify=False, timeout=3)
        sid = r.json()["session"]
        self.sid = sid
        print("Session is established.")
    
    def log_search(self):
        req = {
            "id": "1",
            "jsonrpc": "2.0",
            "method": "add",
            "params": [
                {
                "apiver": 3,
                "case-sensitive": False,
                "device": [
                    {
                    "devid": "All_Devices",
                    "devname": ""
                    }
                ],
                "filter": self.filter,
                "logtype": "traffic",
                "time-order": "desc",
                "time-range": {
                    "end": self.etime,
                    "start": self.stime
                },
                "url": "/logview/adom/root/logsearch"
                }
            ],
            "session": self.sid
        }

        res = requests.post(url=self.url, json=req, verify=False)
        res = res.json()
        self.tid = res["result"]["tid"]
        sleep(1)

    def get_log(self):
        req = {
            "id": "1",
            "jsonrpc": "2.0",
            "method": "get",
            "params": [
                {
                "apiver": 3,
                "limit": 1000,
                "offset": 0,
                "url": "/logview/adom/root/logsearch/" + str(self.tid)
                }
            ],
            "session": self.sid 
        }

        res = requests.post(url=self.url, json=req, verify=False)
        self.response = res.json()

    def logout(self):
        req = {"id": 1, 
            "method": "exec", 
            "params": [{"url": "/sys/logout"}], 
            "session": self.sid}
        r = requests.post(url=self.url, json=req, verify=False, timeout=3)
        #print(r.json())
        print("Session was closed. ")
    
    def writeIntoJsonFile(self): 
        with open(file="results.json",mode="w",encoding="utf-8") as file: 
            json.dump(obj=self.response, fp=file, indent=4)
        print(f"{len(self.response['result']['data'])} logs was ingested. ")


instance = API()