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

def importiere_daten(file_path):
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
        
        return sample_rate, mono_data

    except Exception as e:
        print(f"Fehler beim Importieren der Daten aus {file_path}: {str(e)}")
        return None, None

def berechne_energie(sample_rate, audio_data): 
    try:
        # Energie berechnen
        energy = sum(audio_data ** 2) / sample_rate

        return energy

    except Exception as e:
        print(f"Fehler beim Berechnen der Energie: {str(e)}")
        return None

def correlation_factor(energy1, energy2, audio_datei1, audio_datei2):
    signal = sum(audio_datei1 * audio_datei2)

    return signal / np.sqrt(energy1 * energy2)

# Basisverzeichnis, in dem sich das Skript befindet
base_dir = os.path.dirname(os.path.abspath(__file__))

# Dateien untersuchen (verwenden Sie relative Pfade)
dateien = ['vokal1.wav', 'vokal2.wav']
dateien_pfade = [os.path.join(base_dir, datei) for datei in dateien]

# Ausführen
if __name__ == "__main__":
    print("Aufgabe 1a")
    energie = []
    list_audiodata = []
    for datei_pfad in dateien_pfade:
        print(f"Datei: {datei_pfad}")
        sample_rate, mono_data = importiere_daten(datei_pfad)
        list_audiodata.append(mono_data)

        if sample_rate is not None and mono_data is not None:
            print(f"Einzelenergie: {berechne_energie(sample_rate, mono_data):.2f}")
            print("\n")
            #berechne_energie(sample_rate, audio_data)
            energie.append(berechne_energie(sample_rate, mono_data))

    print(f"Korrelationsfaktor:{correlation_factor(energie[0], energie[1], list_audiodata[0], list_audiodata[1]):.2f}")
    

            

