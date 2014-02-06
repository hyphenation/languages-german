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

# Übertrag kategorisierter Trennungen auf Grundwörter mit anderer Endung:
# ::

def grundwortabgleich(wort, endung, vergleichsendung=u'',
                      ganzwort=False, grossklein=False):

    if not wort.endswith(endung):
        return wort
    if ganzwort:
        teile = [wort]
    else:
        teile = wort.split('=')
    grundwort = teile[-1]
    stamm = grundwort[:-len(endung)] + vergleichsendung
    key = join_word(stamm)
    # print u' '.join([wort, key])
    if grossklein:
        key = toggle_case(key)

    if key in words.trennvarianten:
        # print u'fundum', key
        for altstamm in words.trennvarianten[key]:
            if u'·' in altstamm:
                continue
            if grossklein:
                altstamm = toggle_case(altstamm)
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
                print unicode(e), u"(%s -> %s)" % (vergleichsendung, endung)

    return u'='.join(teile)


# "Umgießen" der Wortliste in eine "Teilwörter" Instanz für den
# "Grundwortabgleich" von Wortverbindungen::

def wortliste_to_teilwoerter(wortliste):
    words = teilwoerter()
    for entry in wortliste:
        wort = entry.get(sprachvariante)
        if wort is None: # Wort existiert nicht in der Sprachvariante
            continue
        if u'·' not in wort:
            words.add(wort)
    return words


endungen = (
            (u'', u'd'),
            # (u'', u'·de'),
            # (u'', u'e·rin'),
            # (u'', u'e'),
            (u'', u'er'),
            (u'', u'·en'),
            (u'', u'·er'),
            (u'', u'm'),
            (u'', u'n'),
            # (u'', u'ner'),
            (u'', u'·ne'),
            # (u'', u'·ner'),
            # (u'', u'·nen'),
            # (u'', u'·nem'),
            (u'', u'r'),
            (u'', u's'),
            # (u'', u'st'),
            # (u'', u's·te'),
            (u'', u't'),
            # (u'', u'·tum'),
            # (u'', u't·te'),
            # (u'', u'·schaft'),
            (u'', u's·te'),
            #
            (u'-al', u'a·le'),
            (u'-an', u'a·ne'),
            (u'-at', u'a·te'),
            # (u'-che', u'ch'),
            # (u'-de', u'd'),
            # (u'-de', u'd'),
            # (u'-en', u'e'),
            (u'-en', u'e·ne'),
            (u'-er', u'e·rin'),
            (u'-er', u'e·rei'),
            (u'-ge', u'g'),
            # (u'-gen', u'g'),
            (u'-on', u'o·nen'),
            # (u'-re', u'r'),
            # (u'-sche', u'sch'),
            # (u'-sten', u's·mus'),
            (u'-tern', u't·re'),
            (u'-ös', u'ö·se'),
            #
            # (u'a', u'·as'),
            (u'b', u'·be'),
            (u'b', u'·ber'),
            # (u'bar', u'ba-re'),
            # (u'bar', u't'),
            # (u'ce', u'-cen'),
            (u'ch', u'·che'),
            (u'ch', u'·cher'),
            (u'ck', u'·cke'),
            (u'ck', u'·cker'),
            (u'd', u'·de'),
            # (u'd', u'·dem'),
            # (u'd', u'·den'),
            (u'd', u'·der'),
            # (u'd', u'·des'),
            # (u'de', u'd'),
            (u'e', u'·en'),
            # (u'e-ren', u'sch'),
            (u'el', u'le'),
            (u'en', u'e'),
            # (u'en', u'em'),
            # (u'en', u'en-de'),
            # (u'en', u'end'),
            # (u'en', u'er'),
            # (u'en', u'es'),
            # (u'en', u'est'),
            # (u'en', u't'),
            # (u'en', u'te'),
            (u'en', u'us'),
            # (u'end',u'en' ),
            # (u'er', u'ens'),
            (u'er', u'in'),
            # (u'er', u'e·rei'),
            # (u'er', u'ung'),
            (u'es', u'est'),
            (u'es', u's·te'),
            (u'f', u'·fe'),
            (u'f', u'·fer'),
            (u'g', u'·ge'),
            (u'g', u'·gen'),
            (u'g', u'·ger'),
            # (u'g', u'·ges'),
            # (u'g', u'·gung'),
            # (u'g', u'·ger'),
            # (u'in', u'en'),
            # (u'-in', u'i·ne'),
            # (u'isch', u'i·sche'),
            (u'k', u'·ke'),
            # (u'k', u'·ken'),
            (u'k', u'·ker'),
            (u'l', u'·le'),
            (u'l', u'·ler'),
            # (u'l', u'·len'),
            # (u'le', u'·ler'),
            # (u'li-che', u'tem'),
            # (u'li-che', u'ten'),
            (u'ln', u'·le'),
            (u'lt', u'·le'),
            (u'm', u'·me'),
            (u'm', u'·mer'),
            # (u'me', u'·men'),
            # (u'n', u'·at'),
            # (u'n', u'·er'),
            (u'n', u'·ne'),
            # (u'n', u'·nen'),
            (u'n',u'·ner'),
            (u'n', u't'),
            (u'n', u'st'),
            # (u'nd',u'n'),
            # (u'ne',u'n'),
            # (u'ne',u'·ner'),
            # (u'o',u'·on'),
            # (u'o',u'en'),
            (u'o',u'·os'),
            (u'on',u'o·nen'),
            (u'p', u'·pe'),
            (u'p', u'·pen'),
            (u'p', u'·per'),
            # (u'ph', u'·phen'),
            (u'r', u'·re'),
            # (u'r', u'·rei'),
            (u'r', u'·ren'),
            (u'r', u'·rin'),
            # (u'r', u'·rung'),
            (u're', u'ste'),
            # (u'ren', u'rst'),
            # (u'ren', u'rt'),
            # (u'ren', u'r·te'),
            # (u'rn', u'·re'),
            # (u's', u's-ses'),
            # (u's', u's·se'),
            (u's', u'·se'),
            (u's', u'·ser'),
            # (u's', u'·se·re'),
            # (u's', u'·se·res'),
            (u'sch', u'·sche'),
            # (u'sch', u'·schen'),
            (u'sch', u'·scher'),
            # (u'st', u'n'),
            (u'st', u'·ste'),
            # (u'st', u'·sten'),
            # (u't', u'e'),
            # (u't', u'n'),
            # (u't', u'st'),
            # (u't', u'·bar'),
            # (u't', u'·ba·re'),
            (u't', u'·te'),
            # (u't', u'-te'),
            (u't', u'·ten'),
            (u't', u'·ter'),
            (u't', u'·tes'),
            (u't', u'·tin'),
            # (u'te', u't'),
            # (u'te', u'·le'),
            # (u'te', u'·ten'),
            # (u'te',u't'),
            # (u'ten', u'mus'),
            # (u'ten', u'ren'),
            # (u'ten', u'tung'),
            # (u'ter', u'te·ren'),
            (u'v', u'·ve'),
            (u'v', u'·ver'),
            # (u've', u'v'),
            # (u'z', u'·ten'),
            (u'z', u'·ze'),
            # (u'z', u'·zen'),
            # (u'z', u'·zer'),
            (u'ß', u's·se'),
            (u'ß', u'·ße'),
            (u'ös', u'ö·se'),
       # mit "Grossklein":
            # (u'', u's·los'),
            # (u'', u'·keit'),
            # (u'', u'·heit'),
            # (u'd', u'·heit'),
            # (u'e-ren', u'·ti·on'),
            # (u'-en', u'·bar·keit'),
           )


