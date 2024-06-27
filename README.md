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

## Userguide

Im Folgenden wird das grundlegende Setup, sowie die Bedienelemente der Anwendung erklärt.

### a. Installation

_Zum Ausführen wird eine aktuelle Installation von Python 3 benötigt._

Zu Beginn das Projekt klonen und folgende Befehle ausführen:

```bash
pip install -r requirements.txt
```

### b. Ausführen der Applikation

```bash
python3 entrypoint.py
```

### c. Features
Durch die App ist es möglich, mit selbst festgelegten Gesten, das von Dozenten geliebte Glücksrad zu drehen,
personen zu vergrößern und zu verkleinern. Darüber hinaus kann in einem beliebigen Fenster gescrolled werden und das über 
einfache Handbewegungen. Zu guter Letzt liegt auch eine kleine Überraschung vor, die es mit einer Handgeste 
zu entdecken gilt...

### d. Nutzung der Software

1. Nach dem Starten der Software ist eine grafische Benutzeroberfläche zu sehen und das Programm ist einsatzbereit
2. Im oberen Bereich ist die Ausgabe der angeschlossenen Kamera sichtbar, wird eine Hand erkannt, so werden rote Punkte 
   und Linien auf der Hand/Hände sichtbar. Dies bedeutet, dass die Hand/ Hände erfolgreich erkannt wurde und nun Gesten und 
   Bewegungen erkannt werden können.
3. Für das beste Erlebnis empfehlen wir einen Abstand zwischen Kamera und Hand von ca. 1 Meter und eine möglichst gerade
   Ausrichtung von der Kamera zum Bereich in denen du deine Gesten vollziehen möchtest.
4. Die Funktionen der App teilt sich in zwei Bereiche auf, der Gestenerkennung und der Handbewegungserkennung durch das 
   das Scrooling gesteuert wird
   - Scrolling:
     1. **Klicke in das Fenster in dem du Scrollen möchtest**
     2. Halte deine Hand mit der Handfläche zur Kamera hin
     3. Bewegen deine Hand in die Richtung in die du scrollen möchtest mit einem gewissen Maß an Geschwindigkeit* (die Ausrichtung ist mit einem Touchpad zu vergleichen)
     4. Wenn du anfängst deine Hand zu bewegen, dann schließe diese leicht und schnell und setzte dabei deine Bewegung fort
     5. Stelle dir diese Bewegung vor, als würdest du einen Vorhang hochziehen oder runter lassen und du hälst das Seil dafür in der Hand.
     6. Am Ende deiner Bewegung öffne erneut deine Hand (als würdest du das Seil loslassen), achte darauf, dass eine Bewegung wirklich zum Stillstand kommt.
     7. Nun kannst du eine erneute Bewegung ausführen und weiter scrollen (nach Abschluss einer Bewegung, dauert es einen kurzen Moment
        bis du erneut scrollen kannst, damit es zu keinen Fehlerkennung kommt, wenn du nur deine Hand wieder ablegen möchtest)
     8. Sollte die Erkennung nicht so laufen wie gewünscht, dann nutzte die Slider im GUI
        - Speed Threshold stellt ein wie schnell du deine Handbewegen musst, damit eine Bewegung erkannt wird
        - Spread Threshold stellt ein wie schnell und weit du deine Hand zu machen musst, damit eine Bewegung erkannt wird
        - Scrolling Speed stellt die Geschwindigkeit des Scrollens in deinem angeklickten Fenster ein 
   - Glücksrad:
     1. 
   - ??? (RR):

5. Die App kannst du jederzeit pausieren und wieder fortsetzen lassen in dem du die zugehörigen Knöpfe drückst
6. Beenden kannst du die App über den Quit-Knopf oder über das X am oberen Rand des Fensters

Troubleshooting:
- Sollten diese Punkte nicht sichtbar sein oder häufig bei Bewegungen verloren gehen,
   Dann versuche den Raum in dem du dich befindest mehr auszuleuchten und einen stärkeren Kontrast zwischen deiner Hand und
   dem Hintergrund zu erreichen.
- Sollte das auch nicht helfen oder gerade nicht möglich sein, so versuche etwas näher an die Kamera zu gehen, bis die
   Punkte besser auf deiner Hand erscheinen und bleiben.


GestureGlide © Isa Barbu, Nick Büttner, Luke Grasser, Miguel Themann 2024
