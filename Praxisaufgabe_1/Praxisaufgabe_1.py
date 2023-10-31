'''
Ton 2 Praxisaufgabe 1
Audiogramm mit Verdecker und ohne Verdecker
'''

import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd


fs = 20000

f = 40
y_peak = 1  # amplitude
duration = 3
delta_t = 1. / fs

start_audiolevel = 0.00005
ref_level = 0

t = np.arange(0, duration, delta_t)
freqs = [125, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000]
current_index = 0
audio_level = []


def frequencyHeard():
    value = input(f"\n input n for not hearing the sound, input y for hearing the sound: ")
    # keys = pygame.key.get_pressed()
    while True:
        if value.lower() == "n":
            return False
        elif value.lower() == "y":
            return True
        else:
            print("Eingabe falsch! nur n oder y")
            frequencyHeard()

        # if value == "":
        #     plt.plot(freqs, audio_level)
        #     plt.show()
        #     break


def applyFade(signal, fadeDuration):
    global fs
    global duration

    fadeSamples = int(fs * fadeDuration)
    signalSamples = fs * duration
    deltaSamples = signalSamples - 2 * fadeSamples
    linSpace = np.linspace(1, 10, fadeSamples)

    fadeIn = np.log10(linSpace)
    fadeOut = np.flip(fadeIn)
    fade = np.concatenate((fadeIn, np.ones(deltaSamples), fadeOut))

    return signal * fade


def volumeIncrease():
    global f
    global y_peak
    global start_audiolevel

    y_peak = start_audiolevel

    while True:
        y = y_peak * np.sin(2 * np.pi * f * t)
        y_fade = applyFade(y, 0.3)
        sd.play(y_fade, fs)
        sd.wait()

        heard = frequencyHeard()

        if heard:
            audio_level.append(20 * np.log(y_peak / ref_level))
            break

        if not heard:
            y_peak += 1.8
            if y_peak >= 1:
                break
            continue


def frequencyGenerator():  # erhöht frequenz wenn f gehört wurde
    global f
    global current_index
    global freqs

    while True:
        f = freqs[current_index]
        volumeIncrease()
        current_index += 1

        if current_index >= 11:
            break


def referenzLevel():  # fragt referenzlevel vor Test ab und speicher es ein
    global f
    global y_peak
    global current_index
    global ref_level
    global start_audiolevel

    f = 1000
    y_peak = start_audiolevel

    while True:
        y = y_peak * np.sin(2 * np.pi * f * t)  # selbe Funktion wie volumeincrease
        y_fade = applyFade(y, 0.3)
        sd.play(y_fade, fs)
        sd.wait()

        heard = frequencyHeard()

        if heard:
            ref_level = y_peak  # unterschied : wird in referenzwert eingespeichert
            current_index = 0
            break

        if not heard:
            y_peak *= 1.8
            if y_peak >= 1:
                break
            continue


referenzLevel()
frequencyGenerator()
# fig = plt.figure()
# ax = fig.add_subplot(2, 1, 1)
# graph, = plt.plot(freqs, audio_level)
# ax.set_xscale('log')
# ax.grid(True)
# pylab.show()

plt.figure(figsize=(8,4))
plt.plot(freqs, audio_level)
#plt.ylim(-1*y_peak, y_peak)
plt.xscale('log')
plt.title("Hörschwelle")
plt.xlabel("Frequenzen (Hz)")
plt.ylabel("Audio Level (dB)")
plt.grid(True)
plt.show()

