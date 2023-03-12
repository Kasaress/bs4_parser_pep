# Проект парсинга pep

Парсинг информации с сайтов <https://docs.python.org/3/> и <https://peps.python.org/>

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
