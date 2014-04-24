#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2014 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# Abgleich der Trennstellen zwischen Woertern mit unterschiedlichem Präfix
# ========================================================================
#
# Übertragen von kategorisierten Trennstellen von "Wortresten" nach Abtrennen
# der Präfixe auf Vorkommen dieser Wortteile mit anderem Präfix.
# ::

import re, sys, codecs
import difflib
from werkzeug import (WordFile, WordEntry, join_word, uebertrage, TransferError, sprachabgleich, toggle_case)
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

# Abtrennen von Präfixen und Eintrag aller (Teil-) Wörter in eine neue
# ``teilwoerter`` Instanz::

def find_stems(words):
    stems = teilwoerter()
    for line in words:
        if u'·' in line:
            continue
        word = line.split()[0]
        capitalized = word[0].istitle()
        # un<an<ge<nehm -> [un<an<ge<nehm, an<ge<nehm, ge<nehm]
        parts = []
        for part in word.split(u'<').__reversed__():
            parts.insert(0, part)
            teil = u'<'.join(parts)
            if capitalized: # Großschreibung übertragen
                teil = teil[0].title() + teil[1:]
            stems.add(teil)
    return stems

# Vergleich des Wortteiles nach dem letzten '<' mit ``stems``::

def praefixabgleich(wort, grossklein=False):

    teile = wort.split('<')
    teile[0] = teile[0].replace(u'·', u'-')
    stamm = teile[-1]
    key = join_word(stamm)
    # print u' '.join([wort, key])
    if grossklein:
        key = toggle_case(key)

    if key in stems.trennvarianten:
        # print u'fundum', key
        for altstamm in stems.trennvarianten[key]:
            if u'·' in altstamm:
                continue
            if grossklein:
                altstamm = toggle_case(altstamm)
            try:
                neustamm = uebertrage(altstamm, stamm)
                # print u'alt/neu', wort, altstamm, neustamm
                teile[-1] =  neustamm
                break
            except TransferError, e:
                print unicode(e)

    return u'<'.join(teile)

# Vergleiche zwei Sequenzen von Strings, gib einen "unified diff" als
# Byte-String zurück (weil difflib nicht mit Unicode-Strings arbeiten kann).

def udiff(a, b, fromfile='', tofile='', n=1, encoding='utf8'):

    a = [line.encode(encoding) for line in a]
    b = [line.encode(encoding) for line in b]

    diff = difflib.unified_diff(a, b, fromfile, tofile, n)

    if diff:
        return ''.join(diff)
    else:
        return None



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

# Alle Trennstellen kategorisiert oder kein (markierter) Präfix::

        if (u'·' not in line) or (u'<' not in line):
            words2.append(line)
            continue

# Parsen::

        fields = line.split(' ')
        wort = fields[0]

# Präfixabgleich::

        wort2 = praefixabgleich(wort)
        if wort2 == wort:
            wort2 = praefixabgleich(wort, grossklein=True)
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
