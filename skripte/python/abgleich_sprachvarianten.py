#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2011 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# Abgleich der Trennstellen zwischen Sprachvarianten
# ====================================================
#
# * Übertragen von kategorisierten Trennstellen zwischen Sprachvarianten
#   desselben Wortes, und/oder
#
# * Zusammenfassen von Feldern mit gleichem Inhalt wenn das Ergebnis ein
#   wohlgeformter Eintrag ist.
#
# ::

from copy import deepcopy
import re, sys, codecs
from werkzeug import WordFile, WordEntry, join_word, udiff, sprachabgleich


# Zusammenfassen von Feldern mit gleichem Inhalt z.B.
#
#      hallo;-2-;hal-lo;hal-o     --> hallo;hal-lo
#
# in allen Einträgen von `wortliste`.
# Siehe ``WordEntry.conflate_fields()`` in werkzeug.py.
#
# Anwendung 2012-03-13
# (getestet mit ``texlua validate.lua < ../wortliste``)
#
# =========   ======   =======
# Typ         Vorher   Nachher
# ---------   ------   -------
# ua          371807   374614
# uxtr        41156    38349
# =========   ======   =======
#
# ::

def conflate(wortliste):

    for entry in wortliste:
        if len(entry) <= 2:
            continue # allgemeine Schreibung
        # Felder zusammenfassen:
        entry.conflate_fields()
        continue

if __name__ == '__main__':

    # sys.stdout mit UTF8 encoding.
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)

    # Die `Wortliste`::

    wordfile = WordFile('../../wortliste') # ≅ 400 000 Einträge/Zeilen
    wortliste = list(wordfile)

    wortliste_alt = deepcopy(wortliste)

    # Bearbeiten der wortliste "in-place"
    # conflate(wortliste)

    for entry in wortliste:
        sprachabgleich(entry)

    # Patch erstellen::

    patch = udiff(wortliste_alt, wortliste, 'wortliste', 'wortliste-neu',
                  encoding=wordfile.encoding)
    if patch:
        # print patch
        patchfile = open('wortliste.patch', 'w')
        patchfile.write(patch + '\n')
    else:
        print "empty patch"
