# Evan Tanggo Peter Simamora
# Jo Borgwardt
# Jannik Pohl
# Test der Hörschwelle mit Überdeckungseffekt

import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd


# Abspielen von Tönen
def play_tone(frequency, amplitude, has_masking_sound, masking_frequency):
    fs = 42000
    duration = 1.0
    fade_in_duration = 0.05
    fade_out_duration = 0.05
    fade_out_start = duration - fade_out_duration

    t = np.linspace(0, duration, int(duration * fs))
    signal = amplitude * np.cos(2 * np.pi * frequency * t)

    if has_masking_sound:
        masking_signal = 0.1 * np.cos(2 * np.pi * masking_frequency * t)
        signal += masking_signal

    signal[t <= fade_in_duration] *= t[t <= fade_in_duration] / fade_in_duration
    signal[t >= fade_out_start] *= 1 - (t[t >= fade_out_start] - fade_out_start) / fade_out_duration

    sd.play(signal)


# Funktion Abfrage
def query(frequency, amplitude):
    while True:
        hearable = input(
            f"War der Ton {frequency} Hz mit Amplitude {10 * np.log10(amplitude)} dB noch hörbar? (1 oder Enter): ")
        if hearable == "1":
            print("Ton war hörbar")
            return False
        else:
            return True


# Frequenzen und Amplituden
amplitudes = np.array(
    [1, 0.5, 0.25, 0.1, 0.05, 0.025, 0.01, 0.005, 0.0025, 0.001, 0.0005, 0.00025, 0.0001, 0.00005, 0.000025, 0.00001])
frequencies = np.array([20, 100, 200, 600, 800, 1000, 2000, 6000, 8000, 10000, 15000, 16000, 20000])

# Array
results = np.ones(frequencies.size)

# Testen der Töne
for i, frequency in enumerate(frequencies):
    for j, amplitude in enumerate(amplitudes):
        play_tone(frequency, amplitude, False, 600)
        if query(frequency, amplitude):
            results[i] = amplitude
            break

# Plot
plt.semilogx(frequencies, 10 * np.log10(results) + 10 * np.log10(results[9]), "x", markersize=5, markerfacecolor='red')
plt.semilogx(frequencies, 10 * np.log10(results) + 10 * np.log10(results[9]), color='blue')
plt.xlabel("Frequenz [Hz]")
plt.ylabel("Amplitude [dB]")
plt.title("Audiogram")
plt.grid(True)
plt.show()

# Debug
print("Fertig")