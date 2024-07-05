

wav_file = '/Users/simonbudde/Library/Mobile Documents/com~apple~CloudDocs/HAW Hamburg/TT2/PP1/Datei_B.wav'


import librosa
import matplotlib.pyplot as plt
import numpy as np

# Load WAV file
y, sr = librosa.load(wav_file)


# Compute spectrogram
S = librosa.stft(y)
D = librosa.amplitude_to_db(abs(S), ref=np.max)
# Plot spectrogram
plt.figure(figsize=(10, 4))
librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
plt.colorbar(format='%+2.0f dB')
plt.title('Spectrogram')
plt.show()