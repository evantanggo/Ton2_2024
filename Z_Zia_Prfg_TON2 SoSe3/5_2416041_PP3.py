''' PP3 - Verzerrung und Delay Effekt
Gruppe 5
Zia Asmara (2416041) '''
import numpy as np
import soundfile as sf
import sounddevice as sd
import matplotlib.pyplot as plt

# System A: Verzerrung durch tanh(x)-Funktion
# Aufgabe 1: tanh Funktion
def tanh_verzerrung(input_signal, gain, m, x_AP):
    input_signal /= gain  # Eingangssignal normalisieren (auskommentiert, da es bereits eine Zeile später geladen wird)
    input_signal, sample_rate = sf.read(input_file)  # Eingangs-Audiodatei laden und einlesen
    input_signal = input_signal / np.max(np.abs(input_signal))  # Eingangssignal normalisieren auf [-1, 1]
    output_signal = np.tanh(m * input_signal)  # Verzerrung anwenden (tanh-Funktion)
    output_signal *= x_AP  # Skaliere Ausgangssignal zum Arbeitspunkt
    return output_signal / np.max(np.abs(output_signal))  # Ausgangssignal normalisieren

# Aufgabe 2: Anpassen der Verzerrungsparameter
m = 0.5  # Steigung der tanh-Funktion
x_AP = 0.7  # Arbeitspunkt auf der Kennlinie
y_AP = round(np.tanh(m * x_AP), 2)  # y-Wert am Arbeitspunkt (für Aufgabe A.3)

# Anzeigen der berechneten Parameter
print(f"\n*** SYSTEM A - VERZERRUNG DURCH TANH(X)-FUNKTION ***")
print(f"\n*** Berechnete Werte von System A (Aufgabe A.1 -A.3) ***")
print(f"Steigung: {m}, Arbeitspunkt x-Achse: {x_AP}, Arbeitspunkt y-Achse: {y_AP}")

# Funktion zum Testen verschiedener Audiosignale
def testSignale():
    print("\nVorhandene Audiodateien:")
    print("1. Sinus 1kHz")
    print("2. Sprache")
    print("3. Klavier")
    print("Achtung! Zur Bestimmung des Klirrfaktors und THD, wählen Sie bitte nur 1.")

    choice = int(input("Bitte eine Audiodatei auswählen (1-3): "))

    if choice == 1:
        input_signal = "sinus_1kHz Kopie.wav"
    elif choice == 2:
        input_signal = "Sprache_mono.wav"
    elif choice == 3:
        input_signal = "Klavier_mono.wav"
    else:
        print("Falsche Eingabe...")
        return None
    return input_signal

# Aufrufen der Funktion zur Auswahl einer Audiodatei
input_file = testSignale()

# Einlesen und Normalisieren der Eingangs-Audiodatei
input_signal, sample_rate = sf.read(input_file)
input_signal = input_signal / np.max(np.abs(input_signal))

# Aufgabe 3: Verstärkung und Klirrfaktor von Sinussignal 1kHz berechnen
gain = m * (1 - np.tanh(m * x_AP) ** 2)  # Verstärkung des Eingangssignals
print(f"\nDie Verstärkung: {round(gain, 2)} dB")

# Anwenden der Verzerrung auf das Eingangssignal
output_signal = tanh_verzerrung(input_signal, gain, m, x_AP)

# Speichern des verzerrten Signals in einer Ausgabedatei
output_file = "output.wav"
sf.write(output_file, output_signal, sample_rate)

# FFT Eingang und Ausgangssignal
fft_input = np.fft.fft(input_signal)  # FFT des Eingangssignals
Freq_input = np.fft.fftfreq(len(input_signal), 1 / sample_rate)  # Erzeugung der Frequenzachsen

fft_output = np.fft.fft(output_signal)  # FFT des bearbeiteten Signals
Freq_output = np.fft.fftfreq(len(output_signal), 1 / sample_rate)

# Berechnung des Klirrfaktors und THD-Werts
f1 = abs(fft_output[2000])  # Wert der FFT bei 1 kHz
f2 = abs(fft_output[4000])  # Wert der FFT bei 2 kHz (1. Harmonische)
f3 = abs(fft_output[6000])  # Wert der FFT bei 3 kHz (2. Harmonische)

kl = np.round(100 * (np.sqrt((f2**2 + f3**2) / (f1**2 + f2**2 + f3**2))), 2)  # Klirrfaktor berechnen
THD = np.round((100 * (np.sqrt((f2**2 + f3**2) / (f1**2)))), 2)  # THD-Wert berechnen

# Ausgabe der Ergebnisse
print(f"Der Klirrfaktor: {kl}%")
print(f"Der THD-Wert: {THD}%")

# Plotten der Signale und der FFT
fig, axs = plt.subplots(2, 2, figsize=(10, 10))
fig.suptitle('System A: Verzerrung durch tanh(x)-Funktion', fontsize=20, color="green")

