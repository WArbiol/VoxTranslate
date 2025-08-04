import asyncio
import threading
import tkinter as tk
from src.gui.main_window import TranslationApp
from src.pipeline.audio_pipeline import main_pipeline
from src.services.model_loader import load_all_models

def start_pipeline_thread(models):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main_pipeline(models))
    except Exception as e:
        print(f"Erro fatal no loop assíncrono: {e}")
        
if __name__ == "__main__":
    models = load_all_models()

    pipeline_thread = threading.Thread(
        target=start_pipeline_thread,
        args=(models,),
        daemon=True
    )

    root = tk.Tk()
    app = TranslationApp(root)

    pipeline_thread.start()

    root.mainloop()