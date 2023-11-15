import numpy as np
from scipy.integrate import quad

def f1(x, f1):
    return np.sin(2 * np.pi * f1 * x)

def f2(x, f2):
    return np.sin(2 * np.pi * f2 * x)

def integrand(x, f1, f2):
    return f1(x, 1.0) * f2(x, 2.0)  # Hier ist f2 = 2 * f1

result, error = quad(integrand, 0, 1, args=(f1, f2))

print(f"The result of the integral is: {result}")


# Fs = 44100  # Abtastfrequenz, Fs >= 2*fmax
# f = 100  # Signalfrequenz
# y_dach = 1  # Amplitude (ist Maximalwert für Wiedergabe mit sounddevice)
# dauer = 2  # Dauer in sec.
# deltat = 1. / Fs  # Ts; Schrittweite für Signalerzeugung.
#
# # 1.Sinus erzeugen:
# t = np.arange(0, dauer, deltat)  # Zeit-Werte
# T = len(t)
# y = y_dach * np.sin(2 * np.pi * f * t)  # Sinusschwingung
#
# # 2. Sinus erzeugen:
# n = 2 # für verschiedene Frequenzen
#
# t1 = np.arange(0, dauer, deltat)  # Zeit-Werte
# T1 = len(t)
# y1 = y_dach * np.sin(2 * np.pi * n * f * t)  # Sinusschwingung
#
# fig, (ax1) = plt.subplots(nrows=1)  # Vorbereitung für zwei Plots
# plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
#                     wspace=None, hspace=0.5)  # Abstand zwischen Subplots
#
# # erste Grafik:
# ax1.plot(t, y, t1,y1,'.')  # Plotten von y über t
# ax1.set_ylim(-1 * y_dach, y_dach)  # Grenzen der y-Achse
# ax1.set_xlim(0, 2 / f)  # Grenzen der x-Achse
# ax1.set_xlabel('$n \cdot T_s$ in s')  # Beschriftung x-Achse, $x$ stellt x kursiv dar
# ax1.set_ylabel('$y$($n T_s$)')  # Beschriftung y-Achse
# ax1.set_title(f"Sinus mit {f} und {n*f} Hz")
# #ax1.set_title('$y$ = $\hat{y}$ $\cdot$ sin (2 $\pi$ $f$ $n$ $T_s$)')
# ax1.grid(True)
# plt.show()
