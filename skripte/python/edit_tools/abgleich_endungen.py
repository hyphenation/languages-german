#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2014 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id:        $Id:  $

# Abgleich der Trennstellen zwischen Woertern mit gleichem Stamm
# ==============================================================
# 
# Übertragen von kategorisierten Trennstellen von Wörtern auf
# Wörter anderer Endung und unkategorisierten Trennstellen.
# 
# ::

import re, sys, codecs, copy
from wortliste import (WordFile, WordEntry, join_word, udiff,
                      uebertrage, TransferError, 
                      sprachabgleich, toggle_case)
from analyse import read_teilwoerter, teilwoerter
from abgleich_teilwoerter import wortliste_to_teilwoerter

# Konfiguration
# -------------
# 
# Sprachvarianten
# ~~~~~~~~~~~~~~~
# Sprach-Tag nach [BCP47]_::

# sprachvariante = 'de-1901'         # "traditionell"
sprachvariante = 'de-1996'         # Reformschreibung
# sprachvariante = 'de-1901-x-GROSS'   # ohne ß (Schweiz oder GROSS)
# sprachvariante = 'de-1996-x-GROSS' # ohne ß (Schweiz oder GROSS)
# sprachvariante = 'de-CH-1901'     # ohne ß (Schweiz) ("süssauer")

# Großschreibung
# ~~~~~~~~~~~~~~
# Vergleiche Wörter mit unterschiedlicher Großschreibung 
# (z.T. reiben <-> Reibung)::

grossklein = False
# grossklein = True

# Vergleichsbasis
# ~~~~~~~~~~~~~~~
# Verwende die Wortliste oder die mit ``analyse.py`` generierte Teilwortliste 
# als Quelle der kategorisierten Trennungen::

use_teilwoerter = False
# use_teilwoerter = True

# Grundwort
# ~~~~~~~~~
# Bei Composita, verwende nur das Grundwort für den Abgleich
# (besonders sinnvoll bei Teilwörtern als Vergleichsbasis)::

use_grundwort = use_teilwoerter
# use_grundwort = False


# Funktionen
# -----------
# 
# Übertrag kategorisierter Trennungen auf Wörter mit anderer Endung::

def endungsabgleich(wort, endung, vergleichsendung=u'',
                    use_grundwort=False, grossklein=False):

    if not wort.endswith(endung):
        return wort
    if use_grundwort:
        teile = wort.split('=')
    else:
        teile = [wort]
    grundwort = teile[-1]
    stamm = grundwort[:-len(endung)] + vergleichsendung
    key = join_word(stamm)
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
                # Vergleichsendung abtrennen
                if vergleichsendung:
                    neustamm = neustamm[:-len(vergleichsendung)]
                # Mit Originalendung einsetzen
                teile[-1] =  neustamm + endung.replace(u'·', u'-')
                break
            except TransferError, e:
                print unicode(e), u"(%s -> %s)" % (vergleichsendung, endung)

    return u'='.join(teile)

# Endungen
# --------
# ``(<alt>, <neu>)`` Paare von Endungen
# 
# Achtung: die Auswahl zu testender Wörter erfolgt anhand der "neu"-Endung.
# Daher darf diese nicht leer sein!
# ::

