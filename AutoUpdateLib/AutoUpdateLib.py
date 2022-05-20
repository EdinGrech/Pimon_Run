import urllib.request

def set_url(url_):
    global url; url = url_

def get_latest_version():
    file = urllib.request.urlopen(url)

    lines = ""
    for line in file:
        lines += line.decode("utf-8")

    return lines

def set_current_version(current_):
    global current; current = current_

def set_download_link(link):
    global download_link; download_link = link

def is_up_to_date():
    return current + "\n" == get_latest_version()

def download(path_to_file):
    urllib.request.urlretrieve(download_link,path_to_file)