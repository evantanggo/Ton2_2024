import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter, unit_impulse, freqz

def design_highpass_filter(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def plot_impulse_response(b, a, fs):
    # Erzeuge einen Impuls
    impulse = unit_impulse(100)  # Länge des Impulses
    
    # Filtere den Impuls
    response = lfilter(b, a, impulse)
    
    # Zeitachse basierend auf der Länge des Impulses
    time = np.arange(len(impulse)) / fs

    plt.figure()
    plt.plot(time, response, marker='o', linestyle='-', color='b')
    plt.title('Impulsantwort - Hochpassfilter')
    plt.xlabel('Zeit [s]')
    plt.ylabel('Amplitude')
    plt.ylim(bottom=-1)  # Setzt die untere y-Achsen-Grenze auf -1
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Parameter
fs = 1000  # Abtastrate in Hz
cutoff = 100  # Grenzfrequenz des Hochpassfilters in Hz
order = 1  # Ordnung des Filters

# Filterdesign
b, a = design_highpass_filter(cutoff, fs, order)

# Impulsantwort plotten
plot_impulse_response(b, a, fs)
