import re
import time
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup

# Constants
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
WIKI_BASE_URL = 'https://en.wikipedia.org/wiki/The_Great_British_Bake_Off_series_{}'
REQUEST_DELAY = 1  # seconds

# Result classifications
RESULT_PATTERNS = {
    'WINNER': ['winner', 'win'],
    'RUNNER-UP': ['runner-up', 'finalist'],
    'OUT': ['out', 'eliminated', 'elim'],
    'SB': ['sb', 'star baker', 'star'],
    'HIGH': ['high', 'good', 'strong'],
    'LOW': ['low', 'weak', 'poor']
}

# Color mappings for result classification
COLOR_MAPPINGS = {
    'SB': ['gold', 'yellow', '#ffd700'],
    'OUT': ['red', '#ff', 'pink'],
    'HIGH': ['green', '#90ee90'],
    'LOW': ['orange', '#ffa500']
}

# Table identification patterns
TECHNICAL_INDICATORS = ['technical', 'challenge', 'baker', 'rank', '1st', '2nd', '3rd', 'first', 'second', 'third', 'place']
RANK_WORDS = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th', '11th', '12th']

# Configuration constants
EPISODES_PER_SERIES = 10


class GBBOWikiScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        self.results_data = []
        self.episodes_data = []

    def get_series_url(self, series_num: int) -> str:
        """Generate Wikipedia URL for a given series number."""
        return WIKI_BASE_URL.format(series_num)

    def scrape_series(self, series_num: int) -> None:
        """Scrape a single series from Wikipedia."""
        print(f"Scraping Series {series_num}...")
        url = self.get_series_url(series_num)
        
        try:
            soup = self._fetch_page(url)
            self._extract_series_data(soup, series_num)
            print(f"Successfully scraped Series {series_num}")
        except Exception as e:
            print(f"Error scraping Series {series_num}: {str(e)}")
        
        time.sleep(REQUEST_DELAY)
    
    def _fetch_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a Wikipedia page."""
        response = self.session.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    
    def _extract_series_data(self, soup: BeautifulSoup, series_num: int) -> None:
        """Extract all data for a series."""
        self.extract_results_table(soup, series_num)
        self.extract_episode_technical_rankings(soup, series_num)
        self.extract_episode_info(soup, series_num)
        self._validate_episode_count(series_num)
    
    def _validate_episode_count(self, series_num: int) -> None:
        """Ensure exactly 10 episodes per series."""
        series_episodes = [ep for ep in self.episodes_data if ep['Series'] == series_num]
        episode_count = len(series_episodes)
        
        if episode_count != EPISODES_PER_SERIES:
            print(f"WARNING: Series {series_num} has {episode_count} episodes, expected {EPISODES_PER_SERIES}")
        
        # Also check results data for episode count
        series_results = [result for result in self.results_data if result['Series'] == series_num]
        if series_results:
            unique_episodes = set(result['Episode'] for result in series_results)
            result_episode_count = len(unique_episodes)
            
            if result_episode_count != EPISODES_PER_SERIES:
                print(f"WARNING: Series {series_num} results data has {result_episode_count} episodes, expected {EPISODES_PER_SERIES}")

    def extract_results_table(self, soup: BeautifulSoup, series_num: int) -> None:
        """Extract the results summary chart from the Wikipedia page."""
        tables = soup.find_all('table', class_='wikitable')
        results_table = self._find_results_table(tables)
        
        if not results_table:
            print(f"Could not find results table for Series {series_num}")
            return
        
        self._parse_results_table(results_table, series_num)
    
    def _find_results_table(self, tables: List[BeautifulSoup]) -> Optional[BeautifulSoup]:
        """Find the main results table from candidate tables."""
        for table in tables:
            if self._is_results_table(table):
                return table
        return None
    
    def _is_results_table(self, table: BeautifulSoup) -> bool:
        """Check if a table is the main results table."""
        rows = table.find_all('tr')
        if len(rows) < 2:
            return False
        
        headers = rows[0]
        header_texts = [th.get_text().strip() for th in headers.find_all(['th', 'td'])]
        
        # Method 1: Standard format - "Baker" and numbered episodes in header
        has_baker = any('baker' in header.lower() for header in header_texts)
        has_episodes = sum(1 for header in header_texts if re.match(r'^\d+$', header)) >= 5
        
        if has_baker and has_episodes:
            return True
        
        # Method 2: Alternative format - "Baker" in header, episodes in first data row
        if has_baker and len(rows) > 1:
            return self._check_alternative_format(rows)
        
        return False
    
    def _check_alternative_format(self, rows: List[BeautifulSoup]) -> bool:
        """Check if table uses alternative format with episodes in first data row."""
        first_data_row = rows[1]
        first_row_texts = [td.get_text().strip() for td in first_data_row.find_all(['td', 'th'])]
        
        episode_numbers = [text for text in first_row_texts if re.match(r'^\d+$', text)]
        consecutive_episodes = len(episode_numbers) >= 5
        
        if consecutive_episodes and len(rows) > 2:
            second_row = rows[2]
            second_row_texts = [td.get_text().strip() for td in second_row.find_all(['td', 'th'])]
            result_indicators = ['HIGH', 'LOW', 'SB', 'SAFE', 'OUT', 'WINNER', 'Runner-up']
            has_results = any(text in result_indicators for text in second_row_texts)
            return has_results
        
        return False

    
    def _parse_results_table(self, table: BeautifulSoup, series_num: int) -> None:
        """Parse the results table and extract contestant data."""
        rows = table.find_all('tr')
        if len(rows) < 2:
            return
        
        episode_indices, start_row_idx = self._determine_table_format(rows, series_num)
        
        if not episode_indices:
            print(f"Could not find episode columns in results table for Series {series_num}")
            return
        
        self._extract_contestant_results(rows, episode_indices, start_row_idx, series_num)
    
    def _determine_table_format(self, rows: List[BeautifulSoup], series_num: int) -> Tuple[List[int], int]:
        """Determine table format and return episode indices and starting row."""
        header_row = rows[0]
        headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
        
        episode_indices = []
        start_row_idx = 1
        
        # Method 1: Episodes in header row
        for i, header in enumerate(headers):
            if re.match(r'^\d+$', header) or 'episode' in header.lower() or 'round' in header.lower():
                episode_indices.append(i)
        
        # Special case for Series 12
        if self._is_series_12_format(headers, rows):
            episode_indices, start_row_idx = self._handle_series_12_format(rows)
            print(f"  Using Series 12 special format")
        elif episode_indices:
            print(f"  Using standard table format for Series {series_num}")
        else:
            # Method 2: Episodes in first data row
            episode_indices, start_row_idx = self._check_episodes_in_data_row(rows, series_num)
        
        return episode_indices, start_row_idx
    
    def _is_series_12_format(self, headers: List[str], rows: List[BeautifulSoup]) -> bool:
        """Check if this is the Series 12 special format."""
        return (len(headers) == 2 and 
                'baker' in headers[0].lower() and 
                'episodes' in headers[1].lower() and 
                len(rows) > 1)
    
    def _handle_series_12_format(self, rows: List[BeautifulSoup]) -> Tuple[List[int], int]:
        """Handle Series 12 special format."""
        second_row = rows[1]
        second_row_cells = [td.get_text(strip=True) for td in second_row.find_all(['td', 'th'])]
        
        episode_indices = []
        for i, cell_text in enumerate(second_row_cells):
            if re.match(r'^\d+$', cell_text):
                episode_indices.append(i + 1)  # +1 because first column in data rows will be baker name
        
        return episode_indices, 2 if len(episode_indices) >= 5 else 1
    
    def _check_episodes_in_data_row(self, rows: List[BeautifulSoup], series_num: int) -> Tuple[List[int], int]:
        """Check for episodes in first data row."""
        if len(rows) <= 1:
            return [], 1
        
        first_data_row = rows[1]
        first_row_cells = [td.get_text(strip=True) for td in first_data_row.find_all(['td', 'th'])]
        
        episode_indices = []
        for i, cell_text in enumerate(first_row_cells):
            if re.match(r'^\d+$', cell_text):
                episode_indices.append(i)
        
        if episode_indices:
            print(f"  Using alternative table format for Series {series_num}")
            return episode_indices, 2
        
        return [], 1
    
    def _extract_contestant_results(self, rows: List[BeautifulSoup], episode_indices: List[int], 
                                   start_row_idx: int, series_num: int) -> None:
        """Extract results for each contestant."""
        eliminated_contestants: Set[str] = set()
        
        # Pre-process to identify spanning cells
        spanning_cell_map = self._build_spanning_cell_map(rows[start_row_idx:], episode_indices)
        
        for row_idx, row in enumerate(rows[start_row_idx:]):
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue
            
            contestant_name = cells[0].get_text(strip=True)
            if not self._is_valid_contestant_name(contestant_name):
                continue
            
            # Get spanning results that apply to this row
            row_spanning_results = spanning_cell_map.get(row_idx, {})
            
            self._process_contestant_episodes(cells, contestant_name, episode_indices, 
                                            eliminated_contestants, series_num, 
                                            row_spanning_results)
    
    def _build_spanning_cell_map(self, rows: List[BeautifulSoup], episode_indices: List[int]) -> Dict:
        """Build a map of spanning cells that affect multiple rows."""
        spanning_map = {}
        
        for row_idx, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])
            cell_column_idx = 0
            
            for cell in cells:
                # Skip cells that are occupied by previous spanning cells
                while any(cell_column_idx in spanning_map.get(prev_row, {}) 
                         for prev_row in range(max(0, row_idx - 10), row_idx)):
                    cell_column_idx += 1
                
                rowspan = int(cell.get('rowspan', 1))
                colspan = int(cell.get('colspan', 1))
                
                if rowspan > 1 and cell_column_idx in episode_indices:
                    # This cell spans multiple rows and is in an episode column
                    cell_text = cell.get_text(strip=True).lower()
                    cell_style = cell.get('style', '')
                    cell_class = ' '.join(cell.get('class', []))
                    
                    # Classify the result
                    episode_idx = episode_indices.index(cell_column_idx)
                    result = self.classify_result(cell_text, cell_style, cell_class, episode_idx + 1, 0)
                    
                    if result:
                        # Apply this result to all affected rows
                        for affected_row in range(row_idx + 1, row_idx + rowspan):
                            if affected_row not in spanning_map:
                                spanning_map[affected_row] = {}
                            spanning_map[affected_row][cell_column_idx] = result
                
                # Move to next column position
                cell_column_idx += colspan
        
        return spanning_map
    
    def _is_valid_contestant_name(self, name: str) -> bool:
        """Check if the name is a valid contestant name."""
        return (name and 
                name.lower() not in ['contestant', 'baker'] and 
                not re.match(r'^\d+$', name))
    
    def _process_contestant_episodes(self, cells: List[BeautifulSoup], contestant_name: str,
                                   episode_indices: List[int], eliminated_contestants: Set[str],
                                   series_num: int, spanning_results: Dict = None) -> None:
        """Process episodes for a single contestant."""
        if spanning_results is None:
            spanning_results = {}
        
        for ep_idx, cell_idx in enumerate(episode_indices):
            if contestant_name in eliminated_contestants:
                continue
            
            episode_num = ep_idx + 1
            result = None
            
            # Check if there's a spanning result for this episode column
            if cell_idx in spanning_results:
                result = spanning_results[cell_idx]
            elif cell_idx < len(cells):
                cell = cells[cell_idx]
                result = self._classify_cell_result(cell, episode_num, series_num)
            
            if result:
                result_data = self._create_result_record(series_num, episode_num, contestant_name, result)
                self.results_data.append(result_data)
                
                if result in ['OUT', 'ELIMINATED']:
                    eliminated_contestants.add(contestant_name)
                    break
    
    def _classify_cell_result(self, cell: BeautifulSoup, episode_num: int, series_num: int) -> Optional[str]:
        """Classify the result from a table cell."""
        cell_text = cell.get_text(strip=True).lower()
        cell_style = cell.get('style', '')
        cell_class = ' '.join(cell.get('class', []))
        
        return self.classify_result(cell_text, cell_style, cell_class, episode_num, series_num)
    
    def _create_result_record(self, series_num: int, episode_num: int, contestant_name: str, result: str) -> Dict:
        """Create a result record with proper flags."""
        winner = 1 if result in ['WINNER', 'SB'] else ""
        eliminated = 1 if result == 'OUT' else ""
        final_review = (1 if result in ['SB', 'HIGH'] 
                       else -1 if result in ['OUT', 'LOW'] 
                       else "")
        
        return {
            'Series': series_num,
            'Episode': episode_num,
            'Contestant': contestant_name,
            'Result': result,
            'Final Review': final_review,
            'Winner': winner,
            'Eliminated': eliminated,
            'Technical_Rank': None
        }

    def classify_result(self, cell_text: str, cell_style: str, cell_class: str, 
                       episode_num: int, series_num: int) -> Optional[str]:
        """Classify the result based on cell content and styling."""
        cell_text = cell_text.lower()
        
        # Check text patterns first
        result = self._classify_by_text(cell_text)
        if result:
            return result
        
        # Check styling if text classification failed
        result = self._classify_by_style(cell_style)
        if result:
            return result
        
        # Default to SAFE if content exists
        if cell_text and cell_text not in ['-', '', 'n/a']:
            return 'SAFE'
        
        return None
    
    def _classify_by_text(self, cell_text: str) -> Optional[str]:
        """Classify result based on text content."""
        for result_type, patterns in RESULT_PATTERNS.items():
            if any(pattern in cell_text for pattern in patterns):
                return result_type
        return None
    
    def _classify_by_style(self, cell_style: str) -> Optional[str]:
        """Classify result based on cell styling."""
        cell_style = cell_style.lower()
        for result_type, colors in COLOR_MAPPINGS.items():
            if any(color in cell_style for color in colors):
                return result_type
        return None

    def extract_episode_technical_rankings(self, soup: BeautifulSoup, series_num: int) -> None:
        """Extract technical rankings from episode tables and merge into results data."""
        episode_headings = self._find_episode_headings(soup)
        episode_tables = self._find_episode_tables(soup)
        
        print(f"  Found {len(episode_headings)} episode headings")
        print(f"  Found {len(episode_tables)} episode tables")
        
        self._process_episode_rankings(episode_headings, episode_tables, series_num)
    
    def _find_episode_headings(self, soup: BeautifulSoup) -> List[Tuple[int, BeautifulSoup]]:
        """Find all episode headings and extract episode numbers."""
        episode_headings = []
        all_headings = soup.find_all(['h2', 'h3', 'h4'])
        
        for heading in all_headings:
            heading_text = heading.get_text()
            episode_match = re.search(r'Episode (\d+)', heading_text)
            
            if episode_match:
                episode_num = int(episode_match.group(1))
                if 1 <= episode_num <= EPISODES_PER_SERIES:
                    episode_headings.append((episode_num, heading))
        
        return sorted(episode_headings, key=lambda x: x[0])
    
    def _find_episode_tables(self, soup: BeautifulSoup) -> List[BeautifulSoup]:
        """Find all episode tables."""
        episode_tables = []
        all_tables = soup.find_all('table', class_='wikitable')
        
        for table in all_tables:
            if self.is_episode_table(table):
                episode_tables.append(table)
        
        return episode_tables
    
    def _process_episode_rankings(self, episode_headings: List[Tuple[int, BeautifulSoup]],
                                 episode_tables: List[BeautifulSoup], series_num: int) -> None:
        """Process technical rankings for each episode."""
        for i, (episode_num, episode_heading) in enumerate(episode_headings):
            print(f"  Processing Episode {episode_num}: {episode_heading.get_text().strip()}")
            
            if i < len(episode_tables):
                episode_table = episode_tables[i]
                print(f"    Matched to table {i+1} of {len(episode_tables)}")
                self._extract_and_merge_technical_rankings(episode_table, episode_num, series_num)
            else:
                print(f"    WARNING: No episode table found for Episode {episode_num}")
    
    def _extract_and_merge_technical_rankings(self, episode_table: BeautifulSoup, 
                                            episode_num: int, series_num: int) -> None:
        """Extract technical rankings from a table and merge into results data."""
        technical_rankings = self.extract_technical_from_episode_table(episode_table, episode_num)
        
        if technical_rankings:
            self._merge_technical_rankings_for_episode(technical_rankings, series_num, episode_num)
            print(f"    Found technical rankings for Episode {episode_num}: {len(technical_rankings)} contestants")
        else:
            print(f"    WARNING: No technical rankings extracted for Episode {episode_num}")
    
    def _merge_technical_rankings_for_episode(self, technical_rankings: Dict[str, int],
                                             series_num: int, episode_num: int) -> None:
        """Merge technical rankings for a specific episode."""
        for result in self.results_data:
            if (result['Series'] == series_num and
                result['Episode'] == episode_num and
                result['Contestant'] in technical_rankings):
                result['Technical_Rank'] = technical_rankings[result['Contestant']]

    def get_element_position(self, element: BeautifulSoup) -> int:
        """Get a rough position of element in the document for ordering."""
        position = 0
        current = element
        while current.previous_sibling:
            current = current.previous_sibling
            position += 1
        return position

    def extract_technical_from_episode_table(self, table: BeautifulSoup, episode_num: int) -> Dict[str, int]:
        """Extract technical rankings from an episode table."""
        rows = table.find_all('tr')
        if len(rows) < 2:
            return {}
        
        technical_col_idx = self._find_technical_column(rows[0])
        if technical_col_idx is None:
            return {}
        
        return self._extract_rankings_from_rows(rows[1:], technical_col_idx)
    
    def _find_technical_column(self, header_row: BeautifulSoup) -> Optional[int]:
        """Find the technical challenge column index."""
        headers = [th.get_text(strip=True).lower() for th in header_row.find_all(['th', 'td'])]
        
        for i, header in enumerate(headers):
            if 'technical' in header:
                return i
        return None
    
    def _extract_rankings_from_rows(self, rows: List[BeautifulSoup], technical_col_idx: int) -> Dict[str, int]:
        """Extract rankings from table rows."""
        rankings = {}
        baker_col_idx = 0  # Usually first column
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) <= max(baker_col_idx, technical_col_idx):
                continue
            
            baker_name = self._clean_baker_name(cells[baker_col_idx].get_text(strip=True))
            technical_cell = cells[technical_col_idx].get_text(strip=True)
            rank = self.extract_rank_number(technical_cell)
            
            if baker_name and rank is not None:
                rankings[baker_name] = rank
        
        return rankings
    
    def _clean_baker_name(self, name: str) -> str:
        """Clean up baker name by removing artifacts."""
        return name.replace('†', '').replace('*', '').strip()
    
    def extract_rank_number(self, text: str) -> Optional[int]:
        """Extract numeric rank from text like '1st', '2nd', etc."""
        if not text:
            return None
        
        text = text.strip().lower()
        
        # Look for patterns like "1st", "2nd", "3rd", etc.
        rank_match = re.search(r'(\d+)(?:st|nd|rd|th)', text)
        if rank_match:
            return int(rank_match.group(1))
        
        # Look for standalone numbers at start of text
        number_match = re.search(r'^(\d+)', text)
        if number_match:
            rank = int(number_match.group(1))
            if 1 <= rank <= 15:  # Reasonable range for technical ranks
                return rank
        
        return None

    def is_episode_table(self, table: BeautifulSoup) -> bool:
        """Check if a table is an episode table with multiple challenges."""
        rows = table.find_all('tr')
        if len(rows) < 2:
            return False
        
        headers = [th.get_text(strip=True).lower() for th in rows[0].find_all(['th', 'td'])]
        
        # Episode tables should have baker column and challenge columns
        required_columns = {
            'baker': any('baker' in header for header in headers),
            'technical': any('technical' in header for header in headers),
            'challenges': any(challenge in header for header in headers 
                           for challenge in ['signature', 'showstopper'])
        }
        
        return all(required_columns.values())


    def is_technical_table(self, table: BeautifulSoup) -> bool:
        """Check if a table contains technical challenge data."""
        table_text = table.get_text().lower()
        indicator_count = sum(1 for indicator in TECHNICAL_INDICATORS if indicator in table_text)
        
        # Also check for ranking pattern in table
        rows = table.find_all('tr')
        if len(rows) > 3:  # Must have header + at least 2 data rows
            for row in rows[1:]:  # Skip header
                cells = row.find_all(['td', 'th'])
                for cell in cells:
                    cell_text = cell.get_text(strip=True).lower()
                    if any(rank in cell_text for rank in RANK_WORDS[:5]):
                        return True
        
        return indicator_count >= 3


    def extract_episode_info(self, soup: BeautifulSoup, series_num: int) -> None:
        """Extract episode names from the page content."""
        added_episodes: Set[Tuple[int, int]] = set()
        
        # Method 1: Look for "Episode X: Title" patterns in the text
        if self._extract_episodes_from_text_patterns(soup, series_num, added_episodes):
            return
        
        # Method 2: Look for episode titles in span elements with mw-headline class
        if self._extract_episodes_from_headlines(soup, series_num, added_episodes):
            return
        
        # Method 3: Extract from episode tables
        self._extract_episodes_from_tables(soup, series_num, added_episodes)
    
    def _extract_episodes_from_text_patterns(self, soup: BeautifulSoup, series_num: int, 
                                           added_episodes: Set[Tuple[int, int]]) -> bool:
        """Extract episodes using text pattern matching."""
        page_text = soup.get_text()
        episode_patterns = re.findall(r'Episode (\d+): ([^\n\r]+)', page_text)
        
        if not episode_patterns:
            return False
        
        valid_episodes = 0
        for episode_num_str, title in episode_patterns:
            try:
                episode_num = int(episode_num_str)
                # Only include episodes 1-10 for the current series
                if not (1 <= episode_num <= EPISODES_PER_SERIES):
                    continue
                    
                title = self._clean_episode_title(title)
                
                if title and (series_num, episode_num) not in added_episodes:
                    self.episodes_data.append({
                        'Series': series_num,
                        'Episode': episode_num,
                        'Title': title
                    })
                    added_episodes.add((series_num, episode_num))
                    valid_episodes += 1
            except ValueError:
                continue
        
        if valid_episodes > 0:
            print(f"Found {valid_episodes} episodes for Series {series_num}")
            return True
        return False
    
    def _extract_episodes_from_headlines(self, soup: BeautifulSoup, series_num: int,
                                       added_episodes: Set[Tuple[int, int]]) -> bool:
        """Extract episodes from headline spans."""
        episode_count = 0
        
        for span in soup.find_all('span', class_='mw-headline'):
            span_text = span.get_text().strip()
            episode_match = re.match(r'Episode (\d+)', span_text)
            
            if episode_match:
                episode_num = int(episode_match.group(1))
                # Only include episodes 1-10 for the current series
                if not (1 <= episode_num <= EPISODES_PER_SERIES):
                    continue
                    
                title_match = re.search(r'Episode \d+:?\s*(.+)', span_text)
                title = title_match.group(1).strip() if title_match else f"Episode {episode_num}"
                
                if (series_num, episode_num) not in added_episodes:
                    self.episodes_data.append({
                        'Series': series_num,
                        'Episode': episode_num,
                        'Title': title
                    })
                    added_episodes.add((series_num, episode_num))
                    episode_count += 1
        
        if episode_count > 0:
            print(f"Found {episode_count} episodes for Series {series_num}")
            return True
        
        return False
    
    def _extract_episodes_from_tables(self, soup: BeautifulSoup, series_num: int,
                                    added_episodes: Set[Tuple[int, int]]) -> None:
        """Extract episodes from table analysis."""
        episode_tables = self._find_episode_content_tables(soup)
        
        valid_episodes = 0
        for i, table in enumerate(episode_tables, 1):
            # Only process up to 10 episodes
            if i > EPISODES_PER_SERIES:
                break
                
            theme_title = self._extract_theme_from_table(table)
            
            if theme_title and (series_num, i) not in added_episodes:
                self.episodes_data.append({
                    'Series': series_num,
                    'Episode': i,
                    'Title': theme_title.title()
                })
                added_episodes.add((series_num, i))
                valid_episodes += 1
        
        if valid_episodes > 0:
            print(f"Found {valid_episodes} episodes for Series {series_num} from table analysis")
    
    def _clean_episode_title(self, title: str) -> str:
        """Clean up episode title by removing artifacts."""
        title = title.strip()
        title = re.sub(r'\s*\([^)]*\)\s*$', '', title)  # Remove (Semifinals), etc.
        title = re.sub(r'\[edit\]', '', title)  # Remove [edit] links
        return title.strip()
    
    def _find_episode_content_tables(self, soup: BeautifulSoup) -> List[BeautifulSoup]:
        """Find tables with episode content."""
        episode_tables = []
        tables = soup.find_all('table', class_='wikitable')
        
        for table in tables:
            header_row = table.find('tr')
            if header_row:
                header_cells = [th.get_text().strip().lower() for th in header_row.find_all(['th', 'td'])]
                
                if (any('signature' in cell for cell in header_cells) and 
                    any('technical' in cell for cell in header_cells)):
                    episode_tables.append(table)
        
        return episode_tables
    
    def _extract_theme_from_table(self, table: BeautifulSoup) -> Optional[str]:
        """Extract theme from table headers."""
        header_row = table.find('tr')
        if not header_row:
            return None
        
        header_cells = header_row.find_all(['th', 'td'])
        
        for cell in header_cells:
            cell_text = cell.get_text()
            
            # Extract theme from signature/showstopper descriptions
            for challenge_type in ['signature', 'showstopper']:
                if challenge_type in cell_text.lower() and '(' in cell_text:
                    pattern = f'{challenge_type.title()}\\([^)]*([A-Za-z\\s]+)[^)]*\\)'
                    theme_match = re.search(pattern, cell_text)
                    
                    if theme_match:
                        theme = theme_match.group(1).strip()
                        # Clean up common words
                        theme = re.sub(r'\b(bake|baked|baking)\b', '', theme, flags=re.IGNORECASE).strip()
                        if theme:
                            return theme
        
        return None

    def normalize_theme(self, title: str) -> str:
        """Normalize theme names to group spelling variations."""
        if not title:
            return title

        title_lower = str(title).lower().strip()

        # Handle cake variations
        if 'cake' in title_lower:
            return 'Cake'

        # Handle patisserie variations (with and without accent)
        if 'patisserie' in title_lower or 'pâtisserie' in title_lower:
            return 'Patisserie'

        # Ethnic themes → Ethnic
        if title_lower in ['italian', 'danish', 'mexican', 'german', 'japanese']:
            return 'Ethnic'

        # Temporal themes → Temporal
        if title_lower in ['the \'70s', 'the \'80s', 'the roaring twenties', 'forgotten bakes', 'autumn']:
            return 'Temporal'

        # Celebration themes → Celebration
        if title_lower in ['halloween', 'festivals', 'party']:
            return 'Celebration'

        # Ingredient themes → Ingredient
        if title_lower in ['custard', 'dairy', 'vegan', 'spice', 'puddings']:
            return 'Ingredient'

        # Return title case for consistency
        return str(title).strip().title()

    def scrape_all_series(self, start_series: int = 8, end_series: int = 15) -> None:
        """Scrape all series from start_series to end_series (inclusive)."""
        for series_num in range(start_series, end_series + 1):
            self.scrape_series(series_num)

    def validate_data(self) -> bool:
        """Validate the scraped data for basic consistency."""
        if not self.results_data:
            print("ERROR: No results data to validate")
            return False
        
        df = pd.DataFrame(self.results_data)
        print("\nValidating scraped data...")
        
        # Basic statistics
        series_count = len(df['Series'].unique())
        contestant_count = len(df['Contestant'].unique())
        total_records = len(df)
        
        print(f"\nOverall Statistics:")
        print(f"  Total series: {series_count}")
        print(f"  Total contestants: {contestant_count}")
        print(f"  Total records: {total_records}")
        
        # Check for basic data integrity
        has_required_columns = all(col in df.columns for col in 
                                  ['Series', 'Episode', 'Contestant', 'Result'])
        
        if not has_required_columns:
            print("ERROR: Missing required columns")
            return False
        
        # Check for empty data
        if total_records == 0:
            print("ERROR: No data records found")
            return False
        
        print("\nSUCCESS: Basic validation checks passed!")
        return True

    def save_results(self, results_filename: str = 'gbbo_results.csv', 
                    episodes_filename: str = 'gbbo_episodes.csv') -> None:
        """Save the scraped data to CSV files."""
        if self.results_data:
            results_df = pd.DataFrame(self.results_data)
            # Subtract 3 from series numbers to match other data source labeling
            results_df['Series'] = results_df['Series'] - 3
            results_df.to_csv(results_filename, index=False)
            print(f"Results saved to {results_filename} ({len(results_df)} rows)")
        
        if self.episodes_data:
            episodes_df = pd.DataFrame(self.episodes_data)
            # Subtract 3 from series numbers to match other data source labeling
            episodes_df['Series'] = episodes_df['Series'] - 3
            # Add normalized theme column
            episodes_df['Parsed_Theme'] = episodes_df['Title'].apply(self.normalize_theme)
            episodes_df.to_csv(episodes_filename, index=False)
            print(f"Episodes saved to {episodes_filename} ({len(episodes_df)} rows)")

def main() -> None:
    """Main function to run the scraper."""
    scraper = GBBOWikiScraper()
    
    print("Starting GBBO Wikipedia scraping...")
    print("Scraping all series 8-15...")
    
    scraper.scrape_all_series(8, 16)
    
    print("\nScraping complete. Validating data...")
    validation_passed = scraper.validate_data()
    
    print("\nSaving results...")
    scraper.save_results()
    
    if validation_passed:
        print("\nSUCCESS: Scraping completed successfully with valid data!")
    else:
        print("\nWARNING: Scraping completed but validation found issues!")
    
    print("Done!")

if __name__ == "__main__":
    main()