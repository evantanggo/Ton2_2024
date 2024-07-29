import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import read
import sounddevice as sd

Eingang = 'Fallstudie3/pinknoise.wav'    

fgr_HP = 4000                                         
fgr_TP = 3000    

fs, x_t = read(Eingang)                             
delta_T = 1 / fs

# Normalisierung der Eingabedaten
x_t = x_t / np.max(np.abs(x_t))

lang = len(x_t)
NFFT = int(lang)
X = np.arange(0, fs / 2, 1. * fs / NFFT) 

dauer = lang / fs
t = np.arange(0, dauer, delta_T)     

#####################################
# Tiefpass:
y_TP = np.zeros(lang)

alpha_TP = (fgr_TP * 2 * np.pi * delta_T) / (1 + fgr_TP * 2 * np.pi * delta_T)

y_TP[0] = alpha_TP * x_t[0]

for i in range(1, lang):
    y_TP[i] = alpha_TP * x_t[i] + (1 - alpha_TP) * y_TP[i - 1]
    
y_TP = y_TP / np.max(np.abs(y_TP))  # Normalisierung

# Abspielen des Tiefpass-gefilterten Signals
sd.play(y_TP, fs)
sd.wait()

##### Transformation in den Frequenzbereich, Betrag von H(j omega):
b = y_TP[:NFFT]    
Sp = np.fft.fft(b) / NFFT  
Sp_abs = np.abs(Sp)  
l = len(Sp) // 2
Y_TP = Sp_abs[:l] * 2  

# Plotten des Spektrums
plt.figure()
plt.plot(X[:l], Y_TP)
plt.title('Frequenzspektrum des Tiefpass-gefilterten Signals')
plt.xlabel('Frequenz (Hz)')
plt.ylabel('Amplitude')
plt.grid()
plt.show()

######################################
# Hochpass:
y_HPi = np.zeros(lang)

alpha_HP = 1 / (1 + fgr_HP * 2 * np.pi * delta_T)

y_HPi[0] = x_t[0] * alpha_HP

for i in range(1, lang):
    y_HPi[i] = alpha_HP * (y_HPi[i - 1] + x_t[i] - x_t[i - 1])
    
y_HP = y_HPi / np.max(np.abs(y_HPi))  # Normalisierung

# Abspielen des Hochpass-gefilterten Signals
sd.play(y_HP, fs)
sd.wait()

##### Transformation in den Frequenzbereich, Betrag von H(j omega):
b = y_HP[:(NFFT)]    
Sp = np.fft.fft(b) / (NFFT)  
Sp_abs = np.abs(Sp)  
l = len(Sp) // 2
Y_HP = Sp_abs[:l] * 2  

# Plotten des Spektrums
plt.figure()
plt.plot(X[:l], Y_HP)
plt.title('Frequenzspektrum des Hochpass-gefilterten Signals')
plt.xlabel('Frequenz (Hz)')
plt.ylabel('Amplitude')
plt.grid()
plt.show()

####################################
