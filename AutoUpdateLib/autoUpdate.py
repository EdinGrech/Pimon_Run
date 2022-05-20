import AutoUpdateLib as AutoUpdate
import subprocess
import sys
import pathlib
path = pathlib.Path().resolve()
url_mothership = "https://github.com/EdinGrech/Pimon_Run/blob/master/"
AutoUpdate.set_url("https://github.com/EdinGrech/Pimon_Run/blob/master/version.txt")

def get_update_file_list():
    update_list = [] #"file names"
    with open("updateFiles.txt", "r") as f:
        for line in f:
            update_list.append(line)
        f.close()
    return update_list
        
#read current verson from local file version.txt
def get_current_version():
    with open(str(f"{path}\\version.txt"), "r") as f:
        AutoUpdate.set_current_version(f.read())
        f.close()

def file_updater(update_list):
    for file in update_list:
        url_file = file.replace('\\', '/')
        AutoUpdate.set_download_link(str(f"{url_mothership}{url_file}")) #set the download link
        AutoUpdate.download(str(f"{path}\\{file}")) #if the version is up to date we just start the program

def update_sequence():
    get_current_version()
    if not AutoUpdate.is_up_to_date():
        file_updater(["updateFiles.txt"])#fisrt we update the list of things that need to be updated
        file_updater(get_update_file_list())#then we update the files
        with open(str(f"{path}\\version.txt"), "w") as f: #and finally we update the version file
            f.write(AutoUpdate.get_latest_version())
            f.close()
        print("Update complete")
        subprocess.Popen(str(f"{path}\\PiMon_Main.py")) #and we start the new version
        sys.exit(exit_code=0)

        
