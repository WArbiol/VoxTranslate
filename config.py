LANGUAGES = {
    "Português": {"whisper": "portuguese", "marian": "por"},
    "Espanhol":  {"whisper": "spanish",    "marian": "spa"},
    "Inglês":    {"whisper": "english",    "marian": "eng"},
    "Francês":   {"whisper": "french",     "marian": "fra"},
    "Italiano":  {"whisper": "italian",    "marian": "ita"},
    "Alemão":    {"whisper": "german",     "marian": "deu"},
}

VAD_CONFIG = {
    "SPEECH_PROB_THRESHOLD": 0.38,
    "MIN_SILENCE_DURATION_MS": 90,
    "SPEECH_PAD_MS": 200,
    "MIN_SPEECH_DURATION_MS": 200,
}

FORMAT = 16
CHANNELS = 1
RATE = 16000
CHUNK_AUDIO_SIZE = 1024
CHUNK_VAD_SIZE = 512

ASR_MODEL_SIZE = "base"
MT_MODEL_NAME = "Helsinki-NLP/opus-mt-tc-bible-big-mul-mul"