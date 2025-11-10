import re
from typing import TypeVar

from bs4 import BeautifulSoup

from .constants import (
    DEFAULT_ENCODING,
    ALTERNATIVE_ENCODING,
    ENCODING_CHECK_SIZE,
    REGEX_YEAR_VALID,
    MIN_YEAR,
    MAX_YEAR,
    SEO_WORDS,
    MIN_WORD_LENGTH,
    MIN_SEASON_NUMBER,
    MAX_SEASON_NUMBER,
)

T = TypeVar('T')


def decode_html(html: bytes) -> str:
    """
    Decode HTML bytes to string
    
    Args:
        html: HTML content as bytes
        
    Returns:
        Decoded HTML string
    """
    try:
        html_str_for_check = html[:ENCODING_CHECK_SIZE].decode(
            ALTERNATIVE_ENCODING, errors='ignore'
        )
        if 'charset=utf-8' in html_str_for_check.lower() or 'utf-8' in html_str_for_check.lower():
            return html.decode(ALTERNATIVE_ENCODING, errors='ignore')
        else:
            return html.decode(DEFAULT_ENCODING, errors='ignore')
    except Exception:
        return html.decode(DEFAULT_ENCODING, errors='ignore')


def normalize_html(html: str | bytes) -> str:
    """
    Normalize HTML input (bytes or str) to string
    
    Args:
        html: HTML content (bytes or str)
        
    Returns:
        HTML string
    """
    if isinstance(html, bytes):
        return decode_html(html)
    return html


def clean_text(text: str) -> str:
    """
    Clean text from extra whitespace and special characters
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'^[,\s]+|[,\s]+$', '', text)
    return text


def extract_text_from_link(link) -> str:
    """
    Extract clean text from a link element, removing <i> tags
    
    Args:
        link: BeautifulSoup link element
        
    Returns:
        Cleaned text
    """
    link_copy = BeautifulSoup(str(link), 'lxml').find('a')
    if not link_copy:
        return ""
    
    for i_tag in link_copy.find_all('i'):
        i_tag.decompose()
    
    text = link_copy.get_text(strip=True)
    text = re.sub(r'^Аниме\s*', '', text).strip()
    return clean_text(text)


def is_year(text: str) -> bool:
    """
    Check if text represents a year
    
    Args:
        text: Text to check
        
    Returns:
        True if text is a valid year
    """
    if not text:
        return False
    
    match = re.match(REGEX_YEAR_VALID, text.strip())
    if match:
        try:
            year = int(match.group(0))
            return MIN_YEAR <= year <= MAX_YEAR
        except ValueError:
            return False
    return False


def extract_year_from_text(text: str) -> int | None:
    """
    Extract year from text
    
    Args:
        text: Text to extract year from
        
    Returns:
        Year as integer or None
    """
    match = re.search(r"(\d{4})", text)
    if match:
        try:
            year = int(match.group(1))
            if MIN_YEAR <= year <= MAX_YEAR:
                return year
        except ValueError:
            pass
    return None


def clean_description(description: str) -> str:
    """
    Clean description text from SEO words and duplicates
    
    Args:
        description: Description text
        
    Returns:
        Cleaned description
    """
    if not description:
        return ""
    
    words = description.split()
    cleaned_words = []
    prev_word = None
    
    for word in words:
        should_skip = (
            len(word) > MIN_WORD_LENGTH and word.lower() in SEO_WORDS
        ) or (word in SEO_WORDS)
        
        if not should_skip and word != prev_word:
            cleaned_words.append(word)
            prev_word = word
    
    result = ' '.join(cleaned_words)
    return re.sub(r'\s+', ' ', result).strip()


def normalize_url(url: str, base_url: str = "https://jut.su") -> str:
    """
    Normalize URL to absolute format
    
    Args:
        url: URL to normalize
        base_url: Base URL for relative paths
        
    Returns:
        Normalized absolute URL
    """
    match url:
        case url if url.startswith('/'):
            return f"{base_url}{url}"
        case url if url.startswith('http'):
            return url
        case _:
            return f"{base_url}/{url}"


def is_part_header(header_text: str, header_title: str = "") -> bool:
    """
    Check if header represents a part/arc, not a season
    
    Args:
        header_text: Header text
        header_title: Header title attribute
        
    Returns:
        True if header is a part/arc
    """
    header_combined = f"{header_text} {header_title}".lower()
    
    if re.search(r"часть\s*\d+|part\s*\d+", header_combined, re.IGNORECASE):
        return True
    
    if 'часть' in header_combined:
        return True
    
    if header_title and ('part' in header_title.lower() and 'season' not in header_title.lower()):
        return True
    
    return False


def extract_season_number(text: str) -> int | None:
    """
    Extract season number from text
    
    Args:
        text: Text containing season number
        
    Returns:
        Season number or None
    """
    patterns = [
        r"(\d+)\s+сезон",
        r"\((\d+)\s+сезон\)",
        r"\((\d+)",
        r"^(\d+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                num = int(match.group(1))
                if MIN_SEASON_NUMBER <= num <= MAX_SEASON_NUMBER:
                    return num
            except (ValueError, AttributeError):
                continue
    
    numbers = re.findall(r'\d+', text)
    for num_str in numbers:
        try:
            num = int(num_str)
            if MIN_SEASON_NUMBER <= num <= MAX_SEASON_NUMBER:
                return num
        except ValueError:
            continue
    
    return None
