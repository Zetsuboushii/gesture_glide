<p align="center"><br><br><img src="logo.jpg" width="375" height="380"  alt=""/></p>

<h3 align="center">GestureGlide</h3>
<p align="center"><strong><code>gesture_glide</code></strong></p>
<p align="center">
  <img src="https://img.shields.io/maintenance/yes/2024"  alt=""/>
</p>
<p align="center">Software für kamerabasiertes Hand-Tracking zum Steuern diverser Applikationen</p>
<br>

## Mitwirkende

| Mitwirkende  | GitHub                                                                                                                                                                                 | Mitwirkende    | GitHub                                                                                                                                                                                    |
|--------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Luke Grasser | <a href="https://github.com/zetsuboushii"><img src="https://avatars.githubusercontent.com/u/65507051?v=4" width="150px;" alt=""/><br/>[@Zetsuboushii](https://github.com/zetsuboushii) | Isa Barbu      | <a href="https://github.com/isabellabarbu"><img src="https://avatars.githubusercontent.com/u/78431957?v=4" width="150px;" alt=""/><br/>[@IsaBellaBarbu](https://github.com/isabellabarbu) |
| Nick Büttner | <a href="https://github.com/knick21"><img src="https://avatars.githubusercontent.com/u/115408270?v=4" width="150px;" alt=""/><br/>[@Knick21](https://github.com/knick21)               | Miguel Themann | <a href="https://github.com/mithem"><img src="https://avatars.githubusercontent.com/u/41842729?v=4" width="150px;" alt=""/><br/>[@mithem](https://github.com/mithem)                      |

## Benutzerhandbuch

In diesem Abschnitt wird das grundlegende Setup sowie die Bedienelemente der Anwendung erklärt.

### a. Installation

_Zur Ausführung wird eine aktuelle Installation von Python 3 benötigt._

1. Klone das Projekt und führe folgende Befehle aus:

```bash
pip install -r requirements.txt
```

### b. Ausführen der Applikation

1. Starte die Applikation mit:

```bash
python3 entrypoint.py
```

2. Oder baue eine ausführbare Datei für das jeweilige Betriebssystem und führe diese im Projekt-Root aus:

```bash
python -m PyInstaller -F --collect-data mediapipe entrypoint.py
```

### c. Features

Mit der Applikation können anpassbare Gesten verwendet werden, um das bei Dozenten beliebte Glücksrad zu drehen und die
Rouletteflächen der glücklichen Studenten zu vergrößern oder zu verkleinern. Zudem ermöglicht die App das Scrollen in
gängigen IDEs (Microsoft Visual Studio Code, IntelliJ-basierte IDEs), in Chromium- und Mozilla-basierten Programmen und
in Adobe Acrobat durch einfache vertikale Handbewegungen. Außerdem gibt es eine versteckte Überraschungsfunktion.

### d. Nutzung der Software

1. Nach dem Start der Software erscheint eine grafische Benutzeroberfläche, und die Applikation ist einsatzbereit.
2. Im oberen Bereich wird die Ausgabe der angeschlossenen Kamera sichtbar. Wird eine Hand erkannt, erscheinen rote
   Punkte und Linien auf der Hand. Dies zeigt an, dass die Hand erfolgreich erkannt wurde und Gesten sowie Bewegungen
   erkannt werden können.
3. Für das beste Erlebnis wird ein Abstand von circa 1 Meter zwischen Kamera und Hand sowie eine möglichst gerade
   Ausrichtung der Kamera empfohlen.

#### Funktionen der App

Die Funktionen der App sind in zwei Bereiche aufgeteilt: die Gestenerkennung und die Handbewegungserkennung zur
Steuerung des Scrollings.

**Scrolling:**

1. Klicke in das Fenster, in dem du scrollen möchtest.
2. Halte deine Hand mit der Handfläche zur Kamera.
3. Bewege deine Hand in die Richtung, in die du scrollen möchtest, mit einer gewissen Geschwindigkeit (vergleichbar mit
   einem Touchpad).
4. Schließe beim Start der Handbewegung deine Hand leicht und schnell und setze die Bewegung fort.
5. Stelle dir die Bewegung vor, als würdest du einen Vorhang hochziehen oder herunterlassen und das Seil dafür in der
   Hand halten.
6. Öffne am Ende deiner Bewegung erneut deine Hand, als würdest du das Seil loslassen. Achte darauf, dass die Bewegung
   zum Stillstand kommt.
7. Nun kannst du eine erneute Bewegung ausführen und weiter scrollen. Nach Abschluss einer Bewegung dauert es einen
   kurzen Moment, bis du erneut scrollen kannst, um Fehlfunktionen zu vermeiden.
8. Sollte die Erkennung nicht wie gewünscht funktionieren, nutze die Schieberegler im GUI und drücke den Apply-Knopf:
   - ``Speed Threshold``: Stellt ein, wie schnell du deine Hand bewegen musst, damit eine Bewegung erkannt wird.
   - ``Spread Threshold``: Stellt ein, wie schnell und weit du deine Hand schließen musst, damit eine Bewegung erkannt
     wird.
   - ``Scrolling Speed``: Stellt die Geschwindigkeit des Scrollens im angeklickten Fenster ein.

**Glücksrad:**

1. Speichere deine gewünschten Gesten in der App. Nutze dazu das Textfeld ``Gesture Name``, gib einen der folgenden
   Namen ein und halte die Hand mit der gewünschten Geste in die Kamera. Drücke dann den ``Capture``-Knopf, um die Geste
   zu speichern. Starte die App neu, um die Gesten zu aktivieren.
   - ``OpenRoulette``: Zum Wechseln zwischen dem Default- und Roulette-Modus.
   - ``EnlargeRouletteField``: Vergrößert ein Glücksradfeld.
   - ``ReduceRouletteField``: Verkleinert ein Glücksradfeld.
     Um alle gespeicherte Gesten zu löschen, drücke den ``Delete saved gestures``-Knopf.
2. Öffne das Glücksrad. Es muss nicht im Vordergrund sein.
3. Führe deine Geste zum Wechseln ins Glücksrad vor der Kamera aus.
4. Der Modus wechselt von ``DEFAULT`` zu ``ROULETTE``, und das Glücksrad erscheint im Vordergrund.
5. Führe eine Scrollbewegung in beliebiger Richtung aus, um das Glücksrad zu drehen.
6. Nutze die entsprechenden Gesten, um die Felder zu vergrößern oder zu verkleinern.
7. Um wieder zu scrollen, verwende die Geste, mit der du das Glücksrad geöffnet hast. Das vorherige Fenster wird in den
   Vordergrund gebracht, und der Modus wechselt zu ``DEFAULT``.

**Überraschungsfunktion (???):**

1. Speichere eine Geste mit dem Namen ``RR``.
2. Führe die Geste aus und sieh, was passiert.

Du kannst die App jederzeit pausieren und fortsetzen, indem du die entsprechenden Knöpfe drückst. Beende die Applikation
über den Quit-Knopf oder das X am oberen Rand des Fensters.

### Troubleshooting

- Sollten die roten Punkte nicht sichtbar sein oder häufig verschwinden, versuche, den Raum besser auszuleuchten und
  einen stärkeren Kontrast zwischen deiner Hand und dem Hintergrund zu erreichen.
- Wenn das nicht hilft, gehe etwas näher an die Kamera, bis die Punkte stabil auf deiner Hand erscheinen.

GestureGlide © Isa Barbu, Nick Büttner, Luke Grasser, Miguel Themann 2024
