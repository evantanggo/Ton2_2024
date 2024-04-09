import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt

fs = 10000  # Sample rate (samples per second)
freq = 400  # Frequency in Hertz
dauer = 3  # Duration in seconds
amplitude = 1
delta = 1.0 / fs  # Time step

# Numpy magic to calculate the waveform (sine wave)
t = np.arange(0, dauer, delta)
y = np.sin(2 * np.pi * freq * t)

# Play the waveform through sounddevice
print("Sounddevice play")
sd.play(y, fs)
sd.wait()  # Wait for the sound to finish playing

# Plot the waveform
plt.figure(figsize=(8, 4))
plt.plot(t, y, ".", label="sin(x)")
plt.ylim(-1*amplitude, amplitude)
plt.xlim(0, 2/freq)
plt.title("Sine Wave")
plt.xlabel("Time (s)")
plt.ylabel("sin(x)")
plt.grid(True)
plt.legend()
plt.show()