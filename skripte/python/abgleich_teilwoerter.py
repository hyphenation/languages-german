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
                      uebertrage, TransferError, toggle_case)
from analyse import read_teilwoerter, teilwoerter

# Sprachvarianten
# ---------------
# Sprach-Tag nach [BCP47]_::

sprachvariante = 'de-1901'         # "traditionell"
# sprachvariante = 'de-1996'         # Reformschreibung
# sprachvariante = 'de-x-GROSS'      # ohne ß (Großbuchstaben und Kapitälchen)
# sprachvariante = 'de-1901-x-GROSS'   # ohne ß (Schweiz oder GROSS)
# sprachvariante = 'de-1996-x-GROSS' # ohne ß (Schweiz oder GROSS)
# sprachvariante = 'de-CH-1901'     # ohne ß (Schweiz) ("süssauer")

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
            grossklein = True # retry with case toggled
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
    if grossklein:
        return toggle_case(teilabgleich(toggle_case(teil), strict=strict))
                    
    return teil

# Übertrag kategorisierter Trennungen auf Grundwörter mit anderer Endung:
# ::

def grundwortabgleich(wort, endung, vergleichsendung=u''):

    if not wort.endswith(endung):
        return wort

    teile = wort.split('=')
    grundwort = teile[-1]
    stamm = grundwort[:-len(endung)] + vergleichsendung
    key = join_word(stamm)
    # print u' '.join([wort, key])

    if key in words.trennvarianten:
        # print u'fundum', key
        for altstamm in words.trennvarianten[key]:
            if u'·' in altstamm:
                continue
            try:
                neustamm = uebertrage(altstamm, stamm)
                # print u'alt/neu', wort, altstamm, neustamm
                # Vergleichsendung abtrennen
                if vergleichsendung:
                    neustamm = neustamm[:-len(vergleichsendung)]
                # Mit Originalendung einsetzen
                teile[-1] =  neustamm + endung.replace(u'·', u'-')
                break
            except TransferError, e:
                print unicode(e)

    return u'='.join(teile)


# Übertrag kategorisierter Trennstellen zwischen den Feldern aller Einträge
# in `wortliste`::

def sprachabgleich(entry):

    if len(entry) <= 2:
        return # allgemeine Schreibung

    # if u'{' in unicode(entry):
    #     continue # Spezialtrennung
    mit_vorsilbe = None
    gewichtet = None
    ungewichtet = None
    for field in entry[1:]:
        if field.startswith('-'): # -2-, -3-, ...
            continue
        if u'|' in field:
            mit_vorsilbe = field
        elif u'·' not in field:
            gewichtet = field
        else:
            ungewichtet = field
    if mit_vorsilbe and (gewichtet or ungewichtet):
        for i in range(1,len(entry)):
            if entry[i].startswith('-'): # -2-, -3-, ...
                continue
            if u'|' not in entry[i]:
                try:
                    entry[i] = uebertrage(mit_vorsilbe, entry[i], strict=False)
                except TransferError, e:
                    print u'Sprachabgleich:', unicode(e)
        print mit_vorsilbe+u':', unicode(entry)
    elif gewichtet and ungewichtet:
        for i in range(1,len(entry)):
            if u'·' in entry[i]:
                try:
                    entry[i] = uebertrage(gewichtet, entry[i], strict=False)
                except TransferError, e:
                    print u'Sprachabgleich:', unicode(e)
        print gewichtet, unicode(entry)


# Teste, ob ein Teilwort eine Vorsilbe (oder auch mehrsilbiger Präfix) ist
# und korrigiere die Trennstellenmarkierung.
# `vorsilben` ist eine Sequenz (Tupel, Liste, Set, ...) mit zu testenden
# Vorsilben::

def vorsilbentest(wort, vorsilben):

    # Gleichlautende Vorsilben und Bestimmungswörter:
    doppeldeutig = [u'Drum=com-pu-ter', u'Miss=wahl', u'Miß=wahl']

    teile = wort.split('=')
    # erstes Teilwort
    if teile[0] in vorsilben and (wort not in doppeldeutig):
        return re.sub(r'^%s=' % teile[0], u'%s|' % teile[0], wort)
    # mittlere Teilwörter
    for teil in teile[1:-1]:
        if teil in vorsilben:
            return re.sub(r'=%s=' % teil, u'=%s|' % teil, wort)
    return wort


if __name__ == '__main__':

    # sys.stdout mit UTF8 encoding.
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)

# `Wortliste` einlesen::

    wordfile = WordFile('../../wortliste') # ≅ 400 000 Einträge/Zeilen
    wortliste = list(wordfile)
    wortliste_neu = deepcopy(wortliste)

# Teilwörter einlesen::

    words = read_teilwoerter(path='teilwoerter-%s.txt'%sprachvariante)

    # Alternative - Gesamtwörter als "Teilwörter" um "halbkategorisierte" Wörter 
    # (z.b. "Nicht=wei·ter·ver·brei·tung") abzugleichen
    # words = teilwoerter()
    # for entry in wortliste:
    #     wort = entry.get(sprachvariante)
    #     if wort is None: # Wort existiert nicht in der Sprachvariante
    #         continue
    #     if u'·' not in wort:
    #         words.add(wort)

# Tests::

    # for key, value in words.trennvarianten.iteritems():
    #     if len(value) != 1:
    #         print key, value
    # sys.exit()

    # print grundwortabgleich(u'Aa·chen·ern', u'n')
    # sys.exit()

