import requests
from bs4 import BeautifulSoup
import re
import os
import time

def get_episode_links():
    """Fetch all episode links from the Great British Bake Off transcripts page."""
    url = "https://transcripts.foreverdreaming.org/viewforum.php?f=2837"

    # Fetch the page with headers to avoid being blocked
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Parse HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all episode links
    episodes = []

    # Find all topic links in the forum
    for link in soup.find_all('a', class_='topictitle'):
        episode_title = link.get_text(strip=True)
        episode_url = link.get('href')

        # Make the URL absolute if it's relative
        if episode_url and not episode_url.startswith('http'):
            episode_url = f"https://transcripts.foreverdreaming.org/{episode_url}"

        episodes.append({
            'title': episode_title,
            'url': episode_url
        })

    return episodes

def extract_season_number(title):
    """Extract season number from episode title."""
    match = re.match(r'^(\d+)x\d+', title)
    if match:
        return int(match.group(1))
    return None

def download_transcript(episode_url, headers):
    """Download transcript text from an episode page."""
    response = requests.get(episode_url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the post content (transcripts are typically in post content div)
    content_div = soup.find('div', class_='content')

    if content_div:
        return content_div.get_text(strip=False)
    return None

def save_transcripts():
    """Download and save transcripts for seasons 8 and above."""
    # Create transcripts folder if it doesn't exist
    os.makedirs('', exist_ok=True)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Get all episode links
    print("Fetching episode list...")
    episodes = get_episode_links()

    # Filter for seasons 8 and above
    target_episodes = []
    for episode in episodes:
        season = extract_season_number(episode['title'])
        if season and season >= 8:
            target_episodes.append(episode)

    print(f"Found {len(target_episodes)} episodes from season 8 onwards\n")

    # Download each transcript
    for i, episode in enumerate(target_episodes, 1):
        print(f"[{i}/{len(target_episodes)}] Downloading: {episode['title']}")

        try:
            transcript = download_transcript(episode['url'], headers)

            if transcript:
                # Create safe filename
                safe_title = re.sub(r'[^\w\s-]', '', episode['title']).strip()
                safe_title = re.sub(r'[-\s]+', '_', safe_title)
                filename = f"transcripts/{safe_title}.txt"

                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(transcript)

                print(f"  Saved to: {filename}")
            else:
                print(f"  Warning: No content found")

            # Be polite - wait between requests
            time.sleep(1)

        except Exception as e:
            print(f"  Error: {e}")

    print(f"\nComplete! Downloaded {len(target_episodes)} transcripts to ./transcripts/")

if __name__ == "__main__":
    save_transcripts()
