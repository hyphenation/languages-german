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
import codecs
from collections import defaultdict  # Wörterbuch mit Default
# from copy import deepcopy

from werkzeug import WordFile, join_word, udiff

# teilwoerter
# -----------

# Sammlung von `dictionaries` mit Info über Teilwörter::

class teilwoerter(object):

# Dictionary mit Listen möglicher Trennungen. Es kann unterschiedlche
# Trennungen eines identischen Teilworts geben, z.B. "Ba-se" (keine Säure)
# vs. "Base" (in Base=ball)::

    trennvarianten = defaultdict(list)

# Häufigkeiten des Auftretens der Teilwörter::

    S = defaultdict(int)   # Einzelwort (Solitär)
    E = defaultdict(int)   # erstes Wort in Verbindungen
    M = defaultdict(int)   # mittleres Wort in Verbindungen
    L = defaultdict(int)   # letztes Wort in Verbindungen


# Iterator über alle trennvarianten: Rückgabewert ist ein String::

    def woerter(self):
        for varianten in self.trennvarianten.values():
            for wort in varianten:
                yield wort


def read_teilwoerter(path):

    words = teilwoerter()

    for line in open(path):
        line = line.decode('utf8')
        try:
            wort, flags = line.split()
        except ValueError:
            if line.startswith('#'):
                continue
            else:
                raise ValueError('cannot parse line '+line.encode('utf8'))

        key = join_word(wort)
        flags = [int(n) for n in flags.split(u';')]

        for kategorie, n in zip([words.S, words.E, words.M, words.L], flags):
            if n > 0: # denn += 0 erzeugt "key" (`kategorie` ist defaultdict)
                kategorie[key] += n

        # Ignoriere Spezialtrennungen:
        # if not re.search(r'[.\[{/\]}]', wort):
        if not re.search(r'[.]', wort):
            words.trennvarianten[key].append(wort)

    return words


# Analyse
# =====================

# Hilfsfunktion: Erkenne (Nicht-)Teile wie ``/{ll/ll``  aus
# ``Fuß=ba[ll=/{ll/ll=l}]eh-re``::

def spezialbehandlung(teil):
    if re.search(ur'[\[{/\]}]', teil):
        teil = re.sub(ur'\{([^/]*)[^}]*$', ur'\1', teil)
        teil = re.sub(ur'\[([^/]*)[^\]]*$', ur'\1', teil)
        teil = re.sub(ur'^(.)}', ur'\1', teil)
        teil = re.sub(ur'^(.)\]', ur'\1', teil)
        # print teil
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

        # Zerlegen, leere Teile (wegen Mehrfachtrennzeichen '==') weglassen,
        # "halbe" Spezialtrennungen entfernen:
        teile = [spezialbehandlung(teil) for teil in wort.split(u'=')
                 if teil]

        # Einzelwort
        if len(teile) == 1:
            if u'·' not in wort: # skip unkategorisiert, könnte Kopositum sein
                words.S[wort] += 1
            continue

        gross = wort[0].istitle()

        # erstes Teilwort:
        if (u'·' not in teile[0]
            and not teile[0].endswith(u'|')): # Präfix wie un|=wahr=schein-lich
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
                if not re.search(ur'[\[{].*[\]}]', teil):
                    continue
            if u'·' in teil:
                # unkategorisierte Trennstelle(n): es könnte sich um ein
                # zusammengesetzes Wort handeln -> überspringen
                continue
            if gross: # Großschreibung übertragen
                teil = teil[0].title() + teil[1:]
            words.M[teil] += 1

    return words

# Datenerhebung zum Stand der Präfixmarkierung in der Liste der Teilwörter::

