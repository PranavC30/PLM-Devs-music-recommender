class MusicEnv:
    def __init__(self):
        self.moods = ['Happy', 'Sad', 'Focus', 'Relaxed']
        self.times_of_day = ['Morning', 'Afternoon', 'Evening', 'Night']
        self.genres = ['Pop', 'Lo-fi', 'Rock', 'Instrumental', 'Classical']
        self.languages = ['Hindi', 'English', 'Punjabi', 'Tamil', 'Telugu']

    def get_state(self, mood, time_of_day, last_genre):
        return f"{mood}_{time_of_day}_{last_genre}"

    def get_reward(self, feedback):
        rewards = {'like': 10, 'listen': 2, 'skip': -5}
        return rewards.get(feedback, 0)

    def get_actions(self):
        return self.genres
