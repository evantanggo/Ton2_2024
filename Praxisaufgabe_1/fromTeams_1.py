import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd


# Funktion zum Abspielen von Tönen (Frequenz,Amplitude, Verdecker an oder aus, Frequenz des Verdeckers)
def playtone(f, amplitude, verdecker, verdecker_frequency):
    # Variablen
    fs = 42000
    length = 1
    lengthfadein = 0.05
    lengthfadeout = 0.05
    fadeoutstart = length - lengthfadeout

    # Sinuston und Verdecker
    t = np.linspace(0, length, length * fs)
    y = amplitude * np.cos(2 * np.pi * f * (t))
    # Addition des Verdeckers
    if verdecker == True:
        y2 = 0.1 * np.cos(2 * np.pi * verdecker_frequency * (t))
        y = y + y2

    # Fadein und Fadeout
    y[t <= lengthfadein] *= (t[t <= lengthfadein] / lengthfadein)
    y[t >= fadeoutstart] *= (1 - (t[t >= fadeoutstart] - fadeoutstart) / lengthfadeout)
    # output
    sd.play(y)


# Funktion zur Abfrage ob der Ton hörbar war
def query(frequency, ampli):
    hearable = input(
        "War der Ton {frequency} Hz mit Amplitude {ampli} dB noch hörbar? (1/0): ".format(frequency=frequency,
                                                                                          ampli=10 * np.log10(ampli)))
    if hearable == "1":
        return True
        print("Ton war hörbar")
    elif hearable == "0":
        return False
        print("Eingabe war nicht hörbar")
    else:
        print("Ungültige Eingabe. 1 oder 0")
        query(frequency, ampli)


# Frequenzen und Amplituden zum Testen
amplitudes = np.array(
    [1, 0.5, 0.25, 0.1, 0.05, 0.025, 0.01, 0.005, 0.0025, 0.001, 0.0005, 0.00025, 0.0001, 0.00005, 0.000025, 0.00001])
frequencies = np.array(
    [20, 40, 60, 80, 100, 200, 400, 600, 800, 1000, 2000, 4000, 6000, 8000, 10000, 13000, 16000, 20000])

# Output-Array
results = np.array([1.e-02, 1.e-02, 1.e-03, 1.e-04, 1.e-04, 5.e-05, 1.e-05, 5.e-05, 1.e-05, 1.e-05,
                    1.e-05, 1.e-05, 1.e-05, 1.e-05, 1.e-05, 1.e-04, 1.e+00, 1.e+00])

# Code: Doppelte Schleife die durch Amplituden und Frequenzen des Beiden Arrays geht.

i = 0
j = 0
testnew = False

if testnew == False:
    while i <= frequencies.size - 1:
        while j <= amplitudes.size - 1:
            playtone(frequencies[i], amplitudes[j], False, 600)
            if query(frequencies[i], amplitudes[j]) == True and j != amplitudes.size - 1:
                j += 1
            else:
                if j == 0:
                    results[i] = amplitudes[0]
                else:
                    results[i] = amplitudes[j - 1]
                j = 0
                i += 1
                break

# Plot Results
plt.semilogx(frequencies, 10 * np.log10(np.abs(results)) + abs(10 * np.log10(np.abs(results[9]))), "x", markersize=5,
             markerfacecolor='red')
plt.semilogx(frequencies, 10 * np.log10(np.abs(results)) + abs(10 * np.log10(np.abs(results[9]))), color='blue')
plt.xlabel("Frequenz [Hz]")
plt.ylabel("Amplitute[dB]")
plt.title("Audiogram")
plt.grid(True)
plt.show()

highlight_x = frequencies
highlight_y = results

# Debug
print("Fertig")
print(10 * np.log10(np.abs(results)))