if __name__ == '__main__':

    # sys.stdout mit UTF8 encoding.
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)

# Vorsilben (auch mehrsilbige Präfixe)::

    # vorsilben = set(line.rstrip().decode('utf8')
    #                 for line in open('wortteile/praefixe')
    #                 if not line.startswith('#'))

# `Wortliste` einlesen::

    wordfile = WordFile('../../wortliste') # ≅ 400 000 Einträge/Zeilen
    wortliste = list(wordfile)
    wortliste_neu = deepcopy(wortliste)

# Vergleichswörter einlesen::

    # Teilwoerter:
    # words = read_teilwoerter(path='teilwoerter-%s.txt'%sprachvariante)
    # Gesamtwörter als "Teilwörter":
    words = wortliste_to_teilwoerter(wortliste)

# Bearbeiten der neuen wortliste "in-place"::

    for entry in wortliste_neu:

        # Wort mit Trennungen in Sprachvariante
        wort = entry.get(sprachvariante)
        if wort is None: # Wort existiert nicht in der Sprachvariante
            continue
        if u'·' not in wort: # Alle Trennstellen kategorisiert
            continue

# Auswählen der gewünschten Bearbeitungsfunktion durch Ein-/Auskommentieren::

        # Teilwortabgleich:
        wort2 = teilwortabgleich(wort, grossklein=None, strict=False)

        # Endungsabgleich:
        # for alt, neu in endungen:
        #     wort2 = grundwortabgleich(wort, endung=neu, vergleichsendung=alt,
        #                               ganzwort=True,
        #                               # grossklein=True
        #                              )
        #     if wort != wort2:
        #         break
        
        # Vorsilbentest:
        # wort2 = vorsilbentest(wort, (u'all', u'All'))

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
