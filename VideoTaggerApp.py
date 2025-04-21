import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import time
import threading
import subprocess
import os

class VideoTaggerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Video Tagger")

        self.video_path = None
        self.tags = []
        self.cap = None
        self.playing = False
        self.paused = False

        self.frame = None
        self.photo = None

        self.create_widgets()

    def create_widgets(self):
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(padx=10, pady=10)

        # Controles a la izquierda
        self.controls_frame = tk.Frame(self.main_frame)
        self.controls_frame.grid(row=0, column=0, padx=10)

        self.load_button = tk.Button(self.controls_frame, text="Cargar Video", command=self.load_video)
        self.load_button.pack(pady=5)

        control_frame = tk.Frame(self.controls_frame)
        control_frame.pack(pady=5)

        self.back_button = tk.Button(control_frame, text="⏪ -5s", command=lambda: self.seek(-5))
        self.back_button.grid(row=0, column=0)

        self.play_button = tk.Button(control_frame, text="▶️ Play", command=self.toggle_play_pause)
        self.play_button.grid(row=0, column=1)

        self.forward_button = tk.Button(control_frame, text="⏩ +5s", command=lambda: self.seek(5))
        self.forward_button.grid(row=0, column=2)

        self.tag_button = tk.Button(self.controls_frame, text="Agregar Tag", command=self.add_tag)
        self.tag_button.pack(pady=5)

        self.export_button = tk.Button(self.controls_frame, text="Exportar Clips", command=self.export_clips)
        self.export_button.pack(pady=5)

        self.tag_list = tk.Listbox(self.controls_frame, width=40)
        self.tag_list.pack(pady=10)

        self.remove_button = tk.Button(self.controls_frame, text="Eliminar Último Tag", command=self.remove_last_tag)
        self.remove_button.pack(pady=5)

        # Video a la derecha
        self.video_frame = tk.Frame(self.main_frame)
        self.video_frame.grid(row=0, column=1)

        self.video_label = tk.Label(self.video_frame)
        self.video_label.pack()

        self.video_label.bind("<Configure>", lambda e: self.show_frame())


    def load_video(self):
        path = filedialog.askopenfilename(filetypes=[("Videos", "*.mp4 *.avi *.mov")])
        if path:
            self.video_path = path
            self.tags = []
            self.tag_list.delete(0, tk.END)
            self.cap = cv2.VideoCapture(self.video_path)
            messagebox.showinfo("Video Cargado", f"Video cargado: {os.path.basename(path)}")

    def toggle_play_pause(self):
        if not self.cap:
            messagebox.showwarning("Error", "Carga un video primero.")
            return

        if not self.playing:
            self.playing = True
            self.paused = False
            self._play_video_loop()
            self.play_button.config(text="⏸️ Pause")
        else:
            self.paused = not self.paused
            self.play_button.config(text="▶️ Play" if self.paused else "⏸️ Pause")

    def _play_video_loop(self):
        if not self.playing or self.paused or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            self.playing = False
            self.play_button.config(text="▶️ Play")
            return

        self.frame = frame
        self.show_frame()

        delay = int(1000 / max(10, self.cap.get(cv2.CAP_PROP_FPS)))
        self.master.after(delay, self._play_video_loop)

    def show_frame(self):
        if self.frame is None:
            return

        # Usa el tamaño actual del label para escalar el frame
        width = self.video_label.winfo_width()
        height = self.video_label.winfo_height()

        if width < 10 or height < 10:
            return  # aún no se ha dibujado bien

        frame = cv2.resize(self.frame, (width, height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        self.photo = ImageTk.PhotoImage(image=img)
        self.video_label.config(image=self.photo)
        self.video_label.image = self.photo


    def seek(self, seconds):
        if self.cap:
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            new_frame = current_frame + (fps * seconds)
            new_frame = max(0, min(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) - 1, new_frame))
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)

    def add_tag(self):
        if not self.cap:
            messagebox.showwarning("Error", "Carga y reproduce un video primero.")
            return
        timestamp = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
        self.tags.append(timestamp)
        tag_type = "Inicio" if len(self.tags) % 2 != 0 else "Fin"
        clip_num = (len(self.tags) + 1) // 2
        self.tag_list.insert(tk.END, f"Clip {clip_num} - {tag_type}: {timestamp:.2f}s")

    def remove_last_tag(self):
        if self.tags:
            self.tags.pop()
            self.tag_list.delete(tk.END)

    def export_clips(self):
        if len(self.tags) < 2:
            messagebox.showwarning("Error", "Se necesitan al menos 2 tags.")
            return
        if len(self.tags) % 2 != 0:
            messagebox.showwarning("Advertencia", "Número impar de tags. El último será ignorado.")

        output_dir = filedialog.askdirectory(title="Selecciona carpeta de salida")
        if not output_dir:
            return

        FFMPEG_CMD = "ffmpeg"  # Puedes cambiarlo si tienes una ruta diferente

        for i in range(0, len(self.tags) - 1, 2):
            start = self.tags[i]
            end = self.tags[i+1]
            output_file = os.path.join(output_dir, f"clip_{i//2 + 1}.mp4")
            cmd = [
                FFMPEG_CMD,
                "-i", self.video_path,
                "-ss", str(start),
                "-to", str(end),
                "-c", "copy",
                output_file
            ]
            subprocess.run(cmd)

        messagebox.showinfo("Éxito", "Clips exportados correctamente.")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoTaggerApp(root)
    root.mainloop()
