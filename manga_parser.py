import re
import os
from pathlib import Path
import urllib.request
from curl_cffi import requests
def clear(): return os.system('cls')


session = requests.Session()
opened = False
base_url: str = "https://readmanga.me/"

save_path = "./manga"

def search_manga(search_query):
    url = base_url + "search/suggestion?"
    response = session.get(url + urllib.parse.urlencode({"query": search_query}))
    manga_list = response.json().get("suggestions")
    return manga_list


def choose_volume(manga_url):
    url = base_url + manga_url
    response = session.get(url)
    volumes_data = re.findall(
        r"\" item-title\".*?\s*?<a href=\"(.*?)\".*?>\s*(.*?)\s*<", response.text)[::-1]
    return volumes_data


def get_volume_images(volume_url):
    url = base_url + volume_url + "?mtr=true"
    response = session.get(url)
    images = eval(re.search(r"rm_h\.readerDoInit\((.*?), ", response.text).group(1))
    return images


def download_volume(images, manga_name, volume_name, offset=0):
    global opened
    manga_name = re.sub('[^a-zA-Zа-яA-Я\d -]', '', manga_name)
    volume_name = re.sub('[^a-zA-Zа-яA-Я\d -]', '', volume_name)
    Path(f"{save_path}/{manga_name}").mkdir(exist_ok=True)
    Path(f"{save_path}/{manga_name}/{volume_name}").mkdir(exist_ok=True)
    for n, image in enumerate(images):
        if n < offset: continue
        path = f"{save_path}/{manga_name}/{volume_name}/{n+1}.jpg"
        if Path(path).exists(): 
            if not opened: 
                os.startfile(os.path.normpath(path)) 
                opened = True
            continue
        urllib.request.urlretrieve(image[0] + image[1] + image[2], path)
        clear()
        print(manga_name)
        print(volume_name)
        print(f"Downloaded: {(((n+1)-offset)/((len(images)-offset)))*100:.2f}")
        if not opened:
            os.startfile(os.path.normpath(path))
            opened = True


def main():
    global opened
    while True:
        clear()
        search_name: str = input("Enter manga name: ")
        results = search_manga(search_name)
        for n, result in enumerate(results):
            print(f"({n + 1}) {result.get('value')}")
        try:
            choosen_manga = int(input("Enter manga number: ")) - 1
        except ValueError:
            continue
        manga_name = results[choosen_manga].get("value")
        manga_link = results[choosen_manga].get("link")
        volumes = choose_volume(manga_link)
        while True:
            clear()
            print(manga_name)
            for n, volume in enumerate(volumes):
                print(f"({n + 1}) {volume[1]}")
            try:
                choosen_volume = int(input("Enter volume number: ")) - 1
            except ValueError:
                break
            volume_name = volumes[choosen_volume][1]
            volume_link = volumes[choosen_volume][0]
            images = get_volume_images(volume_link)
            clear()
            print(manga_name)
            print(volume_name, f" ({len(images)} pages)")
            offset = input("Enter page offset: ")
            if not offset or offset == "0":
                offset = 0
            else:
                try:
                    offset = int(offset) - 1
                except ValueError:
                    continue
            clear()
            download_volume(images, manga_name, volume_name, offset)
            opened = False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear()
