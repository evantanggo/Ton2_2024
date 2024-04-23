import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import threading
import soundfile as sf

# dBr (relativ). unsere dBr für die Amplitude ist 1kHz, Hörschwelle
amplitudes = np.array([1, 0.5, 0.25, 0.1, 0.05, 0.025,
                       0.01, 0.005, 0.0025, 0.001, 0.0005,
                       0.00025, 0.0001, 0.00005, 0.000025, 0.00001])
freqs = np.array([20, 100, 200, 600, 800, 1000, 2000,
                  6000, 8000, 10000, 15000, 16000, 20000])


def play_tone(freq, amplitude):
    fs = 42000
    duration = 1.0

    t = np.linspace(0, duration, int(duration * fs))
    y = amplitude * np.sin(2 * np.pi * freq * t)

    sd.play(y, fs)
    sd.wait()


# def play_audiofile():
#    data, fs = sf.read('rosa rauschen.wav')
#    sd.play(data, fs)
#    sd.wait()

def play_tone2():
    fs = 42000
    duration = 1.0

    t = np.linspace(0, duration, int(duration * fs))
    y = 1 * np.sin(2 * np.pi * 1000 * t)

    sd.play(y, fs)
    sd.wait()


def input_frequency(frequency, amplitude):
    while True:
        user_input = input(f"War der Ton {frequency} Hz mit {amplitude} Amplitude noch hörbar? (Enter = ja, 1 = nein)")
        if user_input == "1":
            return False
        elif user_input == "":
            print("Ton war hörbar")
            return True


results = np.ones(freqs.size)

input_ab = input("Mit oder ohne Verdecker? a = mit, b = ohne ")
if input_ab == "a":
    for i, frequency in enumerate(freqs):
        for amplitude in amplitudes:
            audio_thread = threading.Thread(target=play_tone2)
            audio_thread.start()
            play_tone(frequency, amplitude)
            if input_frequency(frequency, amplitude):
                results[i] = amplitude
            else:
                break
    plt.semilogx(freqs, 20 * np.log10(results), "x", markersize=5, markerfacecolor='red')
    plt.semilogx(freqs, 20 * np.log10(results), color='red')
    plt.semilogx(1000, 0, 'bs')
    plt.xlabel("Frequenz [Hz]")
    plt.ylabel("Amplitude [dB]")
    plt.title("Audiogram mit Verdecker")
    plt.grid(True)
    plt.show()
else:
    for i, frequency in enumerate(freqs):
        for amplitude in amplitudes:
            play_tone(frequency, amplitude)
            if input_frequency(frequency, amplitude):
                results[i] = amplitude
            else:
                break
    plt.semilogx(freqs, 20 * np.log10(results), "x", markersize=5, markerfacecolor='red')
    plt.semilogx(freqs, 20 * np.log10(results), color='red')
    plt.xlabel("Frequenz [Hz]")
    plt.ylabel("Amplitude [dB]")
    plt.title("Audiogram ohne Verdecker")
    plt.grid(True)
    plt.show()
