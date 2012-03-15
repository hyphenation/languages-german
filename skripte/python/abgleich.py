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


# Übertrage die (kategorisierten) `trennzeichen` auf das (unkategorisierte)
# `wort`:
#
# >>> from abgleich import uebertrage
# >>> uebertrage(u'=-', u'Haupt·stel·le')
# u'Haupt=stel-le'
#
# Keine Übertragung, wenn `wort` kategorisierte Trennstelle ('-' oder '='
# aufweist):
#
# >>> print uebertrage(u'=-', u'Haupt=stel·le')
# Haupt=stel·le
#
# Keine Übertragung, wenn die Zahl der Trennstellen nicht übereinstimmt:
#
# >>> print uebertrage(u'=--', u'Haupt·stel·le')
# Haupt·stel·le
#
# ::

def uebertrage(trennzeichen, wort):
    silben = wort.split(u'·')
    if len (trennzeichen) != len(silben) -1:
        return wort
    neuwort = silben.pop(0)
    for t in trennzeichen:
        neuwort += t
        neuwort += silben.pop(0)
    return neuwort


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

        if u'{' in unicode(entry):
            continue # Spezialtrennung
        gewichtet = None
        ungewichtet = None
        for field in entry[1:]:
            if field.startswith('-'): # -2-, -3-, ...
                continue
            trennzeichen = re.sub(u'[^-·._|=]', '', field)
            if u'·' not in trennzeichen:
                gewichtet = trennzeichen
            else:
                ungewichtet = trennzeichen
        if gewichtet is None or ungewichtet is None:
            continue

        for i in range(1,len(entry)):
            if u'·' in entry[i]:
                entry[i] = uebertrage(gewichtet, entry[i])

        print gewichtet.encode('utf8'), str(entry)


if __name__ == '__main__':

    # Die `Wortliste`::

    wordfile = WordFile('../../wortliste') # ≅ 400 000 Einträge/Zeilen
    wortliste = list(wordfile)

    wortliste_alt = deepcopy(wortliste)

    # Bearbeiten der wortliste "in-place"
    conflate(wortliste)

    # sprachabgleich(wortliste)

    # Patch erstellen::

    patch = udiff(wortliste_alt, wortliste, 'wortliste', 'wortliste-neu')
    if patch:
        print patch
        patchfile = open('../../wortliste.patch', 'w')
        patchfile.write(patch + '\n')
    else:
        print "empty patch"
