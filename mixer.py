# source code here
# import
# py -m pip install
import numpy as np
import pyaudio
import matplotlib.pyplot as plot
import PySimpleGUI as sg
import sounddevice as sd
from scipy import signal
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import mylib as ml # 出来るだけ関数を別ファイルにしたい

CHUNK = 44100
CH_OUT = 1 
FS = 44100

# function
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





def lpf(wave,fs,fe,n):
    nyq = fs/2.0
    b,a = signal.butter(1,fe/nyq,btype='low')
    for i in range(0,n):
        wave =signal.filtfilt(b,a,wave)
    return wave

def bpf(x, samplerate, fp, fs, gpass, gstop):
    fn = samplerate / 2                           #ナイキスト周波数
    wp = fp / fn                                  #ナイキスト周波数で通過域端周波数を正規化
    ws = fs / fn                                  #ナイキスト周波数で阻止域端周波数を正規化
    N, Wn = signal.buttord(wp, ws, gpass, gstop)  #オーダーとバターワースの正規化周波数を計算
    b, a = signal.butter(N, Wn, "band")           #フィルタ伝達関数の分子と分母を計算
    y = signal.filtfilt(b, a, x,axis=0)                  #信号に対してフィルタをかける
    return y                                      #フィルタ後の信号を返す

def draw_figure(canvas, figure):
    figure_canvas = FigureCanvasTkAgg(figure, canvas)
    figure_canvas.draw()
    figure_canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas

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



## GUI compornent
frame_low1 = sg.Frame("lowpass1", layout=[
                     [sg.Text('lowpass Filter1'), sg.Text('', key='-OUTPUT1-')], # layoutは上からコンポ―ネントを決定していく
                     [sg.T('0',size=(4,1), key='-LEFT1-'),
                     sg.Slider((0,100), key='-SLIDER1-', orientation='h', enable_events=True, disable_number_display=True)]])

frame_low2 = sg.Frame("lowpass2", layout=[
                     [sg.Text('lowpass Filter2'), sg.Text('', key='-OUTPUT2-')], # layoutは上からコンポ―ネントを決定していく
                     [sg.T('0',size=(4,1), key='-LEFT2-'),
                     sg.Slider((0,100), key='-SLIDER2-', orientation='h', enable_events=True, disable_number_display=True)]])

frame_high1 = sg.Frame("highpass1", layout=[
                     [sg.Text('highpass Filter1'), sg.Text('', key='-OUTPUT3-')], # layoutは上からコンポ―ネントを決定していく
                     [sg.T('0',size=(4,1), key='-LEFT3-'),
                     sg.Slider((0,100), key='-SLIDER3-', orientation='h', enable_events=True, disable_number_display=True)]])

frame_high2 = sg.Frame("highpass2", layout=[
                     [sg.Text('highpass Filter2'), sg.Text('', key='-OUTPUT4-')], # layoutは上からコンポ―ネントを決定していく
                     [sg.T('0',size=(4,1), key='-LEFT4-'),
                     sg.Slider((0,100), key='-SLIDER4-', orientation='h', enable_events=True, disable_number_display=True)]])

frame_mix = sg.Frame("mixer", layout=[
                     [sg.Text('Mixer'), sg.Text('', key='-OUTPUT5-')], # layoutは上からコンポ―ネントを決定していく
                     [sg.T('0',size=(4,1), key='-LEFT5-'),
                     sg.Slider((0,100), key='-SLIDER5-', orientation='h', enable_events=True, disable_number_display=True)]])

frame_deck1 = sg.Frame("Deck1", layout=[
                     [sg.Text('Embed Matplotlib Plot')],
                     [sg.Canvas(key='-CANVAS1-')]])

frame_deck2 = sg.Frame("Deck2", layout=[
                     [sg.Text('Embed Matplotlib Plot')],
                     [sg.Canvas(key='-CANVAS2-')]])




## Main
window = sg.Window("DJ app", layout=[
    [sg.Text("DJアプリです")],
    [frame_deck1],
    [frame_deck2],
    [frame_low1,frame_low2],
    [frame_high1,frame_high2],
    [frame_mix],
    ],element_justification='center',finalize=True)

