from os import path
import requests
import subprocess

def requestHandeler(token):
    if token.status_code == 200:
        token = token.json()["token"]
        return token
    elif token.status_code == 400 or token.status_code == 469:
        print(token.json()["error"])
        return False

def configSetUp():
    if path.exists("Pimon_Run/.env") == False:
        subprocess.run("pip install -r Pimon_Run/requirements.txt", shell=True)
        apiUrl = "http://" + input("Enter the IP address of the API: ") + ":5000/"
        token = None
        while True:
            if token == None or requestHandeler(token)==False:
                device_Name = input("Enter a unique Device name: ")
                apiUrl = apiUrl + "deviceName/" + device_Name
                token = "Error"
                try:
                    token = requests.get(url=apiUrl)
                except:
                    print("Connection timed out try again later")
                    
                if token.status_code == 200:
                    token = token.json()["token"]
                    with open("Pimon_Run/config.env", "w") as f:
                        f.write(f"token = {token}")
                    f.close()
                elif token.status_code == 400:
                    print(token.json()["error"])
                elif token.status_code == 469:
                    print(token.json()["error"])
            else:
                break
    
        