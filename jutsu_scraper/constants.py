BASE_URL = "https://jut.su"

SELECTOR_TITLE = "h1.header_video"
SELECTOR_INFO_BLOCK = "div.under_video_additional"
SELECTOR_POSTER = "div.all_anime_title"
SELECTOR_AGE_RATING = "span.age_rating_all"
SELECTOR_DESCRIPTION = "p.under_video"
SELECTOR_RATING_VALUE = "span[itemprop='ratingValue']"
SELECTOR_RATING_BEST = "span[itemprop='bestRating']"
SELECTOR_RATING_WORST = "meta[itemprop='worstRating']"
SELECTOR_RATING_COUNT = "span[itemprop='ratingCount']"
SELECTOR_SEASON_HEADERS = "h2.the-anime-season"
SELECTOR_WATCH_DIV = "div.watch_l"
SELECTOR_EPISODE_LINKS = "a[href*='/episode-']"

PATTERN_WATCH_PREFIX = r"^Смотреть\s+"
PATTERN_ALL_SERIES = r"\s+все серии(?:\s+и сезоны)?$"
PATTERN_AND_SEASONS = r"\s+и сезоны$"
PATTERN_ORIGINAL_TITLE = "Оригинальное название:"
PATTERN_YEARS_RELEASE = "Годы выпуска:"
PATTERN_YEAR_RELEASE = "Год выпуска:"
PATTERN_ONGOING_LINK = r"/anime/ongoing/"

REGEX_SEASON_NUMBER = r"(\d+)\s+сезон"
REGEX_SEASON_IN_BRACKETS = r"\((\d+)\s+сезон\)"
REGEX_NUMBER_IN_BRACKETS = r"\((\d+)"
REGEX_STARTING_NUMBER = r"^(\d+)"
REGEX_YEAR = r"(\d{4})"
REGEX_YEAR_VALID = r"^\d{4}$"
REGEX_EPISODE_URL = r"/episode-(\d+)\.html"
REGEX_SEASON_URL = r"/season-(\d+)/"
REGEX_POSTER_BACKGROUND = r"background:\s*url\(['\"]?(.+?)['\"]?\)"
REGEX_PART_HEADER = r"часть\s*\d+|part\s*\d+"
REGEX_SEASON_TITLE = r"^(.+?)\s*\(\d+\s+сезон\)"
REGEX_PLAIN_SEASON = r"^\d+\s+сезон\s*$"
REGEX_TITLE_BEFORE_NUMBER = r"^(.+?)\s+\d+"
REGEX_QUALITY_FROM_LABEL = r"(\d+)"
REGEX_QUALITY_FROM_URL = r"\.(\d+)\."
REGEX_EPISODE_FROM_URL = r'/([^/]+)/episode-(\d+)\.html'

MIN_YEAR = 1900
MAX_YEAR = 2100
MIN_SEASON_NUMBER = 1
MAX_SEASON_NUMBER = 20

DEFAULT_ENCODING = "windows-1251"
ALTERNATIVE_ENCODING = "utf-8"
ENCODING_CHECK_SIZE = 5000

STATUS_ONGOING = "онгоинг"

SEO_WORDS = ["серия", "серии", "сезон", "онлайн", "аниме", "видео", "смотреть"]

MIN_WORD_LENGTH = 2

VIDEO_QUALITIES = ['1080', '720', '480', '360']
