#!/usr/bin/env python
# -*- coding: utf-8 -*-

# :Author: Pander <pander@users.sourceforge.net>
# :License: GNU General Public License (v. 2 or later)
# :Version: 0.1 (2013-11-05)

import codecs
import operator
import re

directory = '../../..'
#filenames = ['arzneiwirkstoffnamen', 'arzneiwirkstoffnamen-supplement', 'wortliste', ]
filenames = ['wortliste', ]

word_chars = {}
word_chars_upper = {}
pattern_chars = {}
pattern_prios = {}
pattern_spacers = {}

for filename in filenames:
    print filename
    definitions = codecs.open('%s/%s' %(directory, filename), 'r', 'utf-8')

    for line in definitions:
        pos = line.find('#')
        if pos == 0:
            continue
        elif pos != -1:
            line = line.split('#')[0]
        words = line.strip().split(';')
        for char in words[0]:
            if char in word_chars:
                word_chars[char] += 1
            else:
                word_chars[char] = 1
            if char.upper() in word_chars_upper:
                word_chars_upper[char.upper()] += 1
            else:
                word_chars_upper[char.upper()] = 1
        for pattern in words[1:]:
            if pattern in ('-2-', '-3-', '-4-', '-5-', '-6-', '-7-', '-8-', '-9-', ):
                if pattern in pattern_spacers:
                    pattern_spacers[pattern] += 1
                else:
                    pattern_spacers[pattern] = 1
            else:
                for char in pattern:
                    if char in pattern_chars:
                        pattern_chars[char] += 1
                    else:
                        pattern_chars[char] = 1
                for prio in (r'\|=', r'\|\.', r'--=', r'-=', r'---', r'--', r'-', r'\|', r'===', r'==', r'=', r'\.\.\.', r'\.\.', r'\.', u'·', ):
                    count = len(re.findall(prio, pattern))
                    if count != 0:
                        prio = prio.replace('\\', '')
                        if prio in pattern_prios:
                            pattern_prios[prio] += count
                        else:
                            pattern_prios[prio] = count
                        pattern = pattern.replace(prio, '')

histogram_words = codecs.open('histogram-word-characters.tsv', 'w', 'utf-8')
sorted_x = sorted(word_chars.iteritems(), key=operator.itemgetter(1), reverse=True)
number = 1
for (char, count) in sorted_x:
    histogram_words.write('%d\t%s\t%s\n'.decode('utf-8') %(number, char, count))
    number += 1

histogram_words_upper = codecs.open('histogram-word-characters-case-insensitive.tsv', 'w', 'utf-8')
sorted_x = sorted(word_chars_upper.iteritems(), key=operator.itemgetter(1), reverse=True)
number = 1
for (char, count) in sorted_x:
    histogram_words_upper.write('%d\t%s\t%s\n'.decode('utf-8') %(number, char, count))
    number += 1

histogram_prios = codecs.open('histogram-pattern-priorities.tsv', 'w', 'utf-8')
sorted_x = sorted(pattern_prios.iteritems(), key=operator.itemgetter(1), reverse=True)
number = 1
for (char, count) in sorted_x:
    histogram_prios.write('%d\t%s\t%s\n'.decode('utf-8') %(number, char, count))
    number += 1

histogram_patterns = codecs.open('histogram-pattern-characters.tsv', 'w', 'utf-8')
histogram_reserved = codecs.open('histogram-pattern-reserved.tsv', 'w', 'utf-8')
sorted_x = sorted(pattern_chars.iteritems(), key=operator.itemgetter(1), reverse=True)
number = 1
number_reserved = 1
for (char, count) in sorted_x:
    histogram_patterns.write('%d\t%s\t%s\n'.decode('utf-8') %(number, char, count))
    number += 1
    if char not in word_chars:
        histogram_reserved.write('%d\t%s\t%s\n'.decode('utf-8') %(number_reserved, char, count))
        number_reserved += 1

histogram_spacers = codecs.open('histogram-pattern-spacers.tsv', 'w', 'utf-8')
# sorted on spacer name, sorting like above on spacer count does not work
number = 1
for pattern in sorted(pattern_spacers.keys()):
    histogram_spacers.write('%d\t%s\t%d\n'.decode('utf-8') %(number, pattern, pattern_spacers[pattern]))
    number += 1

