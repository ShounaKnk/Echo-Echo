import soundcard as sc
import soundfile as sf
import numpy as np

SAMPLE_RATE = 48000
DURATION = 5

speaker = sc.default_speaker()

mic = sc.get_microphone(speaker.name, include_loopback=True)

with mic.recorder(samplerate=SAMPLE_RATE) as recorder:
    audio_data = recorder.record(numframes=SAMPLE_RATE*DURATION)

def normalize_audio(audio_file):
    max_val = np.max(np.abs(audio_file))
    if max_val >0:
        audio_file /= max_val
        audio_file *= 0.9
    return audio_file

audio_data = normalize_audio(audio_data)

sf.write('test.wav', audio_data, SAMPLE_RATE)
print('saved')