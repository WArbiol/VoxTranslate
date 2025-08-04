import asyncio
import pyaudio
from config import FORMAT, CHANNELS, RATE, CHUNK_AUDIO_SIZE, CHUNK_VAD_SIZE
import src.state as state
from src.pipeline.processors import vad_processor, asr_processor, mt_processor

async def main_pipeline(models):
    raw_audio_queue = asyncio.Queue()
    speech_chunk_queue = asyncio.Queue()
    source_text_queue = asyncio.Queue()

    asyncio.create_task(vad_processor(raw_audio_queue, speech_chunk_queue, models))
    asyncio.create_task(asr_processor(speech_chunk_queue, source_text_queue, models))
    asyncio.create_task(mt_processor(source_text_queue, models))

    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(FORMAT // 8),
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK_AUDIO_SIZE,
                    start=False)

    print("\n>>> Selecione os idiomas e clique em 'Iniciar' na janela do programa. <<<")
    loop = asyncio.get_running_loop()
    stream_is_active = False

    try:
        while True:
            if state.listening_active.is_set():
                if not stream_is_active:
                    print("Iniciando stream de áudio...")
                    stream.start_stream()
                    stream_is_active = True
                
                audio_data = await loop.run_in_executor(
                    None, lambda: stream.read(CHUNK_AUDIO_SIZE, exception_on_overflow=False)
                )
                
                num_bytes_per_sample = FORMAT // 8
                bytes_per_vad_chunk = CHUNK_VAD_SIZE * num_bytes_per_sample
                for i in range(0, len(audio_data), bytes_per_vad_chunk):
                    sub_chunk = audio_data[i : i + bytes_per_vad_chunk]
                    if len(sub_chunk) == bytes_per_vad_chunk:
                        await raw_audio_queue.put(sub_chunk)
            
            else:
                if stream_is_active:
                    print("Parando stream de áudio...")
                    stream.stop_stream()
                    stream_is_active = False
                    while not raw_audio_queue.empty():
                        raw_audio_queue.get_nowait()
                await asyncio.sleep(0.1)

    except asyncio.CancelledError:
        print("\nPipeline assíncrono cancelado.")
    finally:
        print("A limpar recursos do pipeline...")
        if stream.is_active():
            stream.stop_stream()
        stream.close()
        p.terminate()