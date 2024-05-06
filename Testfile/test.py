import numpy as np
from scipy.integrate import quad

def aufgabe_4():  # Orthogonalität der Sinusschwingungen
    def f1(x, f):
        return np.sin(2 * np.pi * f * x)

    def f2(x, f):
        return np.sin(2 * np.pi * 1*f * x)  # Hier ist f2 = 2 * f1

    def integrand(x, f):
        return f1(x, f) * f2(x, f) 

    result, error = quad(integrand, 0, 2, args=(1.0,))

    # Runden auf Null, wenn das Ergebnis sehr nah an Null liegt
    if abs(result) < 1e-10:
        result = 0

    print("\n")
    print("Aufgabe 4 (Orthogonalität)")
    print(f"Summe des Integrals von beiden Schwingungen ist: {result}")

aufgabe_4()
