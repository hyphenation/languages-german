#!/usr/bin/env python
# -*- coding: utf8 -*-
u"""Hyphenation using a pure Python implementation of Frank Liang's algorithm.

    This module provides a class to hyphenate words.

    `Hyphenator.split_word(word)` takes a string (the word), and returns a
    list of parts that can be separated by hyphens.

    hyphenator = Hyphenator(pattern_file)
    >>> hyphenator.split_word(u"hyphenation")
    [u'hy', u'phen', u'ation']
    >>> hyphenator.hyphenate_word(u"supercalifragilisticexpialidocious", '-')
    u'su-per-cal-ifrag-ilis-tic-ex-pi-ali-do-cious'
    >>> hyphenator.hyphenate_word(u"project")
    u'project'

    based on http://nedbatchelder.com/code/modules/hyphenate.py
    by Ned Batchelder, July 2007.

    version 2: Internationalization (external pattern files, Unicode)
    © 2013 Günter Milde
"""
# See also the independently developed http://pyphen.org/

import re, optparse

__version__ = '2.0 2014-07-04'

class Hyphenator:
    def __init__(self, pattern_file, exceptions=''):
        self.tree = {}
        for pattern in self.yield_patterns(pattern_file):
            self._insert_pattern(pattern)

        self.exceptions = {}
        for ex in exceptions.split():
            # Convert the hyphenated pattern into a point array for use later.
            self.exceptions[ex.replace(u'-', u'')] = [0] + [ int(h == u'-')
                                            for h in re.split(ur"[^-]", ex) ]

    def yield_patterns(self, path, invalid_chars = '%\\{}', encoding='utf8'):
        """
        Yield hyphenation patterns from a file.

        Pattern file format: As used by TEX
        * one pattern per line,
        * every line containing one of the characters in
          the string `invalid_chars` (comments and TeX macros) is discarded,
        * file encoding in argument `encoding` (default 'utf8').
        """
        # TODO: process OpenOffice hyphenation files?
        # (Suffix '.dic', encoding specified in first line of file).
        lines = open(path)
        for line in lines:
            for c in invalid_chars:
                if c in line:
                    line = ''
                    continue
            line = line.decode(encoding).strip()
            if line:
                yield line
        lines.close()

    def _insert_pattern(self, pattern):
        # Convert the a pattern like 'a1bc3d4' into a string of chars 'abcd'
        # and a list of points [ 1, 0, 3, 4 ].
        chars = re.sub(u'[0-9]', u'', pattern)
        points = [ int(d or 0) for d in re.split(u'[^0-9]', pattern) ]

        # Insert the pattern into the tree.  Each character finds a dict
        # another level down in the tree, and leaf nodes have the list of
        # points.
        t = self.tree
        for c in chars:
            if c not in t:
                t[c] = {}
            t = t[c]
        t[None] = points

    def split_word(self, word, lmin=2, rmin=2):
        """ Given a word, returns a list of pieces, broken at the possible
            hyphenation points.
        """
        # Short words aren't hyphenated.
        if len(word) <= (lmin + rmin):
            return [word]
        # If the word is an exception, get the stored points.
        if word.lower() in self.exceptions:
            points = self.exceptions[word.lower()]
        else:
            work = '.' + word.lower() + '.'
            points = [0] * (len(work)+1)
            for i in range(len(work)):
                t = self.tree
                for c in work[i:]:
                    if c in t:
                        t = t[c]
                        if None in t:
                            p = t[None]
                            for j in range(len(p)):
                                points[i+j] = max(points[i+j], p[j])
                    else:
                        break
            # No hyphens in the first `lmin` chars or the last `rmin` ones:
            for i in range(lmin):
                points[i+1] = 0
            for i in range(rmin):
                points[-2-i] = 0
            # points[1] = points[2] = points[-2] = points[-3] = 0

        # Examine the points to build the pieces list.
        pieces = ['']
        for c, p in zip(word, points[2:]):
            pieces[-1] += c
            if p % 2:
                pieces.append('')
        return pieces

    def hyphenate_word(self, word, hyphen=u'­', lmin=2, rmin=2):
        """ Return `word` with (soft-)hyphens at the possible
            hyphenation points.
        """
        return hyphen.join(self.split_word(word, lmin, rmin))


pattern_file = 'en-US.pat'
# pattern_file = '../../dehyphn-x/dehyphn-x-2014-06-25.pat'
# pattern_file = '../../dehyphn-x-fugen/dehyphn-x-fugen-2014-07-01.pat'


if __name__ == '__main__':

    usage = u'%prog [options] [words to be hyphenated]\n\n' + __doc__

    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-f', '--pattern-file', dest='pattern_file',
                      help='Pattern file, Default "en-US.pat"',
                      default='en-US.pat')
    parser.add_option('-e', '--exception-file', dest='exception_file',
                      help='File of hyphenated words (exceptions), '
                      'Default None', default='')
    parser.add_option('-i', '--input-file', dest='input_file',
                      help='Eingabedatei (ein Wort/Zeile)',
                      default='')
    parser.add_option('', '--lmin',
                      help='Unhyphenated characters at start of word, default 2',
                      default='2')
    parser.add_option('', '--rmin',
                      help='Unhyphenated characters at end of word, default 2',
                      default='2')
    (options, args) = parser.parse_args()

    lmin = int(options.lmin)
    rmin = int(options.rmin)

    if options.exception_file:
        ex_file = open(exception_file)
        exceptions = ex_file.read().decode('utf8')
        ex_file.close()
    else:
        exceptions = ''
    if len(args) == 0: # self test
        exceptions = u"""
            as-so-ciate as-so-ciates dec-li-na-tion oblig-a-tory
            phil-an-thropic present presents project projects reci-procity
            re-cog-ni-zance ref-or-ma-tion ret-ri-bu-tion ta-ble
            """
    hyphenator = Hyphenator(options.pattern_file, exceptions)
    del exceptions

    if len(args) > 0:
        words = [word.decode('utf8') for word in args]
        for word in words:
            print hyphenator.hyphenate_word(word, lmin=lmin, rmin=rmin)
    else:
        import doctest
        doctest.testmod(verbose=True)
