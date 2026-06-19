import re
import time
import urllib.parse
import requests
import pandas as pd

PLACEHOLDER_PATTERN = re.compile(r"[A-Z0-9]T2cPWVBI")
SEARCH_PROXY = "https://www.youtube.com/results?search_query={}"


def extract_video_ids(text):
    ids = []
    for match in re.findall(r"watch\?v=([A-Za-z0-9_-]{11})", text):
        if match not in ids:
            ids.append(match)
    for match in re.findall(r'"videoId":"([A-Za-z0-9_-]{11})"', text):
        if match not in ids:
            ids.append(match)
    return ids


def is_placeholder_url(url):
    return bool(PLACEHOLDER_PATTERN.search(url))


def main():
    df = pd.read_csv('data/songs.csv')
    placeholder_rows = df[df['URL'].apply(is_placeholder_url)].copy()

    if placeholder_rows.empty:
        print('No placeholder URLs found. Nothing to update.')
        return

    print(f'Total placeholder songs to update: {len(placeholder_rows)}')

    updated_count = 0
    for idx, row in placeholder_rows.iterrows():
        song = row['Song']
        language = row['Language']
        current_url = row['URL']
        search_query = urllib.parse.quote_plus(f'{song} official music video {language}')
        fetch_url = SEARCH_PROXY.format(search_query)

        print('\nSearching:', song)
        print('Current URL:', current_url)
        print('Fetch URL:', fetch_url)

        try:
            resp = requests.get(fetch_url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
            })
            resp.raise_for_status()
            video_ids = extract_video_ids(resp.text)
        except Exception as exc:
            print('Error fetching search page:', exc)
            continue

        if not video_ids:
            print('No video IDs found in search result. Skipping.')
            continue

        # choose the first valid non-placeholder id
        chosen = None
        for vid in video_ids:
            if vid == current_url.split('v=')[-1]:
                continue
            if PLACEHOLDER_PATTERN.search(vid):
                continue
            chosen = vid
            break

        if not chosen:
            print('Could not choose a new candidate, using first found ID:', video_ids[0])
            chosen = video_ids[0]

        new_url = f'https://www.youtube.com/watch?v={chosen}'
        print('Selected video ID:', chosen)
        print('New URL:', new_url)

        df.loc[idx, 'URL'] = new_url
        updated_count += 1
        df.to_csv('data/songs.csv', index=False)
        print(f'Updated {updated_count}/{len(placeholder_rows)} placeholder URLs so far.')
        time.sleep(1)

    print('\nAll placeholder URLs have been updated and saved to data/songs.csv.')


if __name__ == '__main__':
    main()
