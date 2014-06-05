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

import re, sys, codecs, copy
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

# Prüfe ein getrenntes Wort auf Vorkommen von Regeländerungen der
# Orthographiereform 1996.
# Gib eine Eintragszeile zurück.
#
# >>> from abgleich_sprachvarianten import regelaenderungen
# >>> print regelaenderungen(u'Wür-ste')
# Würste;-2-;Wür-ste;Würs-te
# >>> print regelaenderungen(u'Würs-te')
# Würste;-2-;Wür-ste;Würs-te
# >>> print regelaenderungen(u'He-cke')
# Hecke;-2-;He{ck/k-k}e;He-cke
# >>> print regelaenderungen(u'Ligu-ster=he-cke')
# Ligusterhecke;-2-;Ligu-ster=he{ck/k-k}e;Ligus-ter=he-cke
# >>> print regelaenderungen(u'Hass')
# Hass;-2-;-3-;Hass;Hass
# >>> print regelaenderungen(u'fasst')
# fasst;-2-;-3-;fasst;fasst
#
# ::

def regelaenderungen(wort):
    # Regeländerungen:
    r1901 = (u'-st', u'{ck/k-k}')
    r1996 = (u's-t', u'-ck')
    # kein Schluss-ss und sst in de-1901
    # aber: 'ßt' und Schluß-ß auch in de-1996 möglich (langer Vokal)

    w1901, w1996 = wort, wort
    for r1, r2 in zip(r1901, r1996):
        w1901 = w1901.replace(r2,r1)
        w1996 = w1996.replace(r1,r2)
    if u'sst' in wort or wort.endswith(u'ss'):
        w1901 = None

    if w1901 == w1996: # keine Regeländerung im Wort
        line = u'%s;%s' % (join_word(wort), wort)
    elif w1901 is None:
        line = u'%s;-2-;-3-;%s;%s' % (join_word(wort), w1996, w1996)
    else:
        line = u'%s;-2-;%s;%s' % (join_word(wort), w1901, w1996)

    return line


if __name__ == '__main__':

    # sys.stdout mit UTF8 encoding.
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)

    # Die `Wortliste`::

    wordfile = WordFile('../../wortliste') # ≅ 400 000 Einträge/Zeilen
    wortliste = list(wordfile)
    wortliste_neu = []

    wordfile.seek(0)            # Pointer zurücksetzen
    words = wordfile.asdict()

    # Bearbeiten der wortliste "in-place"
    # conflate(wortliste)

    for oldentry in wortliste:
        if len(oldentry) <= 2:
            wortliste_neu.append(oldentry)
            continue
        entry = copy.copy(oldentry)
        sprachabgleich(entry)
        if oldentry == entry and u'ss' in entry[0]:
            for w in entry[1:]:
                if not w.startswith(u'-'):
                    break
            try:
                sprachabgleich(entry, words[join_word(w.replace(u'ss', u'ß'))])
            except KeyError:
                # print entry[0].replace(u'ss', u'ß'), "fehlt"
                if entry.get('de-1901-x-GROSS'):
                    wort1901 = entry.get('de-1901-x-GROSS')
                    wort1901 = wort1901.replace(u'ss', u'ß')
                    # wort1901 = wort1901.replace(u'sst', u'ßt')
                    # wort1901 = wort1901.replace(u'ss=', u'ß=')
                    # wort1901 = wort1901.replace(u'ss>', u'ß>')
                    # wort1901 = wort1901.replace(u'ss<', u'ß<')
                    # wort1901 = wort1901.replace(u'-ss', u'-ß')
                    # wort1901 = re.sub(u'ss$', u'ß', wort1901)
                    if not u'/' in wort1901 and len(wort1901)>3:
                        print u'%s;-2-;%s;-4-' % (join_word(wort1901), wort1901)
                pass  # e.g. "Abfahrtßpezialisten"
        if oldentry == entry and u'ß' in entry[0]:
            try:
                sprachabgleich(entry, words[entry[0].replace(u'ß', u'ss')])
            except KeyError:
                # print entry[0].replace(u'ss', u'ß'), "fehlt"
                pass
        if oldentry == entry:
            wortliste_neu.append(oldentry)
        else:
            wortliste_neu.append(entry)



    # Patch erstellen::

    patch = udiff(wortliste, wortliste_neu, 'wortliste', 'wortliste-neu',
                  encoding=wordfile.encoding)
    if patch:
        # print patch
        patchfile = open('wortliste.patch', 'w')
        patchfile.write(patch + '\n')
    else:
        print "empty patch"
