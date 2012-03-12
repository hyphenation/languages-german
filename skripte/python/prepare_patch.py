#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2011 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# prepare_patch.py: Helfer für kleine Editieraufgaben
# =============================================
# 
# Erstelle einen Patch für kleinere Korrekturen der Wortliste.
# Ausganspunkt sind "todo"-Dateien mit einer Korrektur pro Zeile.
# 
# ::

from copy import deepcopy

from werkzeug import WordFile, WordEntry, join_word, udiff
from sort import sortkey_wl, sortkey_duden


# Allgemeine Korrektur (z.B. Fehltrennung)
#
# Format:
#  * ein Wort mit Trennstellen (für allgemeingültige Trennstellen):
#    Das ungetrennte Wort wird vorangestellt (durch Semikolon getrennt),
#    oder
#  * vollständiger Eintrag (für Wörter mit Sprachvarianten).
# 
# ::

def korrektur(wortliste, encoding='utf8'):
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
            line = u'%s;%s' % (key, line)
        korrekturen[key] = line

    wortliste_neu = [] # korrigierte Liste

    for entry in wortliste:
        if entry[0] in korrekturen:
            entry = WordEntry(korrekturen[entry[0]])
            del(korrekturen[entry[0]])
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

    korrekturen = open('fehleintraege.todo').readlines()
    # Dekodieren, Zeilenende entfernen, Trennzeichen entfernen
    korrekturen = set(join_word(line.decode('utf8').strip())
                        for line in korrekturen)
    wortliste_neu = [] # korrigierte Liste
    for entry in wortliste:
        if entry[0] in korrekturen: # nicht kopieren
            korrekturen.discard(entry[0]) # erledigt
        else:
            wortliste_neu.append(entry)

    print korrekturen
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

    korrekturen = open('grossklein.todo').readlines()
    # Dekodieren, Zeilenende entfernen
    korrekturen = [line.decode('utf8').strip() for line in korrekturen]
    # erstes Feld, Trennzeichen entfernen
    korrekturen = [join_word(line.split(';')[0]) for line in korrekturen]
    korrekturen = set(korrekturen)
    wortliste_neu = [] # korrigierte Liste

    for entry in wortliste:
        if entry[0] in korrekturen:
            original = entry[0]
            if original.islower():
                fields = [field[0].title() + field[1:] for field in entry]
            else:
                fields = [field.lower() for field in entry]
            entry = WordEntry(';'.join(fields))
            korrekturen.discard(original) # erledigt
        wortliste_neu.append(entry)

    if korrekturen:
        print korrekturen # übrige Einträge
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

    korrekturen = open('reformschreibung.todo').readlines()
    # Dekodieren, Zeilenende entfernen
    korrekturen = [line.decode('utf8').strip() for line in korrekturen]
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

def neu(wortliste, encoding='utf8'):
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
        wortliste_neu.append(WordEntry(line, encoding=encoding))

    # Sortieren
    wortliste_neu.sort(key=sortkey_wl)
    # wortliste_neu.sort(key=sortkey_duden)

    return wortliste_neu

# Default-Aktion::

if __name__ == '__main__':

# Die `Wortliste`::

    wordfile = WordFile('../../wortliste') # ≅ 400 000 Einträge/Zeilen
    wortliste = list(wordfile)

# Behandeln::

    # wortliste_neu = fehleintraege(wortliste)
    # wortliste_neu = grossklein(wortliste)
    # wortliste_neu = neu(wortliste, wordfile.encoding)
    # wortliste_neu = reformschreibung(wortliste)
    wortliste_neu = korrektur(wortliste)

# Patch erstellen::

    patch = udiff(wortliste, wortliste_neu, 'wortliste', 'wortliste-neu')
    if patch:
        print patch
        patchfile = open('../../wortliste.patch', 'w')
        patchfile.write(patch + '\n')
    else:
        print "empty patch"
