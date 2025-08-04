import tkinter as tk
from tkinter import Toplevel, Label, Entry, Button, messagebox
from config import VAD_CONFIG
import src.state as state

class SettingsWindow(Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Configurações do VAD")
        self.geometry("400x250")
        self.transient(master)
        self.grab_set()

        self.entries = {}
        for i, (key, value) in enumerate(VAD_CONFIG.items()):
            Label(self, text=f"{key}:").grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = Entry(self, width=15)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entry.insert(0, str(value))
            self.entries[key] = entry

        save_button = Button(self, text="Salvar", command=self.save_settings)
        save_button.grid(row=len(VAD_CONFIG), columnspan=2, pady=10)

    def save_settings(self):
        try:
            VAD_CONFIG["SPEECH_PROB_THRESHOLD"] = float(self.entries["SPEECH_PROB_THRESHOLD"].get())
            VAD_CONFIG["MIN_SILENCE_DURATION_MS"] = int(self.entries["MIN_SILENCE_DURATION_MS"].get())
            VAD_CONFIG["SPEECH_PAD_MS"] = int(self.entries["SPEECH_PAD_MS"].get())
            VAD_CONFIG["MIN_SPEECH_DURATION_MS"] = int(self.entries["MIN_SPEECH_DURATION_MS"].get())
            print("Configurações salvas:", VAD_CONFIG)
            state.config_changed.set()
            self.destroy()
        except ValueError:
            messagebox.showerror("Erro de Formato", "Por favor, insira valores numéricos válidos.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao salvar: {e}")