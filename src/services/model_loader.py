import torch
import whisper
from transformers import MarianMTModel, MarianTokenizer
from config import ASR_MODEL_SIZE, MT_MODEL_NAME

def load_all_models():
    print("A carregar o modelo Silero VAD...")
    vad_model, utils = torch.hub.load(
        repo_or_dir='snakers4/silero-vad',
        model='silero_vad',
        force_reload=True
    )
    print("Modelo VAD carregado.")

    print(f"A carregar o modelo Whisper ASR: {ASR_MODEL_SIZE}...")
    asr_model = whisper.load_model(ASR_MODEL_SIZE)
    print("Modelo ASR carregado.")

    print(f"A carregar o modelo MT: {MT_MODEL_NAME}...")
    mt_tokenizer = MarianTokenizer.from_pretrained(MT_MODEL_NAME)
    mt_translator = MarianMTModel.from_pretrained(MT_MODEL_NAME)
    print("Modelo MT carregado.")

    models = {
        "vad": {"model": vad_model, "utils": utils},
        "asr": asr_model,
        "mt": {"tokenizer": mt_tokenizer, "translator": mt_translator}
    }
    return models