class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    pass


class FindLatestVersionException(Exception):
    """Вызывается, когда парсер не может найти документацию."""
    pass
