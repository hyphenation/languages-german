#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2011 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# neu.py: Neueinträge prüfen und vorbereiten
# ==========================================
#
# ::

"""Neueinträge prüfen und vorbereiten."""

# Simples Skript zur Vorbereitung neuer Einträge.
#
# Die in einer Datei (ein Neueintrag pro Zeile) gesammelten Vorschläge werden
# auf Neuwert getestet.
#
# Ein Eintrag der Form ``neuwort;neu-wort`` wird erstellt:
#
# * Vorhandene Wörter werden ignoriert
#   (unabhängig von der Groß-/Kleinschreibung).
# * Trennstellen werden aus der "Vorschlagsdatei" übernommen.
# * Das ungetrennte Wort wird vorangestellt (durch Semikolon getrennt).
# * Zur Zeit keine Unterstützung für Sprachvarianten.
#
# Die Liste der Neueinträge wird ausgegeben. Sie kann and die Wortliste
# angehängt werden. Nach einem Sortieren (z.B. mit sort.py) sind die
# Neueinträge eingearbeitet.
#
# ::

from werkzeug import WordFile, join_word

# Einlesen der Einträge der Wortliste:
#
# ::

wordfile = WordFile('../../wortliste')
words = wordfile.asdict()

# Abarbeiten der Liste von Neueintragskanditaten::

for line in open('neueinträge.todo'):

# Prüfen, ob der Eintrag bereits existiert
#
# ::

    neueintrag = line.decode('utf8').strip()
    wort = join_word(neueintrag)
    if wort.lower() not in words and wort.title() not in words:
        print (u'%s;%s' % (wort, neueintrag)).encode('utf8')
    # print join_word(wort), ';', wort
