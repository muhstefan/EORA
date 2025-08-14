class Strategy:
    def __init__(self, processor_data):
        """
        Конструктор принимает словарь с данными:
        {
            'html': str или None,
            'json': dict или None,
            'url': str,
            'status': int,
            'main_data': класс данных
        }
        """
        self.processor_data = processor_data

    def get_html(self):
        return self.processor_data.get('html')

    def get_json(self):
        return self.processor_data.get('json')

    def get_url(self):
        return self.processor_data.get('url')

    def get_status(self):
        return self.processor_data.get('status')

    @property
    def main_data_cls(self):
        # Можно вернуть класс структуры данных, если он нужен в стратегии
        return self.processor_data.get('main_data_cls')

    def get_main_data(self):
        if self.main_data_cls:
            return self.main_data_cls()
        return None

    def parse(self):
        """
        Здесь должна быть основная логика парсинга,
        обязательно переопределяется в наследниках.

        По умолчанию — бросаем исключение,
        чтобы точно знать, что метод не реализован.
        """
        raise NotImplementedError("Метод parse() должен быть реализован в наследнике")