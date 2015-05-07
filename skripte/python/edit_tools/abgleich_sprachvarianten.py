#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2014 Günter Milde.
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
# * Ergänzen von Formen mit SS statt ß.
#
# ::

import re, sys, codecs, copy
from wortliste import WordFile, WordEntry, join_word, udiff, sprachabgleich


# Zusammenfassen von Feldern mit gleichem Inhalt z.B.
#
#      hallo;-2-;hal-lo;hal-o     --> hallo;hal-lo
#
# in allen Einträgen von `wortliste`.
# Siehe ``WordEntry.conflate_fields()`` in wortliste.py.
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

if __name__ == '__main__':

    # sys.stdout mit UTF8 encoding.
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)

    # Die `Wortliste`::

    wordfile = WordFile('../../../wortliste') # ≅ 400 000 Einträge/Zeilen
    wortliste = list(wordfile)
    wortliste_neu = []

    wordfile.seek(0)            # Pointer zurücksetzen
    words = wordfile.asdict()

    for oldentry in wortliste:
        if len(oldentry) <= 2:
            # Ggf. Ergänzen der GROSS-Variante:
            if (u'ß' in oldentry[0]
                and oldentry[0].replace(u'ß', u'ss') not in words
                and oldentry[0].replace(u'ß', u'ss').lower() not in words
                and oldentry[0].replace(u'ß', u'ss').title() not in words
               ):
                entry = WordEntry(oldentry[0].replace(u'ß', u'ss')
                                  + u';-2-;-3-;-4-;'
                                  + oldentry[1].replace(u'ß', u'ss'))
                wortliste_neu.append(entry)
            wortliste_neu.append(oldentry)
            continue
        entry = copy.copy(oldentry)
        sprachabgleich(entry)
        # Sprachabgleich mit ß-Form (Strassenschild vs. Straßenschild)
        if oldentry == entry and u'ss' in entry[0]:
            # Vergleichseintrag für Sprachabgleich finden:
            for field in entry[1:]:
                if not field.startswith(u'-'):
                    break # ``field`` ist jetzt erstes nichtleeres Feld
            sz_key = join_word(field.replace(u'ss', u'ß'))
            try:
                vergleichseintrag = words[sz_key]
                sprachabgleich(entry, vergleichseintrag)
            except KeyError: # sz-Variante fehlt
                wort1901 = entry.get('de-x-GROSS,de-1901-x-GROSS')
                if (wort1901 and 'ss' in wort1901
                    and not sz_key.title() in words):
                    sz_wort = wort1901.replace(u'ss', u'ß')
                    if not u'/' in sz_wort and len(sz_key) > 3:
                        # print wort1901, "sz-Variante fehlt", sz_key
                        print u'%s;-2-;%s;-4-' % (join_word(sz_wort), sz_wort)
        if oldentry == entry and u'ß' in entry[0]:
            try:
                sprachabgleich(entry, words[entry[0].replace(u'ß', u'ss')])
            except KeyError:
                # Ergänzen der GROSS-Variante
                if entry.get('de-1996') is None:
                    oldentry = WordEntry(u';'.join(
                                        [entry[0].replace(u'ß', u'ss'),
                                         u'-2-;-3-',
                                         entry[2].replace(u'ß', u'ss'),
                                         entry[2].replace(u'ß', u'ss')]))
                elif entry.get('de-1996') is None:
                    # Dämmmassnahmen;-2-;-3-;-4-;-5-;-6-;Dämm==mass=nah-men;-8-
                    oldentry = WordEntry(entry[0].replace(u'ß', u'ss')
                                      + u';-2-;-3-;-4-;-5-;-6-;'
                                      + entry[3].replace(u'ß', u'ss')
                                      + u'-8-')
                else:
                    oldentry = WordEntry(u';'.join(
                                        [entry[0].replace(u'ß', u'ss'),
                                         u'-2-;-3-;-4-;-5-',
                                         entry[2].replace(u'ß', u'ss'),
                                         entry[3].replace(u'ß', u'ss'),
                                         u'-8-']))

                wortliste_neu.append(oldentry)
        entry.conflate_fields()
        wortliste_neu.append(entry)

    words = None # Speicher freigeben
    
    # Patch erstellen::

    patch = udiff(wortliste, wortliste_neu, 'wortliste', 'wortliste-neu',
                  encoding=wordfile.encoding)
    if patch:
        # print patch
        patchfile = open('wortliste.patch', 'w')
        patchfile.write(patch + '\n')
        print '"wortliste.patch" geschrieben'
    else:
        print 'empty patch'
