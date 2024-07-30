import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import read
from scipy.signal import butter, sosfilt, sosfreqz
import sounddevice as sd
import warnings

# Basisverzeichnis, in dem sich das Skript befindet
base_dir = os.path.dirname(os.path.abspath(__file__))

# Dateien untersuchen (verwenden Sie den relativen Pfad)
file_noise = os.path.join(base_dir, "pinknoise.wav")
file_voice = os.path.join(base_dir, "sprache.wav")

def import_data(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Die Datei {file_path} existiert nicht.")
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sample_rate, audio_data = read(file_path)
        
        if audio_data.ndim == 2:
            left_channel = audio_data[:, 0]
            right_channel = audio_data[:, 1]
            left_channel = 0.5 * left_channel
            right_channel = 0.5 * right_channel
            mono_data = (left_channel + right_channel) / 2
        else:
            mono_data = audio_data
        
        max_amp = np.max(np.abs(mono_data))
        mono_data_normalized = mono_data / max_amp
        return sample_rate, mono_data_normalized

    except Exception as e:
        print(f"Fehler beim Importieren der Daten aus {file_path}: {str(e)}")
        return None, None
    
def play_sound(file_path):
    sample_rate, audio_data = import_data(file_path)
    if audio_data is not None:
        sd.play(audio_data, sample_rate, blocking=True)

# Tiefpassfilter mit Rückkopplung
def tiefpass_filter(x, dt, RC):
    n = len(x)
    y = np.zeros(n)
    alpha = dt / (RC + dt)
    y[0] = alpha * x[0]
    for i in range(1, n):
        y[i] = alpha * x[i] + (1 - alpha) * y[i - 1]
    return y

# Hochpassfilter mit Rückkopplung
def hochpass_filter(x, dt, RC):
    n = len(x)
    y = np.zeros(n)
    alpha = RC / (RC + dt)
    y[0] = x[0]
    for i in range(1, n):
        y[i] = alpha * (y[i - 1] + x[i] - x[i - 1])
    return y

# Funktionen zur Bandstop-Filtererstellung
def db_to_linear(Q_dB):
    # Umrechnung von dB in linearen Gütefaktor
    return 10**(Q_dB / 10)

def calculate_fl_fh(fc, Q_linear):
    fbw = fc / Q_linear
    fl = (-fbw + np.sqrt(fbw**2 + 4 * fc**2)) / 2
    fh = fbw + fl
    return fl, fh

def create_bandstop_filter(fs, fc, Q_dB):
    # Konvertieren des Gütefaktors von dB in linear
    Q_linear = db_to_linear(Q_dB)
    
    # Berechnen von fl und fh
    fl, fh = calculate_fl_fh(fc, Q_linear)
    
    # Sicherstellen, dass fl und fh innerhalb des gewünschten Bereichs liegen
    fl = max(fl, 20)
    fh = min(fh, 2000)
    
    # Erstellen des Bandstop-Filters
    nyquist = 0.5 * fs
    low = fl / nyquist
    high = fh / nyquist
    sos = butter(N=2, Wn=[low, high], btype='bandstop', output='sos')
    return sos, fl, fh

def plot_bode(sos, fs):
    w, h = sosfreqz(sos, worN=2000, fs=fs)
    plt.figure()
    plt.semilogx(w, 20 * np.log10(np.abs(h)), label='Amplitude')
    plt.title('Bode-Diagramm des Bandstop-Filters')
    plt.xlabel('Frequenz [Hz]')
    plt.ylabel('Amplitude [dB]')
    plt.grid()
    plt.show()

def impulsantworten(dt, RC, fs, filter_typ, sos=None):
    impulse = np.zeros(100)
    impulse[0] = 1

    if filter_typ == 'tp':
        y = tiefpass_filter(impulse, dt, RC)
        title = 'Impulsantwort - Tiefpassfilter'
    elif filter_typ == 'hp':
        y = hochpass_filter(impulse, dt, RC)
        title = 'Impulsantwort - Hochpassfilter'
    elif filter_typ == 'bs' and sos is not None:
        y = sosfilt(sos, impulse)
        title = 'Impulsantwort - Bandsperre'
    else:
        print("Ungültiger Filtertyp.")
        return

    zeit = np.arange(len(impulse)) * dt

    plt.figure()
    plt.stem(zeit, y)
    plt.title(title)
    plt.xlabel('Zeit [s]')
    plt.ylabel('Amplitude')

    plt.tight_layout()
    plt.show()

def plot_frequenzantworten(y, fs, filter_typ):
    NFFT = 1024  # Anzahl der Punkte für die FFT
    X = np.arange(0, fs / 2, fs / NFFT)

    def frequenzantwort(signal):
        Sp = np.fft.fft(signal, NFFT) / NFFT
        Sp_abs = np.abs(Sp)
        Sp_phase = np.angle(Sp)
        return Sp_abs[:NFFT // 2] * 2, Sp_phase[:NFFT // 2]

    Y, Phase = frequenzantwort(y)

    if filter_typ == 'tp':
        title = 'Frequenzantwort - Tiefpassfilter'
    elif filter_typ == 'hp':
        title = 'Frequenzantwort - Hochpassfilter'
    elif filter_typ == 'bs':
        title = 'Frequenzantwort - Bandsperre'
    else:
        print("Ungültiger Filtertyp.")
        return

    plt.figure()
    plt.subplot(2, 1, 1)
    plt.plot(X, Y)
    plt.title(title)
    plt.xlabel('Frequenz (Hz)')
    plt.ylabel('Amplitude')
    plt.grid()
    plt.subplot(2, 1, 2)
    plt.plot(X, Phase)
    plt.xlabel('Frequenz (Hz)')
    plt.ylabel('Phase (Radiant)')
    plt.grid()
    plt.tight_layout()
    plt.show()

def impulsantworten_bs(sos, fs):
    impulse = np.zeros(100)
    impulse[0] = 1  # Setze den Impuls an den Anfang
    y = sosfilt(sos, impulse)

    zeit = np.arange(len(impulse)) / fs  # Zeitbereich ab Null

    plt.figure()
    plt.stem(zeit, y)
    plt.title('Impulsantwort - Bandsperre')
    plt.xlabel('Zeit [s]')
    plt.ylabel('Amplitude')
    plt.tight_layout()
    plt.show()

def plot_frequenzantworten_bs(sos, fs):
    w, h = sosfreqz(sos, worN=2000, fs=fs)

    # Begrenzung der Frequenzachse auf 2000 Hz
    max_freq = 2000
    mask = w <= max_freq
    w = w[mask]
    h = h[mask]

    plt.figure()
    plt.subplot(2, 1, 1)
    plt.plot(w, 20 * np.log10(np.abs(h)))
    plt.title('Frequenzantwort - Bandsperre')
    plt.xlabel('Frequenz (Hz)')
    plt.ylabel('Amplitude [dB]')
    plt.grid()
    
    plt.subplot(2, 1, 2)
    plt.plot(w, np.angle(h))
    plt.xlabel('Frequenz (Hz)')
    plt.ylabel('Phase (Radiant)')
    plt.grid()
    plt.tight_layout()
    plt.show()

"""def plot_frequenzantworten_bs(sos, fs):
    w, h = sosfreqz(sos, worN=2000, fs=fs)

    plt.figure()
    plt.subplot(2, 1, 1)
    plt.plot(w, 20 * np.log10(np.abs(h)))
    plt.title('Frequenzantwort - Bandsperre')
    plt.xlabel('Frequenz (Hz)')
    plt.ylabel('Amplitude [dB]')
    plt.grid()
    
    plt.subplot(2, 1, 2)
    plt.plot(w, np.angle(h))
    plt.xlabel('Frequenz (Hz)')
    plt.ylabel('Phase (Radiant)')
    plt.grid()
    plt.tight_layout()
    plt.show()"""


"""def filter_auf_audio_anwenden(x_t, fs, fgr, filter_typ, Q_dB=-3):
    delta_T = 1 / fs

    if filter_typ == 'tp':
        RC = 1 / (2 * np.pi * fgr)
        y = tiefpass_filter(x_t, delta_T, RC)  # TP 1. Ordnung
        title = 'Tiefpass-gefiltertes Audiosignal'
    elif filter_typ == 'hp':
        RC = 1 / (2 * np.pi * fgr)
        y = hochpass_filter(x_t, delta_T, RC)  # HP 1. Ordnung
        title = 'Hochpass-gefiltertes Audiosignal'
    elif filter_typ == 'bs':
        sos, fl, fh = create_bandstop_filter(fs, fgr, Q_dB)
        y = sosfilt(sos, x_t)
        title = 'Bandsperre-gefiltertes Audiosignal'
    else:
        print("Ungültiger Filtertyp. Bitte 'tp' für Tiefpass, 'hp' für Hochpass oder 'bs' für Bandsperre eingeben.")
        return

    # Audiosignal abspielen
    sd.play(y, fs)
    sd.wait()

    # Visualisierung der Audiosignale
    zeit = np.arange(len(x_t)) / fs
    plt.figure()
    plt.subplot(2, 1, 1)
    plt.plot(zeit, x_t)
    plt.title('Originales Audiosignal')
    plt.xlabel('Zeit [s]')
    plt.ylabel('Amplitude')

    plt.subplot(2, 1, 2)
    plt.plot(zeit, y)
    plt.title(title)
    plt.xlabel('Zeit [s]')
    plt.ylabel('Amplitude')

    plt.tight_layout()
    plt.show()

    # Berechnung und Anzeige der Impulsantworten
    if filter_typ == 'bs':
        impulsantworten(delta_T, fgr, fs, filter_typ, sos)
    else:
        impulsantworten(delta_T, 1 / (2 * np.pi * fgr), fs, filter_typ)

    # Berechnung und Anzeige der Frequenzantworten
    plot_frequenzantworten(y, fs, filter_typ)"""

def filter_auf_audio_anwenden(x_t, fs, fc, filter_typ, Q_dB=None):
    delta_T = 1 / fs

    if filter_typ == 'tp':
        RC = 1 / (2 * np.pi * fc)
        y = tiefpass_filter(x_t, delta_T, RC)  # TP 1. Ordnung
        title = 'Tiefpass-gefiltertes Audiosignal'
    elif filter_typ == 'hp':
        RC = 1 / (2 * np.pi * fc)
        y = hochpass_filter(x_t, delta_T, RC)  # HP 1. Ordnung
        title = 'Hochpass-gefiltertes Audiosignal'
    elif filter_typ == 'bs' and Q_dB is not None:
        sos, fl, fh = create_bandstop_filter(fs, fc, Q_dB)
        y = sosfilt(sos, x_t)
        title = 'Bandsperre-gefiltertes Audiosignal'
    else:
        print("Ungültiger Filtertyp. Bitte 'tp' für Tiefpass, 'hp' für Hochpass oder 'bs' für Bandsperre eingeben.")
        return

    # Audiosignal abspielen
    sd.play(y, fs)
    sd.wait()

    # Visualisierung der Audiosignale
    zeit = np.arange(len(x_t)) / fs
    plt.figure()
    plt.subplot(2, 1, 1)
    plt.plot(zeit, x_t)
    plt.title('Originales Audiosignal')
    plt.xlabel('Zeit [s]')
    plt.ylabel('Amplitude')

    plt.subplot(2, 1, 2)
    plt.plot(zeit, y)
    plt.title(title)
    plt.xlabel('Zeit [s]')
    plt.ylabel('Amplitude')

    plt.tight_layout()
    plt.show()

    if filter_typ == 'bs':
        impulsantworten_bs(sos, fs)
        plot_frequenzantworten_bs(sos, fs)

# Funktion für den PingPong-Delay
def pingpong_delay(x_t, fs, delay_ms=500):
    t_ms = round(delay_ms / 1000 * fs)  # Zeitdifferenz in Arraylänge umgerechnet
    
    # Aufteilen der Kanäle
    if x_t.ndim == 2 and x_t.shape[1] == 2:
        links = x_t[:, 0]
        rechts = x_t[:, 1]
    else:
        links = x_t
        rechts = x_t
    
    # Signale auf 1 normieren
    links = links / np.max(np.abs(links))
    rechts = rechts / np.max(np.abs(rechts))
    
    # Array mit Nullen gefüllt, abhängig von der gewählten Zeitdifferenz
    extra_L = np.zeros(t_ms, dtype=int)
    extra_R = np.zeros(2 * t_ms, dtype=int)
    
    # Delay-Effekt für den linken Kanal erzeugen
    links_delay_L_1 = np.append(extra_L, links)
    links_delay_L = np.append(links_delay_L_1, extra_L)
    rechts_delay_L = np.append(rechts, extra_R)
    
    # Delay-Effekt für den rechten Kanal erzeugen
    links_delay_R = np.append(links, extra_R)
    rechts_delay_R = np.append(extra_R, rechts)
    
    # Stereo-Array für den linken und rechten Effekt
    stereo_delay_L = np.vstack((links_delay_L, rechts_delay_L)).transpose()
    stereo_delay_R = np.vstack((links_delay_R, rechts_delay_R)).transpose()
    
    # Zusammenfügen der beiden Effektarrays in ein Effektarray und halbieren (Signalpegel/Amplitude verringern)
    stereo_delay_LR = (stereo_delay_L + stereo_delay_R) / 2
    
    # Ausgangssignal verlängern, um den Effektarray addieren zu können
    links_new = np.append(links, extra_R)
    rechts_new = np.append(rechts, extra_R)
    stereo = np.vstack((links_new, rechts_new)).transpose()
    
    # Signal + PingPongDelay
    stereo_output = stereo + stereo_delay_LR
    
    return stereo_output

def main():
    fc = 700  # Mittenfrequenz der Bandsperre
    Q_dB = -3  # Gütefaktor der Bandsperre in dB
    
    fs_noise, y_noise = import_data(file_noise)
    fs_voice, y_voice = import_data(file_voice)
    
    if y_noise is None or y_voice is None:
        return

    # Anzeige der Impulsantwort
    filter_auf_audio_anwenden(y_noise, fs_noise, fc, 'bs', Q_dB)    
    # Ping Pong Delay
    #y_pingpong = pingpong_delay(y_voice, fs_voice)
    #sd.play(y_pingpong, fs_voice)
    #sd.wait()

if __name__ == "__main__":
    main()
