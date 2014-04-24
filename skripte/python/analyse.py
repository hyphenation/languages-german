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
# .. _wortliste: ../../wortliste
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

from werkzeug import WordFile, join_word, udiff, uebertrage, TransferError

# teilwoerter
# -----------
#
# Sammlung von `dictionaries` mit Info über Teilwörter.
#
# >>> from analyse import teilwoerter
#
# >>> words = teilwoerter()
#
# ::

class teilwoerter(object):

# Dictionary mit Listen möglicher Trennungen. Es kann unterschiedlche
# Trennungen eines identischen Teilworts geben, z.B. "Ba-se" (keine Säure)
# vs. "Base" (in Base=ball)::

    trennvarianten = {}

# Häufigkeiten des Auftretens der Teilwörter::

    S = defaultdict(int)   # Einzelwort (Solitär)
    E = defaultdict(int)   # erstes Wort in Verbindungen
    M = defaultdict(int)   # mittleres Wort in Verbindungen
    L = defaultdict(int)   # letztes Wort in Verbindungen

# >>> words.S['na'] += 1
# >>> print words.S['na'], words.E['na'], words.M['na'], words.L['na']
# 1 0 0 0
#
# Wort eintragen
#
# >>> words.add(u'ein<tra·gen')
# >>> words.add(u'ein·tra-gen')
# >>> words.add(u'un<klar')
# >>> words.add(u'un<.klar')
# >>> words.add(u'un-klar')
# >>> print words.trennvarianten
# {u'unklar': [u'un<klar', u'un-klar'], u'eintragen': [u'ein<tra-gen']}
#
# ::

    def add(self, wort):

        key = join_word(wort)

        # Ignoriere Spezialtrennungen:
        if re.search(r'[\[{/\]}]', wort):
            return
        # ungünstige Trennungen:
        if u'.' in wort:
            # Wort ignorieren
            return
            # Entferne/Ersetze Markierung
            # wort = re.sub(ur'([-<=])\.+', ur'\1', wort)  # =. <. -.
            # wort = re.sub(ur'\.+', ur'·', wort)
        # wort schon vorhanden?
        if key in self.trennvarianten:
            # Abgleich der Trennmarker
            eintrag = self.trennvarianten[key]
            try:
                wort = uebertrage(eintrag[-1], wort, upgrade=False)
                eintrag[-1] = uebertrage(wort, eintrag[-1], upgrade=False)
            except TransferError:
                pass
            if wort != eintrag[-1]:
                self.trennvarianten[key].append(wort)
        else:
            self.trennvarianten[key] = [wort]

# Iterator über alle trennvarianten: Rückgabewert ist ein String
#
# >>> print [word for word in words.woerter()]
# [u'un<klar', u'un-klar', u'ein<tra-gen']
#
# ::

    def woerter(self):
        for varianten in self.trennvarianten.values():
            for wort in varianten:
                yield wort

# Schreibe (Teil)wörter und Häufigkeiten in eine Datei `path`::

    def write(self, path):

        outfile = codecs.open(path, 'w', encoding='utf8')
        header = u'# wort S;E;M;L (Solitär, erstes/mittleres/letztes Wort)\n'
        outfile.write(header)

        for key in sorted(self.trennvarianten.keys()):
            for wort in self.trennvarianten[key]:
                line = u'%s %d;%d;%d;%d\n' % (wort,
                            self.S[key], self.E[key], self.M[key], self.L[key])
                outfile.write(line)


# Funktion zum Einlesen der Teilwortdatei::

def read_teilwoerter(path):

    words = teilwoerter()

    for line in open(path):
        if line.startswith('#'):
            continue
        line = line.decode('utf8')
        try:
            wort, flags = line.split()
        except ValueError:
            wort = line
            flags = '0;0;0;0'
            # raise ValueError('cannot parse line '+line.encode('utf8'))

        key = join_word(wort)
        flags = [int(n) for n in flags.split(u';')]

        for kategorie, n in zip([words.S, words.E, words.M, words.L], flags):
            if n > 0: # denn += 0 erzeugt "key" (`kategorie` ist defaultdict)
                kategorie[key] += n
        words.add(wort)

    return words


