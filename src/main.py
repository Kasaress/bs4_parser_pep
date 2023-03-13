import logging
import re
from collections import defaultdict
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_URL
from exceptions import FindLatestVersionException
from outputs import control_output
from utils import find_tag, get_response, get_soup

MESSAGE_UNEXPECTED_STATUS = ('\nНесовпадающие статусы:'
                             '\n{link}\nСтатус в карточке: {pep_status}'
                             '\nОжидаемые статусы: {preview_status}\n')
MESSAGE_BROKEN_URL = 'Адрес {link} не вернул ожидаемый ответ'
MESSAGE_SUCCESS_SAVE = 'Архив был загружен и сохранён: {path}'
MESSAGE_START = 'Парсер запущен!'
MESSAGE_FINISH = 'Парсер завершил работу.'
MESSAGE_ARGS = 'Аргументы командной строки: {args}'
MESSAGE_ERROR = 'Во время исполнения скрипта произошла ошибка: {error}'


def pep(session):
    """Парсинг статусов PEP."""
    response = get_response(session, PEP_URL)
    if response is None:
        logging.error(MESSAGE_BROKEN_URL.format(link=PEP_URL))
        return
    soup = get_soup(response.text)
    rows = soup.select('#numerical-index tbody tr')
    statuses = defaultdict(int)
    for row in tqdm(rows):
        status_tag, number_tag, *_ = row.find_all('td')
        status = status_tag.text[1:]
        preview_status = (EXPECTED_STATUS.get(status) if len(status)
                          else EXPECTED_STATUS.get(''))
        link = urljoin(
            PEP_URL,
            find_tag(
                number_tag,
                'a',
                attrs={'class': 'pep reference internal'})['href']
            )
        response = get_response(session, link)
        if response is None:
            logging.error(MESSAGE_BROKEN_URL.format(link=link))
            return
        soup = get_soup(response.text)
        table = find_tag(
            soup,
            'dl',
            attrs={'class': 'rfc2822 field-list simple'}
        )
        pep_status = str(
            table.find(string='Status').parent.find_next_sibling('dd').string
        )
        statuses[pep_status] += 1
    for status in statuses:
        if status not in preview_status:
            logging.warning(
                MESSAGE_UNEXPECTED_STATUS.format(
                    link=link,
                    pep_status=pep_status,
                    preview_status=preview_status
                    )
                )
    return [
        ('Статус', 'Количество'),
        *statuses.items(),
        ('Всего', sum(statuses.values())),
    ]


def whats_new(session):
    """Парсинг обновлений документации."""
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        logging.error(MESSAGE_BROKEN_URL.format(link=whats_new_url))
        return
    soup = get_soup(response.text)
    sections_by_python = soup.select(
        '#what-s-new-in-python div.toctree-wrapper li.toctree-l1'
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_link = urljoin(whats_new_url, find_tag(section, 'a')['href'])
        response = get_response(session, version_link)
        if response is None:
            logging.error(MESSAGE_BROKEN_URL.format(link=version_link))
            continue
        soup = get_soup(response.text)
        results.append(
            (
                version_link,
                find_tag(soup, 'h1').text,
                find_tag(soup, 'dl').text.replace('\n', ' ')
                )
        )
    return results


def latest_versions(session):
    """Парсинг последней версии документации."""
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        logging.error(MESSAGE_BROKEN_URL.format(link=MAIN_DOC_URL))
        return
    soup = get_soup(response.text)
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' not in ul.text:
            raise FindLatestVersionException('Ничего не нашлось')
        a_tags = ul.find_all('a')
        break
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (a_tag['href'], version, status)
        )
    return results


def download(session):
    """Загрузка документации в виде архива."""
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        logging.error(MESSAGE_BROKEN_URL.format(link=downloads_url))
        return
    soup = get_soup(response.text)
    pdf_a4_link = soup.select_one(
        'table.docutils a[href$="pdf-a4.zip"]'
    )['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    #  pytest падает, если использовать константу вместо создания папки
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(MESSAGE_SUCCESS_SAVE.format(path=archive_path))


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info(MESSAGE_START)
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(MESSAGE_ARGS.format(args=args))
    try:
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results is not None:
            control_output(results, args)
    except Exception as error:
        logging.exception(MESSAGE_ERROR.format(error=error))
    logging.info(MESSAGE_FINISH)


if __name__ == '__main__':
    main()
