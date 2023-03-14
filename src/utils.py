from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import ParserFindTagException

MESSAGE_BROKEN_URL = 'Адрес {link} не вернул ожидаемый ответ'
ERROR_MESSAGE = 'Не найден тег {tag} {attrs}'


def get_soup(session, url, features='html.parser'):
    """Возвращает объект soup."""
    return BeautifulSoup(get_response(session, url).text, features)


def get_response(session, url, encoding="utf-8"):
    """Делает запрос, возвращает ответ
       или перехватывает ошибку."""
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException:
        raise ConnectionError(MESSAGE_BROKEN_URL.format(link=url))


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
