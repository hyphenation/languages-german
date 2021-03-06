#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2014 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# long_s_conversion.py: Demonstrator für die Lang-S Wandlung
# =============================================================================

u"""Rund-S nach Lang-S Wandlung über "hyphenation patterns"."""

import sys, codecs, re, optparse
from hyphenation import Hyphenator


# Konfiguration
# -------------

# Lang-s Pseudo-Trennmuster mit "s-" statt "ſ" (ausſagen -> auss-agen)
# (mit "make de-x-long-s" im Wurzelverzeichnis der wortliste generiert)::

default_pfile = '../../../de-long-s/de-x-long-s.pat'

# Ausnahmen
# ---------

# ſ steht auch am Ende von Abkürzungen, wenn es im abgekürzten Wort steht
# (Abſ. - Abſatz/Abſender, (de)creſc. - (de)creſcendo, daſ. - daſelbst ...)
# s steht auch in der Mitte von Abkürzungen, wenn es im abgekürzten Wort steht
# (Ausg. - Ausgang/Ausgabe, Hrsg. - Herausgeber, ...)
# ::

exceptions = (u'Abſ', # Abſatz/Abſender
              u'beſ',  # beſonders
              u'coſ',  # Ko<ſinus
            # u'daſ',   # da<ſelbſt (nicht von Artikel "das" zu unterscheiden!)
              u'Diſſ',  # Diſſertation
              u'Hſ',    # Handschrift
              u'Maſſ',  # Maſſachuſetts
            # u'Miſſ',  # Miſſiſippi (nicht von Miſs (Frln.) zu unterscheiden)
              # TODO: N-Z
             )
exceptions = dict((ex.replace(u'ſ', u's'), ex) for ex in exceptions)

# Konvertierung mit Hyphenator::

def transformiere(wort, hyphenator):

    if u's' not in wort:
        return wort
    if wort in exceptions:
        return exceptions[wort]

    wort = hyphenator.hyphenate_word(wort, hyphen=u'-', lmin=1, rmin=1)

    # Wandle "s-" in "ſ" (auss-agen -> ausſagen):
    
    return wort.replace(u's-', u'ſ').replace(u'S-', u'S')

def transformiere_text(text, hyphenator):
    # Text zerlegen: finde (ggf. leere) Folgen von nicht-Wort-Zeichen
    # gefolgt von Wort-Zeichen. Der Iterator liefert Match-Objekte, mit
    # den Untergruppen 0: nicht-Wort und 1: Wort.
    it = re.finditer(r"([\W0-9_]*)(\w*)", text, flags=re.UNICODE)
    # Konvertierung und Zusammenfügen
    parts = [match.groups()[0] # nicht-Wort Zeichen
             + transformiere(match.groups()[1], hyphenator)
             for match in it]
    return u''.join(parts)

if __name__ == '__main__':

    usage = u'%prog [options] [words to be transformed]\n\n' + __doc__

    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-f', '--pattern-file', dest='pattern_file',
                      help='Pattern file, Default "%s"' % default_pfile,
                      default=default_pfile)
    parser.add_option('-t', '--test', action="store_true", default=False,
                      help='Vergleiche Eingabe mit Rekonstruktion, '
                      'Melde Differenzen.')

    (options, args) = parser.parse_args()
    

    h_Latf = Hyphenator(options.pattern_file)

    # sys.stdout mit UTF8 encoding.
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)

    if len(args) > 0:
        lines = [' '.join(args).decode('utf8')]
    else:
        lines = (line.decode('utf8') for line in sys.stdin)

    if options.test:
        for line in lines:
            line2 = transformiere_text(line.replace(u'ſ', u's'), h_Latf)
            if line2 != line:
                print line.strip(), '->', line2,
        sys.exit()
        
    for line in lines:
        print transformiere_text(line, h_Latf),
