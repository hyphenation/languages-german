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

# Die Lang-S Pattern-Dateien welche über "make" Ziele
# im Wurzelverzeichnis der wortliste generiert werden::

pfile_1901 = '../../de-Latf/de-1901-Latf.pat'
pfile_1996 = '../../de-Latf/de-1996-Latf.pat'

# Trenner-Instanzen::

h_Latf = Hyphenator(pfile_1901)
# h_1996 = Hyphenator(pfile_1996)


# Konvertierung mit Hyphenator::

def transformiere(wort, hyphenator=h_Latf):
    
    parts = hyphenator.split_word(wort)

    # alle klein S außer Schluss-S zu Lang-s:
    
    parts = [re.sub(u's(.)', ur'ſ\1', part) for part in parts]

    return u''.join(parts)


if __name__ == '__main__':

    usage = u'%prog [options] [words to be transformed]\n\n' + __doc__

    parser = optparse.OptionParser(usage=usage)
    # parser.add_option('-f', '--pattern-file', dest='pattern_file',
    #                   help='Pattern file, Default "en-US.pat"',
    #                   default='en-US.pat')
    (options, args) = parser.parse_args()

    # sys.stdout mit UTF8 encoding.
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)

    words = [word.decode('utf8') for word in args]
    for word in words:
        print transformiere(word)
