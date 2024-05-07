from scipy.io.wavfile import read
import numpy as np

def calculate_energy(file_path):
    try:
        # WAV-Datei einlesen
        sample_rate, audio_data = read(file_path)
        
        # Einzelenergie berechnen
        energy = np.sum(audio_data.astype(np.float64) ** 2) / sample_rate
        
        return energy
    
    except Exception as e:
        print(f"Fehler beim Berechnen der Einzelenergie: {str(e)}")
        return None

# Pfad zur WAV-Datei
file_path = 'Praxisaufgabe_3/vokal1.wav'

# Einzelenergie berechnen
energy = calculate_energy(file_path)
if energy is not None:
    print(f"Einzelenergie der WAV-Datei: {energy:.2f}")
