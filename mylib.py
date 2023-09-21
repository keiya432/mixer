import soundfile as sf

def mixSounds(pan,data_left,data_rigth):
    data_mixed = pan*data_left + (1-pan)*data_rigth
    return data_mixed

def extractInfo(path):
    print()

class extractInfo:
    def __init__(self, path):
        self.path = path
        self.sig, self.sr = sf.read(self.path, always_2d=True)
        self.n_samples, self.n_channels = self.sig.shape