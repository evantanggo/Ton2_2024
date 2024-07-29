import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import read
import sounddevice as sd

def db_to_linear(Q_dB):
    # Umrechnung von dB in linearen Gütefaktor
    return 10**(Q_dB / 10)

def calculate_fl_fh(fc, Q_linear):
    fbw = fc / Q_linear
    fl = (-fbw + np.sqrt(fbw**2 + 4 * fc**2)) / 2
    fh = fbw + fl
    return fl, fh

def create_bandstop_filter(signal, fs, fc, Q_dB):
    # Konvertieren des Gütefaktors von dB in linear
    Q_linear = db_to_linear(Q_dB)
    
    # Berechnen von fl und fh
    fl, fh = calculate_fl_fh(fc, Q_linear)
    
    # Sicherstellen, dass fl und fh innerhalb des gewünschten Bereichs liegen
    fl = max(fl, 20)
    fh = min(fh, 2000)
    
    # Zeitparameter
    delta_T = 1 / fs
    lang = len(signal)
    
    # Hochpass-Filter
    y_HPi = np.zeros(lang)
    alpha_HP = 1 / (1 + 2 * np.pi * fh * delta_T)
    y_HPi[0] = signal[0] * alpha_HP

    for i in range(1, lang):
        y_HPi[i] = alpha_HP * (y_HPi[i - 1] + signal[i] - signal[i - 1])
    
    y_HP = y_HPi / np.max(np.abs(y_HPi))  # Normalisierung
    
    # Tiefpass-Filter
    y_TP = np.zeros(lang)
    alpha_TP = (2 * np.pi * fl * delta_T) / (1 + 2 * np.pi * fl * delta_T)
    y_TP[0] = alpha_TP * signal[0]

    for i in range(1, lang):
        y_TP[i] = alpha_TP * signal[i] + (1 - alpha_TP) * y_TP[i - 1]
    
    y_TP = y_TP / np.max(np.abs(y_TP))  # Normalisierung
    
    # Kombination des Hochpass- und Tiefpass-Filters für Bandstop-Effekt
    y_bandstop = signal - (y_TP + y_HP)  # Signal minus die Kombination von TP und HP
    
    return y_bandstop

def plot_spectrum(signal, fs, title):
    NFFT = len(signal) 
    X = np.linspace(0.0, fs / 2, NFFT // 2)
    # np.arange(0, fs )
    Sp = np.fft.fft(signal) / NFFT
    Sp_abs = np.abs(Sp)
    l = len(Sp) // 2
    Y = Sp_abs[:l] * 2
    
    plt.figure()
    plt.plot(X, Y)
    plt.title(title)
    plt.xlabel('Frequenz (Hz)')
    plt.ylabel('Amplitude')
    plt.grid()
    plt.show()

def main():
    Eingang = 'Fallstudie3/pinknoise.wav'
    fc = 700  # Mittenfrequenz der Bandsperre
    Q_dB = -3  # Gütefaktor der Bandsperre in dB
    
    fs, x_t = read(Eingang)
    delta_T = 1 / fs

    # Normalisierung der Eingabedaten
    x_t = x_t / np.max(np.abs(x_t))

    # Erstellen des Bandsperr-Filters
    y_bandstop = create_bandstop_filter(x_t, fs, fc, Q_dB)

    # Plotten des Spektrums des Bandsperre-gefilterten Signals
    plot_spectrum(y_bandstop, fs, 'Frequenzspektrum des Bandsperre-gefilterten Signals')

    # Optional: Abspielen des gefilterten Signals
    sd.play(y_bandstop, fs)
    sd.wait()

if __name__ == "__main__":
    main()
