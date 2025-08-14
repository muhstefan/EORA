import asyncio
import aiohttp


class AioClient:
    """Клиент, выполняющий асинхронные GET-запросы для получения JSON или HTML"""

    REQ_MODE_GET_JSON = "get_json"
    REQ_MODE_GET_HTML = "get_html"

    def __init__(self, main_data):
        self._session = None
        self._headers = None
        self._req_mode = None
        self._url_template = None
        self._url_modifications = None
        self._strategy_cls = None  # класс стратегии для парсинга
        self._main_data = main_data  # контейнер данных (синглтон)

    async def _fetch(self, url):
        async with self._session.get(url, headers=self._headers) as response:
            await self._process_response(response, url)

    async def _process_response(self, response, url):
        status = response.status

        if self._req_mode == self.REQ_MODE_GET_HTML:
            text_data = await response.text()

            parse_with_strategy(
                html=text_data,
                json=None,
                url=url,
                status=status,
                main_data=self._main_data,  # передаем синглтон сюда
                strategy_cls=self._strategy_cls
            )
        elif self._req_mode == self.REQ_MODE_GET_JSON:
            json_data = await response.json()

            parse_with_strategy(
                html=None,
                json=json_data,
                url=url,
                status=status,
                main_data=self._main_data,  # передаем синглтон сюда
                strategy_cls=self._strategy_cls
            )


    async def main_async(self):
        async with aiohttp.ClientSession() as session:
            self._session = session
            tasks = []
            for modification in self._url_modifications:
                url = self._url_template.format(modification=modification)
                tasks.append(self._fetch(url))
            await asyncio.gather(*tasks)

    # Методы настройки клиента...
    def set_request_mode(self, req_mode):
        self._req_mode = req_mode
        return self

    def set_url_modifications(self, url_modifications):
        self._url_modifications = url_modifications
        return self

    def set_strategy(self, strategy_cls):
        self._strategy_cls = strategy_cls
        return self

    def set_url_template(self, url_template):
        self._url_template = url_template
        return self

    def set_headers(self, headers):
        self._headers = headers
        return self

    def get_main_data(self):
        return self._main_data


# Вспомогательная функция для вызова стратегии
def parse_with_strategy(html=None, json=None, url=None, status=None, main_data=None, strategy_cls=None):
    if strategy_cls is None:
        raise ValueError("strategy_cls must be provided")

    processor_data = {
        'html': html,
        'json': json,
        'url': url,
        'status': status,
        'main_data_cls': main_data,
    }
    strat_instance = strategy_cls(processor_data)
    return strat_instance.parse()