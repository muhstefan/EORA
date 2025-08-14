import asyncio
import json
import os

from bs4 import BeautifulSoup
from nltk.corpus import *

from MyLibs.aioclient import AioClient
from MyLibs.processor import Strategy
from data import *
from giga import GigaChatWrapper
from nlp_module import TextSearchEngine


class ParsePage(Strategy):
    """Класс предназначенный для обработки полученных данных в нашем случае страницы сервиса EORA
    parse() Ключевой метод.
    """

    NOISE_PHRASES = [
        "Напишите нам",
        "Нажимая на кнопку, вы соглашаетесь с нашейПолитикой в отношении обработкиперсональных данных пользователя",
        "Нажимая на кнопку, вы соглашаетесь с нашейПолитикой в отношении обработкиперсональных данных пользователей"
        "Все права защищены",
        "Позвоните нам",
        "Политика в отношении обработки персональных данных",
        "Иннополис",
        "ул. Университетская, д. 7",
        "И наши менеджеры ответят на ваши вопросы",
        "Заполните форму"
    ]

    def parse(self):

        soup = BeautifulSoup(self.get_html(), 'html.parser')
        field_pattern = re.compile(r'^tn_text_')
        url = self.get_url()

        texts = []
        for el in soup.find_all(attrs={'field': field_pattern}):
            text_content = el.get_text(strip=True)
            if text_content:
                # Фильтруем служебные/шумовые фразы
                if any(phrase in text_content for phrase in self.NOISE_PHRASES):
                    continue
                texts.append(text_content)

        h1 = soup.find('h1', attrs={'field': field_pattern})
        title = h1.get_text(strip=True) if h1 else 'No title'

        # Включил заголовок в наш текст, чтобы повысить шансы поиска.
        full_text = f"{title}\n{'\n'.join(texts)}"

        new_page = Page(title=title, url=url, text=full_text)

        self.get_main_data().add_page(new_page)


# Сохраняем полученные данные
def save_pages_to_json(pages, filename="json_data.json"):
    pages_data = [page.to_dict() for page in pages]

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(pages_data, f, ensure_ascii=False, indent=2)


# Читаем ссылки из txt
def read_links():
    file_path = 'links.txt'

    links = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                links.append(line)

    return links

# Фильтрация пробела nbsp
def pages_filter(pages):
    for page in pages:
        page.title = page.title.replace('\u00A0', ' ')
        page.text = page.text.replace('\u00A0', ' ')


def main_funk():
    main_client = AioClient(CompositeData)
    data = CompositeData()
    links = read_links()

    main_client.set_headers(base_headers). \
        set_request_mode(main_client.REQ_MODE_GET_HTML). \
        set_url_template("{modification}"). \
        set_url_modifications(links). \
        set_strategy(ParsePage)
    asyncio.run(main_client.main_async())

    pages_filter(data.pages)
    save_pages_to_json(data.pages)


if not os.path.exists("json_data.json"):
    main_funk()

main_engine = TextSearchEngine()
chat_wrapper = GigaChatWrapper(main_engine)
try:
    while True:
        query = input("\n\nВведите ваш запрос(q - для выхода):\n\n").strip()
        if not query:
            print("Пустой запрос, попробуйте еще раз.")
            continue
        if query == "q":
            break

        response_text = chat_wrapper.query(query)
        print("\nОтвет GPT:\n")
        print(response_text)
        print("\n" + "-" * 50 + "\n")
finally:
    chat_wrapper.close()
