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
import re, sys
from werkzeug import WordFile, WordEntry, join_word, udiff
from analyse import read_teilwoerter


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
#
# Übertrage die Trennzeichen von `wort1` auf `wort2`:
#
# >>> from abgleich_teilwoerter import uebertrage
#
# >>> uebertrage(u'Haupt=stel-le', u'Haupt·stel·le')
# u'Haupt=stel-le'
#
# Auch teilweise Übertragung, von "kategorisiert" nach "unkategorisiert":
#
# >>> print uebertrage(u'Haupt=stel-le', u'Haupt=stel·le')
# Haupt=stel-le
#
# >>> print uebertrage(u'Haupt·stel-le', u'Haupt=stel·le')
# Haupt=stel-le
#
# Keine Übertragung, wenn die Zahl oder Position der Trennstellen
# unterschiedlich ist oder bei unterschiedlichen Wörtern:
#
# >>> try:
# ...     uebertrage(u'Ha-upt=stel-le', u'Haupt=stel·le')
# ...     uebertrage(u'Haupt=ste-lle', u'Haupt=stel·le')
# ...     uebertrage(u'Waupt=stel-le', u'Haupt=stel·le')
# ... except ValueError:
# ...     pass
#
# Übertragung auch bei unterschiedlicher Schreibung oder Position der
# Trennstellen mit `strict=False` (für Abgleich zwischen Sprachvarianten):
#
# >>> uebertrage(u'er-ster', u'ers·ter', strict=False)
# u'ers-ter'
# >>> uebertrage(u'Fluß=bett', u'Fluss·bett', strict=False)
# u'Fluss=bett'
#
# Auch mit `strict=False` muß die Zahl der Trennstellen übereinstimmen:
#
# >>> try:
# ...     uebertrage(u'Ha-upt=ste-lle', u'Haupt=stel·le', strict=False)
# ... except ValueError:
# ...     pass
#
# Akzeptiere unterschiedliche Anzahl von Trennungen bei st und ck nach
# Selbstlaut:
#
# >>> uebertrage(u'acht=ecki-ge', u'acht·e{ck/k·k}i·ge', strict=False)
# u'acht=e{ck/k-k}i-ge'
# >>> uebertrage(u'As-to-ria', u'Asto·ria', strict=False)
# u'Asto-ria'
# >>> uebertrage(u'Asto-ria', u'As·to·ria', strict=False)
# u'As-to-ria'
# >>> uebertrage(u'So-fa=ecke', u'So·fa=e{ck/k-k}e', strict=False)
# u'So-fa=e{ck/k-k}e'
#
# ::

selbstlaute = u'aeiouäöüAEIOUÄÖÜ'

def uebertrage(wort1, wort2, strict=True):

    trennzeichen1 = re.sub(u'[^-·._|=]', '', wort1)
    trennzeichen2 = re.sub(u'[^-·._|=]', '', wort2)

    silben1 = re.split(u'[-·._|=]+', wort1)
    silben2 = re.split(u'[-·._|=]+', wort2)

    if len(trennzeichen1) != len(trennzeichen2) or (
        silben1 != silben2 and strict):
        # Selbstlaut + st oder ck?
        for selbstlaut in selbstlaute:
            if wort2.find(selbstlaut+u'{ck/k·k}') != -1:
                wort2a = wort2.replace(selbstlaut+u'{ck/k·k}',
                                       selbstlaut+u'ck')
                wort3 = uebertrage(wort1, wort2a, strict)
                return wort3.replace(selbstlaut+u'ck',
                                     selbstlaut+u'{ck/k-k}')
            if wort2.find(selbstlaut+u'{ck/k-k}') != -1:
                wort2a = wort2.replace(selbstlaut+u'{ck/k-k}',
                                       selbstlaut+u'ck')
                wort3 = uebertrage(wort1, wort2a, strict)
                return wort3.replace(selbstlaut+u'ck',
                                     selbstlaut+u'{ck/k-k}')
            if wort2.find(selbstlaut+u's·t') != -1:
                wort2a = wort2.replace(selbstlaut+u's·t',
                                       selbstlaut+u'st')
                wort3 = uebertrage(wort1, wort2a, strict)
                return wort3.replace(selbstlaut+u'st',
                                     selbstlaut+u's-t')
            if wort1.find(selbstlaut+u's-t') != -1:
                wort1a = wort1.replace(selbstlaut+u's-t',
                                       selbstlaut+u'st')
                return uebertrage(wort1a, wort2, strict)
        msg = u'Inkompatibel: %s %s' % (wort1, wort2)
        raise ValueError(msg.encode('utf8'))

    wort3 = silben2.pop(0)
    for t1,t2 in zip(trennzeichen1, trennzeichen2):
        if t2 == u'·' and t1 != u'.':
            wort3 += t1
        elif t2 == u'-' and t1 == u'|':  # Vorsilben
            wort3 += t1
        else:
            wort3 += t2
        wort3 += silben2.pop(0)
    return wort3


