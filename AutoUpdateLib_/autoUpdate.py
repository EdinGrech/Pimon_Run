import AutoUpdateLib_.AutoUpdateLib as AutoUpdateLib
import os
import sys
import pathlib
path = str(f"{pathlib.Path().resolve()}/Pimon_Run")
url_mothership = "https://raw.githubusercontent.com/EdinGrech/Pimon_Run/master/"
AutoUpdateLib.set_url("https://raw.githubusercontent.com/EdinGrech/Pimon_Run/master/version.txt")

def get_update_file_list():
    update_list = [] #"file names"
    with open(f"{path}/updateFiles.txt", "r") as f:
        for line in f:
            update_list.append(line)
        f.close()
    return update_list
        
#read current verson from local file version.txt
def get_current_version():
    with open(str(f"{path}/version.txt"), "r") as f:
        AutoUpdateLib.set_current_version(f.read())
        f.close()

def file_updater(update_list):
    for file in update_list:
        AutoUpdateLib.set_download_link(str(f"{url_mothership}{file}")) #set the download link
        AutoUpdateLib.download(str(f"{path}/{file}")) #if the version is up to date we just start the program

def update_sequence():
    get_current_version()
    if not AutoUpdateLib.is_up_to_date():
        file_updater(["updateFiles.txt"])#fisrt we update the list of things that need to be updated
        file_updater(get_update_file_list())#then we update the files
        with open(str(f"{path}/version.txt"), "w") as f: #and finally we update the version file
            f.write(AutoUpdateLib.get_latest_version())
            f.close()
        print("Update complete")
        os.system('{} {}'.format('python', str(f"{path}/PiMon_Main.py"))) #os.system(str(f"{path}/PiMon_Main.py")) #and we start the new version
        os._exit(1)

        
