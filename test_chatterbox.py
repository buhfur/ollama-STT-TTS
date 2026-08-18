#!/usr/bin/env python3 
import torch
import torchaudio as ta

from chatterbox.tts_turbo import ChatterboxTurboTTS


device = "cuda" if torch.cuda.is_available() else "cpu"

print("device:", device)

model = ChatterboxTurboTTS.from_pretrained(
    device=device
)

wav = model.generate(
    "Okay, let me run that system update for you."
)

ta.save(
    "test.wav",
    wav,
    model.sr,
)

print("Wrote test.wav")
