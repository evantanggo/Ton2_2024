''' PP4 - Panning und BRIR
Gruppe 5
Zia Asmara (2416041) '''

import numpy as np
import soundfile as sf
import sounddevice as sd

def pan_spur(signal, Fs, time_difference_ms):
    # Berechne die Anzahl der zusätzlichen Samples für die Verzögerung
    t_samples = round(time_difference_ms / 1000 * Fs)
    # Erzeuge ein Array von Nullen für die Verzögerung
    extra = np.zeros(t_samples, dtype=signal.dtype)
    # Erzeuge eine verzögerte Version des Signals im linken Kanal
    links_a = np.append(extra, signal)
    # Erzeuge eine nicht verzögerte Version des Signals im rechten Kanal
    rechts_a = np.append(signal, extra)
    # Füge die linken und rechten Kanäle zu einem Stereo-Signal zusammen
    stereo_spur = np.vstack((links_a, rechts_a)).T
    return stereo_spur

def lautheit(spur, delta_db):
    # Passe die Lautstärke der Spur um den angegebenen Wert (in dB) an
    set_spur = spur * (10**(delta_db/20))
    return set_spur

if __name__ == "__main__":
    # Einlesen der drei Mono Spuren
    spur1, Fs = sf.read("ELE Guitar 2-M80.wav")
    spur2, _ = sf.read("Drums-Snare Top-M80.wav")
    spur3, _ = sf.read("Vocals-Lead-M80.wav")

    # Spuren gegebenenfalls kürzen
    min_length = min(len(spur1), len(spur2), len(spur3))
    spur1 = spur1[:min_length]
    spur2 = spur2[:min_length]
    spur3 = spur3[:min_length]

    # Lautheit der einzelnen Spuren anpassen
    delta_db = -4.8  # Änderung der Lautheit in dB
    spur1 = lautheit(spur1, delta_db)
    spur2 = lautheit(spur2, delta_db)
    spur3 = lautheit(spur3, delta_db)

    # Panningverfahren für die Spuren
    time_difference_ms = 0.2  # Zeitdifferenz in Millisekunden
    pan_spur1 = pan_spur(spur1, Fs, time_difference_ms)
    pan_spur2 = pan_spur(spur2, Fs, time_difference_ms)
    pan_spur3 = pan_spur(spur3, Fs, time_difference_ms)

    # Alles zusammenfügen in eine Stereospur
    stereo_spur = pan_spur1 + pan_spur2 + pan_spur3

    # Begrenzen der Ausgabe auf maximal 20 Sekunden
    max_duration_samples = int(20 * Fs)
    stereo_spur = stereo_spur[:max_duration_samples]

    # Abspielen
    sd.play(stereo_spur, Fs)
    sd.wait()

    # Optional: Speichern der Stereospur in eine Datei
    sf.write("output1.wav", stereo_spur, Fs)


def stereo_faltung(spur, brir):
    spur_falt = np.convolve(spur[:, 0], brir[:, 0], mode='full') + np.convolve(spur[:, 1], brir[:, 1], mode='full')
    return spur_falt

if __name__ == "__main__":
    # Einlesen der BRIR Stereo Datei
    brir1, Fs = sf.read("BRIR_E/H13azi_0,0_ele_0,0.wav")
    brir2, _ = sf.read("BRIR_E/H13azi_45,0_ele_0,0.wav")
    brir3, _ = sf.read("BRIR_E/H13azi_90,0_ele_0,0.wav")
    brir4, _ = sf.read("BRIR_E/H13azi_135,0_ele_0,0.wav")
    brir5, _ = sf.read("BRIR_E/H13azi_180,0_ele_0,0.wav")
    brir6, _ = sf.read("BRIR_E/H13azi_225,0_ele_0,0.wav")
    brir7, _ = sf.read("BRIR_E/H13azi_270,0_ele_0,0.wav")
    brir8, _ = sf.read("BRIR_E/H13azi_315,0_ele_0,0.wav")

    # Einlesen der drei gegebenen Mono-Spuren
    spur_mono1, Fs = sf.read("ELE Guitar 2-M80.wav")
    spur_mono2, _ = sf.read("Drums-Snare Top-M80.wav")
    spur_mono3, _ = sf.read("Vocals-Lead-M80.wav")

    # Umwandeln der Mono-Spuren in Stereo
    spur_stereo1 = np.column_stack((spur_mono1, spur_mono1))
    spur_stereo2 = np.column_stack((spur_mono2, spur_mono2))
    spur_stereo3 = np.column_stack((spur_mono3, spur_mono3))

    # Lautheit der einzelnen Spuren anpassen
    delta_db = -4.8  # Änderung der Lautheit in dB (Annahme: 3 Spuren)
    spur_stereo1 = lautheit(spur_stereo1, delta_db)
    spur_stereo2 = lautheit(spur_stereo2, delta_db)
    spur_stereo3 = lautheit(spur_stereo3, delta_db)

    # Panningverfahren für die Spuren
    time_difference_ms = 0.2  # Zeitdifferenz in Millisekunden (Annahme: 0.2 ms)
    pan_spur1 = pan_spur(spur_stereo1, Fs, time_difference_ms)
    pan_spur2 = pan_spur(spur_stereo2, Fs, time_difference_ms)
    pan_spur3 = pan_spur(spur_stereo3, Fs, time_difference_ms)

    # Faltung mit den BRIRs
    spur_falt1 = stereo_faltung(pan_spur1, brir1)
    spur_falt2 = stereo_faltung(pan_spur2, brir2)
    spur_falt3 = stereo_faltung(pan_spur3, brir3)
    spur_falt4 = stereo_faltung(pan_spur1, brir4)
    spur_falt5 = stereo_faltung(pan_spur2, brir5)
    spur_falt6 = stereo_faltung(pan_spur3, brir6)
    spur_falt7 = stereo_faltung(pan_spur1, brir7)
    spur_falt8 = stereo_faltung(pan_spur2, brir8)

    # Ermittlung der maximalen Länge nach der Faltung
    max_length = max(len(spur_falt1), len(spur_falt2), len(spur_falt3),len(spur_falt4),len(spur_falt5),len(spur_falt6),len(spur_falt7), len(spur_falt8))

    # Auffüllen der Signale auf die gleiche Länge
    spur_falt1 = np.pad(spur_falt1, (0, max_length - len(spur_falt1)))
    spur_falt2 = np.pad(spur_falt2, (0, max_length - len(spur_falt2)))
    spur_falt3 = np.pad(spur_falt3, (0, max_length - len(spur_falt3)))
    spur_falt4 = np.pad(spur_falt4, (0, max_length - len(spur_falt4)))
    spur_falt5 = np.pad(spur_falt5, (0, max_length - len(spur_falt5)))
    spur_falt6 = np.pad(spur_falt6, (0, max_length - len(spur_falt6)))
    spur_falt7 = np.pad(spur_falt7, (0, max_length - len(spur_falt7)))
    spur_falt8 = np.pad(spur_falt8, (0, max_length - len(spur_falt8)))


    # Kombiniere die aufgefüllten Signale
    mix = spur_falt1 + spur_falt2 + spur_falt3 + spur_falt4 + spur_falt5 + spur_falt6 + spur_falt7 + spur_falt8

    # Begrenzen der Ausgabe auf maximal 20 Sekunden
    max_duration_samples = int(20 * Fs)
    mix = mix[:max_duration_samples]

    # Abspielen
    sd.play(mix, Fs)
    sd.wait()

    # Optional: Speichern der Ausgabe als "output.wav"
    sf.write("AKL_Output.wav", mix, Fs)
