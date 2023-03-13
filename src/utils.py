from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import ParserFindTagException

MESSAGE_BROKEN_URL = 'Адрес {link} не вернул ожидаемый ответ'
ERROR_MESSAGE = 'Не найден тег {tag} {attrs}'


def get_soup(response_text):
    """Возвращает объект soup."""
    return BeautifulSoup(response_text, 'html.parser')


def get_response(session, url):
    """Делает запрос, возвращает ответ
       или перехватывает ошибку."""
    try:
        response = session.get(url)
        response.encoding = "utf-8"
        return response
    except RequestException:
        raise RequestException(MESSAGE_BROKEN_URL.format(link=url))


def find_tag(soup, tag, attrs=None):
    """Поиск тэга и перехват ошибки."""
    search_attributes = attrs if attrs is not None else {}
    searched_tag = soup.find(tag, attrs=(search_attributes))
    if searched_tag is None:
        raise ParserFindTagException(
            ERROR_MESSAGE.format(
                tag=tag,
                attrs=attrs
                )
            )
    return searched_tag
