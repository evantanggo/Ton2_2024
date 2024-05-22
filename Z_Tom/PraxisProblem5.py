#Praxis Problem 5 Gruppe 3
#Tom Butenschön
#

import numpy as np
import scipy
import matplotlib.pyplot as plt
from scipy.io.wavfile import read
from scipy.io.wavfile import write
import sounddevice as sd

#einlesen der einzelnen Spuren

#Spuren gegebenenfalls kürzen
#da beim Zusammenfügen am Ende die Gesamtenergie abhängig von der Anzahl der Spuren ist
# delta_L = 10*log (Anzahl Spuren)
#heisst bei zB 3 Spuren, jede Spur am Anfang -4,8dB leiser

#Panningverfahren aus PP2 verwenden
#jede Monospur auf links und rechts verteilen, nur auf einer Seite klingt nicht ausgewogen
t_ms = round(2/1000 * Fs)   #Zeitdifferenz 0,2 ms umgerechet in Arraylänge
#Array mit Nullen gefüllt abhänging von der gewählten Zeitdifferenz
extra = np.zeros(t_ms, dtype=int)

links_a = np.append(extra,signal)
rechts_a = np.append(signal,extra)
stereo-spurX = np.vstack((links_a,rechts_a)).transpose()

#Lautheit der einzelnen Spuren vor dem Zusammenfügen prüfen/bearbeiten
#alles zusammenfügen in eine Stereospur



#BRIR
#für Faltung muss Signal und BRIR gleich lang sein

#Monotrack einmal für linken und rechten kanal, um später ein stereotrack zu haben

#beide array mit FFT von Zeitbereich in Frequenbereich transformieren

#dann multiplizieren

#linken Track multipliziert mit BRIR (je nach winkelauswahl) und rechter Track multipliziert mit der selben BRIR

# zurücktransformieren mit ifft

#neue Monotracks zu einem Stereotrack zusammenfügen und abspielen

#abspielen

