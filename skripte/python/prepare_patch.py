#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2011 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# prepare_patch.py: Helfer für kleine Editieraufgaben
# =============================================
#
# Erstelle einen Patch für kleinere Korrekturen der Wortliste. Ausganspunkt
# sind "todo"-Dateien mit einer Korrektur pro Zeile. Die ``*.todo``
# Template-Dateien in diesem Verzeichnis beschreiben das erforderliche
# Datenformat im Dateikopf. (Zeilen die mit ``#`` starten werden ignoriert.)
#
# Zur Auswahl der gewünschten Funktion bitte von den Zeilen 281 bis 288 die
# entsprechende Zeile auszukommentieren.
# TODO: Interface für Auswahl über Optionen.
#
# ::

from copy import deepcopy

from werkzeug import WordFile, WordEntry, join_word, udiff
from sort import sortkey_wl, sortkey_duden

# Sprachvarianten
# ---------------
# Sprach-Tag nach [BCP47]_::

sprachvariante = 'de-1901'         # "traditionell"
# sprachvariante = 'de-1996'         # Reformschreibung
# sprachvariante = 'de-x-GROSS'      # ohne ß (Großbuchstaben und Kapitälchen)
# sprachvariante = 'de-1901-x-GROSS'   # ohne ß (Schweiz oder GROSS)
# sprachvariante = 'de-1996-x-GROSS' # ohne ß (Schweiz oder GROSS)
# sprachvariante = 'de-CH-1901'     # ohne ß (Schweiz) ("süssauer")


# Allgemeine Korrektur (z.B. Fehltrennung)
#
# Format:
#  * ein Wort mit Trennstellen (für "Sprachvariante"):
#  * vollständiger Eintrag (für Wörter mit Sprachvarianten).
#
# ::

def korrektur(wortliste):
    """Patch aus korrigierten Einträgen"""
    korrekturen = {}
    for line in open('korrekturen.todo'):
        # Dekodieren, Zeilenende entfernen
        line = line.decode('utf8').strip()
        # Eintrag ggf. komplettieren
        if u';' in line:
            key = line.split(';')[0]
        else:
            key = join_word(line)
        korrekturen[key] = line

    wortliste_neu = [] # korrigierte Liste

    for entry in wortliste:
        key = entry[0]
        if key in korrekturen:
            korrektur = korrekturen.pop(key)
            if u';' in korrektur:
                entry = WordEntry(korrektur)
            else:
                entry.set(korrektur, sprachvariante)
        wortliste_neu.append(entry)

    if korrekturen:
        print korrekturen # übrige Einträge
    return wortliste_neu


# Fehleinträge
# ------------
#::

def fehleintraege(wortliste):
    """Entfernen der Einträge aus einer Liste von Fehleinträgen """

# Fehleinträge aus Datei.
#
# Format:
#   Ein Eintrag/Zeile, mit oder ohne Trennzeichen
#
# ::

    # Dekodieren, Zeilenende entfernen, Trennzeichen entfernen
    korrekturen = set(join_word(line.decode('utf8').strip())
                      for line in open('fehleintraege.todo')
                      if not line.startswith('#'))
    wortliste_neu = [] # korrigierte Liste
    for entry in wortliste:
        if entry[0] in korrekturen: # nicht kopieren
            korrekturen.discard(entry[0]) # erledigt
        else:
            wortliste_neu.append(entry)

    for w in korrekturen:
        print w.encode('utf8')
    return wortliste_neu


# Groß-/Kleinschreibung ändern
# ----------------------------
#
# Umstellen der Groß- oder Kleinschreibung auf die Variante in der Datei
# ``grossklein.todo``
#
# Format:
#   ein Eintrag oder Wort pro Zeile, mit vorhandener Groß-/Kleinschreibung.
#
# ::

def grossklein(wortliste):
    """Groß-/Kleinschreibung umstellen"""

    # Dekodieren, Feldtrenner zu Leerzeichen
    korrekturen = [line.decode('utf8').replace(';',' ')
                   for line in open('grossklein.todo')]
    # erstes Feld, Trennzeichen entfernen
    korrekturen = [join_word(line.split()[0]) for line in korrekturen
                   if not line.startswith('#')]
    korrekturen = set(korrekturen)
    wortliste_neu = deepcopy(wortliste) # korrigierte Liste

    for entry in wortliste_neu:
        if entry[0] in korrekturen:
            korrekturen.discard(entry[0]) # gefunden
            # Anfangsbuchstabe mit geänderter Großschreibung:
            if entry[0][0].islower():
                anfangsbuchstabe = entry[0][0].title()
            else:
                anfangsbuchstabe = entry[0][0].lower()
            # Einträge korrigieren:
            for i in range(len(entry)):
                if entry[i].startswith('-'): # -2-, -3-, ...
                    continue
                entry[i] = anfangsbuchstabe + entry[i][1:]

    if korrekturen:
        print korrekturen # übrige Einträge
    return wortliste_neu

# Anpassung der Großschreibung der Trennmuster an das erste Feld
# (ungetrenntes Wort). Siehe "werkzeug.py" für einen Test auf Differenzen.
# (Differenzen sind größtenteils auf unvorsichtiges Ersetzen mit Texteditor
# zurückzuführen.)
# ::

