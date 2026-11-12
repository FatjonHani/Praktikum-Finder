# Praktikum-Finder

Ein kleines Python-Skript, das auf **karriere.at** nach Jobs in Österreich sucht und **neue Treffer**
in CSV-Dateien speichert, die du mit Excel öffnen kannst.

Was gesucht wird, legst du in **Profilen** fest. Das sind einfache Textdateien, für die du keine
Programmierkenntnisse brauchst. So kann jeder seine eigene Suche anlegen, zum Beispiel:

- `data-science` – Data-Science-Praktika
- `elektriker-teilqualifikation` – Elektro-Helfer und Monteure, auch ohne vollen Lehrabschluss
- `htl-absolventen` – Stellen, die ausdrücklich HTL-Absolventen suchen

Jobs, die schon gespeichert sind, werden erkannt und **nicht doppelt** eingetragen.
So siehst du bei jedem Start nur, was wirklich neu ist.

---

## Was du brauchst

- **Python 3.11 oder neuer** – prüfen mit `python --version`
  (Download: https://www.python.org/downloads/ – beim Installieren **„Add Python to PATH“** anhaken)
- Eine Internetverbindung
- Sonst nichts – es müssen **keine zusätzlichen Pakete** installiert werden.

## Ordnerstruktur

```
Praktikum-Finder/
├── praktikum_finder.py      Das Skript
├── README.md                Diese Anleitung
├── profile/                 Hier liegen die Suchprofile
│   ├── _vorlage.toml        Vorlage für eigene Profile (wird nicht ausgeführt)
│   ├── data-science.toml
│   ├── elektriker-teilqualifikation.toml
│   └── htl-absolventen.toml
└── ergebnisse/              Wird automatisch angelegt – eine CSV pro Profil
    ├── data-science.csv
    └── ...
```

---

## Anleitung: Skript starten

1. **Terminal öffnen**
   Drücke die `Windows-Taste`, tippe `PowerShell` und drücke `Enter`.

2. **In den Projektordner wechseln** (Pfad ggf. anpassen):
   ```powershell
   cd "$env:USERPROFILE\Praktikum-Finder"
   ```

3. **Profile anzeigen:**
   ```powershell
   python praktikum_finder.py --liste
   ```

4. **Suchen:**

   | Befehl | Was passiert |
   |--------|--------------|
   | `python praktikum_finder.py` | Alle Profile werden ausgeführt |
   | `python praktikum_finder.py data-science` | Nur dieses eine Profil |
   | `python praktikum_finder.py data-science htl-absolventen` | Mehrere bestimmte Profile |

5. **Ergebnis ansehen**
   Die neuen Jobs werden im Terminal mit Link angezeigt. Alle Treffer findest du außerdem in
   `ergebnisse/<profilname>.csv`. Öffnest du die Datei per Doppelklick, zeigt Excel sie an.

> Wenn `python` nicht gefunden wird, versuche es stattdessen mit `py`, also `py praktikum_finder.py`.

---

## Eigenes Profil anlegen

1. Im Ordner `profile/` die Datei `_vorlage.toml` **kopieren** und umbenennen, z. B. in `mein-profil.toml`.
   - Der Dateiname ist gleichzeitig der Profilname und der Name der Ergebnisdatei.
   - Keine Leerzeichen verwenden, und **kein `_` am Anfang**, denn solche Dateien werden ignoriert.
2. Die Datei mit einem Editor öffnen (Rechtsklick → *Öffnen mit* → *Editor*) und die Werte anpassen.
3. Starten mit `python praktikum_finder.py mein-profil`.

### Die Einstellungen

| Einstellung | Bedeutung | Beispiel |
|-------------|-----------|----------|
| `name` | Anzeigename | `"HTL-Absolventen"` |
| `beschreibung` | Kurze Beschreibung (optional) | `"Jobs für HTL-Abgänger"` |
| `suchbegriffe` | Jeder Begriff wird einzeln auf karriere.at gesucht, wie im Suchfeld der Website | `["htl absolvent", "htl"]` |
| `ort` | Ort oder Bundesland; leer = ganz Österreich | `"wien"`, `"graz"`, `"tirol"` |
| `pflicht_woerter` | **Titel oder Kurzbeschreibung** muss mindestens eines enthalten | `["data", "python"]` |
| `titel_woerter` | Der **Jobtitel** muss mindestens eines enthalten (strenger) | `["elektriker", "monteur"]` |
| `ausschluss_woerter` | Kommt eines im **Titel** vor, wird der Job aussortiert | `["senior", "meister"]` |
| `jobart_woerter` | Nur bestimmte Jobarten behalten (Anstellungsart + Titel) | `["praktik", "intern"]` |
| `max_seiten` | Höchstens so viele Ergebnisseiten pro Suchbegriff (ca. 15–20 Jobs pro Seite) | `5` |

**So funktionieren die Wortfilter:**
- Groß- und Kleinschreibung ist egal.
- **Teilwörter zählen**: `"elektr"` passt auf *Elektriker*, *Elektrotechnik*, *Elektromonteur* …
- Wörter mit **bis zu 3 Buchstaben** (z. B. `"htl"`, `"ki"`, `"ml"`) zählen nur als **ganzes Wort**,
  damit `"ki"` nicht in *Ski* oder *Kinder* hängen bleibt.
- Eine leere Liste `[]` schaltet den jeweiligen Filter aus.

**Schreibregeln für TOML-Dateien:** Texte stehen in `"Anführungszeichen"`, Listen in `[eckigen Klammern]`,
und Einträge trennst du mit Kommas. Zeilen, die mit `#` anfangen, sind Kommentare.
Bei einem Tippfehler sagt dir das Skript, in welcher Datei und welcher Zeile er steckt.

### Tipps für gute Profile

- Probiere deine Suchbegriffe zuerst direkt auf karriere.at aus. Liefern sie dort 0 Treffer, bringen sie
  auch im Skript nichts. Zum Beispiel findet „Elektriker Teilqualifikation“ fast nichts,
  „Elektriker Helfer“ oder „Elektriker ohne Lehrabschluss“ dagegen schon.
- Zu viele unpassende Treffer? Ergänze `titel_woerter` oder `ausschluss_woerter`.
- Zu wenige Treffer? Füge mehr `suchbegriffe` hinzu oder lockere die Filter.
- **Von vorne anfangen?** Lösche `ergebnisse/<profilname>.csv`. Beim nächsten Start gelten dann alle Treffer wieder als neu.

---

## Spalten in den CSV-Dateien

| Spalte | Bedeutung |
|--------|-----------|
| `gefunden_am` | Wann das Skript den Job zum ersten Mal gefunden hat |
| `id` | Eindeutige Job-Nummer auf karriere.at |
| `titel` | Stellentitel |
| `firma` | Unternehmen |
| `orte` | Arbeitsort(e) |
| `jobart` | Anstellungsart (Vollzeit, Teilzeit, Praktika, …) |
| `datum` | Veröffentlichungsdatum laut karriere.at |
| `gehalt` | Gehaltsangabe (falls vorhanden) |
| `homeoffice` | `ja` / `nein` |
| `suchbegriff` | Mit welchem Suchbegriff der Job gefunden wurde |
| `link` | Direkter Link zur Stellenanzeige |

Als Trennzeichen dient das Semikolon (`;`). So zeigt ein deutsches Excel die Spalten gleich richtig an.

---

## Projekt von GitHub herunterladen (für Freunde)

1. Auf der GitHub-Seite des Projekts auf **Code → Download ZIP** klicken und die ZIP-Datei entpacken.
   (Oder mit Git: `git clone <link-zum-repository>`)
2. Python 3.11+ installieren (siehe oben).
3. In `profile/` ein eigenes Profil anlegen (siehe „Eigenes Profil anlegen“).
4. Im entpackten Ordner `python praktikum_finder.py <dein-profil>` ausführen.

Der Ordner `ergebnisse/` wird **nicht** auf GitHub hochgeladen (siehe `.gitignore`).
Deine persönlichen Suchergebnisse bleiben also auf deinem Computer.

---

## Automatisch täglich ausführen (optional)

Mit der Windows-**Aufgabenplanung** kann das Skript zum Beispiel jeden Morgen von selbst laufen:

1. `Windows-Taste` drücken und `Aufgabenplanung` öffnen.
2. Rechts auf **Einfache Aufgabe erstellen…** klicken.
3. Name `Praktikum-Finder` eingeben, als Trigger **Täglich** wählen und eine Uhrzeit festlegen.
4. Als Aktion **Programm starten** wählen und eintragen:
   - Programm/Skript: `python`
   - Argumente: `praktikum_finder.py` (oder `praktikum_finder.py data-science` für nur ein Profil)
   - Starten in: der Pfad zum Projektordner, z. B. `C:\Users\<DeinName>\Praktikum-Finder`
5. Auf **Fertig stellen** klicken.

---

## Probleme lösen

| Problem | Lösung |
|---------|--------|
| `python` wird nicht erkannt | Versuche `py praktikum_finder.py`. Wenn das auch nicht geht, Python neu installieren und dabei **„Add Python to PATH“** anhaken. |
| `Dieses Skript braucht Python 3.11 oder neuer` | Neuere Python-Version von python.org installieren. |
| `Tippfehler in '….toml'` | In der genannten Datei und Zeile nach fehlenden `"` oder `,` bzw. offenen `[ ]` suchen. |
| `Unbekannte Einstellung(en)` | Name der Einstellung falsch geschrieben – mit der Tabelle oben vergleichen. |
| `Profil(e) nicht gefunden` | Profilnamen **ohne** `.toml` angeben; `--liste` zeigt alle vorhandenen. |
| `HTTP Error 403/429` | karriere.at blockiert gerade zu viele Anfragen. Später noch einmal versuchen. |
| `KeyError: 'data'` | karriere.at hat seine Seite umgebaut, das Skript muss angepasst werden. |
| Umlaute in Excel kaputt | In Excel **Daten → Aus Text/CSV** wählen, dann Codierung **UTF-8** und Trennzeichen **Semikolon** einstellen. |
| CSV lässt sich nicht speichern | Die Datei ist vermutlich noch in Excel geöffnet. Excel schließen und das Skript neu starten. |

---

## Hinweis

Das Skript ruft die öffentliche Suche von karriere.at ab, genau wie es dein Browser tut, und wartet
zwischen den Anfragen jeweils eine Sekunde. Bitte nutze es nur für die persönliche Jobsuche,
lass es nicht im Sekundentakt laufen und beachte die Nutzungsbedingungen von karriere.at.
