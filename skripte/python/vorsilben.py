#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2012 Günter Milde.
# :Licence:   This work may be distributed and/or modified under
#             the conditions of the `LaTeX Project Public License`,
#             either version 1.3 of this license or (at your option)
#             any later  version.
# :Version:   0.1 (2012-02-07)

# vorsilben.py: Bestimmung von Vorsilben
# ============================================================
# 
# ::

"""Analyse der Trennstellen in der `Wortliste`"""

# .. contents::
# 
# Vorspann
# ========
# 
# Importiere Python Module::

import re       # Funktionen und Klassen für reguläre Ausdrücke
from werkzeug import WordFile, join_word

# Ausgangsbasis
# =============
# 
# Die freie `Wortliste der deutschsprachigen Trennmustermannschaft`_
# ("Lehmansche Liste")
# 
# ::

wordfile = WordFile('../../wortliste') # volle Liste (≅ 400 000 Wörter

# Trennzeichen
# ------------
# 
# Die Trennzeichen der Wortliste sind
# 
# == ================================================================
# \· ungewichtete Trennstellen (solche, wo noch niemand sich um die
#    Gewichtung gekümmert hat)
# .  unerwünschte Trennstellen (sinnverwirrend), z.B. Ur-in.stinkt
# =  Haupttrennstellen
# \- Nebentrennstellen
# _  ungünstige Nebentrennstellen, z.B. Pol=ge_bie-te
# == ================================================================
# 
# 
# Sprachvarianten
# ---------------
# 
# Angabe der Sprachvariante nach [BCP47]_::

sprachvariante = 'de-1901'
# sprachvariante = 'de-2006'  # Reformschreibung
# sprachvariante = 'de-CH'    # Schweiz (ohne ß)


# Ausnahmen  
# ---------
# 
# Wörter mit "Vorsilbenkandidaten" die keine Vorsilben sind::

ausnahmen = ('Aussee', 'Auster')


# 1. Durchlauf: Sortieren
# =======================
# 
# Mengen der Wörter der Sprachvariante::

words = {}

# Liste der Datenfelder::

wortliste = []


for fields in wordfile:

    words[fields[0]] = fields # Eintrag in Wörterbuch mit Wort als key
    # TODO: Wörter nach Sprachvariante sortieren?
    wortliste.append(fields)

# print len(wortliste), len(words), "Wörter"

# TODO: add Wortlisten 
# /usr/share/dict/ngerman, /usr/share/dict/ogerman
 
# 
# 2. Durchlauf: Analyse
# =====================
# 
# Suche nach Wörtern mit (Vor-) Silbe::

silbe = 'aus'

pattern = '[%s%s]%s' % (silbe[0].upper(), silbe[0], silbe[1:]) # [Aa]us

# Sortierung in::

fertig = []             # Restwort existiert
test = []               # zum Test neuer Regeln
unbestimmt    = []      # Restwort nicht in der Wortliste


for entry in wortliste:

# Sprachvariante::

    wort = entry.get(sprachvariante)
    if wort is None: # Wort existiert nicht in der Sprachvariante
        continue

# Test auf Vorsilben
# ------------------
# 
# Suche nach der Silbe am Anfang eines Wortes oder Teilwortes::

    match = re.match(u'(.*=|)?(%s)[-·](.+)'%pattern, wort)
    if match:
        vorspann = match.group(1) or ''
        silbe = match.group(2)
        rest = match.group(3)
        ersetzung = '%s%s|%s' %(vorspann, silbe, rest)


# Wenn der Wortbestandteil hinter der getesteten Silbe im Wörterbuch
# vorhanden ist, kann davon ausgegangen werden, daß es sich um eine Vorsilbe
# handelt::

        restwort = join_word(rest)
        # Groß/Kleinschreibung übertragen
        if wort[0].isupper(): # str.title() geht nicht wegen der Trennzeichen
            restwort = restwort.title()

        if restwort in words:
            if not re.search(u'[-=_]', restwort):  # Restwort ist ungewichtet
                einzelwort = words[join_word(restwort)].get(sprachvariante)
                rest = rest[0] + einzelwort[1:]
                ersetzung = '%s%s|%s' %(vorspann, silbe, rest)
            entry.set(ersetzung, sprachvariante)
            fertig.append(ersetzung)
            continue

# Teste den Wortbestandteil bis zur nächsten Wortfuge::

        if '=' in rest:
            restwort = join_word(rest.split('=')[0])
            # Groß/Kleinschreibung übertragen
            if wort[0].isupper():
                restwort = restwort.title()
            if restwort in words or (
                    restwort.endswith(u's') and restwort[:-1]  in words):
                entry.set(ersetzung, sprachvariante)
                fertig.append(ersetzung)
                continue

# Teste ohne Berücksichtigung der Groß/Kleinschreibung::

        if restwort.lower() in words or restwort.title() in words or (
            '=' in rest and restwort.endswith(u's') and
            (restwort[:-1].lower() in words
             or restwort[:-1].title() in words)):
            # Extra abspeichern für manuelle Qualitätskontrolle
            test.append(ersetzung)
            continue


# unklarer Fall::

        unbestimmt.append(ersetzung)


# Ausgabe
# =======
# 
# ::

completed_file = file('vorsilbe-OK', 'w')
completed_file.write(u'\n'.join(unicode(entry) for entry in fertig
                               ).encode('utf8'))
completed_file.write('\n')

test_file = file('vorsilbe-test', 'w')
test_file.write(u'\n'.join(test).encode('utf8'))
test_file.write('\n')

uncompleted_file = file('vorsilbe-kandidaten', 'w')
uncompleted_file.write(u'\n'.join(unbestimmt).encode('utf8'))
uncompleted_file.write('\n')


# Auswertung
# ==========
# 
# ::

print "Gesamtwortzahl (traditionelle Rechtschreibung)", len(words)
print "Mit (Vor-) Silbe", silbe, len(unbestimmt) + len(fertig)
print "Restwort erkannt", len(fertig)
print "Restwort mit anderer Groß-/Kleinschreibung", len(test)
print "Kandidaten (Restwort nicht gefunden)", len(unbestimmt)
