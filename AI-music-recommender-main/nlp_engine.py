from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import speech_recognition as sr

class NLPEngine:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        self.recognizer = sr.Recognizer()

    def detect_mood_from_text(self, text):
        """
        Parses text and maps it to one of: ['Happy', 'Sad', 'Focus', 'Relaxed']
        """
        text = text.lower()
        score = self.analyzer.polarity_scores(text)
        
        # Keyword overrides for strong contextual cues
        focus_keywords = ['work', 'study', 'focus', 'read', 'code', 'exam', 'build']
        relax_keywords = ['sleep', 'tired', 'chill', 'calm', 'peace', 'bed', 'rest']
        happy_keywords = ['party', 'dance', 'excited', 'win', 'awesome', 'amazing']
        sad_keywords = ['broken', 'cry', 'alone', 'lonely', 'miss', 'heart']

        for word in focus_keywords:
            if word in text: return 'Focus'
        for word in relax_keywords:
            if word in text: return 'Relaxed'
        for word in happy_keywords:
            if word in text: return 'Happy'
        for word in sad_keywords:
            if word in text: return 'Sad'

        # Sentiment-based fallback
        compound = score['compound']
        
        if compound >= 0.5:
            return 'Happy'
        elif compound <= -0.5:
            return 'Sad'
        elif compound > 0 and compound < 0.5:
            return 'Relaxed'
        else:
            return 'Focus' # Neutral default to focus

    def generate_quote(self, mood):
        """Generates dynamic AI quotes depending on mood."""
        import random
        quotes = {
            'Happy': ["Keep shining, the world needs your light! ✨", "Dance to the rhythm of your own heart. 💃", "Happiness is an inside job! 🌞"],
            'Sad': ["It's okay to not be okay. Let the music heal you. 🌧️", "Tears are words the heart can't express. 💙", "Take a deep breath. You're stronger than you think. 🌻"],
            'Relaxed': ["Embrace the peace of this moment. 🍃", "Let your soul breathe and your mind drift. 🌊", "Quiet the mind, and the soul will speak. 🧘‍♂️"],
            'Focus': ["Hustle until your haters ask if you're hiring. 🚀", "Stay focused and extra sparkly. ⚡", "The secret of your future is hidden in your daily routine. 📚"]
        }
        return random.choice(quotes.get(mood, ["Enjoy the music! 🎵"]))

    def transcribe_audio(self, audio_data):
        """
        Transcribes an audio file-like object into text using Google Speech Recognition.
        """
        try:
            with sr.AudioFile(audio_data) as source:
                audio = self.recognizer.record(source)
            text = self.recognizer.recognize_google(audio)
            return text
        except Exception as e:
            print("Audio parsing error:", e)
            return ""