# Originales Signal
zeit = np.arange(len(input_signal)) / sample_rate
axs[0, 0].plot(zeit, input_signal, color="blue")
axs[0, 0].set_title("Eingangssignal")
axs[0, 0].grid()
axs[0, 0].set_xlabel("Zeit [s]")
axs[0, 0].set_ylabel("Signalwert")

# Bearbeitetes Signal
zeit = np.arange(0, len(output_signal)/sample_rate, 1/sample_rate)
axs[1, 0].plot(zeit, output_signal, color="orange")
axs[1, 0].set_title("Ausgangssignal")
axs[1, 0].grid()
axs[1, 0].set_xlabel("Zeit [s]")
axs[1, 0].set_ylabel("Signalwert")

# Arbeitspunkt bei tanh(x) Kennlinie
x = np.linspace(-10, 10, 1000)
y = np.tanh(m * x)
axs[1, 1].plot(x, y, label="tanh(x)")  # nichtlineare Kennlinie mit gewähltem Parameter
axs[1, 1].plot(x_AP, np.tanh(m * x_AP), "o", label="Arbeitspunkt")  # festgelegter Arbeitspunkt im fastlinearen Bereich
axs[1, 1].set_title("Kennlinie eines fastlinearen Systems tanh(x)")
axs[1, 1].grid()
axs[1, 1].set_ylabel("Eingangswerte")
axs[1, 1].set_xlabel("Ausgangswerte")

# Plot der FFTs
axs[0, 1].plot(Freq_input, np.abs(fft_input), color="blue")
axs[0, 1].set_title(f"FFT bei Steigung: {m}, Arbeitspunkt: {x_AP}")
axs[0, 1].set_xlabel("Frequenz [Hz]")
axs[0, 1].set_ylabel("Amplitude")
axs[0, 1].plot(Freq_output, np.abs(fft_output), color="orange")
axs[0, 1].grid()
axs[0, 1].set_xlabel("Frequenz [Hz]")
axs[0, 1].set_ylabel("Amplitude")

plt.tight_layout()
plt.show()

# Signale abspielen
abspielen = input("\nDas originale Signal und das verzerrte Signal abhören? ja oder nein -> j/n: ")
if abspielen == "j":
    # Input signal abspielen
    print("Eingangssignal wird abgespielt...")
    sd.play(input_signal, sample_rate)
    sd.wait(2)

    print("Verzerrtes Signal wird abgespielt...")
    sd.play(output_signal, sample_rate)
    sd.wait()

else:
    print("OK")

'''def repeat():
    while True:  # Loop
       testSignale()
       print("Möchten Sie das System A nochmal durchführen?  j/n: ") == 'j'
       if not repeat():
           return  # System B durchführen

repeat()'''

# Aufgabe A.4: Testsignale Klavier und Sprache
print("\n*** Testsignale (Klavier, Stimme) durch das System A schicken (Aufgabe A.4 - A.5) ***")

def testSignale():
    print("\nVorhandene Audiodateien:")
    print("1. Sinus 1kHz")
    print("2. Sprache")
    print("3. Klavier")
    print("Achtung! Zur Bestimmung des Klirrfaktors und THD, wählen Sie nur bitte 1.)")

    choice = int(input("Bitte ein Audiodatei auswählen (1-3): "))

    if choice == 1:
        input_signal = "sinus_1kHz Kopie.wav"
    elif choice == 2:
        input_signal = "Sprache_mono.wav"
    elif choice == 3:
        input_signal = "Klavier_mono.wav"
    else:
        print("Invalid choice. Exiting...")
        return None
    return input_signal

# Laden der Eingangs-Audiodatei
input_file = testSignale()
if input_file is None:
    exit()

input_signal, fs1 = sf.read(input_file)
output_signal = tanh_verzerrung(input_signal, gain, m, x_AP)

# Speichern des verzerrten Signals in einer Ausgabedatei
output_file = "output_test.wav"
sf.write(output_file, output_signal, fs1)

abspielen = input("\nDas originale Signal und das verzerrte Testsignal abhören? ja oder nein -> j/n: ")
if abspielen == "j":
    # Input signal abspielen
    print("Eingangssignal wird abgespielt...")
    sd.play(input_signal, fs1)
    sd.wait(2)

    print("Verzerrtes Signal wird abgespielt...")
    sd.play(output_signal, fs1)
    sd.wait()

else:
    print("OK")

