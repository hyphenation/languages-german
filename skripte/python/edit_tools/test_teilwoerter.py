#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2012 Günter Milde.
# :Licence:   This work may be distributed and/or modified under
#             the conditions of the `LaTeX Project Public License`,
#             either version 1.3 of this license or (at your option)
#             any later  version.
# :Version:   0.1 (2012-02-07)

# test_teilwoerter.py: Test von Wortteilen/Teilwörtern
# ==================================================================
#
# ::

"""Test der Markierung von Komposita in der `Wortliste`"""

# .. contents::
#
# Vorspann
# ========
#
# Importiere Python Module::

import re       # Funktionen und Klassen für reguläre Ausdrücke
import sys      # sys.exit() zum Abbruch vor Ende (für Testzwecke)
from collections import defaultdict  # Wörterbuch mit Default
from copy import deepcopy

from wortliste import WordFile, join_word, udiff

# Sprachvarianten
# ---------------
#
# Sprach-Tag nach [BCP47]_::

sprachvariante = 'de-1901'         # "traditionell"
# sprachvariante = 'de-1996'       # Reformschreibung
# sprachvariante = 'de-x-GROSS'    # ohne ß (Großbuchstaben und Kapitälchen)


# Wortlisten
# -------------
#
# Die freie `Wortliste der deutschsprachigen Trennmustermannschaft`_
# ("Lembergsche Liste")::

wordfile = WordFile('../../../wortliste') # ≅ 400 000 Einträge/Zeilen
wortliste = list(wordfile)

# Wörterbucher für die Rechtschreibprüfprogramme Ispell/Aspell
# (in Debian in den Paketen "wngerman" und "wogerman").
# Unterschieden Groß-/Kleinschreibung und beinhalten kurze Wörter.
#
# * Ein Wort/Zeile
# * Groß/Kleinschreibung unterschieden
# * Kodierung: utf8 (bis auf 'ogerman')
#
# ::

if sprachvariante == 'de-1901':
    words = set(line.rstrip().decode('latin-1')
                  for line in open('/usr/share/dict/ogerman'))
else:
    words = set(line.rstrip().decode('utf8')
                  for line in open('/usr/share/dict/ngerman'))

words_fremd = set(line.rstrip().decode('utf8')
                  for line in open('wortteile/teilwoerter-fremd')
                  if not line.startswith('#'))

# Wörter der Wortliste::

words.update((entry[0] for entry in wortliste
              if entry.lang_index(sprachvariante)))

# print len(words), 'Wörter aus Wörterbüchern'


# Sortierung in::

unbekannt = defaultdict(list)  # Teilwörter nicht in der Wortliste
grossklein = defaultdict(list) # Teilwörter mit anderer Groß/Kleinschreibung
# vorsilben = defaultdict(list)   # Teilwörter mit zusätzlicher Vorsilbe
fremd = defaultdict(list) # fremsprachige Teilwörter


# Analyse
# =====================
#
# Durchlaufe alle Einträge::

for entry in wortliste:

# Wort mit Trennungen in Sprachvariante::

    wort = entry.get(sprachvariante)
    if wort is None: # Wort existiert nicht in der Sprachvariante
        continue
    if sprachvariante != 'de-1901' and wort[0] is not '-1-':
        continue  # Wort mit allgemeingültiger Trennung

# Zerlegen an Wortfugen::

    teile = wort.split('=')

    if len(teile) == 1:
        continue

# Wortteile analysieren::

    for teil in teile:

# gewichtete Trennzeichen (==) erzeugen "leere" Teile::

        if not teil: 
            continue


# Vorsilben die sich auf mehrere Teilwörter beziehen (z.b. un<=regel=mäßig)
# enden auf "<"::

        if teil.endswith(u'<'):
            continue

# Teilwort ohne Trennung, Groß/Kleinschreibung übertragen::

        key = join_word(teil)
        if wort.istitle():
            key = key.title()

# Suche nach Teilwort als Einzelwort::

        if (key in words
            or (key.endswith(u's') and key[:-1] in words)
            # or key.startswith('zu') and key[2:] in words
            or key + 'e' in words
            or key + 'en' in words):
            continue

# Teste ohne Berücksichtigung der Groß/Kleinschreibung::

        if key.lower() in words or key.title() in words:
            grossklein[key].append(wort)
            continue

        if key.endswith('s') and (
                key[:-1].lower() in words or key[:-1].title() in words):
            grossklein[key[:-1]+'\s'].append(wort)
            continue

        if key.lower() + 'en' in words or key.title() + 'en' in words:
            grossklein[key+'(en)'].append(wort)
            continue

        if key.lower() + 'e' in words or key.title() + 'e' in words:
            grossklein[key+'(e)'].append(wort)
            continue

# Test auf fremdsprachige Teilwörter::

        if key.lower() in words_fremd:
            fremd[key].append(wort)
            continue

# Teilwort mit Vorsilbe::

        # ohne_vorsilbe = ''
        # for silbe in praefixe:
        #     if (teil.lower().replace(u'·', u'-').startswith(silbe+'-')
        #         and (key[len(silbe):] in words
        #              or key[len(silbe):].title() in words)):
        #         ohne_vorsilbe = key[len(silbe):]
        #         # print teil.encode('utf8'),
        #         break
        # if ohne_vorsilbe:
        #     vorsilben[key].append(wort)
        #     continue

# Teilwort nicht gefunden::

        unbekannt[key].append(wort)


# Ausgabe
# =======
#
# ::

def testausgabe(checkdict):
    checkliste = ['%3d %-15s %s' %
                  (len(checkdict[key]), key, ', '.join(checkdict[key]))
                  for key in sorted(checkdict.keys())]
    checkliste.sort()
    return u'\n'.join(checkliste).encode('utf8') + '\n'

# Auswertung
# ==========
#
# ::

print 'Einträge in der Wortliste:', len(wortliste)
print 'Gesamtwortzahl (w*german+Wortliste, %s):' % sprachvariante, len(words)

print 'Teilwort mit anderer Groß-/Kleinschreibung:', len(grossklein),
print '-> siehe Datei "wortteile/-grossklein"'
grossklein_file = file('wortteile/-grossklein', 'w')
grossklein_file.write(testausgabe(grossklein))

# print 'Teilwort mit zusätzlicher Vorsilbe:', len(vorsilben)
# vorsilben_file = file('teilwort-vorsilben', 'w')
# vorsilben_file.write(testausgabe(vorsilben))

print 'fremdsprachige Teilwörter:', len(fremd),
print '-> siehe Datei "wortteile/-fremd"'
fremd_file = file('wortteile/-fremd', 'w')
fremd_file.write(testausgabe(fremd))

print 'Teilwort nicht gefunden:', len(unbekannt),
print '-> siehe Datei "wortteile/-unbekannt"'
unbekannt_file = file('wortteile/-unbekannt', 'w')
unbekannt_file.write(testausgabe(unbekannt))


# Quellen
# =======
#
# .. [BCP47]  A. Phillips und M. Davis, (Editoren.),
#    `Tags for Identifying Languages`, http://www.rfc-editor.org/rfc/bcp/bcp47.txt
#
# .. _Wortliste der deutschsprachigen Trennmustermannschaft:
#    http://mirrors.ctan.org/language/hyphenation/dehyph-exptl/projektbeschreibung.pdf
#
