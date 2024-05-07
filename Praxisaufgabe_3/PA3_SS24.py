'''
Praxisaufgabe 3
Tontechnik_SS24
'''

from scipy.io.wavfile import read
import numpy as np
import warnings
import os

def import_data(file_path):
    try:
        # Datei einlesen
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sample_rate, audio_data = read(file_path)
        
        # Datei in Mono umwandeln, wenn Stereo
        if audio_data.ndim == 2:
            left_channel = audio_data[:, 0]
            right_channel = audio_data[:, 1]
            mono_data = (left_channel + right_channel) / 2
        else:
            mono_data = audio_data
        
        # Signal normalisieren
        max_amp = np.max(np.abs(mono_data))
        mono_data_normalized = mono_data / max_amp
        return sample_rate, mono_data_normalized

    except Exception as e:
        print(f"Fehler beim Importieren der Daten aus {file_path}: {str(e)}")
        return None, None

def count_energy(audio_data, sample_rate): 
    try:
        # Energie berechnen
        #energy = (effektiv_wert(audio_data, num_samples)**2) * duration
        energy = sum(audio_data**2) / sample_rate
        return energy

    except Exception as e:
        print(f"Fehler beim Berechnen der Energie: {str(e)}")
        return None

# def effektiv_wert(y, T):
    y = y.astype(np.float64)
    square = np.square(y)
    integral = np.sum(square)
    eWert = (np.sqrt((1 / T) * integral))
    return eWert

# def duration_in_seconds(sample_rate, audio_data):
    # Anzahl der Samples in der Audiodatei
    num_samples = len(audio_data)
    
    # Dauer in Sekunden berechnen
    duration = num_samples / sample_rate
    
    return duration, num_samples

def correlation_factor(energy1, energy2, audio_data1, audio_data2, sample_rate):
    audio_data1 = audio_data1.astype(np.float64) 
    audio_data2 = audio_data2.astype(np.float64) 

    signal = np.sum(audio_data1 * audio_data2) /sample_rate
    norm_factor = np.sqrt(energy1 * energy2)
    
    if norm_factor == 0:
        return 0  # To avoid division by zero
        
    #print(energy1, energy2, audio_data1, audio_data2) 
    return (signal / norm_factor)



def total_energy(energy1, energy2, correlationsfactor):
    total_energy = energy1 + energy2 + 2 * correlationsfactor * np.sqrt(energy1 * energy2)

    return total_energy

def sound_level(correlation_factor, signal_sum):
    if 0 <= correlation_factor < 0.5:
        delta_l = 10 * np.log10(1 / signal_sum)
    elif 0.5 < correlation_factor <= 1:
        delta_l = 10 * (np.log10(1 / signal_sum) ** 2)
    elif -1 <= correlation_factor < 0.5:
        delta_l = 10 * (np.log10(1 / signal_sum) ** 2)
    elif -0.5 < correlation_factor <= 0:
        delta_l = 10 * np.log10(1 / signal_sum)
    else:
        return 0
    
    return delta_l

# Basisverzeichnis, in dem sich das Skript befindet
base_dir = os.path.dirname(os.path.abspath(__file__))

# Dateien untersuchen (verwenden Sie relative Pfade)
dateien = ['vox1.wav', 'vox2.wav']
dateien_pfade = [os.path.join(base_dir, datei) for datei in dateien]

# Main Funktion
def main():
    print("Aufgabe 1a\n")
    energie = []
    list_audiodata = []
    for datei_pfad in dateien_pfade:
        print(f"Datei: {datei_pfad}")
        sample_rate, mono_data = import_data(datei_pfad)
       # duration, num_samples = duration_in_seconds(sample_rate, mono_data)

        list_audiodata.append(mono_data)

        if sample_rate is not None and mono_data is not None:
            print(f"Einzelenergie: {count_energy(mono_data, sample_rate):.2f}")
            print("\n")
            energie.append(count_energy(mono_data, sample_rate))

    correlation = correlation_factor(energie[0], energie[1], list_audiodata[0], list_audiodata[1], sample_rate)
    
    print(f"Korrelationsfaktor: {correlation :.2f}")
    print("\n")
    print(f"Gesamtenergie: {total_energy(energie[0], energie[1], correlation):.2f}")
    print("\n")

    print("Aufgabe 1b")
    soundlevel= sound_level(correlation, len(energie))
    print(f"Jede Kanäle muss um {soundlevel:.2f} db abgesenkt werden, damit es vollgesteuert ist\n")

# Ausführen
if __name__ == "__main__":
    main()


    

    

            

