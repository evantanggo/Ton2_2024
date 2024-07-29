"""
PRAXISPROBLEM 3: Implementieren eines Hochpassfilters zweiter Ordnung und Ping Pong Delay.

Gruppe 3:
Rike Malottke
Hannah Körber
Mira Stahlmann
"""

""" :::::::: import libraries ::::::::"""
import matplotlib.pyplot as plt
from scipy.io.wavfile import read
import numpy as np
from scipy.io.wavfile import write
import sounddevice as sd

def readwav(file):
    """
    Reads the signal that is saved in "file", if it is in .wav format. Extracts data and samplerate. Writes data into \
    array. Converts stereo to mono by selecting only one of the two stereo tracks.
    :param file: wav
    :return: y: array, fs: int
    """
    if ".wav" in file:
        (fs, y_read) = read(file)  # Fs: Abtastfrequenz, y: Abtastwerte des Soundfiles
        if np.ndim(y_read) == 2:  # is stereo
            stereo = y_read
            stereo /= np.max(np.abs(stereo))
            y = stereo[:, 0]
            return y, fs
        else:  # is mono
            y = y_read
            y = y / np.max(np.abs(y))
            return y, fs
    else:
        raise TypeError('file has to be in .wav format')

def xaxis(array, fs):
    """
    Gets array input and sample rate and creates a time array, for instance for plotting.
    :param array: type: array
    :param Fs: type: integer
    :return: type: t: array, N: int, delta_T: float, L:float
    """
    delta_T = 1/fs          #delta T
    N = len(array)          # Länge des Signals
    NFFT = int(N)           #Länge als int
    L = N/fs               # Dauer
    t = np.arange(0, L, delta_T)
    return t, N, delta_T, NFFT, L

def play(signal, Fs):
    """
    Plays an array.
    :param signal: array
    :param Fs: int
    :return: none
    """
    sd.play(signal, Fs)
    status = sd.wait()

""" ::::::::::::::::: Hochpass 1. Ordnung :::::::::::::::: """
def highpass(data):
    """
    Lays a highpass filter over data array, returns normalized, new array.
    :param data: array
    :return: y_HP: array, alpha_HP: float
    """
    y = data    #zu übernehmende Daten für Hochpass
    y_HPi = np.zeros(N)     #Array aus nullen erstellen
    alpha_HP = 1 / (1 + fgr * 2 * np.pi * delta_T)      #Faktor alpha berechnen
    y_HPi[0] = y[0] * alpha_HP  #Array mit alpha multiplizieren

    for i in range(1, N):       #Iteriert durch alle Werte 1 bis N
        y_HPi[i] = alpha_HP * (y_HPi[i - 1] + y[i] - y[i - 1])

    y_HP = y_HPi / max(y_HPi, key=abs)        #Normierung durch Maximalwert des HP-Arrays

    return y_HP, alpha_HP

""" ::::::::::::: Frequenzdarstellung für Plot ::::::::::::::::::: """
def fft(data):
    """
    Does a fast fourier transformation to transform a time signal into a frequency signal. Returns frequency amplitudes\
    and frequency axis.
    :param data: array
    :return: Y: array, F: array
    """
    range_ = data[0:NFFT]                   #NFFT: ganzzahlige Signallänge
    y_f = np.fft.fft(range_) / NFFT         #FFT von index 0 bis Signallänge gemittelt durch Signallänge
    y_f_Abs = np.abs(y_f)                   #Normierung in Frequenzebene auf Maximalwert
    l = int(NFFT/2)
    Y = np.array(y_f_Abs[0:(l*2)]*2)        #Y-achse: Frequenzanteile, doppelt wegen Spiegelspektrum
    F = np.arange(0, fs, 1.*fs/NFFT)        #Frequenzachse
    return Y, F

def log(data, ref):
    """
    Turns amplitude array into level array in dB. Needs reference values.
    :param data: array
    :param ref: array
    :return: array
    """
    log = np.array(20 * np.log10(data / ref))   #logarithmische Umrechnung zu Pegel in dB
    return log

def phase(F):
    """
    Calculates tau as a function of f and omega, returns phase response.
    :param F: array
    :return: array
    """
    tau_w = alpha * delta_T / (1 - alpha)       #Berechnen von Tau von Omega, wie bei RC-Glied
    omega = 2 * np.pi * F     #Berechnen von Omega
    phi_w = 90 - np.degrees(np.arctan(omega * tau_w))   #Berechnen des Phasengangs, für HP immer: von 90° zu 0°
    return phi_w