# Analyse
# =====================
#
# Hilfsfunktion: Erkenne (Nicht-)Teile wie ``/{ll/ll``  aus
# ``Fuß=ba[ll=/{ll/ll=l}]eh-re``::

# >>> from analyse import spezialbehandlung
# >>> print spezialbehandlung(u']er.be')
# er.be
# >>> print spezialbehandlung(u'er[<b/b')
# erb

def spezialbehandlung(teil):
    if re.search(ur'[\[{/\]}]', teil):
        # print teil,
        teil = re.sub(ur'\[<(.+)/[^\]]+', ur'\1', teil) # [<b/b
        teil = re.sub(ur'\{([^/]*)[^}]*$', ur'\1', teil)
        teil = re.sub(ur'\[([^/]*)[^\]]*$', ur'\1', teil)
        teil = re.sub(ur'^(.)}', ur'\1', teil)
        teil = re.sub(ur'^(.)\]', ur'\1', teil)
        teil = re.sub(ur'^\]([^/]*$)', ur'\1', teil) # ]er.be -> er.be
        # print teil
    return teil

# Zerlege Wörter der Wortliste (unter `path`). Gib eine "teilwoerter"-Instanz
# mit dictionaries mit getrennten Teilwörtern als key und deren Häufigkeiten
# an der entsprechenden Position als Wert zurück::


def analyse(path='../../wortliste', sprachvariante='de-1901',
            unfertig=False, halbfertig=True):

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
            if u'·' not in wort or unfertig:
                # skip unkategorisiert, könnte Kopositum sein
                words.add(wort)
                words.S[join_word(wort)] += 1
            continue

        gross = wort[0].istitle()

        # erstes Teilwort:
        if (halbfertig or u'·' not in teile[0]
           ) and not teile[0].endswith(u'<'): # Präfix wie un<=wahr=schein-lich
            words.add(teile[0])
            words.E[join_word(teile[0])] += 1

        # letztes Teilwort:
        teil = teile[-1]
        if (halbfertig or u'·' not in teil
           ) and not teil.startswith(u'>'): # Suffixe wie an-dert=halb=>fach)
            if gross: # Großschreibung übertragen
                teil = teil[0].title() + teil[1:]
            words.add(teil)
            words.L[join_word(teil)] += 1

        # mittlere Teilwörter
        for teil in teile[1:-1]:
            if u'/' in teil:
                if not re.search(ur'[\[{].*[\]}]', teil):
                    continue
            if (not(halbfertig) and u'·' in teil # unkategorisiert
               ) or teil.endswith(u'<'): # Präfix wie un<=wahr=schein-lich
                continue
            if gross: # Großschreibung übertragen
                teil = teil[0].title() + teil[1:]
            words.add(teil)
            words.M[join_word(teil)] += 1

    return words

# Datenerhebung zum Stand der Präfixmarkierung in der Liste der Teilwörter::

def statistik_praefixe(teilwoerter):

    ausnahmen = set(line.decode('utf8').strip()
                    for line in open('wortteile/vorsilbenausnahmen')
                    if not line.startswith('#'))

    # Präfixe (auch als Präfix verwendete Partikel, Adjektive, ...):
    praefixe = set(line.rstrip().lower().decode('utf8')
                   for line in open('wortteile/praefixe')
                   if not line.startswith('#'))
    # Sammelboxen:
    markiert = defaultdict(list)        # mit < markierte Präfixe
    kandidaten = defaultdict(list)      # (noch) mit - markierte Präfixe
    unkategorisiert = defaultdict(list) # mit · markierte Präfixe
    # grundwoerter = defaultdict(int)   # Wörter nach Abtrennen markierter Präfixe
    ausnahmefaelle = defaultdict(int)

    # Analyse
    for wort in teilwoerter.woerter():
        # Abtrennen markierter Präfixe:
        restwort = wort
        teile = restwort.split(u'<')
        for teil in teile[:-1]:
            if teil: # (leere Strings (wegen <<<<) weglassen)
                markiert[join_word(teil.lower())].append(wort)
            restwort = teile[-1]
        # Abtrennen markierter Suffixe:
        restwort = restwort.split(u'>')[0]
        # Silben des Grundworts
        silben = re.split(u'[-·.]+', restwort)
        silben[0] = silben[0].lower()
        
        if (join_word(restwort) in ausnahmen
            or join_word(restwort.split(u'>')[0]) in ausnahmen):
            ausnahmefaelle[silben[0]] += 1
            continue
        for i in range(len(silben)-1, 0, -1):
            kandidat = u''.join(silben[:i])
            if kandidat.lower() in praefixe:
                # print i, kandidat, restwort, restwort[len(kandidat)+i-1]
                if u'>' == restwort[len(kandidat)+i-1]:
                    ausnahmefaelle[kandidat] += 1
                elif u'·' in restwort:
                    unkategorisiert[kandidat].append(wort)
                else:
                    kandidaten[kandidat].append(wort)
                break

