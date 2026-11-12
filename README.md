# Praktikum-Finder

Sucht automatisch auf **karriere.at** nach Jobs in Österreich und speichert **neue Treffer** in einer Liste, die du mit Excel öffnest. Was gesucht wird, legst du in einem **Profil** fest – eine einfache Textdatei, ganz ohne Programmierkenntnisse.

```mermaid
flowchart LR
    A["Dein Profil<br/>(was du suchst)"] --> B["Suche auf<br/>karriere.at"]
    B --> C["Filter<br/>(passt / passt nicht)"]
    C --> D["Nur neue Jobs"]
    D --> E["Excel-Liste<br/>im Ordner ergebnisse"]
```

Jobs, die schon in deiner Liste stehen, werden erkannt und **nicht doppelt** eingetragen. Bei jedem Start siehst du also nur, was wirklich neu ist.

---

## Schnellstart in 5 Minuten

**1. Python installieren** (einmalig)
Auf [python.org/downloads](https://www.python.org/downloads/) die aktuelle Version herunterladen. Beim Installieren unbedingt **„Add Python to PATH"** anhaken. Version 3.11 oder neuer wird gebraucht, sonst nichts.

**2. Projekt herunterladen**
Oben auf dieser Seite auf den grünen Button **Code → Download ZIP** klicken und die ZIP-Datei entpacken – egal wohin, z. B. in *Dokumente*.

**3. Terminal im Projektordner öffnen**
Den entpackten Ordner im Explorer öffnen (du siehst darin `praktikum_finder.py`). Oben in die **Adressleiste** klicken, `powershell` eintippen und Enter drücken. Es öffnet sich ein Terminal, das schon im richtigen Ordner ist.

**4. Suchen**

```powershell
python praktikum_finder.py --liste
```
zeigt alle Profile. Dann eins starten, zum Beispiel:

```powershell
python praktikum_finder.py data-science
```

**5. Ergebnis ansehen**
Die neuen Jobs stehen mit Link im Terminal. Alle Treffer findest du zusätzlich in `ergebnisse\<profilname>.csv` – Doppelklick öffnet sie in Excel.

> Wird `python` nicht erkannt, probier `py` statt `python`.

---

## Suchbefehle

| Befehl | Was passiert |
|---|---|
| `python praktikum_finder.py --liste` | Alle vorhandenen Profile anzeigen |
| `python praktikum_finder.py data-science` | Nur dieses eine Profil |
| `python praktikum_finder.py data-science htl-absolventen` | Mehrere Profile |
| `python praktikum_finder.py` | Alle Profile |

Mitgelieferte Beispielprofile:

| Profil | Sucht nach |
|---|---|
| `data-science` | Praktika in Data Science, Data Analytics und Machine Learning |
| `elektriker-teilqualifikation` | Elektro-Helfer und Monteure, auch ohne vollen Lehrabschluss |
| `htl-absolventen` | Stellen, die ausdrücklich HTL-Absolventen suchen |

---

## Eigenes Profil anlegen

1. Im Ordner `profile` die Datei `_vorlage.toml` **kopieren** und umbenennen, z. B. in `mein-profil.toml`.
   Keine Leerzeichen im Namen und **kein `_` am Anfang** – solche Dateien werden ignoriert.
2. Rechtsklick → *Öffnen mit* → *Editor* und die Werte anpassen.
3. Starten mit `python praktikum_finder.py mein-profil`.

Ein Profil sieht so aus:

```toml
name = "Elektrotechnik & IT (HTL)"
beschreibung = "Elektrotechnik- und IT-Jobs für HTL-Absolventen"

suchbegriffe = [
    "Elektrotechniker HTL",
    "Netzwerktechniker",
    "Systemtechniker",
]

ort = "wien"

pflicht_woerter = []
titel_woerter = []
ausschluss_woerter = ["senior", "leiter"]
jobart_woerter = []

max_seiten = 5
```

### Was die Einstellungen bedeuten

| Einstellung | Bedeutung | Beispiel |
|---|---|---|
| `name` | Anzeigename | `"HTL-Absolventen"` |
| `beschreibung` | Kurze Beschreibung (optional) | `"Jobs für HTL-Abgänger"` |
| `suchbegriffe` | Jeder Begriff wird einzeln gesucht – wie im Suchfeld von karriere.at | `["htl absolvent", "htl"]` |
| `ort` | Ort oder Bundesland, leer = ganz Österreich | `"wien"`, `"graz"`, `"tirol"` |
| `pflicht_woerter` | **Titel oder Kurzbeschreibung** muss mindestens eins enthalten | `["data", "python"]` |
| `titel_woerter` | Der **Jobtitel** muss mindestens eins enthalten (strenger) | `["elektriker", "monteur"]` |
| `ausschluss_woerter` | Steht eins davon im **Titel**, fliegt der Job raus | `["senior", "meister"]` |
| `jobart_woerter` | Nur bestimmte Jobarten behalten | `["praktik", "intern"]` |
| `max_seiten` | Höchstens so viele Ergebnisseiten pro Suchbegriff (ca. 15–20 Jobs pro Seite) | `5` |

**So funktionieren die Wortfilter**

- Groß- und Kleinschreibung ist egal.
- **Teilwörter zählen:** `"elektr"` passt auf *Elektriker*, *Elektrotechnik*, *Elektromonteur* …
- Wörter mit **bis zu 3 Buchstaben** (z. B. `"htl"`, `"ki"`) zählen nur als ganzes Wort, damit `"ki"` nicht in *Ski* hängen bleibt.
- Eine leere Liste `[]` schaltet den Filter aus.

**Schreibregeln, damit nichts abstürzt**

- Texte in `"Anführungszeichen"`, Listen in `[eckigen Klammern]`, Einträge mit Komma trennen.
- Zeilen mit `#` am Anfang sind Kommentare.
- Bei einem Tippfehler sagt dir das Skript, in welcher Datei und Zeile er steckt.

### Tipps für gute Profile

- **Suchbegriffe zuerst auf karriere.at testen.** Bringen sie dort 0 Treffer, bringen sie auch im Skript nichts.
- **Zu wenige Treffer?** Meist sind `pflicht_woerter` zu streng – viele Firmen schreiben z. B. „HTL" erst im ausführlichen Text. Filter leeren (`[]`) und selbst aussortieren.
- **Zu viele unpassende Treffer?** `titel_woerter` oder `ausschluss_woerter` ergänzen.
- **Von vorne anfangen?** `ergebnisse\<profilname>.csv` löschen – dann gelten alle Treffer wieder als neu.

---

## Jeden Tag automatisch suchen (optional)

Terminal im Projektordner öffnen (siehe Schnellstart, Schritt 3). In der zweiten Zeile `mein-profil` durch deinen Profilnamen ersetzen (mehrere mit Leerzeichen getrennt, oder weglassen für alle Profile), dann die fünf Zeilen **zusammen** reinkopieren:

```powershell
$py = (Get-Command python).Source
$a = New-ScheduledTaskAction -Execute $py -Argument "praktikum_finder.py mein-profil" -WorkingDirectory "$PWD"
$b = New-ScheduledTaskAction -Execute "explorer.exe" -Argument "$PWD\ergebnisse"
$t = New-ScheduledTaskTrigger -Daily -At 8am
Register-ScheduledTask -TaskName "Jobsuche" -Action $a,$b -Trigger $t -Settings (New-ScheduledTaskSettingsSet -StartWhenAvailable)
```

Ab jetzt sucht Windows jeden Tag um 8 Uhr und öffnet danach den Ergebnisordner. Ist der Computer um 8 aus, wird es beim nächsten Hochfahren nachgeholt.

| Was | Befehl |
|---|---|
| Sofort suchen, ohne zu warten | `Start-ScheduledTask -TaskName "Jobsuche"` |
| Andere Uhrzeit, z. B. 22 Uhr | `Set-ScheduledTask -TaskName "Jobsuche" -Trigger (New-ScheduledTaskTrigger -Daily -At 10pm)` |
| Ausschalten | `Unregister-ScheduledTask -TaskName "Jobsuche"` |

> Wichtig: Wenn du den Projektordner später verschiebst, Automatik ausschalten und neu anlegen.

---

## Spalten in der Excel-Liste

| Spalte | Bedeutung |
|---|---|
| `gefunden_am` | Wann das Skript den Job zum ersten Mal gefunden hat |
| `id` | Job-Nummer auf karriere.at |
| `titel` | Stellentitel |
| `firma` | Unternehmen |
| `orte` | Arbeitsort(e) |
| `jobart` | Anstellungsart (Vollzeit, Teilzeit, Praktikum …) |
| `datum` | Veröffentlichungsdatum |
| `gehalt` | Gehaltsangabe, falls vorhanden |
| `homeoffice` | `ja` / `nein` |
| `suchbegriff` | Mit welchem Suchbegriff der Job gefunden wurde |
| `link` | Direkter Link zur Anzeige |

Trennzeichen ist das Semikolon (`;`), damit ein deutsches Excel die Spalten gleich richtig anzeigt.

---

## Probleme lösen

| Problem | Lösung |
|---|---|
| `python` wird nicht erkannt | `py` statt `python` probieren. Sonst Python neu installieren und **„Add Python to PATH"** anhaken. |
| `can't open file ... praktikum_finder.py` | Das Terminal ist im falschen Ordner. Schnellstart Schritt 3 wiederholen. |
| `Der Pfad ... kann nicht gefunden werden` | Ordner liegt woanders als gedacht. Am einfachsten Schnellstart Schritt 3 nutzen statt `cd`. |
| `git` wird nicht erkannt | Git brauchst du nicht – einfach **Download ZIP** nehmen. |
| `Dieses Skript braucht Python 3.11 oder neuer` | Neuere Version von python.org installieren. |
| `Tippfehler in '….toml'` | In der genannten Zeile nach fehlenden `"` oder `,` bzw. offenen `[ ]` suchen. |
| `Unbekannte Einstellung(en)` | Einstellungsname falsch geschrieben – mit der Tabelle oben vergleichen. |
| `Profil(e) nicht gefunden` | Profilnamen **ohne** `.toml` angeben; `--liste` zeigt alle. |
| `HTTP Error 403/429` | karriere.at blockiert gerade zu viele Anfragen. Später nochmal versuchen. |
| `KeyError: 'data'` | karriere.at hat die Seite umgebaut – das Skript muss angepasst werden. |
| Umlaute in Excel kaputt | Excel: **Daten → Aus Text/CSV**, Codierung **UTF-8**, Trennzeichen **Semikolon**. |
| CSV lässt sich nicht speichern | Datei ist noch in Excel offen. Excel schließen und neu starten. |

---

## Hinweis

Das Skript ruft die öffentliche Suche von karriere.at ab, genau wie dein Browser, und wartet zwischen den Anfragen jeweils eine Sekunde. Bitte nur für die persönliche Jobsuche nutzen, nicht im Sekundentakt laufen lassen und die Nutzungsbedingungen von karriere.at beachten.

Der Ordner `ergebnisse` wird nicht auf GitHub hochgeladen (siehe `.gitignore`) – deine Suchergebnisse bleiben auf deinem Computer.
