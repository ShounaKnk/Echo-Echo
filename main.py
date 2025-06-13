import soundcard as sc
import soundfile as sf
import numpy as np
import socket
import threading
import time

SAMPLE_RATE = 48000
CHANNEL = 2
CHUNK_SIZE = 512
PORT = 50007

speaker = sc.default_speaker()
mic = sc.get_microphone(speaker.name, include_loopback=True)

# Socket Setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', PORT))
server_socket.listen(1)

print(f"waiting for the client on port {PORT}...")

client_socket, addr = server_socket.accept()
print(f'client connected from {addr}')

def normalize_audio(audio_file):
    max_val = np.max(np.abs(audio_file))
    if max_val >0:
        audio_file /= max_val
        audio_file *= 0.9
    return audio_file

with mic.recorder(samplerate=SAMPLE_RATE) as recorder:
    print('streaming started')
    try:
        while True:
            time.sleep(0.01)
            data = recorder.record(numframes=CHUNK_SIZE)
            data = normalize_audio((data))
            pcm = (data*32767).astype(np.int16).tobytes()
            print(f"Sending chunk: {len(pcm)} bytes")
            client_socket.sendall(pcm)
    except BrokenPipeError:
        print('Client Disconnected')
    except KeyboardInterrupt:
        print('server stopped')
    
client_socket.close()
server_socket.close()