# Ausgabe
    print (u'\nPräfixe aus der Liste "wortteile/praefixe" und '
           u'gleiche Wortanfangssilben\nmarkiert mit:')
    for vs in sorted(praefixe):
        einzel = (teilwoerter.E[vs] + teilwoerter.M[vs]
                  + teilwoerter.E[vs.title()] + teilwoerter.M[vs.title()])
        print u'%-10s %5d = %5d < %5d - %5d · %5d offen' % (vs, einzel,
            len(markiert[vs]), ausnahmefaelle[vs], 
            len(unkategorisiert[vs]), len(kandidaten[vs])),
        if kandidaten[vs]:
            print u':', u' '.join(kandidaten[vs][:30]),
            if len(kandidaten[vs]) > 30:
                print u' ...',
        print
        markiert.pop(vs, None)

    print u'Markierte Präfixe die nicht in der Präfix-Liste stehen:'
    # markiert.pop('lang', 0) # von "ent<lang<<"
    for vs, i in markiert.items():
        print vs, u' '.join(i)


# Trennungsvarianten zum gleichen Key::

def mehrdeutigkeiten(words):
    for teil in sorted(words.trennvarianten):
        if len(words.trennvarianten[teil]) == 1:
            continue
        # Bekannte Mehrdeutigkeiten (meist engl./dt.):
        if teil in ('Anhalts', 'Base',  'George',
                    'herzog', # Her-zog/her>zog
                    'Mode', 'Name',
                    'Page', 'Pole', 'Planes', 'Rate', 'Real',
                    'Spare', 'Station', 'Stations', 'Wales', 'Ware',
                    'griff' # gri[f-f/{ff/ff=f}]est
                   ):
            continue
        # Einzelwort und Präfix gleichlautend:
        if len(words.trennvarianten[teil]) == 2:
            varianten = [i.rstrip(u'<') for i in words.trennvarianten[teil]]
            if varianten[0] == varianten[1]:
                continue
        print teil + u': ' + u' '.join(words.trennvarianten[teil])


# Bei Aufruf (aber nicht bei Import)::

if __name__ == '__main__':

    # sys.stdout mit UTF8 encoding.
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)

# erstelle/aktualisiere die Datei ``teilwoerter.txt`` mit den Häufigkeiten
# nicht zusammengesetzer Wörter als Einzelwort oder in erster, mittlerer,
# oder letzter Position in Wortverbindungen::

    # sprachvariante = 'de-1901'         # "traditionell"
    sprachvariante = 'de-1996'         # Reformschreibung
    # sprachvariante = 'de-1901-x-GROSS' # ohne ß (Schweiz oder GROSS)
    # sprachvariante = 'de-1996-x-GROSS' # ohne ß (Schweiz oder GROSS)
    # sprachvariante = 'de-CH-1901'     # ohne ß (Schweiz) ("süssauer")

    words = analyse(sprachvariante=sprachvariante, 
                    halbfertig=True, unfertig=True)
    words.write('teilwoerter-%s.txt'%sprachvariante)

# Test::

    # sys.exit()

    words = read_teilwoerter(path='teilwoerter-%s.txt'%sprachvariante)

    # Trennungsvarianten zum gleichen Key:
    mehrdeutigkeiten(words)

    # Stand der Vorsilbenmarkierung:
    statistik_praefixe(words)
