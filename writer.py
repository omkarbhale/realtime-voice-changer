import pyaudio
import numpy as np
import wave
import os
import hashlib
import time
import whisper
import pyttsx3


def getCableInputIndex():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info["maxOutputChannels"] == 0:
            continue
        if device_info["name"].startswith("CABLE"):
            print(f"Cable input index found: {i}")
            return i


def getDeviceOutputIndex():
    p = pyaudio.PyAudio()
    device_info = p.get_default_output_device_info()
    print(f"Default output index found: {device_info['index']}")
    return device_info["index"]


class AudioWriter:
    def __init__(self, cable_input_index, device_output_index) -> None:
        self.cable_input_index = cable_input_index
        self.device_output_index = device_output_index
        self.model = whisper.load_model("base")
        self.engine = pyttsx3.Engine()
        pass

    def convert_audio(self, filename, target="converted_audio.wav"):
        result = self.model.transcribe(filename)
        print(f'"{result["text"]}"')
        if not result:
            return False
        self.engine.save_to_file(result["text"], target)
        self.engine.runAndWait()
        print(f"saved {result['text']}")
        return True

    def play_audio(self, filename):
        target = "converted_audio.wav"
        if not self.convert_audio(filename, target):
            return

        CHUNK_SIZE = 1024
        p = pyaudio.PyAudio()

        wf = wave.open(target)
        stream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True,
            output_device_index=7,
        )
        playbackstream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True,
            output_device_index=self.device_output_index,
        )

        while len(data := wf.readframes(CHUNK_SIZE)):  # Requires Python 3.8+ for :=
            stream.write(data)
            playbackstream.write(data)

        stream.close()
        playbackstream.close()
        wf.close()
        p.terminate()


# Play the audio data on the virtual microphone
# AudioWriter(getCableInputIndex(), getDeviceOutputIndex()).play_audio(
#     "ke ha - backstabber.wav"
# )


class FileWatcher:
    def __init__(self, file_path):
        self.file_path = file_path
        self.current_hash = self.get_file_hash()

    def get_file_hash(self):
        """
        Generates the hash of the file using SHA-256 algorithm.
        """
        hash_object = hashlib.sha256()
        with open(self.file_path, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                hash_object.update(chunk)
        return hash_object.hexdigest()

    def watch(self):
        """
        Monitors the specified file for modifications.
        """
        while True:
            time.sleep(0.1)  # Sleep for 1 second before the next check

            if not os.path.exists(self.file_path):
                print(f"File '{self.file_path}' not found.")
                break

            new_hash = self.get_file_hash()
            if new_hash != self.current_hash:
                print(f"File '{self.file_path}' has been modified.")

                AudioWriter(getCableInputIndex(), getDeviceOutputIndex()).play_audio(
                    self.file_path
                )
                self.current_hash = new_hash


# Usage example
watcher = FileWatcher("recorded_audio.wav")
watcher.watch()
