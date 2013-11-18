#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2011 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# prepare_patch.py: Helfer für kleine Editieraufgaben
# ===================================================
# ::

u"""
Erstelle einen Patch für kleinere Korrekturen der Wortliste.
Ausgangspunkt sind Dateien mit einer Korrektur pro Zeile.
(Zeilen, die mit ``#`` starten, werden ignoriert.)

AKTION ist eine von:
  doppelte:       Einträge mit gleichem Schlüssel entfernen,
  fehleintraege:  Einträge entfernen,
  grossklein:     Großschreibung ändern,
  grossabgleich:  Großschreibung der Trennmuster wie erstes Feld,
  korrektur:      Einträge durch alternative Version ersetzen.
  neu:            Einträge hinzufügen,
"""

# Die ``<AKTION>.todo`` Dateien in diesem Verzeichnis beschreiben das
# jeweils erforderliche Datenformat im Dateikopf.
# 
# ::

import optparse, sys, os
from copy import copy, deepcopy


from werkzeug import WordFile, WordEntry, join_word, udiff
# sort.py im Überverzeichnis:
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from sort import sortkey_wl, sortkey_duden


def teste_datei(datei):
    """Teste, ob Datei geöffnet werden kann."""

    try:
        file = open(datei, 'r')
        file.close()
    except:
        sys.stderr.write("Kann '" + datei + "' nicht öffnen\n" )
        sys.exit()


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

def korrektur(wordfile, datei):
    """Patch aus korrigierten Einträgen"""

    if not datei:
        datei = 'korrektur.todo'
    teste_datei(datei)

    korrekturen = {}
    for line in open(datei, 'r'):
        if line.startswith('#'):
            continue
        # Dekodieren, Zeilenende entfernen
        line = line.decode('utf8').strip()
        if not line:
            continue
        # Eintrag ggf. komplettieren
        if u';' in line:
            key = line.split(';')[0]
        else:
            key = join_word(line)
        korrekturen[key] = line

    wortliste = list(wordfile)
    wortliste_neu = [] # korrigierte Liste

    for entry in wortliste:
        key = entry[0]
        if key in korrekturen:
            korrektur = korrekturen.pop(key)
            if u';' in korrektur:
                entry = WordEntry(korrektur)
            else:
                entry = copy(entry)
                entry.set(korrektur, sprachvariante)
                # print entry
        wortliste_neu.append(entry)

    if korrekturen:
        print korrekturen # übrige Einträge

    return (wortliste, wortliste_neu)


# Fehleinträge
# ------------
#::

def fehleintraege(wordfile, datei):
    """Entfernen der Einträge aus einer Liste von Fehleinträgen """

# Fehleinträge aus Datei.
# 
# Format:
#   Ein Eintrag/Zeile, mit oder ohne Trennzeichen
# 
# ::

    if not datei:
        datei = 'fehleintraege.todo'
    teste_datei(datei)

    # Dekodieren, Zeilenende entfernen, Trennzeichen entfernen
    korrekturen = set(join_word(line.decode('utf8').strip().split(u';')[0])
                      for line in open(datei, 'r')
                      if not line.startswith('#'))
    wortliste = list(wordfile)
    wortliste_neu = [] # korrigierte Liste
    for entry in wortliste:
        if entry[0] in korrekturen: # nicht kopieren
            korrekturen.discard(entry[0]) # erledigt
        else:
            wortliste_neu.append(entry)

    print 'nicht gefunden:'
    for w in korrekturen:
        print w.encode('utf8')

    return (wortliste, wortliste_neu)


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

def grossklein(wordfile, datei):
    """Groß-/Kleinschreibung umstellen"""

    if not datei:
        datei = 'grossklein.todo'
    teste_datei(datei)

    wortliste = list(wordfile)

    # Dekodieren, Feldtrenner zu Leerzeichen
    korrekturen = [line.decode('utf8').replace(';',' ')
                   for line in open(datei, 'r')]
    # erstes Feld, Trennzeichen entfernen
    korrekturen = [join_word(line.split()[0]) for line in korrekturen
                   if line.strip() and not line.startswith('#')]
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

    return (wortliste, wortliste_neu)

# Anpassung der Großschreibung der Trennmuster an das erste Feld
# (ungetrenntes Wort). Siehe "werkzeug.py" für einen Test auf Differenzen.
# (Differenzen sind größtenteils auf unvorsichtiges Ersetzen mit Texteditor
# zurückzuführen.)
# ::

def grossabgleich(wordfile):
    wortliste = list(wordfile)
    wortliste_neu = deepcopy(wortliste) # korrigierte Liste
    for entry in wortliste_neu:
        # Übertrag des Anfangsbuchstabens
        for i in range(1,len(entry)):
            if entry[i].startswith('-'):
                continue
            entry[i] = entry[0][0] + entry[i][1:]
    return (wortliste, wortliste_neu)


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

