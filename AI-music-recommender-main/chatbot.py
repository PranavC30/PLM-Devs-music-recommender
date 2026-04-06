import random
import pandas as pd
import os

class MusicChatbot:
    """
    Rule-based AI chatbot that understands natural language song requests
    and returns recommendations from the songs database.
    """

    LANG_KEYWORDS = {
        'Hindi':   ['hindi', 'bollywood', 'desi', 'indian'],
        'English': ['english', 'western', 'english songs'],
        'Punjabi': ['punjabi', 'bhangra', 'punjab'],
        'Tamil':   ['tamil', 'kollywood', 'tamilnadu'],
        'Telugu':  ['telugu', 'tollywood', 'andhra'],
    }
    MOOD_KEYWORDS = {
        'Happy':   ['happy', 'party', 'dance', 'fun', 'excited', 'celebrate', 'khush', 'mast', 'enjoy'],
        'Sad':     ['sad', 'cry', 'heartbreak', 'lonely', 'miss', 'dukhi', 'broken', 'udaas', 'dard'],
        'Focus':   ['focus', 'study', 'work', 'concentrate', 'padhai', 'exam', 'code', 'productive'],
        'Relaxed': ['relax', 'chill', 'calm', 'sleep', 'peace', 'rest', 'sukoon', 'aaram', 'soothing'],
    }
    GENRE_KEYWORDS = {
        'Lo-fi':        ['lofi', 'lo-fi', 'lo fi', 'chill beats'],
        'Rock':         ['rock', 'metal', 'guitar', 'band'],
        'Classical':    ['classical', 'sufi', 'devotional', 'instrumental classical'],
        'Instrumental': ['instrumental', 'background', 'no lyrics'],
        'Pop':          ['pop', 'mainstream', 'trending'],
    }

    GREETINGS = ['hi', 'hello', 'hey', 'hii', 'helo', 'namaste', 'sup', 'yo']
    THANKS     = ['thanks', 'thank you', 'shukriya', 'dhanyawad', 'ty', 'thx']

    def __init__(self, data_path=None):
        if data_path is None:
            data_path = os.path.join(os.path.dirname(__file__), 'data', 'songs.csv')
        self.df = pd.read_csv(data_path)

    def _detect(self, text, keyword_map):
        text = text.lower()
        for label, keywords in keyword_map.items():
            for kw in keywords:
                if kw in text:
                    return label
        return None

    def respond(self, user_input: str) -> dict:
        """
        Returns dict: { 'text': str, 'songs': list[dict] }
        songs is empty list if no recommendations needed.
        """
        text = user_input.strip().lower()

        # Greetings
        if any(g in text for g in self.GREETINGS):
            return {"text": "Hey! 👋 Tell me what kind of songs you want — mood, language, genre, anything!", "songs": []}

        # Thanks
        if any(t in text for t in self.THANKS):
            return {"text": "Anytime! 🎵 Music is always here for you.", "songs": []}

        # Help
        if 'help' in text or 'kya kar' in text:
            return {"text": (
                "Main tumhare liye songs dhundh sakta hoon! Bas bolo:\n"
                "- 'Sad Hindi songs do'\n"
                "- 'Kuch party songs chahiye'\n"
                "- 'Punjabi chill songs'\n"
                "- 'Focus ke liye lofi'\n"
                "- 'Surprise me!'"
            ), "songs": []}

        # Surprise
        if 'surprise' in text or 'random' in text or 'kuch bhi' in text:
            songs = self.df.sample(min(3, len(self.df))).to_dict('records')
            return {"text": "🎲 Surprise! Yeh lo random picks:", "songs": songs}

        # Detect mood, language, genre
        mood    = self._detect(text, self.MOOD_KEYWORDS)
        lang    = self._detect(text, self.LANG_KEYWORDS)
        genre   = self._detect(text, self.GENRE_KEYWORDS)

        if mood is None and lang is None and genre is None:
            return {"text": (
                "Hmm, samajh nahi aaya 🤔 Thoda aur batao!\n"
                "Example: 'sad hindi songs', 'party punjabi', 'lofi focus music'"
            ), "songs": []}

        # Filter
        filtered = self.df.copy()
        if mood:   filtered = filtered[filtered['Mood'] == mood]
        if lang:   filtered = filtered[filtered['Language'].str.lower() == lang.lower()]
        if genre:  filtered = filtered[filtered['Genre'] == genre]

        # Fallback if too few
        if len(filtered) < 3:
            if mood and lang:
                filtered = self.df[(self.df['Mood'] == mood) | (self.df['Language'].str.lower() == lang.lower())]
            elif mood:
                filtered = self.df[self.df['Mood'] == mood]
            elif lang:
                filtered = self.df[self.df['Language'].str.lower() == lang.lower()]

        if len(filtered) == 0:
            filtered = self.df

        songs = filtered.sample(min(3, len(filtered))).to_dict('records')

        parts = []
        if mood:  parts.append(mood)
        if lang:  parts.append(lang)
        if genre: parts.append(genre)
        label = " + ".join(parts) if parts else "random"

        responses = [
            f"🎵 Yeh lo {label} songs!",
            f"Found some great {label} tracks for you 🎧",
            f"Here are your {label} picks ✨",
        ]
        return {"text": random.choice(responses), "songs": songs}
