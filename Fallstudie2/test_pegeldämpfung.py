import numpy as np
import matplotlib.pyplot as plt

x_values = np.linspace(1, 10, 100)  # 100 Punkte im Bereich von 1 bis 10
y_values = []

for i in x_values:
    y_values.append(10 * np.log10(i))

# Konvertieren der Liste in ein numpy-Array für die Verwendung mit matplotlib
y_values = np.array(y_values)


#Dämpfung 
tracks = 6
daempfung = 10 * np.log10(1/tracks)
print(f"Pegeldämpfung um {daempfung:.2f}" )

plt.figure()
plt.plot(x_values, y_values)
plt.xlabel('x')
plt.ylabel('10 * log10(x)')
plt.title('Plot of 10 * log10(x)')
plt.grid(True)
plt.show()



