#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2012 Günter Milde.
# :Licence:   This work may be distributed and/or modified under
#             the conditions of the `LaTeX Project Public License`,
#             either version 1.3 of this license or (at your option)
#             any later  version.
# :Version:   0.1 (2012-02-07)

# vorsilben_in_teilwoertern.py: Bestimmung von Vorsilben
# ============================================================
#
# Suche nach Wörtern beginnend mit::

term = u'neo'  # Angabe mit Trennzeichen, z.B. 'pa-ra'

# in der Datei ``teilwoerter-<sprachtag>.txt`` und analysiere das
# folgende (Teil)wort. Schreibe Änderungen in die Datei ``teilwoerter.patch``
# wobei alle Vorkommnisse des gesuchten Präfix am Anfang eines Wort oder nach
# anderen Präfixen mit ``<`` markiert sind, es sei den das Wort (ohne bereits
# markierte Präfixe) ist in der Datei ``wortteile/vorsilbenausnahmen``
# gelistet. Die Ausgabe der Analyse hilft bei der Vervollständigung der
# Ausnahmeliste.
#
# Sprachvarianten
# ---------------
#
# Sprach-Tag nach [BCP47]_::

# sprachvariante = 'de-1901'
sprachvariante = 'de-1996'  # Reformschreibung
# sprachvariante = 'de-x-GROSS'    # ohne ß (Großbuchstaben und Kapitälchen)


# Vorbetrachtungen
# ----------------
#
# Die Unterscheidung von Vorsilben (Präfixen) von
# Teilwörtern in Komposita ist im Deutschen nicht eindeutig.
# (Siehe z.B. `Präfixe im Deutschen` (Diss. 1999)
# http://kups.ub.uni-koeln.de/528/1/11w1043.pdf
#
#   Bei Verbalpräfixen ist zu unterscheiden zwischen Präfixen im engeren Sinne
#   und Partikeln. Während Erstere untrennbar mit dem Verbstamm verbunden sind
#   (z. B. sich be-nehmen), können Letztere in bestimmten Konstruktionen vom
#   Stamm gelöst werden (z. B. ab-nehmen: ich nehme den Hut ab).
#
#   -- http://de.wikipedia.org/wiki/Präfix
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
# ``<`` nur für Präfixe, die keine eigenständigen Wörter sind:
#
# | An=fangs==ver<dacht
# | Ein=gangs==lied
# | Ge<samt==be<triebs=rats===chef
# | Her<aus=ge-ber
# | Straf==voll=zugs===an-stalt
# | un<voll=stän-dig
# | Vor=sor-ge==voll=macht
#
# ``<`` für "eng gebundene" Präfixe:
#
# | An<fangs=ver<dacht
# | Ein<gangs=lied
# | Ge<samt<<be<triebs=rats==chef
# | Her<aus=ge-ber
# | Straf=voll<zugs==an-stalt
# | un<<voll<stän-dig
# | Vor<sor-ge=voll<macht
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
import codecs

from wortliste import WordFile, join_word
from analyse import read_teilwoerter
from abgleich_praefixe import udiff  # unified diff aus Vergleich zweier Listen

# sys.stdout mit UTF8 encoding.
sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)

# Ausnahmen
# ---------
#
# Wörter mit "Vorsilbenkandidaten" die keine Vorsilben sind::

ausnahmen = set(line.decode('utf8').strip()
                for line in open('wortteile/vorsilbenausnahmen')
                if not line.startswith('#'))

# Ausgangsbasis
# -------------
#
# Teilwörter für die angegebene Sprachvariante (extrahiert aus der
# `Wortliste` mit ``analyse.py``)::

words = read_teilwoerter(path='teilwoerter-%s.txt'%sprachvariante)

# Grundwörter welche Vorsilben folgen::

grundwoerter = set()
for wort in words.woerter():
    match = re.search(ur'\<([^<]+)$', wort)
    if match:
        grundwoerter.add(match.group(1))

# print grundwoerter
# print len(words.trennvarianten), len(grundwoerter)
# sys.exit()

# Teilwörterdatei für die zeilenweise Modifikation::

teilwoerter = list(io.open('teilwoerter-%s.txt'%sprachvariante, 
                           encoding='utf8'))
neuteile = [] # Übertrag

# Analyse
# =======
#
# Muster für die gesuchte Silbe unabhängig von der Großschreibung::

pattern = '[%s%s]%s' % (term[0].upper(), term[0], term[1:]) # aus -> [Aa]us

