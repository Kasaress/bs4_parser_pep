import csv
import datetime as dt
import logging
from csv import unix_dialect

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT, FILE_OUTPUT, PRETTY_OUTPUT


def file_output(results, cli_args):
    """Вывод результата в csv файл."""
    results_dir = BASE_DIR / "results" # pytest падает, если использовать константу вместо создания папки
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f"{parser_mode}_{now_formatted}.csv"
    file_path = results_dir / file_name
    with open(file_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f, dialect=unix_dialect)
        writer.writerows(results)
    logging.info(f"Файл с результатами был сохранён: {file_path}")


def pretty_output(results):
    """Вывод результа в консоль в виде таблицы."""
    # import sys
    # sys.setrecursionlimit(100000)
    try:
        table = PrettyTable()
        table.field_names = results[0]
        table.align = "l"
        table.add_rows(results[1:])
        print(table)
    except Exception as e:
        print(e)

def default_output(results):
    """Вывод результата в консоль"""
    for row in results:
        print(*row)


def control_output(results, cli_args):
    """Определяет формат вывода результатов."""
    if cli_args.output == PRETTY_OUTPUT:
        pretty_output(results)
    elif cli_args.output == FILE_OUTPUT:
        file_output(results, cli_args)
    else:
        default_output(results)