# 埋め込む用のfigを作成する．
fig = plot.figure(figsize=(8, 2))
ax1 = fig.add_subplot(111)
ax2 = fig.add_subplot(111)
ax1.set_ylim(-10, 10)
ax2.set_ylim(-10, 10)

# figとCanvasを関連付ける．
# 引数の一つ目が対象を表し，二つ目がグラフ自体を表し，
fig_agg1 = draw_figure(window['-CANVAS1-'].TKCanvas, fig)
fig_agg2 = draw_figure(window['-CANVAS2-'].TKCanvas, fig)

# property
duration = 1
n = 6
cutoff = 450
note_hz1 = 440
note_hz2 = 880

gpass = 3                     
gstop = 40                     

sd.default.device = [2, 4] 
filepath1 = R"C:\Users\ma210\Desktop\pyPractice\music1.wav"
filepath2 = R"C:\Users\ma210\Desktop\pyPractice\music2.wav"

f1 = extractInfo(filepath1)
f2 = extractInfo(filepath2)

dtype = np.float32
blocksize = 4096
n_chunks = 0
current_frame = 0

while True:             # Event Loop
    event, values = window.read()
    # buffer_event = event
    window['-LEFT1-'].update(int(values['-SLIDER1-']))
    window['-LEFT2-'].update(int(values['-SLIDER2-']))
    window['-LEFT3-'].update(int(values['-SLIDER3-']))
    window['-LEFT4-'].update(int(values['-SLIDER4-']))
    window['-LEFT5-'].update(int(values['-SLIDER5-']))

    # pre process
    fp1 = np.array([440-220*int(values['-SLIDER1-'])/100, 1320+880*int(values['-SLIDER3-'])/100])     #通過域端周波数[Hz]※ベクトル
    fp2 = np.array([440-220*int(values['-SLIDER2-'])/100, 1320+880*int(values['-SLIDER4-'])/100])     #通過域端周波数[Hz]※ベクトル
    fs = np.array([20, 20000])      #阻止域端周波数[Hz]※ベクトル
 
    nsp1 = f1.n_samples
    sr1 = f1.sr
    nchs1 = f1.n_channels

    chunk = np.zeros((blocksize, f1.n_channels))

    with sd.OutputStream(samplerate = sr1, 
                         blocksize = blocksize,
                         channels = nchs1,
                         dtype = dtype) as stream1:
        #sd.OutputStream(samplerate = f2.sr, blocksize = blocksize,channels = f2.n_channels,dtype = dtype) as stream2:
        # with 関数 as  変数，で勝手にcloseしてくれる
        while True:
            event, values = window.read(timeout=5, timeout_key='-timeout-') # 値の読み取りを5ｍｓ行い，変化が無かったらvaluesに-timeout-が代入される
            chunksize = min(int(nsp1) - current_frame, blocksize)

            # mix
            d1 =  bpf(f1.sig[current_frame:current_frame + chunksize, :],sr1, fp1, fs, gpass, gstop) * (1 - int(values['-SLIDER5-'])/100)
            d2 =  bpf(f2.sig[current_frame:current_frame + chunksize, :],sr1, fp2, fs, gpass, gstop) * int(values['-SLIDER5-'])/100
            
            data_filtered = d1 + d2
            stream1.write( data_filtered.astype(dtype) ) 
            n_chunks += 1
            
            # ax1.cla() # 更新前のグラフを消去
            # ax1.plot(data_filtered, alpha=0.4)
            # ax2.cla() # 更新前のグラフを消去
            # ax1.plot(data_filtered, alpha=0.4)
            # fig_agg1.draw()
            # fig_agg2.draw()

            if chunksize < blocksize: 
                break
            current_frame += chunksize

            # timeoutが代入されている場合，ループを抜け出す
            if event != '-timeout-':
                break




    if event == 'Show':
        sg.popup(f'The slider value = {values["-SLIDER-"]}')
window.close()
   
    