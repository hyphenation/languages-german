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

# >>> print uebertrage(u'Haupt·stel-le', u'Haupt=stel·le')
# Haupt=stel-le
#
# Keine Übertragung, wenn die Zahl oder Position der Trennstellen
# unterschiedlich ist oder bei unterschiedlichen Wörtern:
#
# >>> print uebertrage(u'Ha-upt=stel-le', u'Haupt=stel·le')
# Haupt=stel·le
# >>> print uebertrage(u'Haupt=ste-lle', u'Haupt=stel·le')
# Haupt=stel·le
# >>> print uebertrage(u'Waupt=stel-le', u'Haupt=stel·le')
# Haupt=stel·le
#
# ::

def uebertrage(wort1, wort2):
    
    trennzeichen1 = re.sub(u'[^-·._|=]', '', wort1)
    trennzeichen2 = re.sub(u'[^-·._|=]', '', wort2)

    silben1 = re.split(u'[-·._|=]+', wort1)
    silben2 = re.split(u'[-·._|=]+', wort2)

    if silben1 != silben2:
        msg = u'Inkompatible Wörter: %s %s\n' % (wort1, wort2)
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


# Übertrag kategorisierter Trennstellen aus Teilwort-Datei auf die
# `wortliste`::

def teilwortabgleich(wortliste):

    for entry in wortliste:

# Wort mit Trennungen in Sprachvariante::

        wort = entry.get(sprachvariante)
        if wort is None: # Wort existiert nicht in der Sprachvariante
            continue

        if u'·' not in wort: # Alle Trennstellen kategorisiert
            continue
        
        teile = []
        for teil in wort.split(u'='):
            key = join_word(teil) 
            if (join_word(teil) in words.trennungen and
                len(words.trennungen[key]) == 1):
                try:
                    neuteil = uebertrage(words.trennungen[key][0], teil)
                except ValueError, e:
                    print e
                    neuteil = teil
                teile.append(neuteil)
            else:
                teile.append(teil)
                
        wort2 = u'='.join(teile)
        
        if wort == wort2:
            continue
        
        entry.set(wort2, sprachvariante)
        # print ('%s -> %s' % (wort, wort2)).encode('utf8')



if __name__ == '__main__':

    # Die `Wortliste`::

    wordfile = WordFile('../../wortliste') # ≅ 400 000 Einträge/Zeilen
    wortliste = list(wordfile)
    wortliste_alt = deepcopy(wortliste)
    
    words = read_teilwoerter()

    # Bearbeiten der wortliste "in-place"

    teilwortabgleich(wortliste)

    # Patch erstellen::

    patch = udiff(wortliste_alt, wortliste, 'wortliste', 'wortliste-neu',
                 encoding=wordfile.encoding)
    if patch:
        print patch
        patchfile = open('wortliste.patch', 'w')
        patchfile.write(patch + '\n')
    else:
        print "empty patch"
