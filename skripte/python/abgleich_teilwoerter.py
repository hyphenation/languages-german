#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2011 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# Abgleich der Trennstellen zwischen Teilwoertern
# ===============================================
#
# Übertragen von kategorisierten Trennstellen von Teilwörtern auf
# Vorkommen dieser Teilwörter mit unkategorisierten Trennstellen.
#
# ::

from copy import deepcopy
import re, sys, codecs
from werkzeug import (WordFile, WordEntry, join_word, udiff,
                      uebertrage, TransferError, 
                      sprachabgleich, toggle_case)
from analyse import read_teilwoerter, teilwoerter

# Sprachvarianten
# ---------------
# Sprach-Tag nach [BCP47]_::

# sprachvariante = 'de-1901'         # "traditionell"
sprachvariante = 'de-1996'         # Reformschreibung
# sprachvariante = 'de-1901-x-GROSS'   # ohne ß (Schweiz oder GROSS)
# sprachvariante = 'de-1996-x-GROSS' # ohne ß (Schweiz oder GROSS)
# sprachvariante = 'de-CH-1901'     # ohne ß (Schweiz) ("süssauer")

# Vergleichsbasis
# ~~~~~~~~~~~~~~~
# Verwende die Wortliste oder die mit ``analyse.py`` generierte Teilwortliste 
# als Quelle der kategorisierten Trennungen::

use_teilwoerter = False
use_teilwoerter = True


# Funktionen
# -----------

# Übertrag kategorisierter Trennstellen aus Teilwort-Datei auf die
# `wortliste`::

def teilwortabgleich(wort, grossklein=False, strict=True):
    teile = [teilabgleich(teil, grossklein, strict)
             for teil in wort.split(u'=')
            ]
    return u'='.join(teile)

def teilabgleich(teil, grossklein=False, strict=True):
    if grossklein:
        return toggle_case(teilabgleich(toggle_case(teil), strict=strict))
    try:
        key = join_word(teil)
    except AssertionError, e:
        print e
        return teil
    if key not in words.trennvarianten:
        # print teil, u'not in words'
        if grossklein is None:
            return toggle_case(teilabgleich(toggle_case(teil), strict=strict))
    else:
        # Gibt es eine eindeutige Trennung für Teil?
        eindeutig = len(words.trennvarianten[key]) == 1
        for wort in words.trennvarianten[key]:
            # Übertrag der Trennungen
            try:
                teil = uebertrage(wort, teil, strict, upgrade=eindeutig)
            except TransferError, e: # Inkompatible Wörter
                # print unicode(e)
                if grossklein is None:
                    grossklein = True # retry with case toggled
    return teil

# "Umgießen" der Wortliste in eine "Teilwörter" Instanz für den
# "Grundwortabgleich" von Wortverbindungen::

def wortliste_to_teilwoerter(wortliste, sprachvariante=sprachvariante):
    words = teilwoerter()
    for entry in wortliste:
        wort = entry.get(sprachvariante)
        if wort is None: # Wort existiert nicht in der Sprachvariante
            continue
        if u'·' not in wort:
            words.add(wort)
    return words


if __name__ == '__main__':

    # sys.stdout mit UTF8 encoding.
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)

# `Wortliste` einlesen::

    wordfile = WordFile('../../wortliste') # ≅ 400 000 Einträge/Zeilen
    wortliste = list(wordfile)
    wortliste_neu = deepcopy(wortliste)

# Vergleichswörter einlesen::

    if use_teilwoerter:
        words = read_teilwoerter(path='teilwoerter-%s.txt'%sprachvariante)
    else: # Gesamtwörter als "Teilwörter":
        words = wortliste_to_teilwoerter(wortliste, sprachvariante)

# Bearbeiten der neuen wortliste "in-place"::

    for entry in wortliste_neu:

        # Wort mit Trennungen in Sprachvariante
        wort = entry.get(sprachvariante)
        if wort is None: # Wort existiert nicht in der Sprachvariante
            continue
        if u'·' not in wort and u'.' not in wort: # Alle Trennstellen kategorisiert
            continue

# Teilwortabgleich::

        wort2 = teilwortabgleich(wort, grossklein=None, strict=False)

# Eintrag ändern::

        if (wort != wort2): #and (u'·' not in wort2):
            entry.set(wort2, sprachvariante)
            print u'%s -> %s' % (wort, wort2)
            if len(entry) > 2:
                sprachabgleich(entry)

# Patch erstellen::

    patch = udiff(wortliste, wortliste_neu, 'wortliste', 'wortliste-neu')
    if patch:
        # print patch
        patchfile = open('wortliste.patch', 'w')
        patchfile.write(patch + '\n')
    else:
        print u'empty patch'