def statistik_praefixe(teilwoerter):

    ausnahmen = set(line.decode('utf8').strip()
                for line in open('wortteile/vorsilbenausnahmen'))

    # Präfixe (auch als Präfix verwendete Partikel, Adjektive, ...):
    praefixe = set(line.rstrip().lower().decode('utf8')
                   for line in open('wortteile/praefixe')
                   if not line.startswith('#'))
    # Sammelboxen:
    markiert = defaultdict(list)    # mit | markierte Präfixe
    kandidaten = defaultdict(list)   # nicht mit | markierte Präfixe
    # grundwoerter = defaultdict(int)   # Wörter nach Abtrennen markierter Präfixe

    # Analyse
    for wort in teilwoerter.woerter():
        # abtrennen markierter Präfixe:
        restwort = wort
        for trenner in (u'||||', u'|||', u'||', u'|'):
            teile = restwort.split(trenner)
            for teil in teile[:-1]:
                # if teil: # (leere Strings (wegen ||||) weglassen)
                    markiert[join_word(teil.lower())] .append(wort)
            restwort = teile[-1]
        # grundwoerter[restwort] += 1
        # Silben des Grundworts
        if join_word(restwort) in ausnahmen:
            continue
        # silben = re.split(u'[-·.]+', restwort)
        silben = restwort.split('-')
        silben[0] = silben[0].lower()
        for i in range(len(silben)-1, 0, -1):
            kandidat = ''.join(silben[:i])
            if kandidat.lower() in praefixe:
                # print kandidat, wort, silben[i]
                if silben[i-1]: # kein '--' nach dem Kandidaten
                    kandidaten[kandidat].append(wort)
                break

# Ausgabe
    print u'\nPräfixe aus der Liste "wortteile/praefixe":'
    print u'markiert mit      |     -    ='
    for vs in sorted(praefixe):
        print (u'%-13s %5d %5d %4d' %
               (vs, len(markiert[vs]), len(kandidaten[vs]),
                teilwoerter.E[vs] + teilwoerter.M[vs]
                + teilwoerter.E[vs.title()] + teilwoerter.M[vs.title()])
              ),
        if kandidaten[vs] and len(kandidaten[vs]) < 30:
            print u' '.join(kandidaten[vs])
        else:
            print
        markiert.pop(vs, None)

    print u'Markierte Präfixe die nicht in der Präfix-Liste stehen:'
    # markiert.pop('lang', 0) # von "ent|lang||"
    for vs, i in markiert.items():
        print vs, u' '.join(i)


# Trennungsvarianten zum gleichen Key:

def mehrdeutigkeiten(words):
    for teil in sorted(words.trennvarianten):
        if len(words.trennvarianten[teil]) == 1:
            continue
        # Bekannte Mehrdeutigkeiten:
        if teil in ('Base',  'Mode', 'Page', 'Planes', 'Rate', 'Real',
                    'Spare', 'Wales', 'Ware', 'griff'):
            continue
        line = u' '.join([teil]+words.trennvarianten[teil])
        print line


# Ausgabe
# ==========

# Schreibe das Resultat von `analyse` in eine Datei `path`::

def write_teilwoerter(words, path):

    outfile = codecs.open(path, 'w', encoding='utf8')

    header = u'# wort S;E;M;L (Solitär, erstes/mittleres/letztes Wort)\n'

    # Menge aller Teilwörter:
    teilwoerter = set()

    for kategorie in (words.S, words.E, words.M, words.L):
        teilwoerter.update(set(kategorie.keys()))

    outfile.write(header)
    for teil in sorted(teilwoerter):
        line = u'%s %d;%d;%d;%d\n' % (
            teil, words.S[teil], words.E[teil], words.M[teil], words.L[teil])
        outfile.write(line)


# Bei Aufruf (aber nicht bei Import):;

if __name__ == '__main__':

    # sys.stdout mit UTF8 encoding.
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)

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

# Test::

    # sys.exit()

    words = read_teilwoerter(path='teilwoerter-%s.txt'%sprachvariante)

    # Trennungsvarianten zum gleichen Key:
    mehrdeutigkeiten(words)

    # Stand der Vorsilbenmarkierung:
    statistik_praefixe(words)
