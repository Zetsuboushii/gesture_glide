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
     8. Sollte die Erkennung nicht so laufen wie gewünscht, dann nutzte die Slider im GUI und drücke wenn du alles eingestellt hast auf den Apply-Knopf
        - Speed Threshold stellt ein wie schnell du deine Handbewegen musst, damit eine Bewegung erkannt wird
        - Spread Threshold stellt ein wie schnell und weit du deine Hand zu machen musst, damit eine Bewegung erkannt wird
        - Scrolling Speed stellt die Geschwindigkeit des Scrollens in deinem angeklickten Fenster ein 
   - Glücksrad:
     1.  Speichere deine gewünschten Gesten in der App ab, benutzte dazu das Textfeld namens "Gesture Name" und gib einen 
         der folgenden Befehle ein und halte deine Hand mit der gewünschten Geste in die Kamera, drücke darauf hin den Capture-Knopf
         damit die Geste für den Befehl gespeichert wird. Wenn du alles eingespeichert hast, starte die App neu und deine
         Gesten sind nun einsatz bereit (Hinweis: nehme zum Speichern der Gesten die Distanz zur Kamera ein, die du auch wirklich haben wirst, wenn du sie ausführen möchtest).
         - OpenRoulette, zum Wechseln zwischen dem Default (Scrolling) und Roulette Mode ein, wobei zum Glücksrad oder zur
         zuletzt geöffneten Fenster gesprungen wird
         - EnlargeRouletteField um ein Glücksradfeld zu vergrößern
         - ReduceRouletteField um ein Glücksradfeld zu verkleinern
     2. Habe die Glücksradapp geöffnet, du musst sie aber nicht angeklickt haben
     3. Führe nun deine Geste zum Wechseln ins Glücksrad vor der Kamera vor
     4. Daraufhin ändert der Modus sich von DEFAULT zu ROULETTE und das Glücksrad ist nun im Vordergrund
     5. Führe eine Scrollbewegung in egal welcher Richtung aus, um das Glücksrad zu drehen
     6. Wenn der Ball auf einem Segment liegt, dann kannst du deine entsprechenden Gesten zum Vergrößern oder Verkleinern der Felder verwenden
     7. Wenn du wieder Scrollen möchtest, dann verwende wieder die Geste, mit der du das Glücksrad geöffnet hast, dann 
        wird das vorherige Fenster vor dem Öffnen des Roulettes in den Vordergrund gebracht und der Modus ändert sich zu DEFAULT
     8. Du kannst auch mehrere Gesten für einen Befehl speichern, solltest du sie löschen wollen, dann drücke auf den Delete saved gestures Knopf
        und alle gespeicherten Gesten werden gelöscht. Starte darauf hin die App erneut, um neue Gesten einzuspeichern
   - ???:
     1. Wie im Glücksrad beschrieben, speichere eine weitere Geste mit dem Namen RR ein
     2. Führe sie durch und schau was passiert :^)

5. Die App kannst du jederzeit pausieren und wieder fortsetzen lassen in dem du die zugehörigen Knöpfe drückst
6. Beenden kannst du die App über den Quit-Knopf oder über das X am oberen Rand des Fensters

Troubleshooting:
- Sollten diese Punkte nicht sichtbar sein oder häufig bei Bewegungen verloren gehen,
   Dann versuche den Raum in dem du dich befindest mehr auszuleuchten und einen stärkeren Kontrast zwischen deiner Hand und
   dem Hintergrund zu erreichen.
- Sollte das auch nicht helfen oder gerade nicht möglich sein, so versuche etwas näher an die Kamera zu gehen, bis die
   Punkte besser auf deiner Hand erscheinen und bleiben.


GestureGlide © Isa Barbu, Nick Büttner, Luke Grasser, Miguel Themann 2024
