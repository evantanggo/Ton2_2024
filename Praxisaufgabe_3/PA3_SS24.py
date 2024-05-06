'''
Praxisaufgabe 3
Tontechnik_SS24
'''

import math
from scipy.io.wavfile import read
import numpy as np
from scipy.io import wavfile
import warnings
import os

def berechne_energie(file_path): 
    try:
        # Datei einlesen
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
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

# Basisverzeichnis, in dem sich das Skript befindet
base_dir = os.path.dirname(os.path.abspath(__file__))

# Dateien untersuchen (verwenden Sie relative Pfade)
dateien = ['vokal1.wav', 'vokal2.wav']
dateien_pfade = [os.path.join(base_dir, datei) for datei in dateien]

# Ausführen
if __name__ == "__main__":
    print("Aufgabe 1a")
    for datei_pfad in dateien_pfade:
        berechne_energie(datei_pfad)
