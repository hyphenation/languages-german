#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2011 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id:        $Id:  $

# Versuche Trennstellen neuer Wörter aus vorhandenen zu ermitteln
# ===============================================================
# 
# Übertragen von kategorisierten Trennstellen vorhandener Wörter
# auf neu aufzunehmende, ungetrennte Wörter.
#
# Erwartet eine Datei mit 1 Wort/Zeile.

# Erstellt einen Patch mit den Wörtern, welche durch Abgleich mit der
# Datenbasis getrennt werden konnten.
# ::

import re, sys, codecs, copy, os
from werkzeug import WordFile, WordEntry, join_word, toggle_case
# sort.py im Überverzeichnis:
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from sort import sortkey_duden

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

# Funktionen
# -----------
# 
# Übertrag von Einträgen auf Wörter mit anderer Endung::

def endungsabgleich(key, alt, neu, grossklein=False):

    if not key.endswith(join_word(neu)):
        return ''
    
    altkey = key[:-len(join_word(neu))] + join_word(alt)
    if grossklein:
        altkey = toggle_case(altkey)
    
    try:
        altentry = words[altkey]
    except KeyError:
        return ''
    
    entry = WordEntry(key)
    # print "fundum", key, unicode(entry)
    for wort in altentry[1:]:
        if not wort.startswith(u'-'):
            if alt:
                wort = wort[:-len(alt)]
            wort += neu
            if grossklein:
                wort = toggle_case(wort)
            if join_word(wort) != key:
                print u"# Übertragungsproblem: %s -> %s (%s,%s) %s" % (
                                            altkey, key, alt, neu, wort)
                return ''
        entry.append(wort)

    return entry


# Endungen
# --------
# ``(<alt>, <neu>)`` Paare von Endungen
# 
# Achtung: die Auswahl zu testender Wörter erfolgt anhand der "neu"-Endung.
# Daher darf diese nicht leer sein!
# ::

