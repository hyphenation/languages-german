#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2011 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# long_s_quasihyph.py: 
# ============================================================

u"""Filter zum Wandeln von Wörtern mit langem S in
Pseudo-Trennbeispiele (ausſagen -> aus-sagen)."""

import sys, optparse, re


usage = u'%prog [Optionen]\n' + __doc__
parser = optparse.OptionParser(usage=usage)
parser.add_option('-e', '--encoding', dest='encoding',
                    help=u'Kodierung der Ausgabe, '
                    u'Vorgabe "iso-8859-15"',
                    default='iso-8859-15')

(options, args) = parser.parse_args()

lines = (line.decode('utf-8') for line in sys.stdin)

words = (re.sub(ur'\[(.*)/.*\]', ur'\1',
                word.replace(u's', u's-').replace(u'ſ', u's').replace(u'-\n', u'\n'))
         for word in lines)

sys.stdout.writelines(line.encode(options.encoding) for line in words)
