# 重複してimportするとどうなるんだろう
import numpy as np
import pyaudio
import matplotlib.pyplot as plot
from scipy import signal

CHUNK = 44100
CH_OUT = 1 
FS = 44100


def lpf(wave,fs,fe,n):
    nyq = fs/2.0
    b,a = signal.butter(1,fe/nyq,btype='low')
    for i in range(0,n):
        wave =signal.filtfilt(b,a,wave)
    return wave

def audiostart():
    audio = pyaudio.PyAudio() 
    stream = audio.open( format = pyaudio.paInt16,
                         rate = 44100,
                         channels = 1, 
                         input_device_index = 1,
                        input = True, 
                        frames_per_buffer = 1024)
    return audio, stream

def audiostop(audio, stream):
    stream.stop_stream()
    stream.close()
    audio.terminate()

def read_plot_data(stream):
    data = stream.read(1024)
    audiodata = np.frombuffer(data, dtype='int16')
    
    plot.plot(audiodata)
    plot.draw()
    plot.pause(0.001)
    plot.cla()


def procSound(data):
    y=data[0:CHUNK-1]
    # array to buffer
    #  float -> 16bit signed intに変換する
    sndBuf = y.astype(np.int16).tobytes()
    return sndBuf


def demoBlockingMode(data):
    pyAud = pyaudio.PyAudio()
    sndStrm = pyAud.open(rate=FS,channels=CH_OUT,format=pyaudio.paInt16,input=False,output=True)

    for cnt in range(100):
        obuf = procSound(data)
        if sndStrm.is_active :
            sndStrm.write(obuf) # blocking mode. blocks until all the give frames have been played
    sndStrm.stop_stream()
    sndStrm.close()
    pyAud.terminate()

def callback(indata, frames, time, status):
    # indata.shape=(n_samples, n_channels)
    # print root mean square in the current frame
    print(np.sqrt(np.mean(indata**2)))
