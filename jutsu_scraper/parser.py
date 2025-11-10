import re
from bs4 import BeautifulSoup

from .models.episode import Episode
from .models.season import Season
from .models.arc import Arc
from .models.rating import Rating
from .models.anime import Anime
from .constants import (
    SELECTOR_TITLE,
    SELECTOR_INFO_BLOCK,
    SELECTOR_POSTER,
    SELECTOR_AGE_RATING,
    SELECTOR_DESCRIPTION,
    SELECTOR_RATING_VALUE,
    SELECTOR_RATING_BEST,
    SELECTOR_RATING_WORST,
    SELECTOR_RATING_COUNT,
    SELECTOR_SEASON_HEADERS,
    SELECTOR_WATCH_DIV,
    PATTERN_WATCH_PREFIX,
    PATTERN_ALL_SERIES,
    PATTERN_AND_SEASONS,
    PATTERN_ORIGINAL_TITLE,
    PATTERN_ONGOING_LINK,
    REGEX_EPISODE_URL,
    REGEX_SEASON_URL,
    REGEX_POSTER_BACKGROUND,
    REGEX_SEASON_TITLE,
    REGEX_PLAIN_SEASON,
    REGEX_TITLE_BEFORE_NUMBER,
    STATUS_ONGOING,
    BASE_URL,
)
from .utils import (
    normalize_html,
    extract_text_from_link,
    is_year,
    extract_year_from_text,
    clean_description,
    normalize_url,
    is_part_header,
    extract_season_number,
)


