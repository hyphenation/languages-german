#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2011 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# wortfugen.py: Teste unkategorisierte Trennstellen auf Wortfugen
# ===============================================================
#
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
import codecs
from collections import defaultdict  # Wörterbuch mit Default
from copy import deepcopy

from werkzeug import WordFile, join_word, udiff

# sys.stdout mit UTF8 encoding.
sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)

# Globale Variablen
# -----------------
#
# Ausgangsbasis
# -------------
#
# Die freie `Wortliste der deutschsprachigen Trennmustermannschaft`_
# ("Lembergsche Liste")::

wordfile = WordFile('../../wortliste') # ≅ 400 000 Einträge/Zeilen

# Sprachvarianten
# ---------------
#
# Sprach-Tag nach [BCP47]_::

# sprachvariante = 'de-1901'         # "traditionell"
sprachvariante = 'de-1996'         # Reformschreibung
# sprachvariante = 'de-x-GROSS'      # ohne ß (Großbuchstaben und Kapitälchen)
# sprachvariante = 'de-1901-x-GROSS'   # ohne ß (Schweiz oder GROSS)
# sprachvariante = 'de-1996-x-GROSS' # ohne ß (Schweiz oder GROSS)
# sprachvariante = 'de-CH-1901'     # ohne ß (Schweiz) ("süssauer")


# Textdateien mit Wortbestandteilen
# ---------------------------------
#
# * Ein Wortteil/Zeile
# * Groß/Kleinschreibung unterschieden
# * Kodierung: utf8 (bis auf 'ogerman')

# Wörterbucher für die Rechtschreibprüfprogramme Ispell/Aspell
# (in Debian in den Paketen "wngerman" und "wogerman").
# Unterscheiden Groß-/Kleinschreibung und beinhalten auch kurze Wörter. ::

def wortdatei(wortfile, encoding='utf8'):
    for line in open(wortfile):
        yield line.rstrip().decode(encoding)

if sprachvariante == 'de-1901':
    wgerman = set(w for w in wortdatei('/usr/share/dict/ogerman',
                                       encoding='latin-1'))
else:
    wgerman = set(w for w in wortdatei('/usr/share/dict/ngerman'))

# Entferne Silben, die nie in Wortverbindungen vorkommen
# TODO: Solitäre aus einer Datei lesen. ::

for solitaer in ('Ra', 'He', 'As', 'Co', 'Fa'):
    wgerman.discard(solitaer)

# Präfixe (auch als Präfix verwendete Partikel, Adjektive, ...)::

praefixe = set(w for w in wortdatei('wortteile/praefixe'))

# Präfixe die keine selbständigen Wörter sind::

vorsilben = set(w for w in wortdatei('wortteile/vorsilben'))

# Erstellen der Liste durch Aussortieren selbständiger Wörter
# (Auskommentieren und Ausgabe unter wortteile/vorsilben abspeichern)::

# words = wordfile.asdict()
# for vs in sorted(praefixe - wgerman, key=unicode.lower):
#     if (vs not in words 
#         and vs.lower() not in words and vs.title() not in words
#         and vs.lower() not in wgerman and vs.title() not in wgerman):
#         print vs
#     
# sys.exit()


# Erstsilben: Wörter, die häufig als erste
# Silbe eines Wortes (aber nicht oder nur selten als Teilwörter) auftreten
# aber keine Vorsilben sind ::

erstsilben = set(w for w in wortdatei('wortteile/erstsilben'))

# Endsilben, die keine eigenständigen Wörter sind
# (nicht (nur) Endungen im morphologischen Sinne, sondern ganze Silben)::

endsilben = set(w for w in wortdatei('wortteile/endsilben'))

# Teilwörter: Wörter die in der Wortliste nur in Wortverbindungen vorkommen
# (zu kurz, keine eigenständigen Wörter, andere Großschreibung)
# und auch im Rechtschreibwörterbuch (wgerman) fehlen ::

teilwoerter = set(w for w in wortdatei('wortteile/teilwoerter'))

# Wörter, die in Zusammensetzungen verkürzt vorkommen (und daher nicht an
# letzter Stelle), z.b. "Farb"::

kurzwoerter = set(w for w in wortdatei('wortteile/kurzwoerter'))

# Bereits gesammelte Neueinträge::

neu_todo = set(join_word(w) for w in wortdatei('neu.todo'))

# Einträge der "Wortliste"
# ------------------------
# ::

