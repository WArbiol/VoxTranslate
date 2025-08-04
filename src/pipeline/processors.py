import asyncio
import torch
import numpy as np
import src.state as state
from config import VAD_CONFIG, RATE
from src.services.translator import translate_text

async def vad_processor(raw_audio_queue, speech_chunk_queue, models):
    print("Processador VAD iniciado.")
    vad_model = models["vad"]["model"]
    (get_speech_timestamps, _, read_audio, VADIterator, collect_chunks) = models["vad"]["utils"]

    def create_vad_iterator():
        return VADIterator(
            vad_model,
            threshold=VAD_CONFIG["SPEECH_PROB_THRESHOLD"],
            min_silence_duration_ms=VAD_CONFIG["MIN_SILENCE_DURATION_MS"],
            speech_pad_ms=VAD_CONFIG["SPEECH_PAD_MS"]
        )

    vad_iterator = create_vad_iterator()
    MIN_SPEECH_SAMPLES = int(RATE * VAD_CONFIG["MIN_SPEECH_DURATION_MS"] / 1000)
    triggered = False
    speech_chunks = []

    while True:
        if state.config_changed.is_set():
            print("VAD: Novas configurações recebidas. Reiniciando o iterador VAD.")
            vad_iterator = create_vad_iterator()
            MIN_SPEECH_SAMPLES = int(RATE * VAD_CONFIG["MIN_SPEECH_DURATION_MS"] / 1000)
            state.config_changed.clear()

        try:
            audio_chunk_bytes = await asyncio.wait_for(raw_audio_queue.get(), timeout=0.1)
        except asyncio.TimeoutError:
            continue

        audio_tensor = torch.from_numpy(np.frombuffer(audio_chunk_bytes, dtype=np.int16)).float() / 32768.0
        speech_dict = vad_iterator(audio_tensor, return_seconds=False)

        if speech_dict:
            if "start" in speech_dict:
                if not triggered:
                    print("VAD: Início da fala detetado.")
                    triggered = True
                speech_chunks.append(audio_tensor)
            elif "end" in speech_dict and triggered:
                speech_chunks.append(audio_tensor)
                full_utterance = torch.cat(speech_chunks)
                if len(full_utterance) > MIN_SPEECH_SAMPLES:
                    print(f"VAD: Fim da fala detetado. Enviando segmento de {len(full_utterance)/RATE:.2f}s para ASR.")
                    await speech_chunk_queue.put(full_utterance)
                else:
                    print(f"VAD: Segmento de fala muito curto ({len(full_utterance)/RATE:.2f}s), ignorando.")
                triggered = False
                speech_chunks = []
        elif triggered:
            speech_chunks.append(audio_tensor)
        raw_audio_queue.task_done()

async def asr_processor(speech_chunk_queue, source_text_queue, models):
    print("Processador ASR (Whisper) iniciado.")
    asr_model = models["asr"]
    while True:
        audio_tensor = await speech_chunk_queue.get()
        audio_np = audio_tensor.numpy()

        lang = None
        if state.source_lang_config:
            lang = state.source_lang_config['whisper']

        if lang:
            result = asr_model.transcribe(audio_np, language=lang, fp16=torch.cuda.is_available())
            text = result.get('text', '').strip()

            if text:
                if state.operation_mode == 'translate':
                    print(f"ASR ({lang}): {text}")
                    await source_text_queue.put(text)
                elif state.operation_mode == 'transcribe':
                    print(f"ASR ({lang}): {text}")
                    state.gui_queue.put(text.upper() + " ")

        speech_chunk_queue.task_done()

async def mt_processor(source_text_queue, models):
    print("Processador MT iniciado.")
    mt_tokenizer = models["mt"]["tokenizer"]
    mt_translator = models["mt"]["translator"]
    while True:
        source_text = await source_text_queue.get()
        if source_text and state.operation_mode == 'translate' and state.target_lang_config:
            target_code = state.target_lang_config['marian']
            translated_text = translate_text(source_text, target_code, mt_tokenizer, mt_translator)
            print(f"TRADUÇÃO ({target_code}): {translated_text}")
            state.gui_queue.put(translated_text + " ")
        source_text_queue.task_done()