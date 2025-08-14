from MyLibs.CompositeDataBase import SingletonMeta


class CompositeData(metaclass=SingletonMeta):
    def __init__(self):
        self.pages = []

    def add_page(self, page):
        self.pages.append(page)

class Page:

    counter = 0

    def __init__(self, title, url, text):
        self.id = self.counter  # Присваиваем текущий номер
        self.title = title
        self.url = url
        self.text = text
        Page.counter += 1

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'text': self.text
        }

base_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "cache-control": "max-age=0",
    "if-modified-since": "Thu, 05 Jun 2025 08:14:43 GMT",
    "if-none-match": "\"be36b-636ceb4b80493-gzip\"",
    "priority": "u=0, i",
    "sec-ch-ua": "\"Not;A=Brand\";v=\"99\", \"Google Chrome\";v=\"139\", \"Chromium\";v=\"139\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1"
  }