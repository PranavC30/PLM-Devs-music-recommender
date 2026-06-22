import pandas as pd
import os

class Recommender:
    def __init__(self, data_path=None):
        if data_path is None:
            data_path = os.path.join(os.path.dirname(__file__), 'data', 'songs.csv')
        self.df = pd.read_csv(data_path)

    def recommend_songs(self, mood, genre, language, n=3):
        """Recommends songs with progressive fallback if exact match not found."""
        filtered = self.df[
            (self.df['Mood'] == mood) &
            (self.df['Genre'] == genre) &
            (self.df['Language'].str.lower() == language.lower())
        ]
        if len(filtered) < n:
            filtered = pd.concat([
                filtered,
                self.df[(self.df['Mood'] == mood) & (self.df['Language'].str.lower() == language.lower())]
            ]).drop_duplicates()
        if len(filtered) < n:
            filtered = pd.concat([
                filtered,
                self.df[self.df['Language'].str.lower() == language.lower()]
            ]).drop_duplicates()
        if len(filtered) == 0:
            filtered = self.df

        return filtered.sample(min(n, len(filtered))).to_dict('records')
