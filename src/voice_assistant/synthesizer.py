import logging
import queue
import threading

import numpy as np
import sounddevice as sd
import torch

from scipy.signal import resample_poly

from chatterbox.tts_turbo import ChatterboxTurboTTS

from .audio_utils import MAX_TTS_ERRORS


class Synthesizer:
    def __init__(self, args, interrupt_event: threading.Event):
        self.args = args
        self.interrupt_event = interrupt_event

        self.queue = queue.Queue()
        self.stop_event = threading.Event()
        self.is_speaking_event = threading.Event()
        self.has_failed = threading.Event()

        self.model = None
        self.sample_rate = None

        # Debugging for correct sample rate 
        print("Chatterbox rate:", self.sample_rate)

        device_info = sd.query_devices(
                self.args.piper_output_device_index,
                "output",
                )

        print("Output device:", device_info["name"])
        print("Output rate:", device_info["default_samplerate"])

        self._load_model()

        self.thread = threading.Thread(
            target=self._worker,
            daemon=True,
        )
        self.thread.start()

    def _load_model(self):
        logging.info("Initializing Chatterbox-Turbo TTS...")

        try:
            # ROCm uses PyTorch's CUDA-compatible API.
            device = "cuda" if torch.cuda.is_available() else "cpu"

            logging.info(f"Chatterbox device: {device}")

            self.model = ChatterboxTurboTTS.from_pretrained(
                device=device
            )

            self.sample_rate = self.model.sr

            device_info = sd.query_devices(
                    self.args.piper_output_device_index,
                    "output",
                    )

            self.output_rate = int(
                    device_info["default_samplerate"]
                    )

            logging.info(
                f"Loaded Chatterbox-Turbo. "
                f"Rate: {self.sample_rate}Hz"
            )

        except Exception as e:
            logging.critical(
                f"Chatterbox TTS initialization failed: {e}"
            )
            self.has_failed.set()
    def _generate_audio(self, text: str) -> np.ndarray:
        wav = self.model.generate(text)

        audio = (
            wav
            .detach()
            .squeeze()
            .float()
            .cpu()
            .numpy()
        )

        audio = np.asarray(audio, dtype=np.float32)

        print("model sample rate:", self.sample_rate)
        print("output sample rate:", self.output_rate)
        print("before resample:", len(audio))

        if self.sample_rate != self.output_rate:
            audio = resample_poly(
                audio,
                self.output_rate,
                self.sample_rate,
            ).astype(np.float32)

        print("after resample:", len(audio))

        return audio

    def _worker(self):
        consecutive_errors = 0

        while not self.stop_event.is_set():
            text = None

            try:
                text = self.queue.get(timeout=0.1)

                if text is None:
                    break

                if self.interrupt_event.is_set():
                    continue

                self.is_speaking_event.set()

                logging.debug(
                    f"Generating Chatterbox speech: {text!r}"
                )

                audio = self._generate_audio(text)

                # User may have interrupted while generation was running.
                if self.interrupt_event.is_set():
                    continue

                device_info = sd.query_devices(
                self.args.piper_output_device_index,
                "output",
                )

                output_rate = int(device_info["default_samplerate"])

                if self.sample_rate != output_rate:
                    audio = resample_poly(
                        audio,
                        output_rate,
                        self.sample_rate,
                    ).astype(np.float32)

                audio = self._generate_audio(text)

                print("audio shape:", audio.shape)
                print("audio dtype:", audio.dtype)
                print("audio min/max:", audio.min(), audio.max())

                sd.play(
                    audio,
                    #samplerate=self.sample_rate,
                    samplerate=44100,
                    #device=self.args.piper_output_device_index,
                    blocking=True,
                )

                consecutive_errors = 0

            except queue.Empty:
                continue

            except Exception as e:
                logging.error(f"TTS Error: {e}")

                consecutive_errors += 1

                if consecutive_errors >= MAX_TTS_ERRORS:
                    self.has_failed.set()
                    break

            finally:
                if text is not None:
                    self.queue.task_done()

                if self.queue.empty():
                    self.is_speaking_event.clear()

    def speak(self, text: str):
        if not self.has_failed.is_set():
            self.queue.put(text)

    def stop(self):
        self.stop_event.set()

        self.clear_queue()

        # Stop any currently playing sounddevice audio.
        sd.stop()

        self.queue.put(None)

        self.thread.join(timeout=5.0)

        if self.model is not None:
            del self.model
            self.model = None

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def clear_queue(self):
        with self.queue.mutex:
            self.queue.queue.clear()

        # Also interrupt current playback.
        sd.stop()