# Großschreibung in Kleinschreibung wandeln und umgekehrt
#
# Diese Version funktioniert auch für Wörter mit Trennzeichen (während
# str.title() nach jedem Trennzeichen wieder groß anfängt)
#
# >>> from abgleich_teilwoerter import toggle_case
# >>> toggle_case('Ha-se')
# 'ha-se'
# >>> toggle_case('arm')
# 'Arm'
# >>> toggle_case('frei=bier')
# 'Frei=bier'
#
# ::

def toggle_case(wort):
    if wort[0].istitle():
        return wort.lower()
    else:
        return wort[0].upper() + wort[1:]


# Übertrag kategorisierter Trennstellen aus Teilwort-Datei auf die
# `wortliste`::

def teilwortabgleich(wort, grossklein=False):

        teile = [teilabgleich(teil, grossklein)
                 for teil in wort.split(u'=')]
        return u'='.join(teile)

def teilabgleich(teil, grossklein=False):
    if grossklein:
        return toggle_case(teilabgleich(toggle_case(teil)))
    key = join_word(teil)
    if key not in words.trennungen:
        # print teil.encode('utf8'), 'not in words'
        return teil
    if len(words.trennungen[key]) != 1:
        print 'mehrdeutig:', words.trennungen[key]
        return teil
    try:
        return uebertrage(words.trennungen[key][0], teil)
    except ValueError, e: # Inkompatible Wörter
        print e
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
    # print ' '.join([wort, key]).encode('utf8')

    if (key in words.trennungen and
        len(words.trennungen[key]) == 1):
        # print 'fundum', key.encode('utf8')
        try:
            neustamm = uebertrage(words.trennungen[key][0], stamm)
            # Vergleichsendung abtrennen
            if vergleichsendung:
                neustamm = neustamm[:-len(vergleichsendung)]
            # Mit Originalendung einsetzen
            teile[-1] =  neustamm + endung.replace(u'·', u'-')
        except ValueError, e:
            print e

    return u'='.join(teile)


if __name__ == '__main__':


# Teilwörter einlesen::

    words = read_teilwoerter(path='teilwoerter-%s.txt'%sprachvariante)

    # for key, value in words.trennungen.iteritems():
    #     # if len(value) != 1:
    #         # print key.encode('utf8'), value
    # sys.exit()


# Test::

    # print grundwortabgleich(u'Aa·chen·ern', 'n').encode('utf8')
    # sys.exit()

# `Wortliste` einlesen::

    wordfile = WordFile('../../wortliste') # ≅ 400 000 Einträge/Zeilen
    wortliste = list(wordfile)
    wortliste_alt = deepcopy(wortliste)

# Bearbeiten der wortliste "in-place"::

    for entry in wortliste:

        # Wort mit Trennungen in Sprachvariante
        wort = entry.get(sprachvariante)
        if wort is None: # Wort existiert nicht in der Sprachvariante
            continue

        if u'·' not in wort: # Alle Trennstellen kategorisiert
            continue

        # wort2 = teilwortabgleich(wort, grossklein=False)
        wort2 = grundwortabgleich(wort, endung=u'·res',
                                  vergleichsendung=u'r')

        if wort != wort2:
            entry.set(wort2, sprachvariante)
            print ('%s -> %s' % (wort, wort2)).encode('utf8')

# Patch erstellen::

    patch = udiff(wortliste_alt, wortliste, 'wortliste', 'wortliste-neu',
                 encoding=wordfile.encoding)
    if patch:
        # print patch
        patchfile = open('wortliste.patch', 'w')
        patchfile.write(patch + '\n')
    else:
        print "empty patch"
