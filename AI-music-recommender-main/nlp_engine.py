from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# SpeechRecognition + PyAudio are optional — voice input gracefully disabled if missing
try:
    import speech_recognition as sr
    _SR_AVAILABLE = True
except ImportError:
    _SR_AVAILABLE = False

class NLPEngine:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        if _SR_AVAILABLE:
            self.recognizer = sr.Recognizer()
        else:
            self.recognizer = None

    def detect_mood_from_text(self, text):
        text = text.lower()
        score = self.analyzer.polarity_scores(text)
        for word in ['work','study','focus','read','code','exam','build']:
            if word in text: return 'Focus'
        for word in ['sleep','tired','chill','calm','peace','bed','rest']:
            if word in text: return 'Relaxed'
        for word in ['party','dance','excited','win','awesome','amazing']:
            if word in text: return 'Happy'
        for word in ['broken','cry','alone','lonely','miss','heart']:
            if word in text: return 'Sad'
        c = score['compound']
        if c >= 0.5:    return 'Happy'
        elif c <= -0.5: return 'Sad'
        elif c > 0:     return 'Relaxed'
        else:           return 'Focus'

    def generate_quote(self, mood):
        import random
        quotes = {
            'Happy':   ["Keep shining, the world needs your light! ✨","Dance to the rhythm of your own heart. 💃","Happiness is an inside job! 🌞"],
            'Sad':     ["It's okay to not be okay. Let the music heal you. 🌧️","Tears are words the heart can't express. 💙","Take a deep breath. You're stronger than you think. 🌻"],
            'Relaxed': ["Embrace the peace of this moment. 🍃","Let your soul breathe and your mind drift. 🌊","Quiet the mind, and the soul will speak. 🧘‍♂️"],
            'Focus':   ["Hustle until your haters ask if you're hiring. 🚀","Stay focused and extra sparkly. ⚡","The secret of your future is hidden in your daily routine. 📚"],
        }
        return random.choice(quotes.get(mood, ["Enjoy the music! 🎵"]))

    def transcribe_audio(self, audio_data):
        if not _SR_AVAILABLE or self.recognizer is None:
            return ""
        try:
            with sr.AudioFile(audio_data) as source:
                audio = self.recognizer.record(source)
            return self.recognizer.recognize_google(audio)
        except Exception as e:
            print("Audio parsing error:", e)
            return ""
