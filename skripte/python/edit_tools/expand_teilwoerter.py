#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2014 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# Erweitern der Wortliste um Kombinationen von Teilwörtern
# ========================================================
#
# Zerlegen von Composita an den Wortfugen und Übernahme der Teile als
# eigenständige Einträge.
#
# >>> from expand_teilwoerter import *
#
# ::

import os, re, sys, codecs, copy
from wortliste import (WordFile, WordEntry, join_word,
                      sprachabgleich, toggle_case, sortkey_duden)


# Funktionen
# -----------
#
# Iterator, gibt alle geordneten Teilkombinationen zurück
#
# >>> list(multisplitter(u'test', u'='))
# [u'test']
#
# >>> list(multisplitter(u'a=b', u'='))
# [u'a', u'a=b', u'b']
#
# >>> list(multisplitter(u'a=b=c', u'='))
# [u'a', u'a=b', u'a=b=c', u'b', u'b=c', u'c']
#
# >>> list(multisplitter('a=b=c=d', '='))
# ['a', 'a=b', 'a=b=c', 'a=b=c=d', 'b', 'b=c', 'b=c=d', 'c', 'c=d', 'd']
#
# >>> list(multisplitter(u'a=b==c', u'=='))
# [u'a=b', u'a=b==c', u'c']
#
# >>> list(multisplitter('a=b==c=de', '=='))
# ['a=b', 'a=b==c=de', 'c=de']
#
# >>> list(multisplitter('a=b==c=de', '==='))
# ['a=b==c=de']
#
# >>> list(multisplitter('er[<st/st=]ritt', u'='))
# [u'er[<st/st=]ritt']
# >>> list(multisplitter('Schiff[=s/s=]tau', u'='))
# [u'Schiff[=s/s=]tau']
# >>> list(multisplitter('a{ll/ll=l}ie-bend', u'='))
# [u'a{ll/ll=l}ie-bend']
# >>> list(multisplitter('Be[t=t/{tt/tt=t}]uch', u'='))
# [u'Be[t=t/{tt/tt=t}]uch']
#
# ::

def multisplitter(wort, sep):
    specials = re.findall(ur'\[.*%s.*\]|\{[^}]*%s[^}]*\}'%(sep,sep), wort)
    for sp in specials:
        wort = wort.replace(sp, sp.replace(sep, '*'))
    parts = wort.split(sep)
    length = len(parts)
    for start in range(length):
        for end in range(start+1, length+1):
            part = sep.join(parts[start:end])
            if specials:
                part = part.replace('*', sep)
            yield part


# Gib eine Liste möglicher Zerlegungen eines Kompositums zurück.
# Berücksichtige dabei die Bindungsstärke bis zum Level 3
# ("===", zur Zeit höchste Auszeichnung in der Wortliste).
#
# >>> multisplit(u'test')
# [u'test']
#
# >>> multisplit(u'a=b')
# [u'a', u'a=b', u'b']
#
# >>> multisplit(u'a=b=c')
# [u'a', u'a=b', u'a=b=c', u'b', u'b=c', u'c']
#
# >>> multisplit(u'a==b=c')
# [u'a', u'a==b=c', u'b', u'b=c', u'c']
#
# >>> multisplit(u'a==b=c==d')
# [u'a', u'a==b=c', u'a==b=c==d', u'b', u'b=c', u'c', u'b=c==d', u'd']
#
# >>> for w in multisplit(u'Brenn=stoff==zel-len===an<trieb'):
# ...    print w
# Brenn
# Brenn=stoff
# Stoff
# Brenn=stoff==zel-len
# Zel-len
# Brenn=stoff==zel-len===an<trieb
# An<trieb
#
# ::

def multisplit(wort):
    parts = []
    for p3 in multisplitter(wort, u'==='):
        if u'===' in p3:
            parts.append(p3)
            continue
        for p2 in multisplitter(p3, u'=='):
            if u'==' in p2:
                parts.append(p2)
                continue
            p2 = p2.replace(u'<=', u'<')
            p2 = p2.replace(u'=>', u'>')
            for p1 in multisplitter(p2, u'='):
                parts.append(p1)
    if wort[:2].istitle():
        parts = [part[0].title() + part[1:] for part in parts]
    return parts

