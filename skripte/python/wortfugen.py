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

# Globale Variablen
# -----------------

# Ausgangsbasis
# -------------
#
# Die freie `Wortliste der deutschsprachigen Trennmustermannschaft`_
# ("Lehmansche Liste")::

wordfile = WordFile('../../wortliste') # ≅ 400 000 Einträge/Zeilen

# Sprachvarianten
# ---------------
#
# Sprach-Tag nach [BCP47]_::

sprachvariante = 'de-1901'         # "traditionell"
# sprachvariante = 'de-1996'       # Reformschreibung
# sprachvariante = 'de-x-GROSS'    # ohne ß (Großbuchstaben und Kapitälchen)


# Textdateien mit Wortbestandteilen
# ---------------------------------
#
# * Ein Wortteil/Zeile
# * Groß/Kleinschreibung unterschieden
# * Kodierung: utf8 (bis auf 'ogerman')

# Wörterbucher für die Rechtschreibprüfprogramme Ispell/Aspell
# (in Debian in den Paketen "wngerman" und "wogerman").
# Unterschieden Groß-/Kleinschreibung und beinhalten auch kurze Wörter. ::


if sprachvariante == 'de-1996':
    wgerman = set(line.rstrip().decode('utf8')
                  for line in open('/usr/share/dict/ngerman'))
elif sprachvariante == 'de-1901':
    wgerman = set(line.rstrip().decode('latin-1')
                  for line in open('/usr/share/dict/ogerman'))


# Erstsilben: Wörter, die häufig als erste
# Silbe eines Wortes (aber nicht oder nur selten als Teilwörter) auftreten
# aber keine Vorsilben sind ::

erstsilben = set(line.rstrip().decode('utf8') for line in open('erstsilben.txt'))

# Vorsilben (auch mehrsilbige Präfixe)::

vorsilben = set(line.rstrip().decode('utf8') for line in open('vorsilben.txt'))

# Endsilben, die keine eigenständigen Wörter sind
# (nicht (nur) Endungen im morphologischen Sinne, sondern ganze Silben)::

endsilben = set(line.rstrip().decode('utf8') for line in open('endsilben.txt'))

# Teilwörter: Wörter die in der Wortliste nur in Wortverbindungen vorkommen
# (zu kurz, keine eigenständigen Wörter, andere Großschreibung)
# und auch im Rechtschreibwörterbuch (wgerman) fehlen ::

teilwoerter = set(line.rstrip().decode('utf8')
                  for line in open('teilwoerter.txt'))


# Wörter, die in Zusammensetzungen verkürzt vorkommen (und daher nicht an
# letzter Stelle), z.b. "Farb"::

kurzwoerter = set(line.rstrip().decode('utf8')
                  for line in open('kurzwoerter.txt'))

# Bereits gesammelte Neueinträge::

neu_todo = set(join_word(line.rstrip().decode('utf8'))
               for line in open('neu.todo'))

# Einträge der "Wortliste"
# ------------------------
# ::

wortliste = []

# Wörterbuch zum Aufsuchen der Teilwörter
# ---------------------------------------

# initialisiert mit Ausnahmen und Wörtern der Rechtschreiblisten::

words = dict([(w, '') for w in wgerman.union(teilwoerter, kurzwoerter, neu_todo)])

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

# Suche (zunächst) nur nach Wörtern mit Fugen-s::

        # if not erstwort.endswith('s'):
        #     continue

# Restliche zweisilbigen Wörter:

        # print ' '.join([erstwort,zweitwort]).encode('utf8')
        # continue


# Teilwort ohne Trennung, Groß/Kleinschreibung übertragen::

        try:
            erstkey = join_word(erstwort)
            zweitkey = join_word(zweitwort)
        except AssertionError:  # Spezialtrennung
            continue
        if wort[0].istitle():
            zweitkey = zweitkey.title()

# Suche als Einzelwort::

        if (erstkey in words and erstkey not in erstsilben
            and erstkey not in vorsilben
            and zweitkey in words
            and zweitkey.lower() not in endsilben
            and zweitkey not in kurzwoerter
           ):
            print str(entry), (u'%s=%s'% (erstkey,zweitkey)).encode('utf8')
            entry.set('='.join((erstwort, zweitwort.lower())), sprachvariante)

# Vorsilben::

        # if erstkey.lower() in vorsilben and zweitkey in words:
        #     print str(entry), (u'%s-%s'% (erstkey,zweitkey)).encode('utf8')
        #     entry.set('-'.join((erstwort, zweitwort.lower())), sprachvariante)

# endsilben::

        # if erstkey in words and zweitkey.lower() in endsilben:
        #     print str(entry), (u'%s-%s'% (erstkey,zweitkey)).encode('utf8')
        #     entry.set('-'.join((erstwort, zweitwort.lower())), sprachvariante)

# # Neueintragskandidaten::
# 
#         if (erstkey in words 
#             and erstkey not in erstsilben
#             and zweitkey not in words
#             and zweitkey.lower() not in endsilben:
#             # if erstkey in vorsilben:
#             #     print ("%s  (%s|%s)" %
#             #            (zweitkey, erstwort, zweitwort)).encode('utf8')
#             else:
#                 print ("%s  (%s-%s)" %
#                        (zweitkey, erstwort, zweitwort)).encode('utf8')


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
