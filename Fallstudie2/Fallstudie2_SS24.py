"""
Ton2 SS24, Fallstudie
Praxisproblem 2
Evan Tanggo Peter Simamora
2332397
"""

import os
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import read, write
import warnings
import matplotlib.pyplot as plt


# Basisverzeichnis, in dem sich das Skript befindet
base_dir = os.path.dirname(os.path.abspath(__file__))

# Datei untersuchen (verwenden Sie den relativen Pfad)
file_path = os.path.join(base_dir, "gitarre.wav")

def import_data(file_path):
    try:
        # Überprüfe, ob die Datei existiert
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Die Datei {file_path} existiert nicht.")
        
        # Datei einlesen
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sample_rate, audio_data = read(file_path)
        
        # Datei in Mono umwandeln, wenn Stereo
        if audio_data.ndim == 2:
            left_channel = audio_data[:, 0]
            right_channel = audio_data[:, 1]
            left_channel = 0.5 * left_channel
            right_channel = 0.5 * right_channel
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
    
def waveform_plot(audio_data, sample_rate):
    duration = len(audio_data) / sample_rate                              # Dauer des Signals in Sekunden definieren
    time = np.linspace(0, duration, len(audio_data))         # Numpy-Array mit linearen Zeitwerten definieren

    # Plot der Impulantwort
    plt.figure()
    plt.plot(time, audio_data, color='red')
    plt.xlabel('Zeit in s')
    plt.ylabel('Amplitude normalisiert')
    ax = plt.gca()
    ax.set_ylim([-1, 1])
    plt.title('Impulsantwort h(t)')
    plt.grid()
    plt.show()

# Pegeldifferenz
def pan_audio(audio_data, pan):
    """
    Pan the audio data.
    
    Parameters:
    - audio_data: The input mono audio signal.
    - pan: Panning value. -1 is full left, +1 is full right, 0 is center.
    
    Returns:
    - stereo_data: The panned stereo audio signal.
    """
    if pan < -1 or pan > 1:
        raise ValueError("Pan value must be between -1 and +1")
    
    left = np.sqrt(0.5 * (1 - pan))
    right = np.sqrt(0.5 * (1 + pan))
    print(left)
    print(right)
    
    stereo_data = np.vstack((audio_data * left, audio_data * right)).T
    return stereo_data

def main():
    sample_rate, audio_data = import_data(file_path)
    
    if sample_rate is not None and audio_data is not None:
        # Apply panning
        pan_value = 0.75  # Panning value: -1 is full left, +1 is full right, 0 is center
        panned_audio = pan_audio(audio_data, pan_value)
        
        # Play the panned audio
        print("Playing panned audio...")
        sd.play(panned_audio, sample_rate)
        sd.wait()  # Wait until the audio is finished playing

         # Plot the waveform
        #waveform_plot(audio_data, sample_rate)
        
        # Save the panned audio to a file
        """output_file_path = os.path.join(base_dir, "gitarre_panned.wav")
        write(output_file_path, sample_rate, (panned_audio * 32767).astype(np.int16))
        print(f"Panned audio saved to {output_file_path}")"""
        
    else:
        print("Fehler beim Laden der Audiodaten.")

if __name__ == "__main__":
    main()