""" :::::::::::::::::::::: generiere Ping-Pong-Delay :::::::::::::::::::::::::: """
def generate_param():
    """
    Lets user decide time shift of delay, between 100 and 900 ms, and intensity (as in: how many signal repetitions) \
    between 1 and 9.
    :return: delay: int, loop: int
    """
    # Delay-Werte
    delay_Werte = np.linspace(100, 900, 801)  # Range an auswählbaren Werten
    while True:
        delay_wert = int(input("Delay time shift? (100...900 ms): "))  # Delay Zeitverschiebung, in ms, über Input anwählbar
        if delay_wert in delay_Werte:       #Fehlerabdeckung
            break       # ist die Eingabe gültig, wird while-Loop beendet
        else:  # falls Wert von Range abweicht
            print("Delay zwischen 100 ms und 900 ms wählbar!")
    while True:
        loop = int(input("Wähle Feedback-Intensität (<10!): "))  # wie oft Läuft das Signal durch Delay-Schleife
        if loop in range(1, 10):    #Fehlerabdeckung
            break  # ist die Eingabe gültig, wird while-Loop beendet
        else:
            print("Feedback-Intensität als ganze Zahl zwischen 1 und 9 wählbar!")   #Fehlerabdeckung

    delay_shift = int(fs * (delay_wert / 1000))  # Delay, Verschiebung um Abtastwerte

    return delay_shift, loop

def concatenate(array1, array2):
    """
    Adjust two arrays, so that they have the same length, by adding zeros to shorter array, returns formally shorter array\
    with new length.
    :param array1: array
    :param array2: array
    :return: output: array
    """
    N1 = len(array1)
    N2 = len(array2)
    if N1 < N2: #first array is shorter than second array
        diff = N2-N1    #length difference
        output = np.concatenate([array1, np.zeros(diff)])  # fill end of array1 with diff zeros
    else:   #second array is shorter than first array
        diff = N1-N2    #length difference
        output = np.concatenate([array2, np.zeros(diff)])  # fill end of array1 with diff zeros

    return output

def add(array1, array2):
    """
    Adds two arrays, returns new array with added values.
    :param array1: array
    :param array2: array
    :return: output: array
    """
    output = np.add(array1, array2)

    return output

def generate_input(input, delay_shift, gain=0.4):
    """
    Executes ping pong delay: Creates time shift arrays for left an right by adding zeros at the beginning of each new \
    array, followed by original data. Dims delay arrays with factor gain. Puts all left delay signals into one and all \
    right signals into another array of arrays.
    :param input: array
    :param delay_shift: int
    :param gain: float
    :return: ping: array[array], pong: array[array]
    """
    signal_l = input
    ping = np.zeros(loop, dtype=np.ndarray)     #Null-array mit in 'loop' festgelegter Länge
    pong = np.zeros(loop, dtype=np.ndarray)     #Null-array mit in 'loop' festgelegter Länge

    for n in range(loop):   #auffüllen der Null-arrays mit einem neuen array pro Eintrag
        ping[n] = np.array((np.pad(input, ((delay_shift * (n+(n+1))), 0), 'constant') * gain))   #links: ungerade Faktoren für Berechnung der nächsten Verschiebung
        pong[n] = np.array((np.pad(input, ((delay_shift * (n+(n+2))), 0), 'constant') * gain)) #rechts: gerade Faktoren für Berechnung der nächsten Verschiebung

    return ping, pong

def stereo_delay(left, right, original):
    """
    Takes left array list and right array list that include all time shift arrays for ping pong delay, adjusts all lengths\
    by overwriting, adds all arrays step by step, so that last entry of array list for each side includes all its arrays \
    added up. Extracts that last entry as leftout and rightout. Then adjusts leftout and right out lengths and adds them.\
    Creates 2-dim array for stereo output, takes leftout as left track and rightout as right track. Adjusts original array \
    to new length, adds half to each track, so that it will appear in the middle.
    :param left: array[array]
    :param right: array[array]
    :param original: array
    :return: array
    """
    for n in range(loop-1):
        left[n] = concatenate(left[-1], left[n])

    for n in range(loop-1):
        left[n+1] = add(left[n+1], left[n])
    leftout = left[-1]

    for n in range(loop-1):
        right[n] = concatenate(right[-1], right[n])

    for n in range(loop - 1):
        right[n + 1] = add(right[n + 1], right[n])
    rightout = right[-1]

    leftout = concatenate(leftout, rightout)
    org = concatenate(original, rightout)
    halforg = np.array(org * 0.5)

    stereo_delay = np.zeros((len(leftout), 2))
    stereo_delay[:, 0] = add(leftout, halforg)
    stereo_delay[:, 1] = add(rightout, halforg)

    return stereo_delay