# Gib eine Liste von allen (sinnvollen) Zerlegungen eines WordEntry zurück
#
# >>> from wortliste import WordEntry
#
# >>> split_entry(WordEntry(u'Aachen;Aa-chen'))
# [[u'Aachen', u'Aa-chen']]
# >>> aalbestand = WordEntry(u'Aalbestand;Aal=be<stand')
# >>> split_entry(aalbestand)
# [[u'Aal', u'Aal'], [u'Aalbestand', u'Aal=be<stand'], [u'Bestand', u'Be<stand']]
#
# >>> godi = WordEntry(u'Abendgottesdienste;-2-;Abend==got-tes=dien-ste;Abend==got-tes=diens-te')
# >>> for entry in split_entry(godi):
# ...     print entry
# Abend;Abend
# Abendgottesdienste;-2-;Abend==got-tes=dien-ste;Abend==got-tes=diens-te
# Gottes;Got-tes
# Gottesdienste;-2-;Got-tes=dien-ste;Got-tes=diens-te
# Dienste;-2-;Dien-ste;Diens-te
#
# >>> bb = WordEntry(u'Biberbettuch;-2-;Bi-ber==be[t=t/{tt/tt=t}]uch')
# >>> for entry in split_entry(bb):
# ...     print entry
# Biber;-2-;Bi-ber
# Biberbettuch;-2-;Bi-ber==be[t=t/{tt/tt=t}]uch
# Bettuch;-2-;Be[t=t/{tt/tt=t}]uch
#
# ::

def split_entry(entry):

    entries = []

    for col in range(1, len(entry)):
        wort = entry[col]
        if u'=' not in wort:
            continue # nichts zu splitten
        parts = multisplit(wort)

        # Kopien des Originaleintrags erstellen
        if not entries:
            for part in parts:
                entries.append(copy.copy(entry))
                entries[-1][0] = join_word(part)
        # Entries ausfüllen
        for i in range(len(parts)):
            entries[i][col] = parts[i]

    if entries:
        for e in entries:
            e.conflate_fields() # Sprachabgleich
        return entries
    else:
        return [entry]

# Gib ein Dictionary mit Einträgen der Wortliste und Teilwortkombinationen
# zurück:

def expand_wordfile(wordfile):
    words = {}  # Wörter aus der Liste

    for entry in wordfile:
        try:
            entries = split_entry(entry)
        except IndexError:  # unterschiedliche Zerlegung je nach Sprache
            # print "problematisch", unicode(entry)
            words[entry[0]] = entry
            continue

        for e in entries:
            if (len(entries) == 1
                or (e[0].lower() not in words and e[0].title() not in words)
                or len(e[0]) <= 3 and len(e) == 2 # kurze einfache Wörter
               ):
                words[e[0]] = e

    return words

def exists(wort):
    key = join_word(wort)
    return (key.title() in words) or (key.lower() in words) or (len(wort)<4)

if __name__ == '__main__':

    # sys.stdout mit UTF8 encoding.
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)

# `Wortliste` einlesen::

    wordfile = WordFile('../../../wortliste') # ≅ 400 000 Einträge/Zeilen

# Wichtung::

    # sprachvariante = 'de-1996'
    # sprachvariante = 'de-1901'
    # words = wordfile.asdict()
    # for entry in words.itervalues():
    #     wort = entry.get(sprachvariante)
    #     if not wort:
    #         continue
    #     if (u'<=' in wort or u'=>' in wort or u'==' in wort):
    #         continue
    #     parts = [part for part in multisplit(wort)
    #              if u'=' not in part]
    #     if len(parts) == 3:
    #         if parts[1] == u'zu':
    #             continue
    #         if (exists(parts[0]) and exists(''.join(parts[1:]))
    #             and not(exists(parts[-1])
    #                     and (exists(''.join(parts[:-1])) or exists(''.join(parts[:-1])+u's')))
    #            ):
    #             for i in range(1,len(parts)):
    #                 parts[i] = parts[i].lower()
    #             wort = u'=='.join([parts[0], u'='.join(parts[1:])])
    #             entry.set(wort, sprachvariante)
    #             sprachabgleich(entry)
    #             print unicode(entry)
    #
    # sys.exit()

# expandieren und Speichern::

    words = expand_wordfile(wordfile)

    print len(words), "expandiert"

    outfile = open('wortliste-expandiert', 'w')

    for entry in sorted(words.values(), key=sortkey_duden):
        outfile.write(str(entry))
        outfile.write('\n')
