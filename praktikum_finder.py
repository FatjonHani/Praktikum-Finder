"""
Praktikum-Finder
================
Sucht auf karriere.at nach Jobs und speichert NEUE Treffer in CSV-Dateien.

Was gesucht wird, steht nicht im Code, sondern in Profil-Dateien im Ordner
"profile/" (eine .toml-Datei pro Profil). Jedes Profil bekommt seine eigene
Ergebnisdatei in "ergebnisse/<profilname>.csv".

Bereits gespeicherte Jobs werden erkannt und nicht doppelt eingetragen.
Es werden nur Python-Standardbibliotheken verwendet (Python 3.11 oder neuer).

Aufruf:
    python praktikum_finder.py                 -> alle Profile ausführen
    python praktikum_finder.py data-science    -> nur dieses Profil
    python praktikum_finder.py --liste         -> vorhandene Profile anzeigen
"""

import argparse
import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

try:
    import tomllib  # ab Python 3.11 eingebaut
except ModuleNotFoundError:
    sys.exit("Dieses Skript braucht Python 3.11 oder neuer (python --version).")

ORDNER = Path(__file__).resolve().parent
PROFIL_ORDNER = ORDNER / "profile"
ERGEBNIS_ORDNER = ORDNER / "ergebnisse"

# Pause zwischen Anfragen in Sekunden – höflich gegenüber dem Server.
PAUSE = 1.0

# Standardwerte, falls ein Profil eine Einstellung nicht angibt.
STANDARD = {
    "name": "",
    "beschreibung": "",
    "suchbegriffe": [],
    "ort": "",
    "pflicht_woerter": [],
    "titel_woerter": [],
    "ausschluss_woerter": [],
    "jobart_woerter": [],
    "max_seiten": 10,
}

SPALTEN = [
    "gefunden_am", "id", "titel", "firma", "orte", "jobart",
    "datum", "gehalt", "homeoffice", "suchbegriff", "link",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Praktikum-Finder/2.0",
    "Accept": "application/json",
    # Mit diesem Header liefert karriere.at die Ergebnisse als JSON statt HTML.
    "X-Requested-With": "XMLHttpRequest",
}


class ProfilFehler(Exception):
    """Ein Profil ist fehlerhaft (z. B. Tippfehler in der .toml-Datei)."""


# ---------------------------------------------------------------------------
# Profile laden
# ---------------------------------------------------------------------------

def profil_dateien() -> list[Path]:
    """Alle Profile im Ordner 'profile/'. Dateien mit '_' am Anfang (Vorlagen) werden ignoriert."""
    return sorted(p for p in PROFIL_ORDNER.glob("*.toml") if not p.name.startswith("_"))


def profil_laden(datei: Path) -> dict:
    """Liest eine Profil-Datei und prüft die wichtigsten Einstellungen."""
    try:
        # "utf-8-sig" entfernt ein unsichtbares BOM-Zeichen, das manche Windows-Editoren einfügen.
        daten = tomllib.loads(datei.read_text(encoding="utf-8-sig"))
    except UnicodeDecodeError:
        raise ProfilFehler(f"'{datei.name}' ist nicht als UTF-8 gespeichert. "
                           f"Im Editor: Speichern unter → Codierung 'UTF-8'.") from None
    except tomllib.TOMLDecodeError as fehler:
        raise ProfilFehler(f"Tippfehler in '{datei.name}': {fehler}") from None

    unbekannt = set(daten) - set(STANDARD)
    if unbekannt:
        raise ProfilFehler(
            f"Unbekannte Einstellung(en) in '{datei.name}': {', '.join(sorted(unbekannt))}. "
            f"Erlaubt sind: {', '.join(STANDARD)}"
        )

    profil = {**STANDARD, **daten, "id": datei.stem}
    if not profil["name"]:
        profil["name"] = datei.stem

    for feld in ("suchbegriffe", "pflicht_woerter", "titel_woerter",
                 "ausschluss_woerter", "jobart_woerter"):
        if not isinstance(profil[feld], list) or not all(isinstance(w, str) for w in profil[feld]):
            raise ProfilFehler(f"'{feld}' in '{datei.name}' muss eine Liste sein, z. B. [\"wort1\", \"wort2\"]")
        profil[feld] = [w.lower().strip() for w in profil[feld] if w.strip()]

    if not profil["suchbegriffe"]:
        raise ProfilFehler(f"'{datei.name}' hat keine suchbegriffe.")
    if not isinstance(profil["max_seiten"], int) or profil["max_seiten"] < 1:
        raise ProfilFehler(f"'max_seiten' in '{datei.name}' muss eine ganze Zahl ab 1 sein.")
    return profil


