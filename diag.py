#!/usr/bin/env python3  

import sounddevice as sd

print("Default devices:", sd.default.device)
print()

for i, dev in enumerate(sd.query_devices()):
    if dev["max_output_channels"] > 0:
        print(
            i,
            dev["name"],
            "channels=", dev["max_output_channels"],
            "default_rate=", dev["default_samplerate"],
        )

        for rate in (24000, 44100, 48000):
            try:
                sd.check_output_settings(
                    device=i,
                    samplerate=rate,
                    channels=1,
                    dtype="float32",
                )
                print("   OK:", rate)
            except Exception as e:
                print("   FAIL:", rate, e)
