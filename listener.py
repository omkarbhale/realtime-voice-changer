import pyaudio
import wave
import threading
import keyboard
import time


class AudioRecorder:
    def __init__(self, filename):
        self.filename = filename
        self.frames = []
        self.is_recording = False

        self.chunk = 1024  # Buffer size
        self.sample_format = pyaudio.paInt16  # 16-bit audio
        self.channels = 1  # Mono audio
        self.sample_rate = 44100  # Sample rate

        self.audio = pyaudio.PyAudio()

    def start_recording(self):
        self.is_recording = True
        self.frames = []
        threading.Thread(target=self._record).start()
        print("Recording started.")

    def stop_recording(self):
        self.is_recording = False
        print("Recording stopped.")
        self.save_audio()

    def _record(self):
        stream = self.audio.open(
            format=self.sample_format,
            channels=self.channels,
            rate=self.sample_rate,
            frames_per_buffer=self.chunk,
            input=True,
        )

        while self.is_recording:
            data = stream.read(self.chunk)
            self.frames.append(data)

        stream.stop_stream()
        stream.close()

    def save_audio(self):
        with wave.open(self.filename, "wb") as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(self.audio.get_sample_size(self.sample_format))
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(b"".join(self.frames))

        print(f"Audio saved as {self.filename}.")


# Usage
filename = "recorded_audio.wav"  # Specify the filename for saving the audio
recorder = AudioRecorder(filename)

while True:
    if keyboard.is_pressed("k"):
        if not recorder.is_recording:
            recorder.start_recording()
    else:
        if recorder.is_recording:
            recorder.stop_recording()
    time.sleep(0.1)
