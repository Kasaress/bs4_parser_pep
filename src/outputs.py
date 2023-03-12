import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT


def file_output(results, cli_args):
    """Вывод результата в csv файл."""
    results_dir = BASE_DIR / "results"
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f"{parser_mode}_{now_formatted}.csv"
    file_path = results_dir / file_name
    with open(file_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f, dialect="unix")
        writer.writerows(results)
    logging.info(f"Файл с результатами был сохранён: {file_path}")


def pretty_output(results):
    """Вывод результа в консоль в виде таблицы."""
    table = PrettyTable()
    table.field_names = results[0]
    table.align = "l"
    table.add_rows(results[1:])
    print(table)


def default_output(results):
    """Вывод результата в консоль"""
    for row in results:
        print(*row)


def control_output(results, cli_args):
    """Определяет формат вывода результатов."""
    if cli_args.output == "pretty":
        pretty_output(results)
    elif cli_args.output == "file":
        file_output(results, cli_args)
    else:
        default_output(results)