endungen = [
            (u'', u'-de'),
            # (u'', u'-en'),
            # (u'', u'-er'),
            # (u'', u'-is-mus'),
            # (u'', u'-ität'),
            (u'', u'-lein'),
            (u'', u'-ne'),
            (u'', u'-nem'),
            (u'', u'-nen'),
            (u'', u'-ner'),
            (u'', u'-sche'),
            (u'', u'-tum'),
            (u'', u'>ar-tig'),
            (u'', u'>chen'),
            (u'', u'>heit'),
            (u'', u'>keit'),
            (u'', u'>schaft'),
            (u'', u'>schaft'),
            (u'', u'>weise'),
            # (u'', u'd'),
            # (u'', u'e'),
            # (u'', u'e-rin'),
            # (u'', u'er'),
            # (u'', u'is-mus'),
            # (u'', u'm'),
            # (u'', u'n'),
            # (u'', u'ner'),
            # (u'', u'r'),
            # (u'', u's'),
            # (u'', u's-te'),
            # (u'', u's-te'),
            # (u'', u's>los'),
            # (u'', u'st'),
            # (u'', u't'),
            # (u'', u't-te'),
            (u'-al', u'a-le'),
            (u'-an', u'a-ne'),
            (u'-at', u'a-te'),
            (u'-ben', u'b-ne'),
            # (u'-che', u'ch'),
            (u'-de', u'd'),
            (u'-en', u'>bar>keit'),
            # (u'-en', u'e'),
            (u'-en', u'e-ne'),
            (u'-er', u'e-rei'),
            (u'-er', u'e-rin'),
            (u'-ern', u'e-re'),
            (u'-ge', u'g'),
            (u'-gen', u'g'),
            (u'-in', u'i-ne'),
            (u'-on', u'o-nen'),
            (u'-re', u'r'),
            (u'-re', u'rt'),
            (u'-ren', u'r-ne'),
            (u'-ren', u'rt'),
            (u'-sche', u'sch'),
            (u'-sen', u's-ne'),
            (u'-sten', u's-mus'),
            (u'-te',u't'),
            (u'-tern', u't-re'),
            (u'-ös', u'ö-se'),
            (u'a', u'-ar'),
            (u'a', u'-as'),
            (u'b', u'-be'),
            (u'b', u'-ber'),
            (u'bar', u't'),
            (u'bt', u'b-te'),
            (u'ce', u'-cen'),
            (u'ch', u'-che'),
            (u'ch', u'-cher'),
            (u'ck', u'-cke'),
            (u'ck', u'-cker'),
            (u'd', u'-de'),
            (u'd', u'-dem'),
            (u'd', u'-den'),
            (u'd', u'-der'),
            (u'd', u'-des'),
            (u'd', u'>heit'),
            (u'e', u'-en'),
            (u'e-ren', u'-ti-on'),
            (u'e-ren', u'sch'),
            (u'el', u'le'),
            # (u'en', u'e'),
            (u'en', u'em'),
            (u'en', u'en-de'),
            (u'en', u'end'),
            (u'en', u'er'),
            (u'en', u'es'),
            (u'en', u'est'),
            (u'en', u't'),
            (u'en', u'te'),
            (u'en', u'us'),
            (u'end',u'en' ),
            # (u'er', u'e'),
            (u'er', u'e-rei'),
            (u'er', u'ens'),
            (u'er', u'in'),
            (u'er', u'ung'),
            (u'es', u'est'),
            (u'es', u's-te'),
            (u'f', u'-fe'),
            (u'f', u'-fer'),
            (u'g', u'-ge'),
            (u'g', u'-gen'),
            (u'g', u'-ger'),
            (u'g', u'-ger'),
            (u'g', u'-ges'),
            (u'g', u'-gung'),
            (u'ie', u'e'),
            (u'in', u'en'),
            (u'isch', u'i-sche'),
            (u'k', u'-ke'),
            (u'k', u'-ken'),
            (u'k', u'-ker'),
            (u'l', u'-le'),
            (u'l', u'-len'),
            (u'l', u'-ler'),
            (u'l', u'-lis-mus'),
            (u'le', u'-ler'),
            (u'li-che', u'tem'),
            (u'li-che', u'ten'),
            (u'ln', u'-le'),
            (u'lt', u'-le'),
            (u'm', u'-me'),
            (u'm', u'-mer'),
            (u'me', u'-men'),
            (u'mus', u'men'),
            (u'mus', u'ten'),
            (u'mus', u'tik'),
            (u'n', u'-at'),
            (u'n', u'-er'),
            (u'n', u'-ne'),
            (u'n', u'-nen'),
            (u'n', u'-nis-mus'),
            (u'n', u'r'),
            (u'n', u'st'),
            (u'n', u't'),
            (u'n',u'-ner'),
            (u'nd',u'n'),
            (u'ne',u'ner'),
            # (u'ne',u'n'),
            (u'o',u'-on'),
            (u'o',u'-os'),
            (u'o',u'en'),
            (u'on',u'o-nen'),
            (u'p', u'-pe'),
            (u'p', u'-pen'),
            (u'p', u'-per'),
            (u'ph', u'-phen'),
            (u'ph', u'-phis-mus'),
            (u'r', u'-re'),
            (u'r', u'-rei'),
            (u'r', u'-ren'),
            (u'r', u'-rin'),
            (u'r', u'-ris-mus'),
            (u'r', u'-rung'),
            (u're', u'ste'),
            (u'ren', u'r-te'),
            (u'ren', u'rst'),
            (u'ren', u'rt'),
            (u'rn', u'-re'),
            (u'rn', u'-rung'),
            (u'rn', u'-rung'),
            (u'rt', u'-re'),
            (u'rt', u'r-te'),
            (u's', u''),
            (u's', u'-se'),
            (u's', u'-se-re'),
            (u's', u'-se-res'),
            (u's', u'-ser'),
            (u's', u's-se'),
            (u's', u's-ses'),
            (u'sch', u'-sche'),
            (u'sch', u'-schen'),
            (u'sch', u'-scher'),
            (u'st', u'-ste'),
            (u'st', u'-sten'),
            (u'st', u'n'),
            (u't', u'-ba-re'),
            (u't', u'-bar'),
            (u't', u'-te'),
            (u't', u'-te'),
            (u't', u'-ten'),
            (u't', u'-ter'),
            (u't', u'-tes'),
            (u't', u'-tin'),
            (u't', u'-tis-mus'),
            # (u't', u'e'),
            (u't', u'n'),
            (u't', u'st'),
            (u'te', u'le'),
            # (u'te', u't'),
            (u'ten', u'mus'),
            (u'ten', u'ren'),
            (u'ten', u'tung'),
            (u'ter', u'te-ren'),
            (u'ti-on', u'tor'),
            (u'um', u'a'),
            (u'us', u'en'),
            (u'v', u'-ve'),
            (u'v', u'-ver'),
            (u'v', u'-vis-mus'),
            (u'-ve', u'v'),
            (u'z', u'-ten'),
            (u'z', u'-ze'),
            (u'z', u'-zen'),
            (u'z', u'-zer'),
            (u'ß', u'-ße'),
            (u'ß', u's-se'),
            (u'ös', u'ö-se'),
           ]

if __name__ == '__main__':

    # sys.stdout mit UTF8 encoding.
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)

# `Wortliste` einlesen::

    wordfile = WordFile('wortliste-expandiert') # + Teilwort-Entries
    words = wordfile.asdict()
    
    neuwortdatei = open("zusatzwörter-de-1996-hunspell-compact")
    neueintraege = []
    neueintraege_grossklein = []

# Erstellen der neuen Einträge::

    for line in neuwortdatei:
        key = line.decode('utf8').strip()
        
        if len(key) <= 3:
            continue
        
# Test auf vorhandene (Teil-) Wörter:

        try:
            entry = words[key]
            neueintraege.append(entry)
            continue
        except KeyError:
            pass
        # kleingeschrieben
        try:
            entry = words[key.lower()]
            neueintraege_grossklein.append(entry)
            continue
        except KeyError:
            pass
        # Großgeschrieben
        try:
            entry = words[key.title()]
            neueintraege_grossklein.append(entry)
            continue
        except KeyError:
            pass

    # Endungsabgleich::

        for alt, neu in endungen:
            entry = endungsabgleich(key, alt, neu, grossklein=False)
            if entry:
                neueintraege.append(entry)
                # break

        for alt, neu in endungen:
            entry = endungsabgleich(key, alt, neu, grossklein=True)
            if entry:
                neueintraege_grossklein.append(entry)
                # break


# Patch erstellen::

    print u'# als Teilwörter'
    for entry in neueintraege:
        print unicode(entry)
    print
    print u'# als Teilwörter (andere Großschreibung)'
    for entry in neueintraege_grossklein:
        print unicode(entry)

