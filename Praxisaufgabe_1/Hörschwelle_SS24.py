import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt

amplitudes = np.array([1, 0.5, 0.25, 0.1, 0.05, 0.025, 
                    0.01, 0.005, 0.0025, 0.001, 0.0005, 
                    0.00025, 0.0001, 0.00005, 0.000025, 0.00001])
freqs = np.array([20, 100, 200, 600, 800, 1000, 2000, 
                6000, 8000, 10000, 15000, 16000, 20000])

#Abspielen von Ton
def play_tone(freqs, amplitude):
    fs = 42000
    dauer = 1

    t = np.linspace(0, dauer, int(dauer * fs))
    y = amplitude * np.sin(2 * np.pi * freqs * t)
    
    sd.play(y)

def input(freqs, amplitude):
    while True:
        hearable = input(f"War der Ton {freqs} Hz mit Amplitude 
                         {10 * np.log(amplitude)} db noch hörbar?")
        if hearable == "1":
            print("Ton war hörbar")
            return False
        else:
            return True
        

results = np.ones(freqs.size)

for i, frequency in enumerate(freqs):
    for j, amplitude in enumerate(amplitudes):
        play_tone(frequency, amplitude)
        if input(frequency, amplitude):
            results[i] = amplitude
            break

plt.semilogx(freqs, 10 * np.log10(results) + 10 * np.log10(results[9]), "x", markersize=5, markerfacecolor='red')
plt.semilogx(freqs, 10 * np.log10(results) + 10 * np.log10(results[9]), color='blue')
plt.xlabel("Frequenz [Hz]")
plt.ylabel("Amplitude [dB]")
plt.title("Audiogram")
plt.grid(True)
plt.show()





