''' PP1 - Nachhallzeit, Deutlichkeitsmaß und Klarheitsmaß
Gruppe 5
Zia Asmara (2416041) '''

import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

# Dateipfad zur WAV-Datei
file = 'Datei_C.wav'

# Auslesen und Speichern der Abtastrate (Fs) und der Impulsantwort als Array (datei) aus der WAV-Datei
datei, Fs = sf.read(file)

# Falls die Impulsantwort Stereo ist, beide Kanäle addieren und halbieren, um Stereo zu Mono zu konvertieren
if datei.ndim == 2:
    datei = datei[:, 0] + datei[:, 1] / 2

# Impulsantwort auf den Wertebereich von -1 bis 1 normieren
n_datei = datei / np.max(np.abs(datei))

# Startzeitpunkt = Index im Array mit dem größten Wert, wird als Start für c50 und c80 verwendet
start = np.argmax(n_datei)

# Gesamtenergie der normierten Impulsantwort berechnen (Summe der Quadrate geteilt durch Abtastrate)
n_ges_energie = np.sum(np.square(n_datei))

# Array mit den Einzelenergien von jedem Zeitpunkt bis zum Ende erstellen
Einzelenergien = np.zeros(len(n_datei))
for n in range(0, len(n_datei)):
    Einzelenergien[n] = np.sum(np.square(n_datei[n:]))

# Zwischenrechnung: Array mit den Teilenergien geteilt durch die Gesamtenergie
Energien = Einzelenergien / n_ges_energie

# Schroeder-Plot erstellen (um den Nachhall zu analysieren) durch Umwandlung in Dezibel
Schroeder = 10 * np.log10(Energien)

# Nachhallzeit T7
# Zeitpunkt: 5 dB Abfall, um Direktschall auszuschließen
t5 = 0
Schroeder_t5 = Schroeder[start:]
for s in range(0, len(Schroeder_t5)):
    if Schroeder_t5[s] < -5:
        t5 = s / Fs
        xt5 = t5
        yt5 = Schroeder[s]
        break

# T12-Zeitpunkt (7 dB Abfall)
T12 = 0
for s in range(0, len(Schroeder_t5)):
    if Schroeder_t5[s] < -12:
        T12 = s / Fs
        break
T7 = (T12 - t5) * (60 / 7)
print("*** Ergebnis Nachhallzeiten ***")
print("- T7: {:.2f}".format(T7)), "Sekunden"

# T15-Zeitpunkt (10 dB Abfall)
T15 = 0
for s in range(0, len(Schroeder_t5)):
    if Schroeder_t5[s] < -15:
        T15 = s / Fs
        break
T10 = (T15 - t5) * 6

# Korrelationsfaktor T10 im Bezug auf T7
K = T7 / T10
print("- T10: {:.2f}".format(T10), "Sekunden")

# T25-Zeitpunkt (15 dB Abfall)
T25 = 0
for s in range(0, len(Schroeder_t5)):
    if Schroeder_t5[s] < -25:
        T25 = s / Fs
        break
T20 = (T25 - t5) * 3

# Korrelationsfaktor T20 im Bezug auf T7
C = T7 / T20
print("- T20: {:.2f}".format(T20), "Sekunden")

# T35-Zeitpunkt (25 dB Abfall)
T35 = 0
for s in range(0, len(Schroeder_t5)):
    if Schroeder_t5[s] < -35:
        T35 = s / Fs
        break
T30 = (T35 - t5) * 2

# Korrelationsfaktor T30 im Bezug auf T7
C = T7 / T30
print("- T30: {:.2f}".format(T30), "Sekunden")

# C50 und C80
# Neue Arrays erstellen und auf den Start der Impulsantwort kürzen
impulsantwort_n = n_datei[start:]

# Indices im Array, die 50 ms und 80 ms entsprechen
t50 = round(50 / 1000 * Fs)
t80 = round(80 / 1000 * Fs)

print()
print("*** Klarheitsmaß und Deutlichkeitsmaß ***")
# Berechnung der Teilenergiesumme bis 50 ms und nach 50 ms + Verhältnis
Energie_C50 = np.sum(np.square(impulsantwort_n[:t50])) / np.sum(np.square(impulsantwort_n[t50 + 1:]))
C50 = 10 * np.log10(Energie_C50)
print("Deutlichkeitsmaß C50: {:.2f}".format(C50), "dB")

# Berechnung der Teilenergiesumme bis 80 ms und nach 80 ms + Verhältnis
Energie_C80 = np.sum(np.square(impulsantwort_n[:t80])) / np.sum(np.square(impulsantwort_n[t80 + 1:]))
C80 = 10 * np.log10(Energie_C80)
print("Klarheitsmaß C80: {:.2f}".format(C80), "dB")

# Plot erstellen (Impulsantwort und Schroeder-Plot)
x1 = np.arange(len(Schroeder)) / Fs
y1 = n_datei
x2 = np.arange(len(Schroeder)) / Fs
y2 = Schroeder

fig, ax = plt.subplots(2)
ax[0].plot(x1, y1, "tab:blue")
ax[0].set_title("Normierte Impulsantwort")
ax[0].set_xlabel("Zeit [s]")

ax[1].plot(x2, y2, "tab:blue")
ax[1].set_title("Schröder Plot")
ax[1].set_xlabel("Zeit [s]")
ax[1].set_ylabel("Schallpegel [dB]")
ax[1].plot(xt5, yt5, marker="X", c="red", label="T5")
ax[1].legend(loc='upper right')
fig.tight_layout()

plt.show()