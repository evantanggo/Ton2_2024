# -*- coding: utf-8 -*-
"""
Created on Sat Sep 22 19:17:52 2018
http://www.cbcity.de/die-fft-mit-python-einfach-erklaert

Anzeige von sin omega t und zugehöriges spektrum
und Spektrogramm

@author: E_Wilk
"""

import matplotlib.pyplot as plt
import numpy as np



Fs = 20000
f = 2000
NFFT = 20000
y_dach = 1
dauer = 3


deltat = 1./Fs
## faktor_dauer = dauer/(NFFT*deltat)
t = np.arange(0, dauer, deltat) 
y = y_dach*np.sin(2 * np.pi * f * t)

#b = np.array( y, dtype=np.int16)


fig, axs = plt.subplots(3, 1)

plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                wspace=None, hspace=0.6)  #Abstand zwischen Subplots
axs[0].plot(t, y)
axs[0].set_ylim(-1*y_dach, y_dach)
axs[0].set_xlim(0, 2/f)
axs[0].set_xlabel('$t$ in s')
axs[0].set_ylabel('$y$($t$)')
axs[0].grid(True)



###################################
# DFT -------------------------
b=y[0:NFFT]
Sp = np.fft.fft(b)
Sp_abs = np.abs(Sp)
l = int(len(Sp))

## l =int(l/2)#+1
Sp_absneu = Sp_abs[0:l]
#b_neu=b[0:l]
#X = np.arange(0,Fs/2,1.*Fs/NFFT)
X = np.arange(0,Fs,1.*Fs/NFFT)


axs[1].plot(X,Sp_absneu/l)
axs[1].set_xlim(0, Fs)#/2)
#axs[1].set_ylim(0, y_dach)
axs[1].set_xlabel('$f$ in Hz')
axs[1].set_ylabel('|$Y$($f$)|')

############################################
# Spektrogramm

Pxx, freqs, bins, im = axs[2].specgram(y, NFFT=NFFT, Fs=Fs, noverlap=900)
axs[2].set_xlabel('$t$ in s')
axs[2].set_ylabel('$f$ in Hz')
plt.show()

