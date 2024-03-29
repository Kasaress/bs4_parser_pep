# Проект парсинга pep

Парсинг информации с сайтов:

 [Python](https://docs.python.org/3/ "https://docs.python.org/3/")

 [Peps](https://peps.python.org/ "https://peps.python.org/")

## Предварительная настройка

Клонируйте репозиторий:

```ini
git clone git@github.com:Kasaress/bs4_parser_pep.git
```

Установите и активируйте виртуальное окружение (пример команд для macOS):

```ini
python -m venv venv
python3 souce/venv/bin/activate
```

Установите зависимости:

```ini
pip install -r requirements.txt
```

Перейдите в папку src:

```ini
cd src/
```

Запустите скрипт в одном из режимов:

```ini
python main.py <parser> <args>
```

## Режимы парсинга

### whats-new

Парсинг последних обновлений с сайта.

```ini
python main.py whats-new <args>
```

### latest_versions

Парсинг документации последней версии.

```ini
python main.py latest_versions <args>
```

### download

Загрузка архива документации.

```ini
python main.py download <args>
```

### pep

Парсинг PEP.

```ini
python main.py pep <args>
```

## Возможные аргументы

При запуске скрипта можно указать дополнительные аргументы:

- Вывести информацию о парсере (-h, --help)

```ini
python main.py <parser> -h
```

- Очистить кэш (-c, --clear-cache)

```ini
python main.py <parser> -c
```

- Настроить режим вывода результатов (-o [pretty,file], --output [pretty,file])

```ini
python main.py <parser> -o file
```

## Сохранение результатов

- Парсер download. В случае выбора режима вывода результатов в файл (указания аргумента -o file), в директории src будет автоматически создана папка downloads. В ней будет сохранен zip-архив с документацией.

- Остальные парсеры (whats-new, latest_versions, pep). В директории src будет автоматически создана results. В ней будут сохранены csv-файлы с соответствующими результатами.

## Автор

Яна Бубнова

[Телеграм](https://t.me/kasares "Напишите мне :)")
