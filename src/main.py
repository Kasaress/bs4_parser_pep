# main.py
import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_URL
from outputs import control_output
from utils import find_tag, get_response
from exceptions import FindLatestVersionException


def get_status_from_pep_page(session, link):
    """Делает запрос на страницу конкретного
       PEP, возвращает его статус."""
    response = get_response(session, link)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'html.parser')
    table = find_tag(soup, 'dl', attrs={'class': 'rfc2822 field-list simple'})
    return table.find(string='Status').parent.find_next_sibling('dd').string


def pep(session):
    """Парсинг статусов PEP."""
    response = get_response(session, PEP_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='html.parser')
    main_section = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    table = find_tag(main_section, 'tbody')
    rows = table.find_all('tr')
    results = [('Статус', 'Количество')]
    status_sum = {}
    total = 0
    for row in tqdm(rows):
        total += 1
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
        pep_status = get_status_from_pep_page(session, link)
        if pep_status not in preview_status:
            logging.warning(
                f'\nНесовпадающие статусы:\n'
                f'{link}\n'
                f'Статус в карточке: {pep_status}\n'
                f'Ожидаемые статусы: {preview_status}\n'
                )
        if status_sum.get(pep_status):
            status_sum[pep_status] += 1
        else:
            status_sum[pep_status] = 1
    results.extend((key, value) for key, value in status_sum.items())
    results.append(('total', total))
    return results


def whats_new(session):
    """Парсинг обновлений документации."""
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='html.parser')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li',
        attrs={'class': 'toctree-l1'}
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        version_link = urljoin(whats_new_url, version_a_tag['href'])
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, 'html.parser')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
    return results


def latest_versions(session):
    """Парсинг последней версии документации."""
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='html.parser')
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
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    """Загрузка документации в виде архива."""
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='html.parser')
    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag,
        'a',
        {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