# Vorsilben (auch mehrsilbige Präfixe)::

    vorsilben = set(line.rstrip().decode('utf8')
                    for line in open('wortteile/praefixe')
                    if not line.startswith('#'))

# Bearbeiten der neuen wortliste "in-place"::

    for entry in wortliste_neu:

        # Wort mit Trennungen in Sprachvariante
        wort = entry.get(sprachvariante)
        if wort is None: # Wort existiert nicht in der Sprachvariante
            continue

        if u'·' not in wort: # Alle Trennstellen kategorisiert
            continue

# Auswählen der gewünschten Bearbeitungsfunktion durch Ein-/Auskommentieren

        # Teilwortabgleich:
        # wort2 = teilwortabgleich(wort, grossklein=None, strict=True)
 
        # Grundwortabgleich:
        for alt, neu in (
                         # (u'', u'm'),
                         # (u'', u'n'),
                         # (u'', u'r'),
                         # (u'', u's'),
                         # (u'', u't'),
                         # (u'-de', u'd'),
                         # (u'bar', u'ba-re'),
                         # (u'bar', u't'),
                         # (u'de', u'd'),
                         # (u'te', u't'),
                         # (u've', u'v'),
                         # (u'ne',u'n'),
                         # (u'te',u't'),
                         # (u'end',u'en' ),
                         (u'en', u'e'),
                         # (u'en', u'end'),
                         # (u'en', u'en-de'),
                         # (u'en', u'em'),
                         # (u'en', u'er'),
                         # (u'en', u'es'),
                         # (u'en', u'est'),
                         # (u'es', u'est'),
                         # (u'en', u't'),
                         # (u'er', u'e·rin'),
                         # (u're', u'ste'),
                         # (u'ren', u'rst'),
                         # (u'ren', u'rt'),
                         # (u'ren', u'r·te'),
                         # (u'ten', u'ren'),
                         # (u'ter', u'te·re'),
                         # (u'ter', u'te·ren'),
                         # (u'd', u'·de'),
                         # (u'd', u'·dem'),
                         # (u'd', u'·den'),
                         # (u'd', u'·der'),
                         # (u'd', u'·des'),
                         # (u'e', u'·em'),
                         # (u'e', u'·en'),
                         # (u'e', u'·er'),
                         # (u'e', u'·es'),
                         # (u'e', u'·et'),
                         # (u'e', u'em'),
                         # (u'e', u'en'),
                         # (u'e', u'er'),
                         # (u'e', u'es'),
                         # (u'e', u'et'),
                         # (u'es', u's·te'),
                         # (u'm', u'·me'),
                         # (u'm', u'·mem'),
                         # (u'm', u'·men'),
                         # (u'm', u'·mer'),
                         # (u'm', u'·mes'),
                         # (u'n', u'·ne'),
                         # (u'n', u'·nem'),
                         # (u'n', u'·nen'),
                         # (u'n', u'·ner'),
                         # (u'n', u'·nes'),
                         # (u'r', u'·re'),
                         # (u'r', u'·rem'),
                         # (u'r', u'·ren'),
                         # (u'r', u'·rer'),
                         # (u'r', u'·res'),
                         # (u's', u'·se·res')
                         # (u'ß', u's·se'),
                         # (u'ß', u's·sem'),
                         # (u'ß', u's·sen'),
                         # (u'ß', u's·ser'),
                         # (u'ß', u's·ses'),
                         # (u'ß', u's·sest'),
                         # (u's', u's·se'),
                         # (u's', u's·sem'),
                         # (u's', u's·sen'),
                         # (u's', u's·ser'),
                         # (u's', u's·ses'),
                         # (u's', u's·sest'),
                         # (u'sch', u'·sche'),
                         # (u'sch', u'·schem'),
                         # (u'sch', u'·schen'),
                         # (u'sch', u'·scher'),
                         # (u'sch', u'·sches'),
                         # (u'sch', u'·schest'),
                         # (u'st', u'n'),
                         # (u't', u'·te'),
                         # (u't', u'·tem'),
                         # (u't', u'·ten'),
                         # (u't', u'·ter'),
                         # (u't', u'·tes'),
                         # (u't', u'·tet'),
                         # (u't', u'·test'),
                         # (u't', u'e'),
                         # (u't', u'st'),
                         # (u'te', u'le'),
                         # (u'v', u'·ve'),
                         # (u'v', u'·vem'),
                         # (u'v', u'·ven'),
                         # (u'v', u'·ver'),
                         # (u'v', u'·ves'),
                         # (u'v', u'·vest'),
                        ):
            wort2 = grundwortabgleich(wort, endung=neu, vergleichsendung=alt)
            if wort != wort2:
                break
        
        # wort2 = vorsilbentest(wort, (u'all', u'All'))

        if (wort != wort2): #and (u'·' not in wort2):
            entry.set(wort2, sprachvariante)
            print u'%s -> %s' % (wort, wort2)
            if len(entry) > 2:
                sprachabgleich(entry)

# Patch erstellen::

    patch = udiff(wortliste, wortliste_neu, 'wortliste', 'wortliste-neu',
                 encoding=wordfile.encoding)
    if patch:
        # print patch
        patchfile = open('wortliste.patch', 'w')
        patchfile.write(patch + '\n')
    else:
        print u'empty patch'
