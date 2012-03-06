#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2011 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# wortfugen.py: Teste unkategorisierte Trennstellen auf Wortfugen
# ===============================================================

# ::

"""Suche nach "Teilwortkandidaten" in der `Wortliste`"""

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

from werkzeug import WordFile, join_word, udiff

# Ausgangsbasis
# -------------
#
# Die freie `Wortliste der deutschsprachigen Trennmustermannschaft`_
# ("Lehmansche Liste")::

wordfile = WordFile('../../wortliste') # ≅ 400 000 Einträge/Zeilen

# Wörterbucher für die Rechtschreibprüfprogramme Ispell/Aspell
# (in Debian in den Paketen "wngerman" und "wogerman").
# Unterschieden Groß-/Kleinschreibung und beinhalten kurze Wörter. ::

wgerman = {'de-1996': ('/usr/share/dict/ngerman', 'utf8'),
                    'de-1901': ('/usr/share/dict/ogerman', 'latin-1'),
                   }


# Sprachvarianten
# ---------------
#
# Sprach-Tag nach [BCP47]_::

sprachvariante = 'de-1901'         # "traditionell"
# sprachvariante = 'de-1996'       # Reformschreibung
# sprachvariante = 'de-x-GROSS'    # ohne ß (Großbuchstaben und Kapitälchen)


# Globale Variablen
# -----------------

vorsilben = set()
for v in open('vorsilben.txt'):
    vorsilben.add(v.decode('utf8').rstrip())

endungen = set()
for e in open('endungen.txt'):
    endungen.add(e.decode('utf8').rstrip())

# Häufige Teilwörter die im Wörterbuch nicht vorkommen
# (zu kurz, oder keine eigenständigen Wörter)::

ausnahmen = (u'Bus',
             u'End',
             u'Erd',
             u'Farb',
             u'Grenz',
             u'Kontroll',
             u'Lehr',
             u'Leit',
             u'Ost',
             u'Sach',
             u'Schul',
             u'Süd',
             u'Wohn',
             u'bewerbs',
             u'hör',
             u'nahme',
             u'ost',
             u'Sach',
             u'schul',
             u'seh',
            )


# Einträge der "Wortliste"::

wortliste = []

# Wörterbuch zum Aufsuchen der Restwörter,
# initialisiert mit Ausnahmen und Wörtern der Rechtschreiblisten::

words = dict([(a, '') for a in ausnahmen])

# Wörterbuch zum Aufsuchen der Restwörter,
# initialisiert mit Ausnahmen und Wörtern der Rechtschreiblisten::

words = {}

for word in open(wgerman[sprachvariante][0]):
    word = word.decode(wgerman[sprachvariante][1]).rstrip()
    words[word] = ''


for wort in open('neu.todo'):
    words[wort.decode('utf8').rstrip()] = ''

# Sortierung in::

unbekannt = defaultdict(list)  # Teilwörter nicht in der Wortliste
grossklein = defaultdict(list) # Teilwörter mit anderer Groß/Kleinschreibung


# 1. Durchlauf: Erstellen der Ausgangslisten
# ==========================================
#
# ::

for entry in wordfile:
    if entry.lang_index(sprachvariante) is not None:
        words[entry[0]] = entry # Eintrag in Wörterbuch mit Wort als key
    wortliste.append(entry)


# 2. Durchlauf: Analyse
# =====================
#
# Durchlaufe alle Einträge::

wortliste_alt = deepcopy(wortliste)

for entry in wortliste:

# Wort mit Trennungen in Sprachvariante::

    wort = entry.get(sprachvariante)
    if wort is None: # Wort existiert nicht in der Sprachvariante
        continue

    if u'·' not in wort:  # keine unkategorisierte Trennstelle
        continue

# Trenne an unkategorisierten Trennstellen (markiert durch '·')::

    teile = wort.split(u'·')

# Zunächst nur 2-silbige Wörter::

    if len(teile) != 2:
        continue

# Wortteile analysieren und ggf. Trennungen übertragen

    for i in range(len(teile)-1):
        erstwort = u'·'.join(teile[:i+1])
        zweitwort =  u'·'.join(teile[i+1:])


# Restliche zweisilbigen Wörter:

        # print ' '.join([erstwort,zweitwort]).encode('utf8')
        # continue


# Suche (zunächst) nur nach Wörtern mit Fugen-s::

        # if not erstwort.endswith('s'):
        #     continue

# Teilwort ohne Trennung, Groß/Kleinschreibung übertragen::

        try:
            erstkey = join_word(erstwort)
            zweitkey = join_word(zweitwort)
        except AssertionError:  # Spezialtrennung
            continue
        if wort[0].istitle():
            zweitwort = zweitwort[0].title() + zweitwort[1:]

# Suche als Einzelwort::

        # if (erstkey in words and zweitkey in words 
        #     and erstkey.lower() not in vorsilben
        #     and zweitkey.lower() not in endungen):
        #     print str(entry), (u'%s=%s'% (erstkey,zweitkey)).encode('utf8')
        #     entry.set('='.join((erstwort, zweitwort.lower())), sprachvariante)


# Suche nach Vorsilben und Endungen::

        # if erstkey.lower() in vorsilben and zweitkey in words:
        #     print str(entry), (u'%s-%s'% (erstkey,zweitkey)).encode('utf8')
        #     entry.set('-'.join((erstwort, zweitwort.lower())), sprachvariante)

        # if erstkey in words and zweitkey.lower() in endungen:
        #     print str(entry), (u'%s-%s'% (erstkey,zweitkey)).encode('utf8')
        #     entry.set('-'.join((erstwort, zweitwort.lower())), sprachvariante)

# Neueintragskandidaten::

        if (erstkey in words and zweitkey not in endungen
           and len(zweitkey) > 3):
            print " ".join([erstwort, zweitwort]).encode('utf8')
            
            


# Ausgabe
# ==========
#
# Ein Patch für die wortliste::


patch = udiff(wortliste_alt, wortliste, 'wortliste', 'wortliste-neu')
if patch:
    # print patch
    patchfile = open('../../wortliste.patch', 'w')
    patchfile.write(patch + '\n')
else:
    print "empty patch"

