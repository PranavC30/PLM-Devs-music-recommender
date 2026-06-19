import pandas as pd
import os

class SongSearchEngine:
    """Advanced search and filtering for songs"""
    
    def __init__(self, data_path=None):
        if data_path is None:
            data_path = os.path.join(os.path.dirname(__file__), 'data', 'songs.csv')
        self.df = pd.read_csv(data_path)
        # Precompute lowercase versions for faster search
        self.df['song_lower'] = self.df['Song'].str.lower()
        self.df['language_lower'] = self.df['Language'].str.lower()
        self.df['mood_lower'] = self.df['Mood'].str.lower()
        self.df['genre_lower'] = self.df['Genre'].str.lower()
    
    def search_songs(self, query, limit=50):
        """Search songs by name (case-insensitive, partial match)"""
        if not query or len(query.strip()) == 0:
            return []
        
        query_lower = query.lower().strip()
        matches = self.df[
            self.df['song_lower'].str.contains(query_lower, na=False)
        ].to_dict('records')
        return matches[:limit]
    
    def filter_songs(self, mood=None, genre=None, language=None, energy=None):
        """Filter songs by mood, genre, language, and energy"""
        result = self.df.copy()
        
        if mood:
            result = result[result['mood_lower'] == mood.lower()]
        
        if genre:
            result = result[result['genre_lower'] == genre.lower()]
        
        if language:
            result = result[result['language_lower'] == language.lower()]
        
        if energy:
            result = result[result['Energy'] == energy]
        
        return result.to_dict('records')
    
    def advanced_search(self, query=None, mood=None, genre=None, language=None, 
                        energy=None, limit=50):
        """Combined search + filter"""
        result = self.df.copy()
        
        # Filter by metadata
        if mood:
            result = result[result['mood_lower'] == mood.lower()]
        if genre:
            result = result[result['genre_lower'] == genre.lower()]
        if language:
            result = result[result['language_lower'] == language.lower()]
        if energy:
            result = result[result['Energy'] == energy]
        
        # Search by name
        if query and len(query.strip()) > 0:
            query_lower = query.lower().strip()
            result = result[result['song_lower'].str.contains(query_lower, na=False)]
        
        return result.to_dict('records')[:limit]
    
    def get_song_suggestions(self, partial_query, limit=10):
        """Get autocomplete suggestions"""
        if not partial_query or len(partial_query.strip()) == 0:
            return []
        
        query_lower = partial_query.lower().strip()
        suggestions = self.df[
            self.df['song_lower'].str.startswith(query_lower)
        ]['Song'].unique().tolist()
        
        return suggestions[:limit]
    
    def get_all_unique_values(self):
        """Get all unique values for filters"""
        return {
            'moods': sorted(self.df['Mood'].unique().tolist()),
            'genres': sorted(self.df['Genre'].unique().tolist()),
            'languages': sorted(self.df['Language'].unique().tolist()),
            'energies': sorted(self.df['Energy'].unique().tolist()),
        }
