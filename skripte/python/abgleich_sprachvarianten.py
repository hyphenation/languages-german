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
import re, sys
from werkzeug import WordFile, WordEntry, join_word, udiff
from abgleich_teilwoerter import uebertrage


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

# Übertrag kategorisierter Trennstellen zwischen den Feldern aller Einträge
# in `wortliste`::

def sprachabgleich(wortliste):

    for entry in wortliste:

        if len(entry) <= 2:
            continue # allgemeine Schreibung

        # if u'{' in unicode(entry):
        #     continue # Spezialtrennung
        gewichtet = None
        ungewichtet = None
        for field in entry[1:]:
            if field.startswith('-'): # -2-, -3-, ...
                continue
            if u'·' not in field:
                gewichtet = field
            else:
                ungewichtet = field
        if gewichtet is None or ungewichtet is None:
            continue
        # print 'Abgleich', str(entry)

        for i in range(1,len(entry)):
            if u'·' in entry[i]:
                try:
                    entry[i] = uebertrage(gewichtet, entry[i], strict=False)
                except ValueError, e:
                    print e
        print gewichtet.encode('utf8'), str(entry)


if __name__ == '__main__':

    # Die `Wortliste`::

    wordfile = WordFile('../../wortliste') # ≅ 400 000 Einträge/Zeilen
    wortliste = list(wordfile)

    wortliste_alt = deepcopy(wortliste)

    # Bearbeiten der wortliste "in-place"
    # conflate(wortliste)

    sprachabgleich(wortliste)

    # Patch erstellen::

    patch = udiff(wortliste_alt, wortliste, 'wortliste', 'wortliste-neu',
                  encoding=wordfile.encoding)
    if patch:
        # print patch
        patchfile = open('wortliste.patch', 'w')
        patchfile.write(patch + '\n')
    else:
        print "empty patch"
