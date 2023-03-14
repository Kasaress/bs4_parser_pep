from pathlib import Path

# urls
MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_URL = 'https://peps.python.org/'
DOWNLOADS_URL = 'download.html'

# dirs and files
BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / "log_dir"
LOG_FILE = LOG_DIR / "parser.log"
DOWNLOADS_DIR = 'downloads'
RESULTS_DIR = "results"

# constants
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
LOG_DT_FORMAT = "%d.%m.%Y %H:%M:%S"
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
PRETTY_OUTPUT = 'pretty'
FILE_OUTPUT = 'file'
DEFAUT_OUTPUT = None
