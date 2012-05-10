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
# Die Unterscheidung von Vorsilben (Präfixen) von
# Teilwörtern in Komposita ist im Deutschen nicht eindeutig.
# (Siehe z.B. `Präfixe im Deutschen` (Diss. 1999)
# http://kups.ub.uni-koeln.de/528/1/11w1043.pdf
#
# Bei Verbalpräfixen ist zu unterscheiden zwischen Präfixen im engeren Sinne
# und Partikeln. Während Erstere untrennbar mit dem Verbstamm verbunden sind
# (z. B. sich be-nehmen), können Letztere in bestimmten Konstruktionen vom
# Stamm gelöst werden (z. B. ab-nehmen: ich nehme den Hut ab).
# [http://de.wikipedia.org/wiki/Präfix]
#
# Wir brauchen eine pragmatische Entscheidung für die optimale Markierung von
# Trennstellen nach Präfixen in der "Wortliste". Kriterien:
#
# * einfach
# * korrekt
# * gut lesbar für Mensch und Maschine
#
# Alternativen:
#
# kein separates Trennzeichen:
#
# | An=fangs==ver=dacht
# | Ein=gangs==lied
# | Ge=samt===be=triebs==rats====chef
# | Her=aus==ge-ber
# | Straf==voll=zugs===an-stalt
# | un==voll=stän-dig
# | Vor=sor-ge==voll=macht
#
# ``|`` nur für Präfixe, die keine eigenständigen Wörter sind:
#
# | An=fangs==ver=|acht
# | Ein=gangs==lied
# | Ge|samt==be|triebs=rats===chef
# | Her|aus=ge-ber
# | Straf==voll=zugs===an-stalt
# | un||voll=stän-dig
# | Vor=sor-ge==voll=macht
#
# ``|`` für "eng gebundene" Präfixe:
#
# | An|fangs=ver|dacht
# | Ein|gangs=lied
# | Ge|samt||be|triebs=rats==chef
# | Her|aus=ge-ber
# | Straf=voll|zugs==an-stalt
# | un||voll|stän-dig
# | Vor|sor-ge=voll|macht
#
# ::

"""Analyse der Trennstellen in der `Wortliste`"""

# .. contents::
#
# Vorspann
# ========
#
# Importiere Python Module::

import io       # (De-) Kodierung beim Schreiben/Lesen von Dateien
import re       # Funktionen und Klassen für reguläre Ausdrücke
import sys      # sys.exit() zum Abbruch vor Ende (für Testzwecke)
import difflib  # unified diff aus Vergleich zweier Listen
import codecs
from copy import deepcopy

from werkzeug import WordFile, join_word
from analyse import read_teilwoerter

# sys.stdout mit UTF8 encoding.
sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)

# Sprachvarianten
# ---------------
#
# Sprach-Tag nach [BCP47]_::

sprachvariante = 'de-1901'
# sprachvariante = 'de-2006'  # Reformschreibung
# sprachvariante = 'de-x-GROSS'    # ohne ß (Großbuchstaben und Kapitälchen)


# Ausnahmen
# ---------
#
# Wörter mit "Vorsilbenkandidaten" die keine Vorsilben sind::

ausnahmen = set(line.decode('utf8').strip() 
        
                for line in open('wortteile/vorsilbenausnahmen'))

# "Nachwörter" (Wörter die nicht ohne Vorsilben vorkommen)::

nachwoerter = (#'bau', 'geh',
               'Gleichs',   # Aus|gleichs
               'Nahme',     # An|nahme
               'Stattung',  # Er|stattung
              )

# Ausgangsbasis
# -------------

# Teilwörter für die angegebene Sprachvariante (extrahiert aus der
# `Wortliste` mit ``analyse.py``)::

words = read_teilwoerter(path='teilwoerter-%s.txt'%sprachvariante)

# Grundwörter welche Vorsilben folgen::

grundwoerter = set()
for wort in words.trennungen.values():
    match = re.search(ur'\|([^|]+)$', wort[-1])
    # if len(wort) > 1:
    #     print wort
    if match:
        grundwoerter.add(match.group(1))

# print grundwoerter
# print len(trennungen), len(grundwoerter)
# sys.exit()

# Teilwörterdatei für die zeilenweise Modifikation::

teilwoerter = io.open('teilwoerter-%s.txt'%sprachvariante, encoding='utf8')
neuteile = [] # Übertrag

