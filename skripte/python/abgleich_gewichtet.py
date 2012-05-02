#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2011 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# Abgleich mit Zweig "keine Trennstellen in zweisilbigen Wörtern
# ==================================================================
# ::

from copy import deepcopy
import re, sys
from werkzeug import WordFile, WordEntry, join_word, udiff
from abgleich_teilwoerter import uebertrage, zerlege

sprachvariante = 'de-1901'
# sprachvariante = 'de-2006'  # Reformschreibung
# sprachvariante = 'de-x-GROSS'    # ohne ß (Großbuchstaben und Kapitälchen)


if __name__ == '__main__':

# Die Wortlisten::

    # Master als Wörterbuch (dict Instanz) oder Liste:
    wordfile = WordFile('../../wortliste')
    # words = wordfile.asdict()
    wortliste = list(wordfile)

    # Branch "keine Trennstellen ..." als Wörterbuch oder Liste:
    wortfile_gewichtet = WordFile('../../wortliste-gewichtet')
    # gewichtet = list(wortfile_gewichtet)
    gewichtet = wortfile_gewichtet.asdict()
    
    # Neue Listen (Sammelbecken)::
    wortliste_alt = deepcopy(wortliste)

# Übertrag der Wichtung/Kategorisierung aus der "gewichteten" Liste::

    for entry in wortliste:
        key = entry[0]
        wort = entry.get(sprachvariante)
        if key in gewichtet:
            g_wort = gewichtet[key].get(sprachvariante)
            if wort is None or g_wort is None:
                continue
            try:
                neuwort = uebertrage(g_wort, wort)
            except ValueError, e:
                print e
                continue
            entry.set(neuwort, sprachvariante)            
        else:
            if key.lower() in gewichtet:
                g_entry = gewichtet[key.lower()]
            elif key.title() in gewichtet:
                g_entry = gewichtet[key.title()]
            print ('? %s %s' % (wort, g_entry.get(sprachvariante))).encode('utf8')


# Patch erstellen::

    patch = udiff(wortliste_alt, wortliste, 'wortliste-alt', 'wortliste')
    if patch:
        # print patch
        if wortfile_gewichtet.encoding != 'utf8':
            patch = patch.decode('utf8').encode(wortfile_gewichtet.encoding)
        patchfile = open('wortliste.patch', 'w')
        patchfile.write(patch + '\n')
    else:
        print "empty patch"
