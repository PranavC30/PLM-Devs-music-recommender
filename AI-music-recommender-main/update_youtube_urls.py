import pandas as pd
import json
import os

def update_song_urls():
    # Load songs data
    df = pd.read_csv('data/songs.csv')

    # Load search queries
    with open('youtube_search_queries.json', 'r', encoding='utf-8') as f:
        search_queries = json.load(f)

    print("🎵 YouTube URL Updater for AI Music Recommender")
    print("=" * 50)
    print(f"Total songs: {len(df)}")
    print(f"Songs needing URL updates: {len([s for s in search_queries if 'T2cPWVBI' in s['current_url']])}")
    print()

    updated_count = 0

    for i, query in enumerate(search_queries):
        if 'T2cPWVBI' in query['current_url']:  # Only update placeholders
            print(f"\n{i+1}/{len(search_queries)}: {query['song']}")
            print(f"Search URL: {query['search_url']}")
            print(f"Current URL: {query['current_url']}")

            # Ask user for new URL
            new_url = input("Enter the YouTube video URL (or press Enter to skip): ").strip()

            if new_url and new_url.startswith('https://www.youtube.com/watch?v='):
                # Update the dataframe
                df.loc[df['Song'] == query['song'], 'URL'] = new_url
                updated_count += 1
                print(f"✅ Updated {query['song']}")
            else:
                print(f"⏭️  Skipped {query['song']}")

            # Save progress every 10 updates
            if updated_count % 10 == 0 and updated_count > 0:
                df.to_csv('data/songs.csv', index=False)
                print(f"\n💾 Progress saved! Updated {updated_count} songs so far.")

    # Final save
    df.to_csv('data/songs.csv', index=False)
    print(f"\n🎉 Complete! Updated {updated_count} songs with real YouTube URLs.")
    print("Run the app again to test the videos!")

if __name__ == "__main__":
    update_song_urls()