'''
# Aufgabe 5: Experiment mit unterschidliche Steigungswerte und Arbeitspunkte
m_ex = [0.1, 2] # Verschiedene Steigungswerte der tanh-Funktion
AP_ex= [0.5, 0.9] # Verschiedene Arbeitspunkte auf der Kennlinie

print(f"\nBei Aufgabe A.5 werden 4 experimentale Signale durchgesucht.")
# Durch alle Parameterkombinationen iterieren und Verzerrungseffekte anwenden
for i, steigung in enumerate(m_ex):
    for j, arbeitspunkte in enumerate(AP_ex):
        # Verstärkung und Klirrfaktor berechnen
        gain_ex = steigung * (1 - np.tanh(steigung * arbeitspunkte) ** 2)
        print(f"- Bei Steigung: {steigung} und Arbeitspunkt: {arbeitspunkte}")
        print(f"- Verstärkung: {round(gain_ex, 2)} dB")

        # Verzerrung anwenden
        verzerrtes_signal = tanh_verzerrung(input_signal, gain_ex, steigung, arbeitspunkte)

        # FFT des verzerrten Signals berechnen
        fft_distorted = np.fft.fft(verzerrtes_signal)
        freq_distorted = np.fft.fftfreq(len(verzerrtes_signal), 1 / sample_rate)

        # FFT-Plot des verzerrten Signals
        plt.subplot(len(m_ex), len(AP_ex), i * len(AP_ex) + j + 1)
        plt.plot(freq_distorted, np.abs(fft_distorted))
        plt.title(f"Steigung: {steigung}, Arbeitspunkt: {arbeitspunkte}")
        plt.xlabel("Frequenz [Hz]")
        plt.ylabel("Amplitude")
        plt.grid()

        # Signal wiedergeben
        abspielen = input("Experimentales Signal abspielen -> j/n: ")
        if abspielen == "j":
            # Input signal abspielen
            print("Experimentsignal wird abgespielt...")
            sd.play(verzerrtes_signal, sample_rate)
            sd.wait()
        else:
            print("OK")

plt.tight_layout()
plt.show()

print("\n*** Ende System A ***\n")'''

'''System B = Echo und Reverse Echo'''

print("\n*** SYSTEM B - ECHO UND REVERSE ECHO ***")
print("In diesem System wird das Eingangssignal mit Delay-Effekt abgespielt\n")

# Funktion zur Anwendung des Echo-Effekts auf das Eingangssignal
def echo(input_signal_effekt, delay, decay):
    output_signal_effekt = np.zeros_like(input_signal_effekt) # ein Ausgangssignal-Array mit der gleichen Größe wie das Eingangssignal erstellen
    for i in range(len(input_signal_effekt)):
        if i < delay:
            output_signal_effekt[i] = input_signal_effekt[i]
        else:
            output_signal_effekt[i] = input_signal_effekt[i] + decay * output_signal_effekt[i - delay]
    return output_signal_effekt

# Funktion zur Anwendung des Reverse Echo-Effekts auf das Eingangssignal
def reverse_echo(input_signal_effekt, delay, decay):
    output_signal_effekt = np.zeros_like(input_signal_effekt)
    reversed_signal = np.flip(input_signal_effekt) # reverse input signal
    reversed_echo = echo(reversed_signal, delay, decay)
    output_signal_effekt = np.flip(reversed_echo) # das resultierende Signal erneut umkehren, um den RE-Effekt zu erhalten
    return output_signal_effekt

def audioDateien():
    print("Vorhandene Audiodateien:")
    print("1. Ausgangssignal von System 1")
    print("2. Sprache")
    print("3. Klavier")

    choice = int(input("Bitte ein Audiodatei auswählen (1-3): "))

    if choice == 1:
        input_file = "output.wav"
    elif choice == 2:
        input_file = "Sprache_mono.wav"
    elif choice == 3:
        input_file = "Klavier_mono.wav"
    else:
        print("Auswahl nicht vorhanden.")
        return None

    return input_file

# Laden der Eingangs-Audiodatei
input_file_effekt = audioDateien()
if input_file_effekt is None:
    exit()

input_signal_effekt, fs = sf.read(input_file_effekt)

# Festlegen der Parameter für den Echo-Effekt
echo_delay = int(fs * 0.5)  # Verzögerung in Samples (in Sekunden)
echo_decay = 0.5  # Abschwächungsfaktor

# Anwendung des Echo-Effekts auf das Eingangssignal
echo_signal = echo(input_signal_effekt, echo_delay, echo_decay)

# Festlegen der Parameter für den Reverse Echo-Effekt
reverse_delay = int(fs * 0.5)  # Verzögerung in Samples (in Sekunden)
reverse_decay = 0.3  # Abschwächungsfaktor

# Anwendung des Reverse Echo-Effekts auf das Eingangssignal
reverse_echo_signal = reverse_echo(input_signal_effekt, reverse_delay, reverse_decay)

# Speichern der Ausgangssignale als Audiodateien
sf.write("echo_output.wav", echo_signal, fs)
sf.write("reverse_echo_output.wav", reverse_echo_signal, fs)

# Abspielen des Eingangssignals, des Echo-Signals und des Reverse Echo-Signals
abspielen = input("\nDelay Effekt Abspielen -> j/n: ")
if abspielen == "j":
    print("- Spiele das Eingangssignal ab...")
    sd.play(input_signal_effekt, fs)
    sd.wait()

    print("- Spiele das Echo-Signal ab...")
    sd.play(echo_signal, fs)
    sd.wait()

    print("- Spiele das Reverse Echo-Signal ab...")
    sd.play(reverse_echo_signal, fs)
    sd.wait()
else:
    print("Program zu Ende")