# ---------------------------------------------------------------------------
# karriere.at abfragen
# ---------------------------------------------------------------------------

def seite_laden(suchbegriff: str, ort: str, seite: int) -> dict:
    """Lädt eine Ergebnisseite von karriere.at und gibt das JSON zurück."""
    parameter = {"keywords": suchbegriff, "page": seite}
    if ort:
        parameter["locations"] = ort
    url = "https://www.karriere.at/jobs?" + urllib.parse.urlencode(parameter)
    anfrage = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(anfrage, timeout=30) as antwort:
        return json.loads(antwort.read().decode("utf-8"))


def jobs_suchen(suchbegriff: str, ort: str, max_seiten: int) -> list[dict]:
    """Holt alle Seiten zu einem Suchbegriff und gibt eine Liste von Jobs zurück."""
    jobs = []
    for seite in range(1, max_seiten + 1):
        daten = seite_laden(suchbegriff, ort, seite)["data"]["jobsSearchList"]
        for eintrag in daten.get("activeItems", {}).get("items", []):
            job = eintrag.get("jobsItem")
            if job:  # Werbeblöcke o. Ä. haben kein "jobsItem"
                jobs.append(job)
        if not daten.get("loadMoreJobsButton", {}).get("next"):
            break  # keine weitere Seite
        time.sleep(PAUSE)
    return jobs


# ---------------------------------------------------------------------------
# Filter
# ---------------------------------------------------------------------------

def normalisieren(text: str) -> str:
    """Kleinbuchstaben, Satzzeichen zu Leerzeichen – für einfache Wortsuche."""
    text = f" {text} ".lower()
    for zeichen in ",.;:()/-!?|*&+\"'":
        text = text.replace(zeichen, " ")
    return text


def enthaelt_eins(text: str, woerter: list[str]) -> bool:
    """True, wenn eines der Wörter im Text vorkommt.
    Kurze Wörter (bis 3 Buchstaben, z. B. 'ki', 'htl') zählen nur als ganzes Wort."""
    for wort in woerter:
        if len(wort) <= 3:
            if f" {wort} " in text:
                return True
        elif wort in text:
            return True
    return False


def passt(job: dict, profil: dict) -> bool:
    """Wendet die Filter des Profils auf einen Job an."""
    titel = normalisieren(job.get("title", ""))
    titel_und_text = normalisieren(f"{job.get('title', '')} {job.get('summary', '')}")
    jobart = normalisieren(f"{job.get('employmentTypes', '')} {job.get('title', '')}")

    if profil["jobart_woerter"] and not enthaelt_eins(jobart, profil["jobart_woerter"]):
        return False
    if profil["pflicht_woerter"] and not enthaelt_eins(titel_und_text, profil["pflicht_woerter"]):
        return False
    if profil["titel_woerter"] and not enthaelt_eins(titel, profil["titel_woerter"]):
        return False
    if profil["ausschluss_woerter"] and enthaelt_eins(titel, profil["ausschluss_woerter"]):
        return False
    return True


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------

def bekannte_ids(csv_datei: Path) -> set[str]:
    """Liest die IDs aller Jobs, die schon in der CSV-Datei stehen."""
    if not csv_datei.exists():
        return set()
    with csv_datei.open(encoding="utf-8-sig", newline="") as f:
        return {zeile["id"] for zeile in csv.DictReader(f, delimiter=";")}


