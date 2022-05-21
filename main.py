from bs4 import BeautifulSoup
from requests import get
from shutil import copyfileobj
from tkinter import filedialog, Tk
from os import mkdir
from threading import Thread


def select_file_path():
    root = Tk()
    root.withdraw()
    dir_path = filedialog.askdirectory()
    return dir_path


def extract_chapter_urls(url):
    parsed = BeautifulSoup(get(url).content, "html.parser")
    chapter_list = parsed.find("ul", class_="row-content-chapter").find_all("a", class_="chapter-name text-nowrap")
    chapter_urls = [i.get("href") for i in chapter_list if i.get("href")]
    return chapter_urls


def extract_image_urls(chapter_url):
    parsed = BeautifulSoup(get(chapter_url).content, "html.parser")
    title = parsed.find("div", class_="panel-chapter-info-top").find("h1").text.lower()
    return [i.get("src") for i in parsed.find_all("img") if i.get("title") and title in i.get("title").lower()]


def download_image(image_url, directory_path):
    file_path = f"{directory_path}/{image_url.split('/', -2)[-2]}/{image_url.split('/', -1)[-1]}"
    try:
        with open(file_path, "wb") as file:
            copyfileobj(get(image_url, headers={"Referer": "Referer: https://readmanganato.com/"}, stream=True).raw,
                        file)
    except FileNotFoundError:
        try:
            mkdir(f"{directory_path}/{image_url.split('/', -2)[-2]}")
        except FileExistsError:
            pass
        finally:
            download_image(image_url, directory_path)


def main():
    list_of_download_threads = []
    list_of_image_extract_threads = []
    url = input("URL: ")
    directory_path = select_file_path()

    def abc(k):
        for j in extract_image_urls(k):
            list_of_download_threads.append(Thread(target=download_image, args=(j, directory_path), daemon=True))

    for i in extract_chapter_urls(url):
        list_of_image_extract_threads.append(Thread(target=abc, args=(i,)))
    for i in list_of_image_extract_threads:
        i.start()
    for i in list_of_image_extract_threads:
        i.join()
    for i in list_of_download_threads:
        i.start()
    for i in list_of_download_threads:
        i.join()


if __name__ == '__main__':
    main()