def abgleich_grossklein(wortliste):
    wortliste_neu = deepcopy(wortliste) # korrigierte Liste
    for entry in wortliste_neu:
        # Übertrag des Anfangsbuchstabens
        for i in range(1,len(entry)):
            if entry[i].startswith('-'):
                continue
            entry[i] = entry[0][0] + entry[i][1:]
    return wortliste_neu


# Sprachvariante ändern
# ---------------------
#
# Einträge mit allgemeingültiger (oder sonstwie mehrfacher) Sprachvariante
# in "nur in Reformschreibung" (allgemein) ändern.
#
# Format:
#   ein Wort/(Alt-)Eintrag pro Zeile.
#
# ::

def reformschreibung(wortliste):
    """Wörter die nur in (allgemeiner) Reformschreibung existieren"""

    # Dekodieren, Zeilenende entfernen
    korrekturen = [line.decode('utf8').strip()
                   for line in open('reformschreibung.todo')]
    # erstes Feld
    korrekturen = [line.split(';')[0] for line in korrekturen]
    korrekturen = set(korrekturen)

    wortliste_neu = [] # korrigierte Liste

    for entry in wortliste:
        if entry[0] in korrekturen:
            key = entry[0]
            wort = entry.get('de-1996')
            entry = WordEntry('%s;-2-;-3-;%s' % (key, wort))
            korrekturen.discard(key) # erledigt
        wortliste_neu.append(entry)

    if korrekturen:
        print korrekturen # übrige Einträge
    return wortliste_neu


# Getrennte Einträge für Sprachvarianten
# --------------------------------------
#
# Korrigiere fehlende Spezifizierung nach Sprachvarianten, z.B.
#
# - System;Sy-stem
# + System;-2-;Sy-stem;Sys-tem
#
# ::

def sprachvariante_split(wortliste, alt, neu,
                         altsprache='de-1901', neusprache='de-1996'):

    wortliste_neu = [] # korrigierte Liste

    for entry in wortliste:
        if len(entry) == 2: # Allgemeine Schreibung
            altwort = entry.get(altsprache)
            neuwort = altwort.replace(alt, neu)
            if altwort != neuwort:
                entry = WordEntry('%s;-2-;3;4' % (join_word(altwort)))
                entry.set(altwort, altsprache)
                entry.set(neuwort, neusprache)
        wortliste_neu.append(entry)
    return wortliste_neu



# Neueinträge prüfen und vorbereiten
# ----------------------------------
#
# Die in einer Datei (ein Neueintrag pro Zeile) gesammelten Vorschläge auf
# auf Neuwert testen (vorhandene Wörter werden ignoriert, unabhängig von der
# Groß-/Kleinschreibung) und einsortieren.
#
# Format:
#  * ein Wort mit Trennstellen (für allgemeingültige Trennstellen):
#    Das ungetrennte Wort wird vorangestellt (durch Semikolon getrennt),
#    oder
#  * vollständiger Eintrag (für Wörter mit Sprachvarianten).
#
# ::

def neu(wortliste):
    """Neueinträge prüfen und vorbereiten."""

    korrekturen = open('neu.todo')
    wortliste_neu = deepcopy(wortliste)
    words = dict()     # vorhandene Wörter
    for entry in wortliste:
        words[entry[0]] = entry

    for line in korrekturen:
        # Dekodieren, Zeilenende entfernen
        line = line.decode('utf8').strip()
        # Eintrag ggf. komplettieren
        if u';' in line:
            key = u';'.split(line)[0]
        else:
            key = join_word(line)
            line = u'%s;%s' % (key, line)
        # Test auf "Neuwert":
        if key.lower() in words or key.title() in words:
            print key.encode('utf8'),
            if key in words:
                print 'schon vorhanden'
            else:
                print 'mit anderer Groß-/Kleinschreibung vorhanden'
            continue
        wortliste_neu.append(WordEntry(line))

    # Sortieren
    # wortliste_neu.sort(key=sortkey_wl)
    wortliste_neu.sort(key=sortkey_duden)

    return wortliste_neu

# Default-Aktion::

if __name__ == '__main__':

# Die `Wortliste`::

    wordfile = WordFile('../../wortliste') # ≅ 400 000 Einträge/Zeilen
    wortliste = list(wordfile)

# Behandeln::

    # wortliste_neu = fehleintraege(wortliste)
    # wortliste_neu = grossklein(wortliste)
    # wortliste_neu = abgleich_grossklein(wortliste)
    # wortliste_neu = neu(wortliste)
    # wortliste_neu = reformschreibung(wortliste)
    # wortliste_neu = sprachvariante_split(wortliste,
    #                                      u'knien', u'kni-en')
    # wortliste_neu = korrektur(wortliste)

# Patch erstellen::

    patch = udiff(wortliste, wortliste_neu, 'wortliste', 'wortliste-neu',
                  encoding= wordfile.encoding)
    if patch:
        print patch
        patchfile = open('wortliste.patch', 'w')
        patchfile.write(patch + '\n')
    else:
        print "empty patch"
