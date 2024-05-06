import numpy as np
import matplotlib.pyplot as plt

class Signals:
    @staticmethod
    def generate_sinus(amplitude, frequency, length):
        x = np.linspace(0, length, int(length * 44100))
        sine = amplitude * np.sin(2 * np.pi * frequency * x)
        return sine
    @staticmethod
    def generate_noise(amplitude, length):
        noise = np.random.normal(0, amplitude / 4, int(length * 44100))
        return noise

class Calculate:
    @staticmethod
    def total_energie(signal1, signal2):
        signal = signal1 + signal2
        return sum([i ** 2 for i in signal])
    @staticmethod
    def cross_energy(signal1, signal2):
        signal = signal1 + signal2
        return sum(signal) * 2
    @staticmethod
    def correlation_factor(signal1, signal2):
        signal = sum(signal1 * signal2)
        energy1 = sum([i ** 2 for i in signal1])
        energy2 = sum([i ** 2 for i in signal2])
        return signal / np.sqrt(energy1 * energy2)
    @staticmethod
    def n_total_energie(amount, amplitude, frequency, length):
        signals = Signals
        sinus = signals.generate_sinus(amplitude, frequency, length)
        for i in range(amount - 1):
            sinus += signals.generate_sinus(amplitude, frequency, length)
        return sum([i ** 2 for i in sinus])
    @staticmethod
    def n_total_energie_noise(amount, amplitude, length, roll):
        signals = Signals
        noise = signals.generate_noise(amplitude, length)
        for i in range(amount - 1):
            noise += np.roll(noise, roll)
        return sum([i ** 2 for i in noise])
    @staticmethod
    def n_total_energie_sinusn(amount, amplitude, frequency, length, plot):
        signals = Signals
        sinus = np.linspace(0, 0, int(length * 44100))
        for i in range(1, amount + 1):
            sinus += signals.generate_sinus(amplitude * i, frequency, length)
            if plot:
                plt.plot(sinus)
        if plot:
            plt.title("Sinussignale")
            plt.xlabel("Zeit [s]")
            plt.xticks([i * 44100 for i in range(length + 1)], [i for i in range(length + 1)])
            plt.ylabel("Amplitude")
            plt.show()
        return sum([i ** 2 for i in sinus])

if __name__ == "__main__":
    signals = Signals()
    calc = Calculate()
    while True:
        eingabe = input("Welche Funktion des Programmes möchten Sie nutzen?"
                        "\n(a) Zwei gleiche Sinussignale vergleichen."
                        "\n(b) Die Gesamtenergie verschiedener identischer Signale bestimmen."
                        "\n(c) Die Gesamtenergie verschiedener, zueinander verschobener Rausch-Signale bestimmen."
                        "\n(d) Die Gesamtenergie einer zu bestimmenden Anzahl n von Sinussignalen der Form"
                        "\x1B[3m xn(t) = x * sin(n*π*f*t)\x1B[23m bestimmen"
                        "\n(e) Programm beenden"
                        "\nIhre Eingabe: ")
        if eingabe == "a":
            print("Zwei gleiche Sinussignale werden verglichen. "
                  "Bitte geben Sie die gewünschten Parameter an: ")
            try:
                amplitude = int(input("Amplitude: "))
                frequency = int(input("Frequenz: "))
                length = int(input("Länge der Signale: "))
                plot = input("Soll das Signal geplottet werden? (J/N) ")
                sinus = signals.generate_sinus(amplitude, frequency, length)
                print("\033[93mEinzelenergie:      "
                      "{number:.{digits}f} J".format(number=sum([i ** 2 for i in sinus]), digits=3))
                print("Gesamtenergie:      "
                      "{number:.{digits}f} J".format(number=calc.total_energie(sinus, sinus), digits=3))
                print("Kreuzenergie:       "
                      "{number:.{digits}f}".format(number=calc.cross_energy(sinus, sinus), digits=3))
                print("Korrelationsfaktor: "
                      "{number:.{digits}f}".format(number=calc.correlation_factor(sinus, sinus), digits=3))
                if plot == "J" or plot == "Ja" or plot == "j" or plot == "ja" or plot == "1":
                    plt.plot(sinus)
                    plt.title("Sinussignal")
                    plt.xlabel("Zeit [s]")
                    plt.xticks([i * 44100 for i in range(length + 1)], [i for i in range(length + 1)])
                    plt.ylabel("Amplitude")
                    plt.show()
            except:
                print("Es wurde eine ungültige Eingabe getätigt. Bitte versuchen Sie es erneut.")
            print("\033[0m========================================================================")
        elif eingabe == "b":
            print("Es wird die Gesamtenergie verschiedener Sinussignale bestimmt. "
                  "Bitte geben Sie die gewünschten Parameter an: ")
            try:
                amplitude = int(input("Amplitude: "))
                frequency = int(input("Frequenz: "))
                length = int(input("Länge der Signale (in Sekunden): "))
                amount = int(input("Anzahl der Sinussignale: "))
                print("\033[93mGesamtenergie: {number:.{digits}f} J".format(
                    number=calc.n_total_energie(amount, amplitude, frequency, length), digits=3))
            except:
                print("Es wurde eine ungültige Eingabe getätigt. Bitte versuchen Sie es erneut.")
            print("\033[0m========================================================================")
        elif eingabe == "c":
            print("Es wird die Gesamtenergie verschiedener, zueinander verschobener Rausch-Signale bestimmt. "
                  "Bitte geben Sie die gewünschten Parameter an: ")
            try:
                amplitude = int(input("Amplitude: "))
                length = int(input("Länge der Signale (in Sekunden): "))
                amount = int(input("Anzahl der Rauschsignale: "))
                roll = int(input("Um wie viele Samples soll das Rauschen verschoben werden? (Samplerate: 44100): "))
                print("\033[93mGesamtenergie: {number:.{digits}f} J".format(
                    number=calc.n_total_energie_noise(amount, amplitude, length, roll), digits=3))
            except:
                print("Es wurde eine ungültige Eingabe getätigt. Bitte versuchen Sie es erneut.")
            print("\033[0m========================================================================")
        elif eingabe == "d":
            print("Es wird die Gesamtenergie einer zu bestimmenden Anzahl n von Sinussignalen der Form"
                  "\x1B[3m xn(t) = x * sin(n*π*f*t)\x1B[23m bestimmt. "
                  "Bitte geben Sie die gewünschten Parameter an: ")
            try:
                plotVar = False
                amplitude = int(input("Amplitude: "))
                frequency = int(input("Frequenz: "))
                length = int(input("Länge der Signale (in Sekunden): "))
                amount = int(input("Anzahl der Sinussignale: "))
                plot = input("Soll das Signal geplottet werden? (J/N) ")
                if plot == "J" or plot == "Ja" or plot == "j" or plot == "ja" or plot == "1":
                    plotVar = True
                print("\033[93mGesamtenergie: {number:.{digits}f} J".format(
                    number=calc.n_total_energie_sinusn(amount, amplitude, frequency, length, plotVar), digits=3))
            except:
                print("Es wurde eine ungültige Eingabe getätigt. Bitte versuchen Sie es erneut.")
            print("\033[0m========================================================================")
        elif eingabe == "e":
            break
        else:
            print("Ihre Eingabe war ungültig, bitte versuchen Sie es erneut.")