def reformschreibung(wordfile, datei):
    """Wörter die nur in (allgemeiner) Reformschreibung existieren"""

    if not datei:
        datei='reformschreibung.todo'
    teste_datei(datei)

    wortliste = list(wordfile)

    # Dekodieren, Zeilenende entfernen
    korrekturen = [line.decode('utf8').strip()
                   for line in open(datei, 'r')]
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

def sprachvariante_split(wordfile, alt, neu,
                         altsprache='de-1901', neusprache='de-1996'):

    wortliste = list(wordfile)
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
    return (wortliste, wortliste_neu)



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

def neu(wordfile, datei):
    """Neueinträge prüfen und vorbereiten."""

    if not datei:
        datei = 'neu.todo'
    teste_datei(datei)
    korrekturen = open(datei, 'r')

    wortliste = list(wordfile)
    wortliste_neu = deepcopy(wortliste)
    words = set(entry[0] for entry in wortliste)     # vorhandene Wörter

    for line in korrekturen:
        if line.startswith('#'):
            continue
        # Dekodieren, Zeilenende entfernen
        line = line.decode('utf8').strip()
        # Eintrag ggf. komplettieren
        if u';' in line:
            key = u';'.split(line)[0]
        else:
            key = join_word(line)
            line = u'%s;%s' % (key, line)
        # Test auf "Neuwert":
        if key in words:
            print key.encode('utf8'), 'schon vorhanden'
            continue
        if key.lower() in words or key.title() in words:
            print (key.encode('utf8'),
                   'mit anderer Groß-/Kleinschreibung vorhanden')
            continue
        wortliste_neu.append(WordEntry(line))

    # Sortieren
    # wortliste_neu.sort(key=sortkey_wl)
    wortliste_neu.sort(key=sortkey_duden)

    return (wortliste, wortliste_neu)


def doppelte(wordfile, use_first=False):
    """Doppeleinträge entfernen (ohne Berücksichtigung der Großschreibung).

    Boolscher Wert `use_first` bestimmt, ob der erste oder der letzte von
    Einträgen mit gleichem Schlüssel in der Liste verbleibt.

    Die neue Liste ist sortiert.
    """
    wortliste = list(wordfile)
    worddict = {}
    for entry in wortliste:
        key = entry[0].lower()
        if use_first and key in worddict:
            continue
        worddict[key] = entry

    wortliste_neu = worddict.values() # korrigierte Liste
    # wortliste_neu.sort(key=sortkey_wl)
    wortliste_neu.sort(key=sortkey_duden)

    print len(wortliste) - len(wortliste_neu), u"Einträge entfernt"
    return (wortliste, wortliste_neu)

# Default-Aktion::

if __name__ == '__main__':

# Optionen::

    usage = '%prog [Optionen] AKTION\n' + __doc__

    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-i', '--file', dest='wortliste',
                      help='Eingangsdatei, Vorgabe "../../wortliste"',
                      default='../../wortliste')
    parser.add_option('-k', '--todofile', dest='todo',
                      help='Korrekturdatei, Vorgabe "<AKTION>.todo"')
    parser.add_option('-o', '--outfile', dest='patchfile',
                      help='Ausgangsdatei (Patch), Vorgabe "wortliste.patch"',
                      default='wortliste.patch')

    (options, args) = parser.parse_args()

    if args:
        aktion = args[0]
    else:
        print 'Nichts zu tun: AKTION Argument fehlt.', '\n'
        parser.print_help()
        sys.exit()

# Die `Wortliste`::
    wordfile = WordFile(options.wortliste)

    # Da der Aufruf von `wortliste = list(wordfile)` lange dauert, wird er
    # in den Aktionsroutinen nach dem Test auf die Eingabedatei ausgeführt.

# Behandeln::

    if aktion == 'neu':
        (wortliste, wortliste_neu) = neu(wordfile, options.todo)
    elif aktion == 'doppelte':
        (wortliste, wortliste_neu) = doppelte(wordfile)
    elif aktion == 'fehleintraege':
        (wortliste, wortliste_neu) = fehleintraege(wordfile, options.todo)
    elif aktion == 'grossklein':
        (wortliste, wortliste_neu) = grossklein(wordfile, options.todo)
    elif aktion == 'grossabgleich':
        (wortliste, wortliste_neu) = grossabgleich(wordfile)
    elif aktion == 'korrektur':
        (wortliste, wortliste_neu) = korrektur(wordfile, options.todo)
    else:
        print 'Unbekannte AKTION', '\n'
        parser.print_help()
        sys.exit()

    # (wortliste, wortliste_neu) = sprachvariante_split(wordfile,
    #                                                   u'knien', u'kni-en')
    # (wortliste, wortliste_neu) = reformschreibung(wordfile)

# Patch erstellen::

    patch = udiff(wortliste, wortliste_neu, 'wortliste', 'wortliste-neu',
                  encoding=wordfile.encoding)
    if patch:
        # print patch
        patchfile = open(options.patchfile, 'w')
        patchfile.write(patch + '\n')
        print u'Änderungen nach %s geschrieben' % options.patchfile
    else:
        print u'keine Änderungen'