def speichern(csv_datei: Path, neue_jobs: list[dict]) -> None:
    """Hängt neue Jobs an die CSV-Datei an (legt sie bei Bedarf an)."""
    csv_datei.parent.mkdir(exist_ok=True)
    neu_anlegen = not csv_datei.exists()
    # utf-8-sig + Semikolon: Excel (deutsch) öffnet die Datei mit Umlauten korrekt.
    with csv_datei.open("a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SPALTEN, delimiter=";", extrasaction="ignore")
        if neu_anlegen:
            writer.writeheader()
        writer.writerows(neue_jobs)


# ---------------------------------------------------------------------------
# Ablauf
# ---------------------------------------------------------------------------

def profil_ausfuehren(profil: dict) -> None:
    csv_datei = ERGEBNIS_ORDNER / f"{profil['id']}.csv"
    print(f"=== Profil: {profil['name']} ===")
    if profil["ort"]:
        print(f"    Ort: {profil['ort']}")

    schon_gespeichert = bekannte_ids(csv_datei)
    gefunden = {}  # id -> Zeile (verhindert Duplikate zwischen Suchbegriffen)
    jetzt = datetime.now().strftime("%Y-%m-%d %H:%M")

    for begriff in profil["suchbegriffe"]:
        try:
            jobs = jobs_suchen(begriff, profil["ort"], profil["max_seiten"])
        except Exception as fehler:
            print(f"  Fehler bei '{begriff}': {fehler}")
            continue
        passende = [j for j in jobs if passt(j, profil)]
        print(f"  '{begriff}': {len(jobs)} Treffer, davon {len(passende)} passend")

        for job in passende:
            job_id = str(job.get("id"))
            if job_id in schon_gespeichert or job_id in gefunden:
                continue
            gefunden[job_id] = {
                "gefunden_am": jetzt,
                "id": job_id,
                "titel": job.get("title", ""),
                "firma": (job.get("company") or {}).get("name", ""),
                "orte": ", ".join(o.get("name", "") for o in job.get("locations", [])),
                "jobart": job.get("employmentTypes", ""),
                "datum": job.get("date", ""),
                "gehalt": job.get("salary", ""),
                "homeoffice": "ja" if job.get("isHomeOffice") else "nein",
                "suchbegriff": begriff,
                "link": job.get("link", ""),
            }
        time.sleep(PAUSE)

    neue = list(gefunden.values())
    if neue:
        speichern(csv_datei, neue)
        print(f"\n  {len(neue)} NEUE Jobs gespeichert in 'ergebnisse/{csv_datei.name}':\n")
        for job in neue:
            print(f"  - {job['titel']} | {job['firma']} | {job['orte']}")
            print(f"    {job['link']}")
    else:
        print("\n  Keine neuen Jobs seit dem letzten Lauf.")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sucht auf karriere.at nach Jobs laut den Profilen im Ordner 'profile/'.")
    parser.add_argument("profile", nargs="*",
                        help="Name(n) der Profile ohne .toml (leer = alle Profile)")
    parser.add_argument("--liste", action="store_true", help="vorhandene Profile anzeigen")
    args = parser.parse_args()

    dateien = profil_dateien()
    if not dateien:
        sys.exit(f"Keine Profile gefunden. Lege eine .toml-Datei in '{PROFIL_ORDNER}' an "
                 f"(Vorlage: profile/_vorlage.toml).")

    if args.liste:
        print("Vorhandene Profile:\n")
        for datei in dateien:
            try:
                p = profil_laden(datei)
                print(f"  {datei.stem:<28} {p['name']}" + (f" – {p['beschreibung']}" if p["beschreibung"] else ""))
            except ProfilFehler as fehler:
                print(f"  {datei.stem:<28} FEHLER: {fehler}")
        return

    if args.profile:
        verfuegbar = {d.stem: d for d in dateien}
        fehlend = [n for n in args.profile if n not in verfuegbar]
        if fehlend:
            sys.exit(f"Profil(e) nicht gefunden: {', '.join(fehlend)}. "
                     f"Vorhanden: {', '.join(verfuegbar)}")
        dateien = [verfuegbar[n] for n in args.profile]

    print("Praktikum-Finder startet ...\n")
    for datei in dateien:
        try:
            profil_ausfuehren(profil_laden(datei))
        except ProfilFehler as fehler:
            print(f"!!! {fehler}\n")


if __name__ == "__main__":
    # Damit Umlaute in der Windows-Konsole korrekt angezeigt werden.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
