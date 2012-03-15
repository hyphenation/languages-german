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
import sys      # sys.exit() zum Abbruch vor Ende (für Testzwecke)

from werkzeug import WordFile, join_word

# Ausgangsbasis
# -------------
# 
# Die freie `Wortliste der deutschsprachigen Trennmustermannschaft`_
# ("Lehmansche Liste")::

wordfile = WordFile('../../wortliste') # ≅ 400 000 Einträge/Zeilen

# Wörterbucher für die Rechtschreibprüfprogramme Ispell/Aspell
# (in Debian in den Paketen "wngerman" und "wogerman").
# Unterschieden Groß-/Kleinschreibung und beinhalten kurze Wörter. ::

spell_listen = {'de-1996': ('/usr/share/dict/ngerman', 'utf8'),
                    'de-1901': ('/usr/share/dict/ogerman', 'latin-1'),
                   }


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

ausnahmen = set(('Altausseer', 'Altaussee', 'Aussee', 'Ausseer',
                 'Alster',
                ))
# TODO: fehler: Alt=aus|see !!!!!!!!!!!!!!!!!!!!!!!!!!1

# "Nachwörter" (Wörter die nicht ohne Vorsilben vorkommen)::

nachwoerter = ('bau', 'geh',
               'Gleichs',   # Aus|gleichs
               'Nahme',     # An|nahme
               'Stattung',  # Er|stattung
              )

doppelvorsilben = ('mitaus', 'veraus',
                   'voraus', # Vorauswahl, vor·aus·ge·wählt
                   'unaus')

# Globale Variablen
# -----------------
# 
# Sammeln der Wörter/Daten für die angegebene Sprachvariante.
# 
# Einträge der "Wortliste"::

wortliste = []

# Wörterbuch zum Aufsuchen der Restwörter.
# Initialisiert mit Ausnahmen und Wörtern der Rechtschreiblisten::

words = {}

for word in open(spell_listen[sprachvariante][0]):
    word = word.decode(spell_listen[sprachvariante][1]).rstrip()
    words[word] = ''

# print len(words), "Wörter aus", spell_listen[sprachvariante]
# 
# 
# 1. Durchlauf: Erstellen der Ausgangslisten
# ==========================================
# 
# 
# ::

for entry in wordfile:
    if entry.lang_index(sprachvariante) is not None:
        words[entry[0]] = entry # Eintrag in Wörterbuch mit Wort als key
        wortliste.append(entry)

# print len(wortliste), len(words), "Wörter"
# 
# for k,v in words.iteritems():
#     if v == '':
#         print k.encode('utf8')
# 
# sys.exit()
# 
# 
# 2. Durchlauf: Analyse
# =====================
# 
# Suche nach Wörtern mit (Vor-) Silbe::

silbe = 'aus'

pattern = '[%s%s]%s' % (silbe[0].upper(), silbe[0], silbe[1:]) # [Aa]us

# Sortierung in::

fertig = []             # Restwort existiert
test = []               # zum Test neuer Regeln, z Zt. Groß-/Kleinschreibung
kandidat = []           # Restwort nicht in der Wortliste
mittig = []             # Silbe nicht am Wortanfang

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

        restwort = join_word(rest)
        # Groß/Kleinschreibung übertragen
        if wort[0].isupper(): # str.title() geht nicht wegen der Trennzeichen
            restwort = restwort.title()

# Ausnahmen aus der Ausnahmeliste::

        if wort in ausnahmen:
            continue

# Wenn der Wortbestandteil hinter der getesteten Silbe im Wörterbuch
# vorhanden ist, kann davon ausgegangen werden, daß es sich um eine Vorsilbe
# oder ein Teilwort handelt::

        if restwort in words:
            if not re.search(u'[-=_|]', rest):  # Rest ist ungewichtet
                try:
                    einzelwort = words[restwort].get(sprachvariante)
                    # Groß-/Kleinschreibung erhalten:
                    rest = rest[0] + einzelwort[1:]
                    # Update Ersetzung mit (evt.) kategorisiertem Rest:
                    ersetzung = '%s%s|%s' %(vorspann, silbe, rest)
                except AttributeError:
                    pass
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
            test.append(' '.join((ersetzung, restwort)))
            continue

# Restwort nicht gefunden::

        kandidat.append(ersetzung)

# Silbe nicht am Wortanfang::

    elif re.search(u'[-·](%s)[-·]'%pattern, wort):
        is_mittig = True
        for vorsilben in doppelvorsilben:
            if join_word(wort).lower().startswith(vorsilben):
                is_mittig = False
        if is_mittig:
            mittig.append(wort)


# Ausgabe
# =======
# 
# ::

fertig_file = file('vorsilbe-OK', 'w')
fertig_file.write(u'\n'.join(fertig).encode('utf8') + '\n')

test_file = file('vorsilbe-test', 'w')
test_file.write(u'\n'.join(test).encode('utf8') + '\n')

kandidat_file = file('vorsilbe-kandidat', 'w')
kandidat_file.write(u'\n'.join(kandidat).encode('utf8') + '\n')

kandidat_file = file('vorsilbe-TODO', 'w')
kandidat_file.write(u'\n'.join(mittig).encode('utf8') + '\n')


# Auswertung
# ==========
# 
# ::

print 'Gesamtwortzahl (w*german+Wortliste, %s):' % sprachvariante, len(words)
print 'Einträge (%s):' % sprachvariante, len(wortliste)
print 'Mit (Vor-) Silbe: "%s"' % silbe, len(fertig) + len(test) + len(kandidat)
print 'Restwort erkannt:', len(fertig)
print 'Restwort mit anderer Groß-/Kleinschreibung:', len(test)
print 'Kandidaten (Restwort nicht gefunden):', len(kandidat)
print 'unsichere Kandidaten (Silbe im Wortinneren)', len(mittig)

# Mit (Vor-) Silbe "aus" 8248
# 
# Ohne die "spell" Wortlisten:
# 
# Restwort erkannt 6328
# Restwort mit anderer Groß-/Kleinschreibung 612
# Kandidaten (Restwort nicht gefunden) 1705
# 
# Mit "spell" Wortlisten:
# 
# Restwort erkannt 6427
# Restwort mit anderer Groß-/Kleinschreibung 589
# Kandidaten (Restwort nicht gefunden) 1629
# 
# Mit Ausnahmen:
# 
# Restwort erkannt: 6553
# Restwort mit anderer Groß-/Kleinschreibung: 533
# Kandidaten (Restwort nicht gefunden): 1559
# 
# Alle Kandidaten geprüft.
# 
# Quellen
# =======
# 
# .. [BCP47]  A. Phillips und M. Davis, (Editoren.),
#    `Tags for Identifying Languages`, http://www.rfc-editor.org/rfc/bcp/bcp47.txt
# 
# .. _Wortliste der deutschsprachigen Trennmustermannschaft:
#    http://mirrors.ctan.org/language/hyphenation/dehyph-exptl/projektbeschreibung.pdf
# 
