# source code here
# import
# py -m pip install

import numpy as np
import matplotlib.pyplot as plot
import PySimpleGUI as sg
import sounddevice as sd

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import mylib_processing as mlp
import mylib_sound as mls # 出来るだけ関数を別ファイルにしたい


## FUNCTION
def draw_figure(canvas, figure):
    figure_canvas = FigureCanvasTkAgg(figure, canvas)
    figure_canvas.draw()
    figure_canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas

def logical_invert(num):
    return int(not num)

## PRE PROCESS
# GUI compornent
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


window = sg.Window("DJ app", layout=[
    [sg.Text("DJアプリです")],
    [frame_deck1],
    [frame_deck2],
    [frame_low1,frame_low2],
    [frame_high1,frame_high2],
    [frame_mix],
    [sg.Button("play1")],
    [sg.Button("play2")],
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


gpass = 3                     
gstop = 40                     
dtype = np.float32
blocksize = 4096
n_chunks = 0
current_frame1 = 0
current_frame2 = 0
sd.default.device = [2, 4]
dispoflag = 0
play_flag1 = 0
play_flag2 = 0

filepath1 = R"C:\Users\ma210\Desktop\pyPractice\music1.wav"
filepath2 = R"C:\Users\ma210\Desktop\pyPractice\music2.wav"
f1 = mls.extractInfo(filepath1)
f2 = mls.extractInfo(filepath2)

# 今後複数のファイルを読み込んで処理するので，ここの書き方は変える
nsp1 = f1.n_samples
nchs1 = f1.n_channels
sr1 = f1.sr
# chunk = np.zeros((blocksize, f1.n_channels))

## MAIN PROCESS
while True:             # Event Loop
    print("before window.read")
    if dispoflag == 0:
        event, values = window.read()
        dispoflag = 1

    print("after window.read")
        
    # buffer_event = event
    window['-LEFT1-'].update(int(values['-SLIDER1-']))
    window['-LEFT2-'].update(int(values['-SLIDER2-']))
    window['-LEFT3-'].update(int(values['-SLIDER3-']))
    window['-LEFT4-'].update(int(values['-SLIDER4-']))
    window['-LEFT5-'].update(int(values['-SLIDER5-']))

    fp1 = np.array([440-220*int(values['-SLIDER1-'])/100, 1320+880*int(values['-SLIDER3-'])/100])     #通過域端周波数[Hz]※ベクトル
    fp2 = np.array([440-220*int(values['-SLIDER2-'])/100, 1320+880*int(values['-SLIDER4-'])/100])     #通過域端周波数[Hz]※ベクトル
    fs = np.array([20, 20000])      #阻止域端周波数[Hz]※ベクトル
    
    # 出来るだけif文を使いたくない…　いい方法は無いか…
    if event == 'play1':
        play_flag1 = logical_invert(play_flag1)
        # print("flag1: {}".format(mute_flag1))
    else:
        print("flag1: {}".format(play_flag1))

    if event == 'play2':
        play_flag2 = logical_invert(play_flag2)
        # print("flag2: {}".format(play_flag2))
    else:
        print("flag2: {}".format(play_flag2))

    with sd.OutputStream(samplerate = sr1, 
                         blocksize = blocksize,
                         channels = nchs1,
                         dtype = dtype) as stream1:
        # with 関数 as  変数，で勝手にcloseしてくれる
        print("after with")
        
        while True:
            event, values = window.read(timeout=5, timeout_key='-timeout-') # 値の読み取りを5ｍｓ行い，変化が無かったらvaluesに-timeout-が代入される
            chunksize1 = min(int(nsp1) - current_frame1, blocksize)
            chunksize2= min(int(nsp1) - current_frame2, blocksize)

            # ここも出来るだけif文を使いたくない
            if chunksize1 < blocksize:
                current_frame1 = 0
                play_flag1 = 0
                break
            
            if chunksize2 < blocksize:
                current_frame2 = 0
                play_flag2 = 0
                break

            # mix
            d1 =  mlp.bpf(f1.sig[current_frame1:current_frame1 + chunksize1, :],sr1, fp1, fs, gpass, gstop) * (1 - int(values['-SLIDER5-'])/100)
            d2 =  mlp.bpf(f2.sig[current_frame2:current_frame2 + chunksize2, :],sr1, fp2, fs, gpass, gstop) * int(values['-SLIDER5-'])/100
            

            data_mixed = d1*play_flag1 + d2*play_flag2

            stream1.write( data_mixed.astype(dtype) ) 
            # n_chunks += 1
            # この処理を入れると重くなる
            # ax1.cla() # 更新前のグラフを消去 
            # ax1.plot(data_filtered, alpha=0.4)
            # ax2.cla() # 更新前のグラフを消去
            # ax1.plot(data_filtered, alpha=0.4)
            # fig_agg1.draw()
            # fig_agg2.draw()

            current_frame1 += chunksize1*play_flag1
            current_frame2 += chunksize2*play_flag2
            # 0，１の値を取るmute_flagをchunk_sizeにかけることで音を止めた後，バックグラウンドで曲が進まないようにしている

            # timeoutが代入されている場合，ループを抜け出す
            if event != '-timeout-':
                # event = ''
                break


    if event == 'Show':
        sg.popup(f'The slider value = {values["-SLIDER-"]}')
window.close()
   

# 1 git add .
# 2 git commit -m "commit name"
# 3 git push origin main