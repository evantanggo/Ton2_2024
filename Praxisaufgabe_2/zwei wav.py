import numpy as np
from scipy.io.wavfile import read
from scipy.signal import correlate, resample

def calculate_energy(signal):
    return np.sum(np.square(signal))

def calculate_total_energy(signal1, signal2):
    return calculate_energy(signal1) + calculate_energy(signal2)

def calculate_correlation_factor(signal1, signal2):
    correlation = correlate(signal1, signal2, mode='full')
    max_correlation = np.max(correlation)
    energy_product = calculate_energy(signal1) * calculate_energy(signal2)
    return max_correlation / np.sqrt(energy_product)

def main():
    file1 = '21_Piano2.wav'  # Pfad zu Ihrer ersten WAV-Datei
    file2 = '45_VoxSFX4.wav'  # Pfad zu Ihrer zweiten WAV-Datei

    fs1, signal1 = read(file1)
    fs2, signal2 = read(file2)

    # Wenn die Abtastraten unterschiedlich sind, angleichen
    if fs1 != fs2:
        min_fs = min(fs1, fs2)
        signal1 = resample(signal1, int(len(signal1) * min_fs / fs1))
        signal2 = resample(signal2, int(len(signal2) * min_fs / fs2))

    individual_energy1 = calculate_energy(signal1)
    individual_energy2 = calculate_energy(signal2)
    total_energy = calculate_total_energy(signal1, signal2)
    correlation_factor = calculate_correlation_factor(signal1, signal2)

    print(f'Individual Energy 1: {individual_energy1}')
    print(f'Individual Energy 2: {individual_energy2}')
    print(f'Total Energy: {total_energy}')
    print(f'Correlation Factor: {correlation_factor}')

if __name__ == "__main__":
    main()
