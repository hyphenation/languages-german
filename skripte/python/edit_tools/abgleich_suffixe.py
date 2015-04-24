#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2014 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# Abgleich der Trennstellen zwischen Woertern mit unterschiedlichem Suffix
# ========================================================================
#
# Übertragen von kategorisierten Trennstellen von "Wortresten" nach Abtrennen
# der Suffixe auf Vorkommen dieser Wortteile mit anderem Suffix.
# ::

import re, sys, codecs
import difflib
from wortliste import (WordFile, WordEntry, join_word, uebertrage, TransferError, sprachabgleich, toggle_case)
from analyse import read_teilwoerter, teilwoerter
from abgleich_praefixe import udiff
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

# Abtrennen von Suffixen und Eintrag aller (Teil-) Wörter in eine neue
# ``teilwoerter`` Instanz::

def find_stems(words):
    stems = teilwoerter()
    for line in words:
        if u'·' in line:
            continue
        word = line.split()[0]
        # Wis-sen>schaft>lich>keit -> [Wis-sen, Wis-sen>schaft, Wis-sen>schaft>lich]
        parts = []
        for part in word.split(u'>'):
            parts.append(part)
            teil = u'>'.join(parts)
            stems.add(teil)
    return stems

# Vergleich des Wortteiles nach dem ersten '>' mit ``stems``::

def suffixabgleich(wort, grossklein=False):

    teile = wort.split('>')
    stamm = teile[0]
    key = join_word(stamm)
    # print u' '.join([wort, key])
    if grossklein:
        key = toggle_case(key)

    if key in stems.trennvarianten:
        # print u'fundum', key, teile
        for altstamm in stems.trennvarianten[key]:
            if u'·' in altstamm:
                continue
            if grossklein:
                altstamm = toggle_case(altstamm)
            try:
                neustamm = uebertrage(altstamm, stamm)
                # print u'alt/neu', wort, altstamm, neustamm
                teile[0] =  neustamm
                break
            except TransferError, e:
                print unicode(e)

    return u'>'.join(teile)



if __name__ == '__main__':

    # sys.stdout mit UTF8 encoding.
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)

# Teilwörter einlesen::

    wordfile = open('teilwoerter-%s.txt'%sprachvariante)
    # 1. Zeile ist Kommentar:
    comment = wordfile.readline().decode('utf8')
    words = [line.decode('utf8') for line in wordfile]

# Vorsilben abtrennen::

    stems = find_stems(words)

# Erstellen der neuen wortliste
# =============================
# ::

    words2 = []

    for line in words:

# Alle Trennstellen kategorisiert oder kein (markierter) Suffix::

        if (u'·' not in line) or (u'>' not in line):
            words2.append(line)
            continue

# Parsen::

        fields = line.split(' ')
        wort = fields[0]

# Suffixabgleich::

        wort2 = suffixabgleich(wort)
        if wort2 == wort:
            wort2 = suffixabgleich(wort, grossklein=True)
        fields[0] = wort2
        words2.append(' '.join(fields))

# Rückmeldung::

        if (wort != wort2): #and (u'·' not in wort2):
            print u'%s -> %s' % (wort, wort2)

# Patch erstellen::

    words.insert(0, comment)
    words2.insert(0, comment)
    patch = udiff(words, words2, 'teilwoerter', 'teilwoerter-neu')
    if patch:
        # print patch
        patchfile = open('teilwoerter.patch', 'w')
        patchfile.write(patch + '\n')
    else:
        print u'empty patch'
