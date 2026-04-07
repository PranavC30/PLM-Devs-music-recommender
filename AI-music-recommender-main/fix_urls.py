#!/usr/bin/env python3
"""
YouTube URL Fixer for AI Music Recommender

This script helps identify and fix duplicate YouTube URLs in songs.csv
Run this to see which songs need URL fixes, then manually update them.
"""

import pandas as pd
import json

def analyze_duplicates():
    """Analyze and report duplicate URLs"""
    print("🎵 AI Music Recommender - YouTube URL Fixer")
    print("=" * 50)

    # Load CSV
    df = pd.read_csv('data/songs.csv')

    # Find duplicate URLs
    url_counts = df['URL'].value_counts()
    duplicates = url_counts[url_counts > 1]

    print(f"\n📊 Analysis Results:")
    print(f"Total songs: {len(df)}")
    print(f"Unique URLs: {len(url_counts)}")
    print(f"Duplicate URL groups: {len(duplicates)}")
    print(f"Songs affected: {sum(duplicates)}")

    print(f"\n🔍 Duplicate URL Details:")
    print("-" * 30)

    for i, (url, count) in enumerate(duplicates.items(), 1):
        songs = df[df['URL'] == url]['Song'].tolist()
        print(f"{i}. {url}")
        print(f"   Used by {count} songs: {', '.join(songs[:5])}{'...' if len(songs) > 5 else ''}")

        # Suggest search queries for each song
        print("   Suggested fixes:")
        for song in songs:
            language = df[df['Song'] == song]['Language'].iloc[0]
            search_query = f"{song} official music video {language}"
            print(f"   - {song}: Search '{search_query}' on YouTube")
        print()

def generate_fix_template():
    """Generate a template for manual fixes"""
    df = pd.read_csv('data/songs.csv')
    url_counts = df['URL'].value_counts()
    duplicates = url_counts[url_counts > 1]

    template = {
        "duplicate_urls": {},
        "fix_instructions": []
    }

    for url, count in duplicates.items():
        songs = df[df['URL'] == url]['Song'].tolist()
        template["duplicate_urls"][url] = songs

    template["fix_instructions"] = [
        "1. Go to YouTube.com",
        "2. Search for each song with 'official music video [language]'",
        "3. Copy the video URL (format: https://www.youtube.com/watch?v=VIDEO_ID)",
        "4. Replace the duplicate URL in songs.csv",
        "5. Run this script again to check progress"
    ]

    with open('url_fix_template.json', 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)

    print("📝 Generated url_fix_template.json with detailed instructions")

def check_progress():
    """Check how many duplicates are fixed"""
    df = pd.read_csv('data/songs.csv')
    url_counts = df['URL'].value_counts()
    duplicates = url_counts[url_counts > 1]

    total_affected = sum(duplicates)
    total_duplicates = len(duplicates)

    print(f"\n📈 Progress Check:")
    print(f"Songs still affected: {total_affected}")
    print(f"Duplicate groups remaining: {total_duplicates}")

    if total_affected == 0:
        print("🎉 All URLs are now unique! Great job!")
    else:
        print(f"💪 {total_affected} songs still need unique URLs")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "progress":
            check_progress()
        elif command == "template":
            generate_fix_template()
        else:
            print("Usage: python fix_urls.py [progress|template]")
    else:
        analyze_duplicates()
        print("\n💡 Commands:")
        print("  python fix_urls.py template  # Generate fix template")
        print("  python fix_urls.py progress  # Check fixing progress")