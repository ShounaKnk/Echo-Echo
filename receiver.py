import socket
import numpy as np
import queue
import threading
import sounddevice as sd

SAMPLE_RATE =48000  
CHANNELS = 2
CHUNK_SIZE = 512
SERVER_IP = '192.168.0.102'
PORT = 50007

audio_queue = queue.Queue(maxsize=5)

#CONNECT TO SERVER

print("connected to audio stream")

def callback(outdata, frames, time, status):
    # data = sock.recv(CHUNK_SIZE*CHANNELS*2)
    # print(f'received {len(data)} bytes')
    # if not data:
    #     raise sd.CallbackAbort
    # outdata[:] = np.frombuffer(data, dtype=np.int16).reshape(-1, CHANNELS)/32767
    try:
        data = audio_queue.get_nowait()
    except queue.Empty:
        print("buffer underrun")
        outdata[:] = np.zeros((frames, CHANNELS), dtype=np.float32)
        return
    outdata[:]=data

    
stream = sd.OutputStream(samplerate=SAMPLE_RATE, channels= CHANNELS, callback=callback, blocksize=CHUNK_SIZE, dtype='float32')
stream.start()

def receive_audio():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, PORT))
    print("connected to stream")
    
    try:
        while True:
            data = sock.recv(CHUNK_SIZE*CHANNELS*2)
            if not data:
                break
            audio = np.frombuffer(data, dtype=np.int16).astype(np.float32)/32767.0
            audio = audio.reshape(-1, CHANNELS)

            if audio.shape[0] < CHUNK_SIZE:
                pad_len = CHUNK_SIZE - audio.shape[0]
                audio = np.pad(audio, ((0, pad_len), (0, 0)), mode='constant')
            elif audio.shape[0] > CHUNK_SIZE:
                audio = audio[:CHUNK_SIZE, :]
            audio_queue.put(audio)
    except Exception as e:
        print(f'ERROR: {e}')
    finally:
        sock.close()
        
receiver_thread = threading.Thread(target=receive_audio)
receiver_thread.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    print('stopping...')
    stream.stop()
    stream.close()