# Sortierung in::

ist_ausnahme = []         # erkannte Ausnahmen
# teil_und_grundwort = [] # Restwort existiert als Teil- und Grundwort
mit_teilwort = []         # Restwort existiert als Teilwort
mit_stamm = []            # Restwort existiert mit anderer Vorsilbe
mit_Teilwort = []         # Restwort mit anderer Groß-/Kleinschreibung
ohne_teilwort = []        # Restwort nicht in der Wortliste

# Iteration über bekannte Einzelwörter
# ------------------------------------
# ::

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

    match = re.match(ur'(.+\<)?(%s)[-·]([^<]+)$'%pattern, wort)
    if not match:
        neuteile.append(line)
        continue

# Zerlegung::

    praefix = match.group(1) or u'' # bereits markierter Präfix
    kandidat = match.group(2)         # Präfixkandidat
    rest = match.group(3)

    if praefix:
        ersetzung = u'%s%s<%s' % (praefix, kandidat, rest)
    else:
        ersetzung = u'%s<%s' % (kandidat, rest)
    key = join_word(rest.split(u'=')[0])
    if wort[0].isupper():
        key = key.title()

# Sortieren und ggf. Präfix markieren
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Wenn der Wortbestandteil hinter dem Präfixkandidaten
#
# * im Wörterbuch vorhanden ist,
# * mit anderer Großschreibung im Wörterbuch vorhanden ist, oder
# * als Stamm hinter anderen Präfixen vorkommt
#
# kann davon ausgegangen werden, daß es sich bei dem Kandidaten um einen
# Präfix handelt.
#
# Ausnahmen aus der Ausnahmeliste::

    if join_word(kandidat+rest.split(u'>')[0]) in ausnahmen:
        ist_ausnahme.append(wort)

# Ausnahme Praefixkandidat + Suffix (z.B. ein>fach)::

    elif rest.startswith('>'):
        ist_ausnahme.append(wort)

# ::

    elif key in words.trennvarianten:
        mit_teilwort.append(ersetzung)
        # Zeile ändern:
        line = u'%s %s\n' % (ersetzung, tags)

    elif key in grundwoerter:
        mit_stamm.append(ersetzung)
        # Zeile ändern:
        line = u'%s %s\n' % (ersetzung, tags)

# Teste ohne Berücksichtigung der Groß/Kleinschreibung::

    elif (key.lower() in words.trennvarianten
          or key.title() in words.trennvarianten):
        # Extra abspeichern für manuelle Qualitätskontrolle
        mit_Teilwort.append(ersetzung)
        # Zeile ändern:
        line = u'%s %s\n' % (ersetzung, tags)

# key nicht gefunden::

    else:
        ohne_teilwort.append(ersetzung)
        # Zeile ändern:
        line = u'%s %s\n' % (ersetzung, tags)

    neuteile.append(line)


# Auswertung
# ==========
#
# ::

print u'Mit (Vor-) Silbe: "%s"' % term,
print len(mit_teilwort) + len(mit_Teilwort) + len(ohne_teilwort)
print

print u'* erkannte Ausnahmen:', len(ist_ausnahme)
for wort in ist_ausnahme:
    print wort
print

print u'* Restwort existiert als Teilwort:', len(mit_teilwort)
for wort in mit_teilwort:
    print wort
print

print u'* Restwort existiert mit anderem Präfix:', len(mit_stamm)
for wort in mit_stamm:
    print wort
print

print u'* Restwort mit anderer Groß-/Kleinschreibung:', len(mit_Teilwort)
for wort in mit_Teilwort:
    print wort
print

print u'* Restwort nicht gefunden:', len(ohne_teilwort)
for wort in ohne_teilwort:
    print wort

# Ausgabe
# =======

# Patch erstellen::

patch = udiff(teilwoerter, neuteile, 'teilwoerter', 'teilwoerter-neu')
if patch:
    # print patch
    patchfile = open('teilwoerter.patch', 'w')
    patchfile.write(patch + '\n')
else:
    print u'empty patch'

# Nach Durchsicht können die Änderungen mit ``patch
# teilwoerter-<sprachtag>.txt < teilwoerter.patch`` in die Teilwortdatei
# übernommen werden.

# Mit dem Skript ``abgleich_teilwoerter.py`` können dann die Kategorisierungen
# in alle Vorkommen der Teilwörter in der ``wortliste`` übertragen werden.
