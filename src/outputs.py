import csv
import datetime as dt
import logging
from csv import unix_dialect

from prettytable import PrettyTable

from constants import (
    BASE_DIR, DATETIME_FORMAT, DEFAUT_OUTPUT, FILE_OUTPUT,
    PRETTY_OUTPUT, RESULTS_DIR
)

MESSAGE_SUCCESS_SAVE = 'Файл с результатами сохранён: {path}'


def file_output(results, cli_args):
    """Вывод результата в csv файл."""
    results_dir = BASE_DIR / RESULTS_DIR
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f"{parser_mode}_{now_formatted}.csv"
    file_path = results_dir / file_name
    with open(file_path, "w", encoding="utf-8") as f:
        csv.writer(
            f, dialect=unix_dialect
        ).writerows(
            results
        )
    logging.info(MESSAGE_SUCCESS_SAVE.format(path=file_path))


def pretty_output(results, cli_args=None):
    """Вывод результа в консоль в виде таблицы."""
    table = PrettyTable()
    table.field_names = results[0]
    table.align = "l"
    table.add_rows(results[1:])
    print(table)


def default_output(results, cli_args=None):
    """Вывод результата в консоль"""
    for row in results:
        print(*row)


OUTPUT_FORMAT = {
    PRETTY_OUTPUT: pretty_output,
    FILE_OUTPUT: file_output,
    DEFAUT_OUTPUT: default_output
}


def control_output(results, cli_args):
    """Определяет формат вывода результатов."""
    OUTPUT_FORMAT.get(cli_args.output)(results, cli_args)