endungen = [
            (u'', u'·chen'),
            (u'', u'd'),
            # (u'', u'·de'),
            # (u'', u'e·rin'),
            # (u'', u'e'),
            # (u'', u'er'),
            (u'', u'·en'),
            (u'', u'·er'),
            (u'', u'is·mus'),
            (u'', u'·is·mus'),
            (u'', u'·ität'),
            (u'', u'·lein'),
            (u'', u'm'),
            (u'', u'n'),
            # (u'', u'ner'),
            (u'', u'·ne'),
            # (u'', u'·ner'),
            (u'', u'·nen'),
            # (u'', u'·nem'),
            (u'', u'r'),
            (u'', u's'),
            (u'', u'·sche'),
            (u'', u'st'),
            # (u'', u's·te'),
            (u'', u't'),
            (u'', u'·tum'),
            # (u'', u't·te'),
            # (u'', u'·schaft'),
            (u'', u's·te'),
            #
            (u'-al', u'a·le'),
            (u'-an', u'a·ne'),
            (u'-at', u'a·te'),
            (u'-ben', u'b·ne'),
            (u'-che', u'ch'),
            (u'-de', u'd'),
            # (u'-en', u'e'),
            (u'-en', u'e·ne'),
            (u'-er', u'e·rin'),
            (u'-er', u'e·rei'),
            (u'-ern', u'e·re'),
            (u'-ge', u'g'),
            (u'-gen', u'g'),
            (u'-on', u'o·nen'),
            (u'-re', u'r'),
            (u'-re', u'rt'),
            (u'-ren', u'rt'),
            (u'-ren', u'r·ne'),
            (u'-sche', u'sch'),
            (u'-sen', u's·ne'),
            (u'-sten', u's·mus'),
            (u'-te',u't'),
            (u'-tern', u't·re'),
            (u'-ös', u'ö·se'),
            #
            (u'a', u'·ar'),
            (u'a', u'·as'),
            (u'b', u'·be'),
            (u'b', u'·ber'),
            (u'bt', u'b·te'),
            (u'bar', u't'),
            (u'ce', u'-cen'),
            (u'ch', u'·che'),
            # (u'ch', u'-che'), # Test "if u'·' not in wort" auskommentieren!
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
            (u'er', u'e'),
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
            (u'ie', u'e'),
            (u'-in', u'i·ne'),
            (u'isch', u'i·sche'),
            (u'k', u'·ke'),
            # (u'k', u'·ken'),
            (u'k', u'·ker'),
            (u'l', u'·le'),
            (u'l', u'·ler'),
            # (u'l', u'·len'),
            # (u'le', u'·ler'),
            (u'l', u'·lis·mus'),
            # (u'li-che', u'tem'),
            # (u'li-che', u'ten'),
            (u'ln', u'·le'),
            (u'lt', u'·le'),
            (u'm', u'·me'),
            (u'm', u'·mer'),
            (u'mus', u'men'),
            (u'mus', u'tik'),
            (u'mus', u'ten'),
            # (u'me', u'·men'),
            # (u'n', u'·at'),
            # (u'n', u'·er'),
            (u'n', u'·ne'),
            # (u'n', u'·nen'),
            (u'n',u'·ner'),
            (u'n', u'·nis·mus'),
            (u'n', u'r'),
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
            (u'ph', u'·phis·mus'),
            (u'r', u'·re'),
            # (u'r', u'·rei'),
            (u'r', u'·ren'),
            (u'r', u'·rin'),
            (u'r', u'·ris·mus'),
            # (u'r', u'·rung'),
            (u're', u'ste'),
            # (u'ren', u'rst'),
            # (u'ren', u'rt'),
            (u'ren', u'r·te'),
            (u'rn', u'·re'),
            (u'rn', u'·rung'),
            (u'rt', u'r·te'),
            (u'rt', u'·re'),
            (u's', u''),
            # (u's', u's-ses'),
            # (u's', u's·se'),
            (u's', u'·se'),
            (u's', u'·ser'),
            (u's', u'·se·re'),
            (u's', u'·se·res'),
            (u'sch', u'·sche'),
            # (u'sch', u'·schen'),
            (u'sch', u'·scher'),
            # (u'st', u'n'),
            (u'st', u'·ste'),
            # (u'st', u'·sten'),
            # (u't', u'e'),
            (u't', u'n'),
            (u't', u'st'),
            (u't', u'·bar'),
            (u't', u'·ba·re'),
            (u't', u'·te'),
            # (u't', u'-te'),
            (u't', u'·ten'),
            (u't', u'·ter'),
            (u't', u'·tes'),
            (u't', u'·tin'),
            (u't', u'·tis·mus'),
            (u'te', u't'),
            (u'te', u'·le'),
            (u'te', u'·ten'),
            (u'ten', u'mus'),
            (u'ten', u'ren'),
            (u'ten', u'tung'),
            (u'ter', u'te·ren'),
            (u'ti-on', u'tor'),
            (u'um', u'a'),
            (u'us', u'en'),
            (u'v', u'·ve'),
            (u'v', u'·ver'),
            (u'v', u'·vis·mus'),
            # (u've', u'v'),
            # (u'z', u'·ten'),
            (u'z', u'·ze'),
            # (u'z', u'·zen'),
            (u'z', u'·zer'),
            (u'ß', u's·se'),
            (u'ß', u'·ße'),
            (u'ös', u'ö·se'),
           ]

if grossklein:
    endungen.extend([
                     (u'', u'·ar·tig'),
                     (u'', u's·los'),
                     (u'', u'·keit'),
                     (u'', u'·heit'),
                     (u'', u'·schaft'),
                     (u'd', u'·heit'),
                     (u'', u'·weise'),
                     (u'e-ren', u'·ti·on'),
                     (u'-en', u'·bar·keit'),
                     (u'rn', u'·rung'),
                    ])

if __name__ == '__main__':

    # sys.stdout mit UTF8 encoding.
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)

# `Wortliste` einlesen::

    wordfile = WordFile('../../../wortliste') # ≅ 400 000 Einträge/Zeilen
    wortliste = list(wordfile)
    wortliste_neu = []

# Vergleichswörter einlesen::
                    
    if use_teilwoerter:
        words = read_teilwoerter(path='teilwoerter-%s.txt'%sprachvariante)
    else: # Gesamtwörter als "Teilwörter":
        words = wortliste_to_teilwoerter(wortliste, sprachvariante)

# Erstellen der neuen wortliste::

    for entry in wortliste:

        # Wort mit Trennungen in Sprachvariante
        wort = entry.get(sprachvariante)
        if (wort is None # Wort existiert nicht in der Sprachvariante
            or u'·' not in wort): # Alle Trennstellen kategorisiert
            wortliste_neu.append(entry)
            continue

# Endungsabgleich::

        for alt, neu in endungen:
            wort2 = endungsabgleich(wort, endung=neu, vergleichsendung=alt,
                                    use_grundwort=use_grundwort,
                                    grossklein=grossklein
                                   )
            if wort != wort2:
                break
        
# Eintrag ändern::

        if (wort != wort2): #and (u'·' not in wort2):
            entry = copy.copy(entry)
            entry.set(wort2, sprachvariante)
            print u'%s -> %s' % (wort, wort2)
            if len(entry) > 2:
                sprachabgleich(entry)
                
        wortliste_neu.append(entry)


# Patch erstellen::

    patch = udiff(wortliste, wortliste_neu, 'wortliste', 'wortliste-neu')
    if patch:
        # print patch
        patchfile = open('wortliste.patch', 'w')
        patchfile.write(patch + '\n')
    else:
        print u'empty patch'