def plot(x1,y1,X1, Y1, phi2,X2,Y2,phi3,X3,Y3):
    """
    Makes 6 plots: 1-original data as a function of t, 2-FFT of original data, 3-signal in dB after HP1 as a function of f, \
    4-phase response after HP1 as a function of f, 5-signal in dB after HP2 as a function of f, 6-phase response after HP2 as \
    a function of f
    :return: none
    """
    fig, axs = plt.subplots(3, 2)

    axs[0, 0].plot(x1, y1)
    axs[0, 0].set(xlabel="time [s]", ylabel='y(t)', title='Original im Zeitbereich')
    axs[0, 0].grid(which='major', linestyle='--')
    axs[0, 0].grid(which='minor', linestyle=':')

    axs[0, 1].plot(X1, Y1)
    axs[0, 1].set(xlabel="freq [Hz]", ylabel='Amplitude', title='FFT des Originals')
    axs[0, 1].grid(which='major', linestyle='--')
    axs[0, 1].grid(which='minor', linestyle=':')

    axs[1, 0].plot(X2, Y2)
    axs[1, 0].set(xlabel="freq [Hz]", ylabel='|H(f)| [dB]', xscale= "log", title='Amplitudengang HP1')
    axs[1, 0].grid(which='major', linestyle='--')
    axs[1, 0].grid(which='minor', linestyle=':')
    axs[1, 0].axvline(x=fgr, color='darkturquoise', linestyle='-', label='fg')
    axs[1, 0].legend()

    axs[1, 1].plot(X2, phi2)
    axs[1, 1].set(xlabel="freq [Hz]", ylabel='phi(f)', xscale= "log", title='Phasenfrequenzgang HP1')
    axs[1, 1].grid(which='major', linestyle='--')
    axs[1, 1].grid(which='minor', linestyle=':')
    axs[1, 1].axvline(x=fgr, color='darkturquoise', linestyle='-', label='fg')
    axs[1, 1].legend()

    axs[2, 0].plot(X3, Y3)
    axs[2, 0].set(xlabel="freq [Hz]", ylabel='|H(f)| [dB]', xscale= "log", title='Amplitudengang HP2')
    axs[2, 0].grid(which='major', linestyle='--')
    axs[2, 0].grid(which='minor', linestyle=':')
    axs[2, 0].axvline(x=fgr, color='darkturquoise', linestyle='-', label='fg')
    axs[2, 0].legend()

    axs[2, 1].plot(X3, phi3)
    axs[2, 1].set(xlabel="freq [Hz]", ylabel='phi(f)', xscale= "log", title='Phasenfrequenzgang HP2')
    axs[2, 1].grid(which='major', linestyle='--')
    axs[2, 1].grid(which='minor', linestyle=':')
    axs[2, 1].axvline(x=fgr, color='darkturquoise', linestyle='-', label='fg')
    axs[2, 1].legend()

    fig.tight_layout()

"""
::::::::::::::::::::::::::::::::::::::
:::::::::::::::ACTIONS::::::::::::::::
::::::::::::::::::::::::::::::::::::::
"""

"""
0. FIRST SETTINGS
"""
file2 = "Datei_B.wav"
file1 = "CantinaBand3.wav"

fgr = 4000                  #grenzfrequenz in Hz, vorgegeben
Ausgang_HP1 = 'HP1_CantinaBand3.wav'
Ausgang_HP2 = 'HP2_CantinaBand3.wav'

""" 
1. READ FILE, CREATE TIME AXIS AND NAME ALL VARIABLES, DO FFT OF ORIGINAL ARRAY, PLAY ORIGINAL ARRAY
"""
y = readwav(file1)[0]
fs = readwav(file1)[1]

t = xaxis(y, fs)[0]
N = xaxis(y, fs)[1]
delta_T = xaxis(y, fs)[2]
NFFT = xaxis(y, fs)[3]
L = xaxis(y, fs)[4]

F_org = fft(y)[1]
Y_org = fft(y)[0]

print("playing: original file")
play(y, fs)

"""
2. PUT ORIGINAL FILE THROUGH FIRST AND SECOND HP, GET ALPHA, FOR HP1 AND HP2: GET TIME AXIS, WRITE NEW WAV FILE, DO FFT,\
   GET LOGARITHMIC ARRAY, GET PHASE RESPONSE, PLAY BOTH NEW SIGNALS
"""
HP1 = highpass(y)[0]
alpha = highpass(y)[1]
t_HP1 = xaxis(HP1, fs)[0]
write(Ausgang_HP1, fs, HP1)
print("\nplaying: original file after HP1")
play(HP1, fs)

X_HP1 = fft(HP1)[1]
Y_HP1 = fft(HP1)[0]
Y_HP1_log = log(Y_HP1, Y_org)

HP2 = highpass(HP1)[0]
t_HP2 = xaxis(HP2, fs)[0]
write(Ausgang_HP1, fs, HP2)
print("\nplaying: original file after HP2")
play(HP2, fs)

X_HP2 = fft(HP2)[1]
Y_HP2 = fft(HP2)[0]
Y_HP2_log = log(Y_HP2, Y_org)

phi_w_HP1 = phase(X_HP1)
phi_w_HP2 = phase(X_HP2)

"""
3. SET PING PONG DELAY PARAMETERS, CREATE DELAY TRACK LIST, COMPOSE STEREO ARRAY THAT INCLUDES ORIGINAL TRACK AND DELAY,\
   PLAY SIGNAL WITH PING PONG DELAY.
"""
print("\nSet Ping Pong Delay...")
param_delay = generate_param()
delay_shift = param_delay[0]
loop = param_delay[1]

pingpong = generate_input(y, delay_shift)
ping = pingpong[0]
pong = pingpong[1]
final = stereo_delay(ping, pong, y)
print("\nplaying: signal with ping pong delay")
play(final, fs)

"""
4. PLOTS
"""

plot(t, y, F_org, Y_org, phi_w_HP1, X_HP1, Y_HP1_log, phi_w_HP2, X_HP2, Y_HP2_log)
plt.show()