# Analyse
# =======
#
# Suche nach Wörtern mit (Vor-) Silbe::

silbe = 'her'

# elek-tro, öko, bio, geo, zoo, ra-dio, ar-chäo, 
# kontra=

pattern = '[%s%s]%s' % (silbe[0].upper(), silbe[0], silbe[1:]) # [Aa]us

# Sortierung in::

ist_ausnahme = []       # erkannte Ausnahmen
teil_und_grundwort = [] # Restwort existiert als Teil- und Grundwort
mit_teilwort = []       # Restwort existiert als Teilwort
mit_grundwort = []      # Restwort existiert mit anderer Vorsilbe
grossklein = []         # Restwort mit anderer Groß-/Kleinschreibung
kandidat = []           # Restwort nicht in der Wortliste

# Iteration über bekannte Einzelwörter::

for line in teilwoerter:
    try:
        wort, tags = line.split()
    except ValueError:
        if line.startswith('#'):
            neuteile.append(line)
            continue
        else:
            raise
            

# Test auf Vorsilben
# ------------------
#
# Suche nach der Silbe am Anfang eines Teilwortes::

    match = re.match(ur'(.+\|)?(%s)[-·](.+)'%pattern, wort)
    if not match:
        neuteile.append(line)
        continue

# Zerlegung::

    vorsilbe = match.group(1) or ''
    silbe = match.group(2)
    rest = match.group(3)
    if vorsilbe:
        ersetzung = '%s|%s|%s' %(vorsilbe, silbe, rest)
    else:
        ersetzung = '%s%s|%s' %(vorsilbe, silbe, rest)
    key = join_word(rest)
    if wort[0].isupper():
        key = key.title()

# Ausnahmen aus der Ausnahmeliste::

    if join_word(silbe+rest) in ausnahmen:
        ist_ausnahme.append(wort)

# Wenn der Wortbestandteil hinter der getesteten Silbe im Wörterbuch
# vorhanden ist, kann davon ausgegangen werden, daß es sich um eine Vorsilbe
# oder ein Teilwort handelt::

    elif key in words.trennungen and key in grundwoerter:
        teil_und_grundwort.append(ersetzung)
        # Zeile ändern:
        line = u'%s %s\n' % (ersetzung, tags)

    elif key in words.trennungen:
        mit_teilwort.append(ersetzung)
        # Zeile ändern:
        line = u'%s %s\n' % (ersetzung, tags)

    elif key in grundwoerter:
        mit_grundwort.append(ersetzung)
        # Zeile ändern:
        line = u'%s %s\n' % (ersetzung, tags)

# Teste ohne Berücksichtigung der Groß/Kleinschreibung::

    elif key.lower() in words.trennungen or key.title() in words.trennungen:
        # Extra abspeichern für manuelle Qualitätskontrolle
        grossklein.append(' '.join((ersetzung, key)))
        # Zeile ändern:
        line = u'%s %s\n' % (ersetzung, tags)

# key nicht gefunden::

    else:
        kandidat.append(ersetzung)
        # Zeile ändern:
        line = u'%s %s\n' % (ersetzung, tags)

    neuteile.append(line)


# Auswertung
# ==========
#
# ::

print u'Mit (Vor-) Silbe: "%s"' % silbe, 
print len(mit_teilwort) + len(grossklein) + len(kandidat)
print

print u'* erkannte Ausnahmen:', len(ist_ausnahme)
for wort in ist_ausnahme:
    print wort
print

print u'* Grundwort existiert als Teil- und Grundwort:', len(teil_und_grundwort)
for wort in teil_und_grundwort:
    print wort
print

print u'* Grundwort existiert als Teilwort:', len(mit_teilwort)
for wort in mit_teilwort:
    print wort
print

print u'* Grundwort existiert mit anderer Vorsilbe:', len(mit_grundwort)
for wort in mit_grundwort:
    print wort
print

print u'* Grundwort mit anderer Groß-/Kleinschreibung:', len(grossklein)
for wort in grossklein:
    print wort
print

print u'* Grundwort nicht gefunden:', len(kandidat)
for wort in kandidat:
    print wort

# Ausgabe
# =======
# ::

ausgabedatei = io.open('teilwoerter-neu', mode='w', encoding='utf8')
ausgabedatei.writelines(neuteile)
