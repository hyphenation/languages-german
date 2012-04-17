#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2011 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# analyse.py: Sammeln und Sortieren von Teilwörtern
# =================================================
#
# Erstelle eine Liste der Teilwörter von in der Wortliste_ markierten
# zusammengesetzten Wörtern mit den Häufigkeiten des Auftretens als:
#
# :S: Einzelwort (Solitär)
# :E: erstes Wort in Verbindungen
# :M: mittleres Wort in Verbindungen
# :L: letztes Wort in Verbindungen
#
# Format:
#
# * Teilwort mit Trennungen. Großschreibung wie Gesamtwort
# * Leerraum (whitespace)
# * Häufigkeiten in der Reihenfolge S;E;M;L
#
# Beispiel:
#
# Ho-se 1;0;0;7
#
#
# TODO: Vorsilben, Silben
#
# .. contents::
#
# Vorspann
# ========
#
# Importiere Python Module::

import re       # Funktionen und Klassen für reguläre Ausdrücke
import sys      # sys.exit() zum Abbruch vor Ende (für Testzwecke)
from collections import defaultdict  # Wörterbuch mit Default
# from copy import deepcopy

from werkzeug import WordFile, join_word, udiff


# teilwoerter
# -----------

# Sammlung von `dictionaries` mit Info über Teilwörter::

class teilwoerter(object):

# Liste möglicher Trennungen. Es kann unterschiedlche Trennungen eines
# identischen Teilworts geben, z.B. "Ba-se" (keine Säure) vs. "Base" (in
# Base=ball)::

    trennungen = defaultdict(list)

# Häufigkeiten des Auftretens der Teilwörter::

    S = defaultdict(int)   # Einzelwort (Solitär)
    E = defaultdict(int)   # erstes Wort in Verbindungen
    M = defaultdict(int)   # mittleres Wort in Verbindungen
    L = defaultdict(int)   # letztes Wort in Verbindungen


def read_teilwoerter(path):

    words = teilwoerter()

    for line in open(path):
        line = line.decode('utf8')
        wort, flags = line.split()

        key = join_word(wort)
        flags = [int(n) for n in flags.split(u';')]

        for kategorie, n in zip([words.S, words.E, words.M, words.L], flags):
            if n > 0: # denn += 0 erzeugt "key" (`kategorie` ist defaultdict)
                kategorie[key] += n

        # Ignoriere Spezialtrennungen:
        # if not re.search(r'[.\[{/\]}]', wort):
        if not re.search(r'[.]', wort):
            words.trennungen[key].append(wort)

    return words


# Analyse
# =====================

# Hilfsfunktion: Erkenne (Nicht-)Teile wie ``/{ll/ll``  aus
# ``Fuß=ba[ll=/{ll/ll=l}]eh-re``::

def spezialbehandlung(teil):
    if re.search(r'[\[{/\]}]', teil):
        teil = re.sub(r'\{([^/]*)[^}]*$', r'\1', teil)
        teil = re.sub(r'\[([^/]*)[^\]]*$', r'\1', teil)
        teil = re.sub(r'^(.)}', r'\1', teil)
        # print teil.encode('utf8')
    return teil

# Zerlege Wörter der Wortliste (unter `path`). Gib eine "teilwoerter"-Instanz
# mit dictionaries mit getrennten Teilwörtern als key und deren Häufigkeiten
# an der entsprechenden Position als Wert zurück::


def analyse(path='../../wortliste', sprachvariante='de-1901'):

    wordfile = WordFile(path)
    words = teilwoerter()

    for entry in wordfile:

# Wort mit Trennungen in Sprachvariante::

        wort = entry.get(sprachvariante)
        if wort is None: # Wort existiert nicht in der Sprachvariante
            continue

# Teilwörter suchen::

        teile = [spezialbehandlung(teil) for teil in wort.split(u'=')]
        
        # Einzelwort
        if len(teile) == 1:
            if u'·' not in wort:
                words.S[wort] += 1
            continue

        gross = wort[0].istitle()

        # erstes Teilwort:
        if u'·' not in teile[0]:
            words.E[teile[0]] += 1

        # letztes Teilwort:
        teil = teile[-1]
        if u'·' not in teil:
            if gross: # Großschreibung übertragen
                teil = teil[0].title() + teil[1:]
            words.L[teil] += 1

        # mittlere Teilwörter
        for teil in teile[1:-1]:
            if u'/' in teil:
                if not re.search(r'[\[{].*[\]}]', teil):
                    continue
            if u'·' in teil:
                # unkategorisierte Trennstelle(n): es könnte sich um ein
                # zusammengesetzes Wort handeln -> überspringen
                continue
            if gross: # Großschreibung übertragen
                teil = teil[0].title() + teil[1:]
            words.M[teil] += 1

    return words


# Ausgabe
# ==========

# Schreibe das Resultat von `analyse` in eine Datei `path`::

def write_teilwoerter(words, path):

    outfile = open(path, 'w')

    # Menge aller Teilwörter:
    teilwoerter = set()

    for kategorie in (words.S, words.E, words.M, words.L):
        teilwoerter.update(set(kategorie.keys()))

    for teil in sorted(teilwoerter):
        line = '%s %d;%d;%d;%d\n' % (
            teil, words.S[teil], words.E[teil], words.M[teil], words.L[teil])
        outfile.write(line.encode('utf8'))


# Bei Aufruf (aber nicht bei Import):;

if __name__ == '__main__':

# erstelle/aktualisiere die Datei ``teilwoerter.txt`` mit den Häufigkeiten
# nicht zusammengesetzer Wörter als Einzelwort oder in erster, mittlerer,
# oder letzter Position in Wortverbindungen.

    sprachvariante = 'de-1901'         # "traditionell"
    # sprachvariante = 'de-1996'         # Reformschreibung
    # sprachvariante = 'de-x-GROSS'      # ohne ß (Großbuchstaben und Kapitälchen)
    # sprachvariante = 'de-1901-x-GROSS'   # ohne ß (Schweiz oder GROSS)
    # sprachvariante = 'de-1996-x-GROSS' # ohne ß (Schweiz oder GROSS)
    # sprachvariante = 'de-CH-1901'     # ohne ß (Schweiz) ("süssauer")

    words = analyse(sprachvariante=sprachvariante)
    write_teilwoerter(words, 'teilwoerter-%s.txt'%sprachvariante)
    sys.exit()

# Test::

    words = read_teilwoerter(path='teilwoerter-%s.txt'%sprachvariante)

    for teil in sorted(words.trennungen):
        line = u' '.join([teil]+words.trennungen[teil]) + u'\n'
        print line.encode('utf8'),