wortliste = []

# Wörterbuch zum Aufsuchen der Teilwörter
# ---------------------------------------
#

words = {}

# initialisiert mit Ausnahmen und Wörtern der Rechtschreiblisten::

# words = dict([(w, '')
#               for w in wgerman.union(teilwoerter, kurzwoerter, neu_todo)])

# Sammeln unbekannter Wortteile::

unbekannt1 = defaultdict(list)
unbekannt2 = defaultdict(list)


# Erstellen der Ausgangslisten
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
    
# Spezielle Teilwörter suchen::

    # teile = wort.split(u'=')
    # if ('Stopp' in teile or 'stopp' in teile
    #     print entry[0]
    # continue

    # teile = wort.split(u'-')
    # if teile[-1] == 'burg':
    #     print ('-'.join(teile[:-1]) + '=' + teile[-1])
    # continue

    if u'·' not in wort:  # keine unkategorisierte Trennstelle
        continue

# Trenne an unkategorisierten Trennstellen (markiert durch '·')::

    teile = wort.split(u'·')

# Wortteile analysieren::

    for i in range(1,len(teile)-1):
        erstwort = u'·'.join(teile[:i])
        zweitwort =  u'·'.join(teile[i:])

# Key: Teilwort ohne Trennung, Groß/Kleinschreibung übertragen::

        try:
            erstkey = join_word(erstwort)
            zweitkey = join_word(zweitwort)
        except AssertionError, e:  # Spezialtrennung
            print e
            continue
        if wort[0].istitle():
            zweitkey = zweitkey.title()

# Bearbeiten
# ==========

# Blöcke zur regelbasierten Kategorisierung.
# Zum Auskommentieren und Anpassen.

# Komposita::

        if ((erstkey in words 
             or erstkey.lower() in words
             or erstkey.upper() in words)
            and erstkey not in erstsilben
            # and erstkey not in vorsilben
            and erstkey.lower() not in praefixe
            and (zweitkey in words
                 or zweitkey.lower() in words
                 or zweitkey.upper() in words)
            and zweitkey.lower() not in endsilben
            and zweitkey not in kurzwoerter
           ):
            compound = '='.join((erstwort, zweitwort.lower()))
            print u'%-30s %-15s %s'% (compound, erstkey,zweitkey)
            entry.set(compound, sprachvariante)

# Vorsilben::

        # if (erstkey in vorsilben
        #     # and zweitkey in words
        #    ):
        #     print str(entry), (u'%s<%s'% (erstkey,zweitwort))
        #     entry.set('-'.join((erstwort, zweitwort)), sprachvariante)

# Endsilben::

        # if (erstkey in words
        #     and zweitkey.lower() in endsilben
        #    ):
        #     print str(entry), (u'%s-%s'% (erstkey,zweitwort))
        #     entry.set('-'.join((erstwort, zweitwort)), sprachvariante)
        

# # Erstsilben::

        # if (erstkey in erstsilben or erstkey in vorsilben):
        #     print str(entry), (u'%s-%s'% (erstkey,zweitwort))
        #     entry.set('-'.join((erstwort, zweitwort)), sprachvariante)

# # Neueintragskandidaten::
#
#         if (erstkey not in words
#             and erstkey not in vorsilben
#             and erstkey not in erstsilben
#            ):
#             unbekannt1[erstwort].append(wort)
#         #
#         elif (zweitkey not in words
#             and zweitkey.lower() not in endsilben
#            ):
#             unbekannt2[zweitwort].append(wort)
#         else:
#             print ("%s-%s %s" % (erstwort, zweitwort, entry))


# Ausgabe
# ==========

# Unbekannte Teilwörter/Silben::

def testausgabe(unbekannt):
    checkliste = ['%3d %s %s' % (len(unbekannt[key]), key,
                                 ','.join(unbekannt[key]))
                  for key in sorted(unbekannt.keys())]
    checkliste.sort()
    return u'\n'.join(checkliste) + '\n'


if unbekannt1:
    print testausgabe(unbekannt1)
if unbekannt2:
    print testausgabe(unbekannt2)



# Ein Patch für die wortliste::

patch = udiff(wortliste_alt, wortliste,
              wordfile.name, wordfile.name+'-neu',
              encoding=wordfile.encoding)

if patch:
    # print patch
    patchfile = open('wortliste.patch', 'w')
    patchfile.write(patch + '\n')
else:
    print 'keine Änderungen'
