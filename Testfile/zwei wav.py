def file1():
    file = '../Praxisaufgabe_2/21_Piano2.wav'  # um file zu ändern Dateinamen anpassen
    (Fs, y) = read(file)  # Fs = 44100Hz

    if y.ndim == 2:  # überprüft, ob die Datei Stereo oder Mono ist und rechnet sie in Mono um
        y_L = y[:, 0]
        y_R = y[:, 1]
        dataMono = (y_L + y_R) / 2
    else:
        dataMono = y

    return dataMono


def file2():
    file = '../Praxisaufgabe_2/45_VoxSFX4.wav'  # um file zu ändern Dateinamen anpassen
    (Fs, y) = read(file)  # Fs = 44100Hz

    if y.ndim == 2:  # überprüft, ob die Datei Stereo oder Mono ist und rechnet sie in Mono um
        y_L = y[:, 0]
        y_R = y[:, 1]
        dataMono1 = (y_L + y_R) / 2
    else:
        dataMono1 = y

    return dataMono1


def calculate_energy(signal):
    signal = signal.astype(np.float64)
    square = np.square(signal)  # quadrieren
    integral = sum(square)  # summiert alle Werte des Arrays

    return integral


def calculate_total_energy(signal1, signal2):
    return calculate_energy(signal1) + calculate_energy(signal2)


def calculate_correlation_factor(signal1, signal2):
    correlation = correlate(signal1, signal2, mode='full')
    max_correlation = np.max(correlation)
    energy_product = calculate_energy(signal1) * calculate_energy(signal2)
    return max_correlation / np.sqrt(energy_product)


individual_energy1 = calculate_energy(file1())
individual_energy2 = calculate_energy(file2())
total_energy = calculate_total_energy(file1(), file2())
correlation_factor = calculate_correlation_factor(file1(), file2())

print("\n")
print("Aufgabe 5")
print(f'Individual Energy 1: {individual_energy1}')
print(f'Individual Energy 2: {individual_energy2}')
print(f'Total Energy: {total_energy}')
print(f'Correlation Factor: {correlation_factor}')