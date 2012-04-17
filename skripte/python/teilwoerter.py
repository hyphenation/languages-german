#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2012 Günter Milde.
# :Licence:   This work may be distributed and/or modified under
#             the conditions of the `LaTeX Project Public License`,
#             either version 1.3 of this license or (at your option)
#             any later  version.
# :Version:   0.1 (2012-02-07)

# teilwoerter.py: Test und Komplettierung von Wortteilen/Teilwörtern
# ==================================================================
# 
# ::

"""Erkennen und Markieren von Komposita in der `Wortliste`"""

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

# sprachvariante = 'de-1901'         # "traditionell"
sprachvariante = 'de-1996'       # Reformschreibung
# sprachvariante = 'de-x-GROSS'    # ohne ß (Großbuchstaben und Kapitälchen)


# Globale Variablen
# -----------------
# 
# Häufige Teilwörter die im Wörterbuch nicht vorkommen
# (zu kurz, oder keine eigenständigen Wörter)::

ausnahmen = ('Bus',
             'End',
             'Erd',
             'Farb',
             'Grenz',
             'Kontroll',
             'Lehr',
             'Leit',
             'Ost',
             'Sach',
             'Schul',
             'Süd',
             'Wohn',
             'bewerbs',
             'hör',
             'nahme',
             'ost',
             'Sach',
             'schul',
             'seh',
            )


# Einträge der "Wortliste"::

wortliste = []

# Wörterbuch zum Aufsuchen der Restwörter,
# initialisiert mit Ausnahmen und Wörtern der Rechtschreiblisten::

words = dict([(a, '') for a in ausnahmen])

for word in open(wgerman[sprachvariante][0]):
    word = word.decode(wgerman[sprachvariante][1]).rstrip()
    words[word] = ''

print len(words), "Wörter aus", wgerman[sprachvariante]

# Sortierung in::

unbekannt = defaultdict(list)  # Teilwörter nicht in der Wortliste
grossklein = defaultdict(list) # Teilwörter mit anderer Groß/Kleinschreibung
vorsilben = defaultdict(list)   # Teilwörter mit zusätzlicher Vorsilbe


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
    # if wort[0] is not '-1-': # Wort mit allgemeingültiger Trennung
    #     continue

# Trenne an Wortfugen (markiert durch '=')::

    teile = wort.split('=')

    if len(teile) == 1:
        continue

# Wortteile analysieren und ggf. Trennungen übertragen
# 
# ::

    neuteile = []
    for teil in teile:
        
# Teilwort ohne Trennung, Groß/Kleinschreibung übertragen::
        
        teilwort = join_word(teil)
        if wort.istitle():
            teilwort = teilwort.title()

# Suche nach Teilwort als Einzelwort::

        if (teilwort in words
            or teilwort.endswith('s') and teilwort[:-1] in words):
            if u'·' in teil:  # unkategorisierte Trennstelle
                # Versuche Ersetzung mit kategorisiertem Rest
                try:
                    einzelteil = words[teilwort].get(sprachvariante)
                except (KeyError, AttributeError):
                    einzelteil = None
                if (einzelteil and u'·' not in einzelteil and
                    re.sub(ur'[-=|]', ur'·', einzelteil) == teil):
                    # Groß-/Kleinschreibung erhalten:
                    teil = teil[0] + einzelteil[1:]
                    # print teil.encode('utf8')
            neuteile.append(teil)
            continue
        
# Teste ohne Berücksichtigung der Groß/Kleinschreibung::

        if (teilwort.lower() in words or teilwort.title() in words
            or teilwort.endswith('s') and teilwort[:-1].lower() in words
                                       or teilwort[:-1].title() in words):
            grossklein[teilwort].append(wort)
            neuteile.append(teil)
            continue

# Teilwort mit Vorsilbe::

        ohne_vorsilbe = ''
        for silbe in ('ab', 'an', 'be', 'ex', 'ge', 'un', 
                      'ver', 'vor', 'zu'):
            if (teil.lower().replace(u'·', '-').startswith(silbe+'-')
                and (teilwort[len(silbe):] in words
                     or teilwort[len(silbe):].title() in words)):
                ohne_vorsilbe = teilwort[len(silbe):]
                # print teil.encode('utf8'),
                break
        if ohne_vorsilbe:
            vorsilben[teilwort].append(wort)
            neuteile.append(teil)
            continue

# Teilwort nicht gefunden::

        unbekannt[teilwort].append(wort)
        neuteile.append(teil)
        
    if neuteile != teile:
        # print '='.join(neuteile).encode('utf8')
        entry.set('='.join(neuteile), sprachvariante)


# Ausgabe
# =======
# 
# ::

def testausgabe(checkdict):
    checkliste = ['%3d %s %s' % (len(checkdict[key]), key, checkdict[key][0])
                  for key in sorted(checkdict.keys())]
    checkliste.sort()
    return u'\n'.join(checkliste).encode('utf8') + '\n'

unbekannt_file = file('teilwort-unbekannt', 'w')
# unbekannt_file.write(u'\n'.join(unbekannt).encode('utf8') + '\n')
unbekannt_file.write(testausgabe(unbekannt))

grossklein_file = file('teilwort-grossklein', 'w')
grossklein_file.write(testausgabe(grossklein))

vorsilben_file = file('teilwort-vorsilben', 'w')
vorsilben_file.write(testausgabe(vorsilben))


# Auswertung
# ==========
# 
# ::

patch = udiff(wortliste_alt, wortliste, 'wortliste', 'wortliste-neu')
if patch:
    print patch
    patchfile = open('../../wortliste.patch', 'w')
    patchfile.write(patch + '\n')
else:
    print "empty patch"


print 'Gesamtwortzahl (w*german+Wortliste, %s):' % sprachvariante, len(words)
print 'Einträge (%s):' % sprachvariante, len(wortliste)
# print 'Mit (Vor-) Silbe: "%s"' % silbe, len(fertig) + len(test) + len(kandidat)
# print 'Teilwort erkannt:', len(fertig)
print 'Teilwort mit anderer Groß-/Kleinschreibung:', len(grossklein)
print 'Teilwort mit zusätzlicher Vorsilbe:', len(vorsilben)
print 'Teilwort nicht gefunden:', len(unbekannt)


# Quellen
# =======
# 
# .. [BCP47]  A. Phillips und M. Davis, (Editoren.),
#    `Tags for Identifying Languages`, http://www.rfc-editor.org/rfc/bcp/bcp47.txt
# 
# .. _Wortliste der deutschsprachigen Trennmustermannschaft:
#    http://mirrors.ctan.org/language/hyphenation/dehyph-exptl/projektbeschreibung.pdf
# 
