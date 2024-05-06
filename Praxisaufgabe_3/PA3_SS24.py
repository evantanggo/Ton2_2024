'''
Praxisaufgabe 3
Tontechnik_SS24
'''

import math
from scipy.io.wavfile import read
import numpy as np
from scipy.io import wavfile

def berechne_energie(file_path): 
    try:
        # Datei einlesen
        sample_rate, audio_data = wavfile.read(file_path)
        
        # Datei in Mono umwandeln, wenn Stereo
        if audio_data.ndim == 2:
            left_channel = audio_data[:, 0]
            right_channel = audio_data[:, 1]
            mono_data = (left_channel + right_channel) / 2
        else:
            mono_data = audio_data
        
        # Energie berechnen
        energy = sum(mono_data ** 2) / sample_rate

        

        print(f"Datei: {file_path}")
        print(f"Einzelenergie: {energy:.2f}")
        print("\n")

    except Exception as e:
        print(f"Fehler beim Verarbeiten der Datei {file_path}: {str(e)}")
        print("\n")

# Dateien untersuchen
dateien = ['Praxisaufgabe_3/vokal1.wav', 'Praxisaufgabe_3/vokal2.wav']

# Ausführen
if __name__ == "__main__":
    print("Aufgabe 1 / 2")
    for datei in dateien:
        berechne_energie(datei)
