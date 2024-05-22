# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 12:43:47 2020

@author: ogygo
"""

import numpy as np 
from scipy.io.wavfile import read
#import wavfile
import matplotlib.pyplot as plt

 


abtastrate, raum = read('/Users/evantanggo/VisualStudio/Ton2_2024/Z_Ogy/PP1/test_h_von_t_S22 (online-audio-converter.com).wav') #einlesen der Raumimpulsantwort
print('Abtastrate: ' + str(abtastrate) + ' Hz')
 


raum = [x[0] for x in raum] #monospur von stereo

#Nomierung auf 1
raum_max = max(raum, key=abs)
raum = raum / raum_max


signallaenge = len(raum)/ abtastrate #Laenge des Signals

raumquad = np.square(raum)

print('Laenge des Signals: ' + str(np.round(signallaenge,3)) + ' sek.') 




Energie_raum = sum(raumquad) / abtastrate #Gesamtenergie

 


print('Gesamtenergie: ' + str(np.around(Energie_raum, 5)) + ' dB')

 
E = np.float64(np.zeros((len(raum)))) #Energie-Array initialisieren
t = np.arange(len(raum))/float(abtastrate)  # Zeitachse vorbereiten

 
schroeder = list()
zeit = list()
t_10 = None
t_30 = None
 

# Energie von t bis Ende 
for t in range(0, len(raum), 1000):
    E[t] = np.sum(np.square(raum[t:])) / abtastrate
    # Logarithmieren zur Gesamtenergie
    energie_db = 10 * np.log10( E[t] / Energie_raum)
  
    if energie_db <= -20: # Wenn Energie auf -10dB fällt
        if t_10 is None:  # und wenn t_10 noch nie benutzt wurde
            t_10 = t   # tau in Variable t_10 merken

    if energie_db <= -40: # Wenn Energie auf -30dB fällt
        if t_30 is None:  # und wenn t_30 noch nie benutzt wurde
            t_30 = t    # tau in variable t_30 werden

    schroeder.append(energie_db)  # Energie-Wert in Schroeder-Variable speichern
    zeit.append(t / abtastrate) # Zeitpunkt berechnen

# T60 berechnen
T_60 = (((t_30 - t_10) *3 )/ abtastrate)
print('T60 = ' + str(np.round(T_60,3)) + ' Sek.')


#Deutlichkeitsmaß und Klarheitsmaß berechnen
n_50 = int(abtastrate * 0.05)
n_80 = int(abtastrate * 0.08)

C50 = 10 * np.log10(sum(raumquad[0:n_50])/sum(raumquad[n_50:]))
print('C50 = ' + str(np.round(C50, 3)) + ' dB')

C80 = 10 * np.log10(sum(raumquad[0:n_80])/sum(raumquad[n_80:]))
print('C80 = ' + str(np.round(C80, 3)) + ' dB')

# Schroeder Plot
fig, axes = plt.subplots()
axes.plot(zeit, schroeder)
plt.grid()
axes.set_title("Schroeder - Plot")
axes.set_xlabel("Zeit in sek.")
axes.set_ylabel("Energie in dB")

 

plt.show()

#Impulsantwort Plot
max_samples = 1*abtastrate
raum = raum[:max_samples]
tau = np.linspace(0, 1, max_samples)

plt.figure()
plt.plot(tau, raum)
plt.title('Impulsantwort')
plt.xlabel('t in [s]')
plt.ylabel('h(t)')
plt.show()

#Beschränken des Wertebereichs, um erste Reflexionen zu vermeiden
T = int(0.1*abtastrate)
raum_i = raum[T:]

t = np.linspace(0, 0.9, len(raum_i))  
fig, ax = plt.subplots()
ax.plot(t, raum_i)
ax.set_title('Impulsantwort Messbereich')
ax.set_xlabel('$t$ in s')
ax.set_ylabel('$h(t)$')
ax.grid(True)
