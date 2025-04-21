import cv2
from PIL import Image, ImageTk

class VideoPlayer:
    def __init__(self, label_widget, video_path):
        self.label = label_widget
        self.cap = cv2.VideoCapture(video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame = None
        self.photo = None
        self.playing = False
        self.paused = False

        # Lee el primer frame para mostrarlo desde el principio
        ret, frame = self.cap.read()
        if ret:
            self.frame = frame


    def toggle_play_pause(self):
        if not self.cap.isOpened():
            return False
        if not self.playing:
            self.playing = True
            self.paused = False
            self._play_loop()
        else:
            self.paused = not self.paused
        return not self.paused

    def _play_loop(self):
        if not self.playing or self.paused:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.playing = False
            return

        self.frame = frame
        self.show_current_frame()

        delay = int(1000 / max(10, self.fps))
        self.label.after(delay, self._play_loop)

    def show_current_frame(self):
        if self.frame is None:
            return

        # Tamaño del video original
        frame_h, frame_w, _ = self.frame.shape
        aspect_ratio = frame_w / frame_h

        # Tamaño del contenedor
        container_w = self.label.winfo_width()
        container_h = self.label.winfo_height()

        if container_w < 10 or container_h < 10:
            return

        # Calcular nuevo tamaño manteniendo la proporción
        if container_w / container_h > aspect_ratio:
            new_h = container_h
            new_w = int(aspect_ratio * new_h)
        else:
            new_w = container_w
            new_h = int(new_w / aspect_ratio)

        # Redimensionar el frame manteniendo proporción
        resized = cv2.resize(self.frame, (new_w, new_h))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)

        # Convertir a imagen y pegar en un fondo negro del tamaño del contenedor
        full_image = Image.new("RGB", (container_w, container_h), "black")
        x = (container_w - new_w) // 2
        y = (container_h - new_h) // 2
        full_image.paste(img, (x, y))

        self.photo = ImageTk.PhotoImage(image=full_image)
        self.label.config(image=self.photo)
        self.label.image = self.photo


    def seek(self, seconds):
        pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        new_pos = pos + seconds * self.fps
        new_pos = max(0, min(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) - 1, new_pos))
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_pos)

    def get_current_time(self):
        return self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
