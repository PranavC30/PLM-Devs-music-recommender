import pandas as pd
import json

# Load songs data
df = pd.read_csv('data/songs.csv')

# Create search queries for each song
search_queries = []
for idx, row in df.iterrows():
    song = row['Song']
    language = row['Language']
    query = f"{song} official music video {language}"
    search_queries.append({
        'song': song,
        'search_url': f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}",
        'current_url': row['URL']
    })

# Save to JSON for easy reference
with open('youtube_search_queries.json', 'w', encoding='utf-8') as f:
    json.dump(search_queries, f, indent=2, ensure_ascii=False)

print(f"Generated {len(search_queries)} search queries in youtube_search_queries.json")
print("\nFirst 5 queries:")
for i, q in enumerate(search_queries[:5]):
    print(f"{i+1}. {q['song']}: {q['search_url']}")