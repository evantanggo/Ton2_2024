# Ton2_2024
Fallstudie Ton2 SS24

# PP1
Die Raum-Impulsantwort (Room Impulse Response, RIR) ergibt sich aus der Antwort eines Raums auf die Anregung mit
einem MLS-Signal oder einem Sinus-Sweep, wenn das Signal mit einem Mikrofon mit Kugelcharakteristik (Mono)
aufgenommen wird. Ihrer Gruppe wurde eine Raum-Impulsantwort im .wav-Format zugelost.

Berechnen Sie den Amplitudenfrequenzgang und das Spektrogramm der Impulsantwort.

Ermitteln Sie so genau wie möglich die Nachhallzeit4 des Raums. Hierzu berechnen Sie den zeitabhängigen Energieabfall
der Impulsantwort.

Berechnen Sie aus der Impulsantwort das Deutlichkeitsmaß C50 und das Klarheitsmaß C80.

Verschaffen Sie sich durch Auralisation (Faltung der Impulsantwort mit einem trockenen Signal) einen Höreindruck zum
Klang von Sprache und Musik in dem Raum.

Nutzen Sie Ihre Analysen und Berechnungen zur Beurteilung des Raums.


# PP2

A. Untersuchen Sie systematisch die Lokalisation einer Phantomschallquelle auf der Horizontalebene um den Kopf herum
bei Stereo-Wiedergabe. Setzen Sie für die Untersuchung des Pannings 
1.) sinnvoll gewählte Pegeldifferenzen8 und 
2.) sinnvoll gewählte Laufzeitdifferenzen ein.

Orientieren Sie sich dabei an den Werten aus Abb. Anlage PP2-1 sowie aus den Werten der Abb.en PP2-3 und
PP2-4 (sh. Anlage, folgende Seite), um zu überprüfen, ob diese für Ihre Abhörsituation gelten.
Nutzen Sie Python, um diese Untersuchung durchzuführen.

B. Wählen Sie aus der Projektsammlung https://www.cambridge-mt.com/ms/mtk/ vier bis sechs geeignete Spuren eines
Multitrack-Projekts aus. Setzen Sie die beiden Panning-Verfahren getrennt ein, um mit Ihrem eigenen Python-Code und den
von Ihnen implementierten Panning-Verfahren (Aufgabenteil A.) jeweils eine gelungene Stereomischung zu erstellen. Die
Dauer der Mischung soll zwischen 15 und 25 Sekunden liegen. Wählen Sie dafür eine geeignete Stelle des Songs
aus.
Vergleichen Sie die Ergebnisse der beiden Mischungen.

C. Gegeben sind Binaurale Raumimpulsantworten9 (BRIR) für mehrere Winkel auf der Horizontal-Ebene um den Kopf
herum. Setzen Sie diese zum binauralen Panning /Auralisation10 ein.

D. Vergleichen und beurteilen Sie die Verfahren und die Ergebnisse von B. (Stereo-Panning durch Laufzeit- oder
Pegeldifferenz) und C. (binaurales Panning).

# PP3

Audio-Effekt 1: Filter
Realisieren Sie das Filter wie im Anhang zu PP3 vorgegeben im Zeitbereich, durch Rückkopplung des Ausgangssignals. Sie
können hierzu den zur Verfügung gestellten Code verwenden, die Basis dafür ist im Anhang zu Praxisproblem 3 dargestellt,
Herleitung sh. „TON2 RC Hochpass [Tiefpass] Herleitung.pdf“.
Kombinieren Sie zwei Filter zu dem Ihnen vorgegebenen Filter.
Ermitteln Sie für das realisierte Filter die Impulsantwort oder die komplexe Übertragungsfunktion (als Amplitudenfrequenzgang
und Phasenfrequenzgang) und stellen Sie sie grafisch dar. Weisen Sie nach, dass die vorgegebenen Eigenschaften
eingehalten werden.

Audio-Effekt 2: Delay-Effekt
Realisieren Sie den vorgegebenen Delay-Effekt, und experimentieren Sie mit verschiedenen Einstellungen. Weisen Sie
nach, dass die zu erwartenden Eigenschaften eingehalten werden.
Wenden Sie die Effekte auf geeignete Testsignale an, und beurteilen Sie die Klangveränderungen.
