import tkinter as tk
from tkinter import filedialog, messagebox
from video_player import VideoPlayer
from tag_manager import TagManager
from utils import export_clips
from utils import generate_proxy
import os

class VideoTaggerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Video Tagger")
        self.video_path = None

        self.video_player = None
        self.tag_manager = TagManager()

        self.create_widgets()

    def create_widgets(self):
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.controls_frame = tk.Frame(self.main_frame)
        self.controls_frame.grid(row=0, column=0, sticky="ns")

        self.load_button = tk.Button(self.controls_frame, text="Cargar Video", command=self.load_video)
        self.load_button.pack(pady=5)

        self.play_button = tk.Button(self.controls_frame, text="▶️ Play", command=self.toggle_play_pause)
        self.play_button.pack(pady=5)

        self.back_button = tk.Button(self.controls_frame, text="⏪ -5s", command=lambda: self.seek(-5))
        self.back_button.pack(pady=5)

        self.forward_button = tk.Button(self.controls_frame, text="⏩ +5s", command=lambda: self.seek(5))
        self.forward_button.pack(pady=5)

        self.tag_button = tk.Button(self.controls_frame, text="Agregar Tag", command=self.add_tag)
        self.tag_button.pack(pady=5)

        self.remove_button = tk.Button(self.controls_frame, text="Eliminar Último Tag", command=self.remove_last_tag)
        self.remove_button.pack(pady=5)

        self.export_button = tk.Button(self.controls_frame, text="Exportar Clips", command=self.export_clips)
        self.export_button.pack(pady=5)

        self.tag_list = tk.Listbox(self.controls_frame, width=40)
        self.tag_list.pack(pady=10)

        # Video panel
        self.video_frame = tk.Frame(self.main_frame, bg="black")
        self.video_frame.grid(row=0, column=1, sticky="nsew")

        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.video_label = tk.Label(self.video_frame, bg="black")
        self.video_label.pack(fill=tk.BOTH, expand=True)
        self.video_label.bind("<Configure>", lambda e: self.refresh_frame())


    def load_video(self):
        path = filedialog.askopenfilename(filetypes=[("Videos", "*.mp4 *.avi *.mov")])
        if path:
            self.video_path = path
            self.tag_manager.clear()
            self.tag_list.delete(0, tk.END)

            # Crear proxy
            proxy_path = generate_proxy(self.video_path)
            self.video_player = VideoPlayer(self.video_label, proxy_path)
            self.video_player.original_path = self.video_path  # Guarda original para exportar

            self.video_player.show_current_frame()
            messagebox.showinfo("Video Cargado", f"Video cargado en modo edición (proxy)")




    def toggle_play_pause(self):
        if self.video_player:
            playing = self.video_player.toggle_play_pause()
            self.play_button.config(text="▶️ Play" if not playing else "⏸️ Pause")

    def refresh_frame(self):
        if self.video_player:
            self.video_player.show_current_frame()

    def seek(self, seconds):
        if self.video_player:
            self.video_player.seek(seconds)

    def add_tag(self):
        if self.video_player:
            timestamp = self.video_player.get_current_time()
            self.tag_manager.add(timestamp)
            label = self.tag_manager.get_last_tag_label()
            self.tag_list.insert(tk.END, label)

    def remove_last_tag(self):
        self.tag_manager.remove_last()
        self.tag_list.delete(tk.END)

    def export_clips(self):
        if not self.video_path or not self.video_player:
            return

        output_dir = filedialog.askdirectory(title="Selecciona carpeta de salida")
        if output_dir:
            original_path = getattr(self.video_player, "original_path", self.video_path)
            export_clips(original_path, self.tag_manager.tags, output_dir)
            messagebox.showinfo("Éxito", "Clips exportados correctamente.")

