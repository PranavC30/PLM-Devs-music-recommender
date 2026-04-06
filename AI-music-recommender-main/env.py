class MusicEnv:
    def __init__(self):
        self.moods = ['Happy', 'Sad', 'Focus', 'Relaxed']
        self.times_of_day = ['Morning', 'Afternoon', 'Evening', 'Night']
        self.genres = ['Pop', 'Lo-fi', 'Rock', 'Instrumental', 'Classical']
        self.languages = ['Hindi', 'English', 'Punjabi', 'Tamil', 'Telugu']
        
        # State space representation: (mood, time_of_day, last_genre)
        # We start with None for last_genre if it's the first interaction. For simplicity,
        # we'll use a placeholder 'None' string.
        
    def get_state(self, mood, time_of_day, last_genre):
        """Builds a state tuple."""
        return f"{mood}_{time_of_day}_{last_genre}"

    def get_reward(self, feedback):
        """Returns the reward based on user feedback."""
        rewards = {
            'like': 10,
            'listen': 2,
            'skip': -5
        }
        return rewards.get(feedback, 0)
    
    def get_actions(self):
        """Returns available actions (genres)."""
        return self.genres