class AnimeParser:
    """Parser for anime HTML pages"""
    
    def __init__(self, html: str, url: str = ""):
        """
        Initialize parser
        
        Args:
            html: HTML content (str or bytes)
            url: Page URL
        """
        self.html = normalize_html(html)
        self.url = url
        self.soup = BeautifulSoup(self.html, 'lxml')
    
    def parse(self) -> Anime:
        """
        Parse HTML and return Anime object
        
        Returns:
            Parsed Anime object
        """
        title = self._parse_title()
        original_title = self._parse_original_title()
        poster_url = self._parse_poster()
        genres, themes = self._parse_genres_and_themes()
        years, year = self._parse_years()
        age_rating = self._parse_age_rating()
        status = self._parse_status()
        description = self._parse_description()
        rating = self._parse_rating()
        episodes, seasons = self._parse_episodes_and_seasons()
        
        return Anime(
            title=title,
            original_title=original_title,
            url=self.url,
            poster_url=poster_url,
            description=description,
            genres=genres,
            themes=themes,
            years=years,
            year=year,
            age_rating=age_rating,
            rating=rating,
            status=status,
            episodes=episodes,
            seasons=seasons
        )
    
    def _parse_title(self) -> str:
        """Parse anime title"""
        title_elem = self.soup.select_one(SELECTOR_TITLE)
        if not title_elem:
            return ""
        
        title = title_elem.get_text(strip=True)
        title = re.sub(PATTERN_WATCH_PREFIX, '', title)
        title = re.sub(PATTERN_ALL_SERIES, '', title)
        title = re.sub(PATTERN_AND_SEASONS, '', title)
        return title.strip()
    
    def _parse_original_title(self) -> str | None:
        """Parse original title"""
        info_block = self.soup.select_one(SELECTOR_INFO_BLOCK)
        if not info_block:
            return None
        
        info_text = info_block.get_text()
        if PATTERN_ORIGINAL_TITLE not in info_text:
            return None
        
        orig_b_tag = info_block.find('b')
        if orig_b_tag:
            return orig_b_tag.get_text(strip=True)
        return None
    
    def _parse_poster(self) -> str | None:
        """Parse poster URL"""
        poster_div = self.soup.select_one(SELECTOR_POSTER)
        if poster_div and poster_div.get('style'):
            style = poster_div.get('style', '')
            bg_match = re.search(REGEX_POSTER_BACKGROUND, style)
            if bg_match:
                return bg_match.group(1)
        
        meta_image = self.soup.find('meta', property='yandex_recommendations_image')
        if meta_image and meta_image.get('content'):
            return meta_image['content']
        
        return None
    
    def _parse_genres_and_themes(self) -> tuple[list[str], list[str]]:
        """Parse genres and themes"""
        genres = []
        themes = []
        
        info_block = self.soup.select_one(SELECTOR_INFO_BLOCK)
        if not info_block:
            return genres, themes
        
        sections = self._split_info_block_by_br(info_block)
        
        for i, section_html in enumerate(sections):
            section_soup = BeautifulSoup(section_html, 'lxml')
            section_links = section_soup.find_all('a', href=re.compile(r'/anime/'))
            
            if not section_links:
                continue
            
            if self._is_year_section(section_links):
                continue
            
            if i == 0:
                target_list = genres
            elif i == 1:
                target_list = themes
            else:
                continue
            
            for link in section_links:
                text = extract_text_from_link(link)
                if text and not is_year(text) and len(text) > 1 and not text.isdigit():
                    if text not in target_list:
                        target_list.append(text)
        
        return genres, themes
    
    def _parse_years(self) -> tuple[list[int], int | None]:
        """Parse release years"""
        years = []
        
        info_block = self.soup.select_one(SELECTOR_INFO_BLOCK)
        if not info_block:
            return years, None
        
        sections = self._split_info_block_by_br(info_block)
        
        for section_html in sections:
            section_soup = BeautifulSoup(section_html, 'lxml')
            section_links = section_soup.find_all('a', href=re.compile(r'/anime/'))
            
            if not section_links:
                continue
            
            for link in section_links:
                text = extract_text_from_link(link)
                year = extract_year_from_text(text)
                if year and year not in years:
                    years.append(year)
        
        if not years:
            years = self._parse_years_fallback(info_block)
        
        if years:
            years.sort()
            return years, years[0]
        
        return years, None
    
    def _parse_years_fallback(self, info_block) -> list[int]:
        """Fallback method to parse years from info block text"""
        years = []
        info_text = str(info_block)
        
        if 'Годы выпуска:' in info_text:
            years_match = re.search(
                r'Годы выпуска:\s*(.*?)(?:<br>|Оригинальное)', 
                info_text, 
                re.DOTALL
            )
            if years_match:
                years_html = years_match.group(1)
                years_soup = BeautifulSoup(years_html, 'lxml')
                year_links = years_soup.find_all('a', href=re.compile(r'/anime/'))
                for link in year_links:
                    link_text = link.get_text(strip=True)
                    year = extract_year_from_text(link_text)
                    if year and year not in years:
                        years.append(year)
        elif 'Год выпуска:' in info_text:
            year_match = re.search(
                r'Год выпуска:.*?<a[^>]*>.*?<i>.*?</i>\s*(\d{4})', 
                info_text, 
                re.DOTALL
            )
            if not year_match:
                year_match = re.search(r'Год выпуска:.*?(\d{4})', info_text)
            if year_match:
                try:
                    year_val = int(year_match.group(1))
                    if 1900 <= year_val <= 2100:
                        years.append(year_val)
                except (ValueError, IndexError):
                    pass
        
        return years
    
    def _parse_age_rating(self) -> str | None:
        """Parse age rating"""
        age_rating_elem = self.soup.select_one(SELECTOR_AGE_RATING)
        if age_rating_elem:
            return age_rating_elem.get_text(strip=True)
        return None
    
    def _parse_status(self) -> str | None:
        """Parse anime status (ongoing/completed)"""
        ongoing_link = self.soup.find('a', href=re.compile(PATTERN_ONGOING_LINK))
        if ongoing_link:
            return STATUS_ONGOING
        return None
    
    def _parse_description(self) -> str | None:
        """Parse description"""
        desc_elem = self.soup.select_one(SELECTOR_DESCRIPTION)
        if not desc_elem:
            return None
        
        desc_span = desc_elem.find('span')
        if not desc_span:
            return None
        
        for i_tag in desc_span.find_all('i'):
            i_tag.decompose()
        
        for b_tag in desc_span.find_all('b'):
            b_tag.unwrap()
        
        description = desc_span.get_text(separator=' ', strip=True)
        return clean_description(description)
    
    def _parse_rating(self) -> Rating | None:
        """Parse rating"""
        rating_elem = self.soup.select_one(SELECTOR_RATING_VALUE)
        if not rating_elem:
            return None
        
        try:
            value = float(rating_elem.get_text(strip=True))
            best_elem = self.soup.select_one(SELECTOR_RATING_BEST)
            best = float(best_elem.get_text(strip=True)) if best_elem else 10.0
            
            worst_elem = self.soup.select_one(SELECTOR_RATING_WORST)
            worst = float(worst_elem.get('content')) if worst_elem and worst_elem.get('content') else 1.0
            
            count_elem = self.soup.select_one(SELECTOR_RATING_COUNT)
            count = int(count_elem.get_text(strip=True)) if count_elem else 0
            
            return Rating(value=value, best=best, worst=worst, count=count)
        except (ValueError, AttributeError):
            return None
    
    def _parse_episodes_and_seasons(self) -> tuple[list[Episode], list[Season]]:
        """Parse episodes and seasons"""
        episodes = []
        seasons = []
        
        all_season_headers = self.soup.select(SELECTOR_SEASON_HEADERS)
        watch_l_div = self.soup.select_one(SELECTOR_WATCH_DIV)
        
        season_headers, arc_headers_candidates = self._classify_headers(all_season_headers)
        
        has_real_seasons = len(season_headers) > 0
        
        if has_real_seasons and watch_l_div:
            episodes, seasons = self._parse_with_seasons(
                season_headers, 
                arc_headers_candidates, 
                watch_l_div
            )
        else:
            episodes = self._parse_without_seasons(watch_l_div)
        
        episodes.sort(key=lambda x: (x.season_number or 0, x.number))
        if seasons:
            seasons.sort(key=lambda x: x.number)
        
        return episodes, seasons
    
    def _classify_headers(self, headers: list) -> tuple[list, list]:
        """Classify headers into seasons and arcs"""
        season_headers = []
        arc_headers_candidates = []
        
        for header in headers:
            classes = header.get('class', [])
            header_text = header.get_text(strip=True)
            header_title = header.get('title', '')
            
            if is_part_header(header_text, header_title):
                arc_headers_candidates.append(header)
                continue
            
            is_season = False
            
            if 'need_bold_season' in classes:
                is_season = True
            else:
                numbers = re.findall(r'\d+', header_text)
                if numbers:
                    next_ep = header.find_next('a', href=re.compile(REGEX_EPISODE_URL))
                    if next_ep:
                        next_header = header.find_next_sibling('h2', class_='the-anime-season')
                        if next_header:
                            if next_ep in header.find_all_next(limit=100):
                                all_between = header.find_next_siblings('h2', class_='the-anime-season')
                                ep_before_next_header = True
                                for between_header in all_between:
                                    if between_header == next_header:
                                        break
                                    if 'need_bold_season' in between_header.get('class', []):
                                        ep_before_next_header = False
                                        break
                                if ep_before_next_header:
                                    is_season = True
                        else:
                            is_season = True
            
            if is_season:
                season_headers.append(header)
            else:
                arc_headers_candidates.append(header)
        
        return season_headers, arc_headers_candidates
    
    def _parse_with_seasons(
        self, 
        season_headers: list, 
        arc_headers_candidates: list, 
        watch_l_div
    ) -> tuple[list[Episode], list[Season]]:
        """Parse episodes organized by seasons"""
        episodes = []
        seasons = []
        
        all_episode_links = watch_l_div.find_all('a', href=re.compile(REGEX_EPISODE_URL))
        
        seasons_dict, seasons_info = self._build_seasons_info(season_headers)
        arc_headers = [h for h in arc_headers_candidates if h not in season_headers]
        arcs_info = self._build_arcs_info(arc_headers, seasons_dict)
        
        for link in all_episode_links:
            episode = self._parse_episode_link(link, seasons_dict)
            if episode:
                episodes.append(episode)
                season_num = episode.season_number
                if season_num and season_num in seasons_dict:
                    seasons_dict[season_num]['episodes'].append(episode)
                    self._assign_episode_to_arc(episode, link, arcs_info, seasons_dict, season_num)
        
        for season_num in sorted(seasons_dict.keys()):
            season_data = seasons_dict[season_num]
            season_info = seasons_info[season_num]
            
            season_data['episodes'].sort(key=lambda x: x.number)
            
            arcs_list = list(season_data['arcs'].values())
            for arc in arcs_list:
                arc.episodes.sort(key=lambda x: x.number)
            
            seasons.append(Season(
                number=season_num,
                episodes=season_data['episodes'],
                arcs=arcs_list,
                title=season_info['title']
            ))
        
        return episodes, seasons
    
    def _parse_without_seasons(self, watch_l_div) -> list[Episode]:
        """Parse episodes without seasons"""
        episodes = []
        
        if watch_l_div:
            episode_links = watch_l_div.find_all('a', href=re.compile(REGEX_EPISODE_URL))
        else:
            episode_links = self.soup.find_all('a', href=re.compile(REGEX_EPISODE_URL))
        
        for link in episode_links:
            episode = self._parse_episode_link(link, {})
            if episode:
                episodes.append(episode)
        
        return episodes
    
    def _build_seasons_info(self, season_headers: list) -> tuple[dict, dict]:
        """Build seasons information dictionary"""
        seasons_dict = {}
        seasons_info = {}
        
        for season_header in season_headers:
            season_text = season_header.get_text(strip=True)
            season_title = season_header.get('title', '')
            
            season_num = extract_season_number(season_text)
            if not season_num:
                continue
            
            season_title_clean = season_title if season_title else None
            if not season_title_clean:
                title_match = re.search(REGEX_SEASON_TITLE, season_text)
                if title_match:
                    season_title_clean = title_match.group(1).strip()
                else:
                    if not re.match(REGEX_PLAIN_SEASON, season_text):
                        title_match = re.search(REGEX_TITLE_BEFORE_NUMBER, season_text)
                        if title_match:
                            potential_title = title_match.group(1).strip()
                            if not potential_title.isdigit():
                                season_title_clean = potential_title
            
            seasons_info[season_num] = {
                'title': season_title_clean,
                'header': season_header
            }
            seasons_dict[season_num] = {
                'episodes': [],
                'arcs': {}
            }
        
        return seasons_dict, seasons_info
    
    def _build_arcs_info(self, arc_headers: list, seasons_dict: dict) -> list[dict]:
        """Build arcs information list"""
        arcs_info = []
        
        for arc_header in arc_headers:
            arc_name = arc_header.get_text(strip=True)
            arc_title = arc_header.get('title', '')
            
            next_ep = arc_header.find_next('a', href=re.compile(REGEX_EPISODE_URL))
            if next_ep:
                href = next_ep.get('href', '')
                season_match = re.search(REGEX_SEASON_URL, href)
                if season_match:
                    season_num = int(season_match.group(1))
                    if season_num in seasons_dict:
                        arcs_info.append({
                            'header': arc_header,
                            'name': arc_name,
                            'title': arc_title if arc_title else None,
                            'season': season_num
                        })
        
        return arcs_info
    
    def _parse_episode_link(self, link, seasons_dict: dict) -> Episode | None:
        """Parse episode from link element"""
        href = link.get('href', '')
        ep_match = re.search(REGEX_EPISODE_URL, href)
        
        if not ep_match:
            return None
        
        try:
            ep_num = int(ep_match.group(1))
            url_season_match = re.search(REGEX_SEASON_URL, href)
            season_num = int(url_season_match.group(1)) if url_season_match else None
            
            if seasons_dict:
                if season_num is None:
                    if len(seasons_dict) == 1:
                        season_num = list(seasons_dict.keys())[0]
                    else:
                        return None
                
                if season_num not in seasons_dict:
                    return None
            
            ep_title = self._extract_episode_title(link)
            ep_url = normalize_url(href, BASE_URL)
            
            return Episode(
                number=ep_num,
                title=ep_title,
                url=ep_url,
                season_number=season_num
            )
        except (ValueError, AttributeError):
            return None
    
    def _extract_episode_title(self, link) -> str:
        """Extract episode title from link"""
        i_tag = link.find('i')
        if i_tag:
            next_sibling = i_tag.next_sibling
            if next_sibling:
                return str(next_sibling).strip()
        
        link_copy = BeautifulSoup(str(link), 'lxml').find('a')
        if link_copy:
            for i_elem in link_copy.find_all('i'):
                i_elem.decompose()
            return link_copy.get_text(strip=True)
        
        return ""
    
    def _assign_episode_to_arc(
        self, 
        episode: Episode, 
        link, 
        arcs_info: list[dict], 
        seasons_dict: dict, 
        season_num: int
    ):
        """Assign episode to appropriate arc"""
        season_arcs = [ai for ai in arcs_info if ai['season'] == season_num]
        
        if not season_arcs:
            return
        
        prev_headers = link.find_all_previous('h2', class_='the-anime-season', limit=50)
        
        current_arc_info = None
        for arc_info in reversed(season_arcs):
            arc_header = arc_info['header']
            if arc_header in prev_headers:
                arc_pos = prev_headers.index(arc_header)
                found_between = False
                
                for other_arc_info in season_arcs:
                    if other_arc_info != arc_info:
                        other_header = other_arc_info['header']
                        if other_header in prev_headers:
                            other_pos = prev_headers.index(other_header)
                            if other_pos < arc_pos:
                                found_between = True
                                break
                
                if not found_between:
                    current_arc_info = arc_info
                    break
        
        if current_arc_info:
            arc_name = current_arc_info['name']
            if arc_name not in seasons_dict[season_num]['arcs']:
                seasons_dict[season_num]['arcs'][arc_name] = Arc(
                    name=current_arc_info['name'],
                    title=current_arc_info['title'],
                    episodes=[]
                )
            seasons_dict[season_num]['arcs'][arc_name].episodes.append(episode)
    
    def _split_info_block_by_br(self, info_block) -> list[str]:
        """Split info block into sections by <br> tags"""
        sections = []
        current_section = []
        
        for element in info_block.children:
            if hasattr(element, 'name') and element.name == 'br':
                if current_section:
                    sections.append(''.join(str(elem) for elem in current_section))
                    current_section = []
            else:
                current_section.append(element)
        
        if current_section:
            sections.append(''.join(str(elem) for elem in current_section))
        
        return sections
    
    def _is_year_section(self, section_links: list) -> bool:
        """Check if section contains years"""
        for link in section_links:
            text = extract_text_from_link(link)
            if is_year(text) or (len(text) <= 6 and re.search(r'\d{4}', text)):
                return True
        return False


def parse_anime_html(html: str | bytes, url: str = "") -> Anime:
    """
    Parse anime HTML and return Anime object
    
    Args:
        html: HTML content (str or bytes)
        url: Page URL
        
    Returns:
        Parsed Anime object
    """
    parser = AnimeParser(html, url)
    return parser.parse()

