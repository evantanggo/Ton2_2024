'''
Ton 2 Praxisaufgabe 1
Audiogramm
'''

import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import keyboard

Fs = 20000

f = 40                      #Frequenz
y_peak = 1                  #peak amplitde
startAudioLevel = 0.000005  #startwert der amplitude
ref_level = 0               #freie Variable fürs reflevel
duration = 3                #dauer vom ton in s
delta_t = 1./Fs             #Zeit zwischen den Abtastwerten
t = np.arange(0, duration, delta_t) #t ist ein array von 0 bis duration mit schritten von deltaT in s
frequencies = [125, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000] #frequenz array
currentIndex = 0                                                             #zähler für frequenz array
audioLevels = []                                                             #leeres array für die abgespeicherten Werte


def referenzLevel(referenzfreq, verdecker, verdecker_frequency):            #fragt referenzlevel vor Test ab und speichert es ein
    global f
    global y_peak
    global currentIndex
    global ref_level
    #f = 1000
    global startAudioLevel
    y_peak = startAudioLevel

    while True:
        y = y_peak*np.sin(2 * np.pi * referenzfreq * t)
        #y_fade = applyFade(y, 0.3)

        if verdecker == True:
            y2 = 0.1 * np.cos(2 * np.pi * verdecker_frequency * t)
            y += y2

        y_fade = applyFade(y, 0.3)
        sd.play(y_fade,Fs)
        sd.wait()

        heard = frequencyHeard()

        if heard:                                    # unterschied: wird in refernzwert eingespeichert.
            ref_level = y_peak
            currentIndex = 0
            break

        if not heard:
            y_peak *= 1.8
            if y_peak >= 1:
                break
            continue

def frequencyGenerator():                                           #erhöht Frequenz, wenn f gehört wurde
    global f
    global currentIndex
    global frequencies
    while True:
        f = frequencies[currentIndex]
        volumeIncrease()
        currentIndex += 1
        if currentIndex >= 11:
            break

def volumeIncrease():   #erhöht "Lautstärkepegel" in +5dB Schritten und gibt Sound aus
    global f
    global y_peak
    global startAudioLevel
    y_peak = startAudioLevel
    while True:
        y = y_peak*np.sin(2 * np.pi * f * t)        # SInuskurve wird erzeugt
        y_fade = applyFade(y, 0.3)                  # Fade wird auf Kurve angewandt
        sd.play(y_fade, Fs)                         # spielt ton ab
        sd.wait()                                   # pausiert code bis sound abgespielt ist

        heard = frequencyHeard()                    #fragt ab, ob ton gehört bzw 2 als input gegeben wurde

        if heard:
            audioLevels.append(20*np.log10(y_peak/ref_level))       #gibt in array einen Pegel aus refernzwert bei 1khz und dem peak der gehört wurde ein
            break

        if not heard:                                               # erhöht Pegel, wenn nicht gehört
            y_peak *= 1.8
            if y_peak >= 1:
                break
            continue


def applyFade(signal, fadeDuration):                                                        #function to fade in or fade out the sound signal
    global Fs
    global duration
    fadeSamples = int(Fs * fadeDuration)        #how many samples has the fade?
    signalSamples = Fs * duration               # how many samples has the signal
    deltaSamples = signalSamples - 2 * fadeSamples # delta samples from signal and fade
    linSpace = np.linspace(1, 10, fadeSamples)      #compiles array with as many slots as theres fadesamples with values climbing linear from 0-10
    fadeIn = np.log10(linSpace)                     #nimmt den log10 zur Basis fadeIn, sodass Werte von 0-1 und ein log Kurve entstehen
    fadeOut = np.flip(fadeIn)                       #dreht das Array FadeIn um
    fade = np.concatenate((fadeIn, np.ones(deltaSamples), fadeOut)) #fügt alle Arrays aneinander, wodurch wieder ursprüngliche Länge entsteht
    return signal * fade                            # multipliziert Amplitudenarray mit SIgnalarray


def frequencyHeard():                                                                      #Function to get a user input
    print(f"\ninput 1 if you did not hear a sound, input 2 if you heard the sound")
    while True:
        if keyboard.is_pressed("1"):
            return False
        if keyboard.is_pressed("2"):
            return True                                                                     #checks if sound was heard
        if keyboard.is_pressed(" "):                                                        #shows picture of frequencies and audiolevels plotted
            plt.plot(frequencies, audioLevels)
            plt.show()
            break





referenzLevel(1000, True, 600)                                             #main durchlauf
frequencyGenerator()
fig = plt.figure()                                          # erstellt Endgrafik
ax = fig.add_subplot(2, 1, 1)
ax.plot(frequencies, audioLevels, label="Hörschwelle")
ax.set_xscale('log')
plt.xlabel('Frequenzen')
plt.ylabel('dB')
ax.grid(True)
plt.show()
