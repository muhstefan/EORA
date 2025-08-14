from gigachat import GigaChat

from private import *


class GigaChatWrapper:

    """Класс обертка, для удобного использования GigaChat с NLP двигателем, для обработки информации"""
    def __init__(self, search_engine):
        self.search_engine = search_engine
        self.giga = GigaChat(credentials=authorize_key, verify_ssl_certs=False)

    @staticmethod
    def build_context_from_results(final_results):
        unique_urls = []
        url_to_num = {}

        for item in final_results:
            url = item.get('url', '')
            if url and url not in url_to_num:
                url_to_num[url] = len(unique_urls) + 1
                unique_urls.append(url)

        blocks_text = []
        for item in final_results:
            url = item.get('url', '')
            ref_num = url_to_num.get(url, None)
            ref_str = f"[{ref_num}]" if ref_num is not None else ""
            text = item['block_text'].strip()
            blocks_text.append(f"{text} {ref_str}")

        sources_lines = [f"[{i + 1}] {url}" for i, url in enumerate(unique_urls)]
        sources_text = "Источники информации:\n" + "\n".join(sources_lines) + "\n\n"
        context = sources_text + "\n\n".join(blocks_text)
        return context

    def query(self, user_query, threshold=0.2):
        final_results = self.search_engine.search(user_query, threshold=threshold)

        if not final_results:
            return "По вашему запросу релевантные данные не найдены."

        context = self.build_context_from_results(final_results)

        prompt = (
            f"{context}\n\n"
            f"Вопрос: {user_query}\n\n"
            "Пожалуйста, дай ответ на вопрос в виде пронумерованного списка основных пунктов.\n"
            "В конце ответа обязательно перечисли используемые источники в тексте в формате:\n"
            "[1] ссылка1\n"
            "[2] ссылка2\n"
            "Не используй гиперссылки или markdown-разметку, просто перечисли ссылки как текст.\n\n"
            "Ответ:"
        )

        response = self.giga.chat(prompt)

        return response.choices[0].message.content

    def close(self):
        self.giga.close()
