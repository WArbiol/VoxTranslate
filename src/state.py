import queue
import threading

gui_queue = queue.Queue()

listening_active = threading.Event()
config_changed = threading.Event()

operation_mode = None
source_lang_config = None
target_lang_config = None