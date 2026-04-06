import pandas as pd
import random

class Recommender:
    def __init__(self, data_path='data/songs.csv'):
        self.df = pd.read_csv(data_path)
        
    def recommend_songs(self, mood, genre, language, n=3):
        """
        Recommends songs based on mood, genre, and language preference.
        Provides fallbacks if exact matches aren't found.
        """
        # Filter by Mood, Genre, and Language
        filtered = self.df[(self.df['Mood'] == mood) & 
                           (self.df['Genre'] == genre) & 
                           (self.df['Language'].str.lower() == language.lower())]
        
        if len(filtered) < n:
            # Fallback 1: Match Mood and Language, ignore genre
            fallback_1 = self.df[(self.df['Mood'] == mood) & 
                                 (self.df['Language'].str.lower() == language.lower())]
            filtered = pd.concat([filtered, fallback_1]).drop_duplicates()
            
            if len(filtered) < n:
                # Fallback 2: Match just Language
                fallback_2 = self.df[self.df['Language'].str.lower() == language.lower()]
                filtered = pd.concat([filtered, fallback_2]).drop_duplicates()
                
                if len(filtered) < n:
                    # Ultimate fallback
                    if len(filtered) == 0:
                        filtered = self.df
        
        # Pick up to n random songs
        n_samples = min(n, len(filtered))
        songs = filtered.sample(n_samples).to_dict('records')
        return songs
