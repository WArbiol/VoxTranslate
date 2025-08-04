import tkinter as tk
from tkinter import scrolledtext, Frame, Label, Button, OptionMenu, StringVar
from config import LANGUAGES
import src.state as state
from src.gui.settings_window import SettingsWindow
import queue

class TranslationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tradutor e Transcritor Simultâneo")
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")

        control_frame = Frame(root)
        control_frame.pack(pady=10)
        
        lang_options = list(LANGUAGES.keys())
        self.source_lang_var = StringVar(root)
        self.target_lang_var = StringVar(root)
        self.source_lang_var.set("Espanhol")
        self.target_lang_var.set("Português")

        Label(control_frame, text="De:", font=("Helvetica", 14)).pack(side=tk.LEFT, padx=(10, 0))
        self.source_menu = OptionMenu(control_frame, self.source_lang_var, *lang_options)
        self.source_menu.config(font=("Helvetica", 12))
        self.source_menu.pack(side=tk.LEFT, padx=(0, 10))

        Label(control_frame, text="Para:", font=("Helvetica", 14)).pack(side=tk.LEFT, padx=10)
        self.target_menu = OptionMenu(control_frame, self.target_lang_var, *lang_options)
        self.target_menu.config(font=("Helvetica", 12))
        self.target_menu.pack(side=tk.LEFT, padx=(0, 20))

        self.main_button = Button(control_frame, text="Iniciar", command=self.toggle_process, font=("Helvetica", 14), width=20)
        self.main_button.pack(side=tk.LEFT, padx=10)

        self.settings_button = Button(control_frame, text="Configurações", command=self.open_settings, font=("Helvetica", 14))
        self.settings_button.pack(side=tk.LEFT, padx=10)

        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Helvetica", 70, "bold"))
        self.text_area.pack(expand=True, fill='both', padx=10, pady=10)

        self.check_queue()

    def toggle_process(self):
        if state.listening_active.is_set():
            state.listening_active.clear()
            state.operation_mode = None
            self.main_button.config(text="Iniciar")
            self.source_menu.config(state=tk.NORMAL)
            self.target_menu.config(state=tk.NORMAL)
            print("Pausado.")
        else:
            source_lang_name = self.source_lang_var.get()
            target_lang_name = self.target_lang_var.get()

            if source_lang_name == target_lang_name:
                state.operation_mode = 'transcribe'
                self.main_button.config(text="Pausar")
                print(f"Iniciando TRANSCRIÇÃO no idioma: {source_lang_name}")
            else:
                state.operation_mode = 'translate'
                self.main_button.config(text="Pausar")
                print(f"Iniciando TRADUÇÃO: {source_lang_name} -> {target_lang_name}")

            state.source_lang_config = LANGUAGES[source_lang_name]
            state.target_lang_config = LANGUAGES[target_lang_name]
            
            state.listening_active.set()
            
            self.source_menu.config(state=tk.DISABLED)
            self.target_menu.config(state=tk.DISABLED)

    def open_settings(self):
        SettingsWindow(self.root)

    def check_queue(self):
        try:
            message = state.gui_queue.get_nowait()
            if message:
                self.text_area.insert(tk.END, message)
                self.text_area.yview(tk.END)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.check_queue)