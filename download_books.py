import os
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filepath
import requests
from requests import Response


def download_txt(url: str, filename: str, folder: str = "books/") -> str:
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    filepath = os.path.join(folder, filename)
    clear_filepath = sanitize_filepath(filepath)
    with open(clear_filepath, "wb") as file:
        file.write(response.content)
    return filepath


def download_image(url: str, folder: str = "images/") -> None:
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    filename = urlsplit(url).path.split("/")[-1]
    filepath = os.path.join(folder, filename)
    clear_filepath = sanitize_filepath(filepath)
    with open(clear_filepath, "wb") as file:
        file.write(response.content)


def get_title_params_from_book(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    table = soup.find("body").find("table")
    image = soup.find(class_="bookimage").find("img")["src"]
    image_url = urljoin("http://tululu.org/", image) 
    title = table.find("h1")
    splited_title = title.text.split("::")
    book_title = splited_title[0].strip().lstrip("\xa0")
    return book_title, image_url  # use named tuple


def check_for_redirect(response: Response) -> None:
    if response.history:
        raise requests.HTTPError


def main() -> None:
    book_ids = list(range(1, 11))
    image_url = get_title_params_from_book(f"https://tululu.org/b9/")[1]
    download_image(image_url)
    for book_id in book_ids:
        url = f"https://tululu.org/txt.php?id={book_id}"
        try:
            title = get_title_params_from_book(f"https://tululu.org/b{book_id}/")[0]
            download_txt(url, f"{book_id}.{title}.txt")
            image_url = get_title_params_from_book(f"https://tululu.org/b{book_id}/")[1]
            download_image(image_url)
            print(title)
            print(image_url)
        except:
            continue

if __name__ == "__main__":
    main()

