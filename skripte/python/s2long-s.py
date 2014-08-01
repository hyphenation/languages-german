#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2012, 2014 Günter Milde.
# :Licence:   This work may be distributed and/or modified under
#             the conditions of the `LaTeX Project Public License`,
#             either version 1.3 of this license or (at your option)
#             any later  version.
# :Version:   0.3 (2014-06-14)

# ===================================================================
# Langes oder rundes S: Automatische Konversion nach Silbentrennung
# ===================================================================
#
# ::

"""
Automatische Bestimmung der S-Schreibung auf Basis der Silbentrennung
in der `Wortliste der deutschsprachigen Trennmustermannschaft`."""

# .. contents::
#
# Vorspann
# ========
#
# Lade Funktionen und Klassen für reguläre Ausdrücke::

import re, sys, os, optparse

# path for local Python modules
sys.path.append(os.path.dirname(__file__))
from werkzeug import WordFile, WordEntry, join_word


# Trennzeichen
# ------------
#
# Die Trennzeichen der Wortliste sind
#
# == ================================================================
# \· ungewichtete Trennstellen (solche, wo noch niemand sich um die
#    Gewichtung gekümmert hat)
# .  unerwünschte Trennstellen (sinnverwirrend), z.B. Ur-in.stinkt
# =  Haupttrennstellen
# \- Nebentrennstellen
# <  Trennstellen nach Vorsilben
# >  Trennstellen vor Suffixen
# == ================================================================
#
#
# Funktionen
# ==========
#
# ſ-Regeln
# --------
#
# Siehe [wikipedia]_ und ("DDR"-) [Duden]_ (Regeln K 44,45)::

def s_ersetzen(word):

# Ausnahmeregeln
# ~~~~~~~~~~~~~~
#
# Für sz und sk gelten Regeln, welche die Herkunft der Wörter beachten.
# Diese und weitere spezielle Fälle, welche Lang-S vor Trennstellen verlangen
# sind in `Ausnahmen Lang-S`_ gelistet::

    for fall in ausnahmen_lang_s:
        word = word.replace(fall.replace(u'ſ', u's'), fall)

# Allgemeine Regeln
# ~~~~~~~~~~~~~~~~~
#
# ſ steht im Silbenanlaut::

    word = re.sub(ur'^s', ur'ſ', word)
    word = re.sub(ur'([-<>=·.])s', ur'\1ſ', word)

# ſ steht im Inlaut als stimmhaftes s zwischen Vokalen
# (gilt auch für ungetrenntes ss zwischen Selbstlauten, z.B. Hausse, Baisse)::

    word = re.sub(ur'([AEIOUYÄÖÜaeiouäöüé])s([aeiouyäöüé])', ur'\1ſ\2', word)
    word = re.sub(ur'([AEIOUYÄÖÜaeiouäöüé])ss([aeiouyäöüé])', ur'\1ſſ\2', word)

# ſ steht in den Verbindungen sp, st, sch und in Digraphen, allerdings nicht
# in der Verbindung "sst", die seit 1996 für "ßt" steht::

    word = re.sub(u'(^|[^s])st', ur'\1ſt', word)
    word = word.replace(u'sp', u'ſp')
    word = word.replace(u'sch', u'ſch')

    # word = word.replace(u'ps', u'pſ')
    word = word.replace(u'Ps', u'Pſ')  # Ψ
    word = re.sub(ur'^ps', ur'pſ', word) # ψ (ps am Wortanfang)
    word = re.sub(ur'([-<>=·.])ps', ur'\1pſ', word) # ψ (ps am Silbenanfang)


# ſ vor Trennstellen
# ------------------
#
# Die Verbindungen ss, sp¹, st werden zu ſſ, ſp und ſt, auch wenn sie
# durch eine Nebentrennstelle (Trennung innerhalb eines Wortbestandteiles)
# getrennt sind. Das s bleibt rund im Auslaut, d.h. am Wortende und vor
# einer Haupttrennstelle (Trennung an der Grenze zweier Wortbestandteile
# (Vorsilb<Stamm, Bestimmungswort=Grundwort).
#
# ¹ s bleibt rund vor Nebentrennstelle wenn ph folgt (Phos-phor).
#
# ::

    word = re.sub(ur's([-.]+)ſ([aeiouyäöüé])', ur'ſ\1ſ\2', word)
    word = re.sub(ur's([-.]+)p([^h])', ur'ſ\1p\2', word)
    word = re.sub(ur'(^|[^s])s([-.]+)t', ur'\1ſ\2t', word) # Reformschreibung


# Doppel-S statt SZ am Silbenende und vor t
# -----------------------------------------
#
# Wenn kein ß vorhanden ist, in der Schweiz und seit der Reform 1996 allgemein
# nach kurzem Mitlaut wird ss statt ß geschrieben. Der "Reformduden" empfielt
# im Fraktursatz die Schreibung ſs (die auch vor 1901 in Gebrauch war)::

    word = re.sub(u'ss($|[-=<>.])', ur'ſs\1', word)
    word = word.replace(u'sst', u'ſst')

# Fremdwörter und Eigennamen mit Schluss-ß
# """"""""""""""""""""""""""""""""""""""""
#
# Der 1971er [Duden]_ führt zu englischen Fremdwörtern mit Schluß-ß die
# österreichische Schreibung mit "ss" auf (Miß, engl. und österr. Schreibung
# Miss) wobei das Schluß-s nicht unterstrichen ist (also lang sein müßte?). So
# auch Boss, Business, Stewardess.
#
# Dagegen sagt [en.wiktionary.org]_: "the digraph «ss» was often written «ſs»
# rather than «ſſ»". Die Lang-S Seite der [wikipedia]_ zeigt Beispiele der
# englischen Schreibung "Congreſs".
#
# ::

    # TODO ſſ oder ſs (wie in de-1996)? :
    # if sprachvariante == 'de-1901':
    #     word = re.sub(ur'ss$', ur'ſſ', word)
    #     word = word.replace(u'ss=', u'ſſ=')
    #     word = word.replace(u'ss-ſch', u'ſſ-ſch')

    return word


# Ausnahmen Lang-S
# ~~~~~~~~~~~~~~~~~~~
#
# Teilstrings mit Lang-S vor Trennstelle.
#
# ſ wird geschrieben, wenn der S-Laut nur scheinbar im Auslaut steht,
# weil ein folgendes unbetontes e ausfällt::

# TODO: es fehlen noch "Abwechslung" u.ä. auf ...lung, 
# wechsle" u.ä. auf ...sle,
# und andere Beispiele aus dem neuen Duden!!!
# Regular Expressions?

ausnahmen_lang_s = [

    # Basel, Beisel, Pilsen, drechseln, wechseln, häckseln
    u'Baſ-ler',
    u'Kaſſ-ler',
    u'Pilſ-ner',
    u'echſ-ler',# Dechsler, Wechsler
    u'äckſ-ler',# Häcksler
    u'Röſſl',

    # Insel (Rheininsler), zünseln (Maiszünsler)
    u'inſ-ler',
    u'ünſ-ler',

    # unsre, unsrige, ...
    u'unſ-r',

    # Häusl, Lisl, bissl, Glasl, Rössl
    u'ſſl',
    u'ſl',

    u'Wieſn',

]

# ſ steht auch am Ende von Abkürzungen, wenn es im abgekürzten Wort steht
# (Abſ. - Abſatz/Abſender, (de)creſc. - (de)creſcendo, daſ. - daſelbst ...)
# ::

ausnahmen_lang_s.append(u'creſc')

# Alternativtrennung, wo beide Fälle ſ verlangen::

ausnahmen_lang_s.append(u'er<.]ſa') # Kind=er<.satz/Kin-der=satz
ausnahmen_lang_s.append(u'ſ[-ter=/t') # Tes[-ter=/t=er<.]ken-nung

# Fremdwörter und Eigennamen
# --------------------------
#
# Schreibung nach Regeln der Herkunftssprache. Dabei ist zu bedenken, daß zu
# der Zeit, als das lange s im Antiquasatz noch üblich war (bis ca. 1800), die
# Rechtschreibung freier gehandhabt wurde und mehrfach Wandlungen unterworfen
# war [West06]_.
#
# Im Deutschen werden im Fraktursatz nicht eingedeutschte Fremdwörter
# lateinischen und romanischen Ursprungs in Antiqua mit rund-s geschrieben.
#
# English:
#   The long, medial, or descending ess, as distinct from the short or
#   terminal ess. In Roman script, the long ess was used everywhere except at
#   the end of words, where the short ess was used, and frequently in what is
#   now the digraph «ss», which was often written «ſs» rather than «ſſ»
#   [en.wiktionary.org]_. See also [Typefounder08]_ and [West06]_.
#
# ::

ausnahmen_lang_s.extend([

    u'ſh',       # (englisch)
    # u'Diſc',   # (englisch) TODO: so, oder Disc (wie eingedeutscht Disk)
    u'Cſar',     # Cs -> Tsch (Csardas, ... ungarisch)
    u'ſz',       # polnisch, ungarisch (Liszt, Puszta)

# ts am Silbenanfang (chinesisch, japanisch, griechisch)::

    u'Tſa', u'Tſe', u'tſe', u'tſi', u'Tſu', u'tſu',

# In vielen (aber nicht allen) Fremdwörtern steht ſz trotz Trennzeichen::

    u'ſ-zen',     # Adoleszenz, Aszendent, ...
    u'ſ-ze-n',    # Damaszener, ...
    u'ſ-ze-r',    # vis-ze-ral...
    u'aſ-zi',     # [Ll]asziv, laszive, ...
    u'viſ-zi-do', # Mukoviszidose
    u'ſ-zil-l' ,  # Oszillation, Oszilloskop, ...
    u'asſ-zi',    # faszinieren, fasziniert, ...
    u'gnoſ-zie',  # rekognoszieren,
    u'o-reſ-z',   # fluoreszieren, phosporeszieren, ...
    u'-reſ-c',    # Fluo-res-ce-in
    u'le-biſ-zi', # Plebiszit, ...

# ſ steht in der Endung sk in Wörtern und Namen slawischen Ursprungs
#
# ::

    u'Gdanſk',
    u'Minſk',
    u'Mur-manſk',
    u'ſi-birſk',
    u'Smo-lenſk',

# ſſ steht wenn auf die Vorsilbe "dis-" oder "as-" ein "s" folgt::

    u'aſ<ſ',     # Assoziation, ...
    u'diſ<ſ',    # Dissoziation, ...
    u'Diſ<ſ',    # dissonant, ...

                       ])

# s-Regeln
# --------
#
# Test auf verbliebene Unklarheiten
#
# Wenn ein Wort "s" nur an Stellen enthält wo die Regeln rundes S vorsehen,
# ist die automatische Konversion abgeschlossen.
#
# Ausnahmen und spezielle Regeln
#
# Liste von Teilstrings, welche stets rund-s behalten ::

ausnahmen_rund_s = [

# Abkürzungen::

    u'Ausg', u'ausſchl', u'desgl', u'hrsg', u'insb',

# ausgelassenes flüchtiges e::

    u'Dresd-ne',   # Dresd·ner/Dresd·ner·in

# s steht auch in einigen Fremdwörtern vor z und c::

    u'on<fis-zie', # konfiszieren, ...
    # u'le-bis-z', # plebiszit (nach [duden]_ mit Lang-S)
    u'is-zi-pl',   # Disziplin (nach [duden]_, aber Duden (1934) Diſziplin)
    u'mas-ze-ner', # Damaszener
    u'Disc',       # TODO: rund oder Diſc (aber eingedeutscht Disk)


# ss im Auslaut (vgl. `Fremdwörter und Eigennamen`_)::

    # u'Gauss',    # vgl. "Briefwechsel zwischen C.F. Gauss und H.C. Schumacher, herausg. von C.A.F. Peters"
                   # aber Boſſ, Busineſſ, Dreſſ
                       ]


def is_complete(word):

# Ersetze s an Stellen, wo es rund zu schreiben ist, durch ~ und teste auf
# verbliebene Vorkommen.
#
# Einzelfälle mit rundem S (substrings)::

    for fall in ausnahmen_rund_s:
        word = word.replace(fall, fall.replace('s', '~'))

# s steht am Wortende, auch in Zusammensetzungen (vor Haupttrennstellen)::

    word = re.sub(ur's($|[=<>])', ur'~\1', word)

# Einige ältere Quellen schreiben ss am Schluss von Fremdwörtern oder Namen
# (Gauss). Andere schreiben ſs oder ſſ. (Vgl. `Fremdwörter und Eigennamen
# mit Schluss-ß`_) Wir verwenden ſs (TODO oder?)::

    #word = re.sub(ur'ss(=|$)', ur'~~\1', word)

# s steht am Silbenende (vor Nebentrennstellen), wenn kein p, t, z oder ſ
# folgt (in der traditionellen Schreibung wird st nicht getrennt)::

    word = re.sub(ur'ss?([·.\-][^ptzſ])', ur'~\1', word) # konservativ
    # word = re.sub(ur'ss?([·.\-][^pzſ])', ur'~\1', word)   # traditionell

# s steht auch vor Nebentrennstellen, wenn ph oder sch folgt::

    word = word.replace(u's-ph', u'~-ph')
    word = word.replace(u's-ſch', u'~-ſch')

# s steht nach Vorsilben (wie aus<) auch wenn s, p, t, oder z folgt::

    word = word.replace(u's<', u'~<')

# s steht vor Trennstellen am Suffixanfang (wie >sen, >son),
# auch wenn s, p, t, oder z folgt::

    word = word.replace(u's>', u'~>')

# s steht im Inlaut vor k, n, w::

    word = re.sub(ur's([knw])', ur'~\1', word)

# s steht in der Verbindung sst, die seit 1995 für ßt steht::

    word = word.replace(u'ſst', u'ſ~t')
    word = word.replace(u'ſs-t', u'ſ~-t')

# s steht als zweiter Buchstabe im ersetzten ß::

    word = word.replace(u'-ſs', u'-ſ~') # traditionelle Orthographie

# und suche nach übrigen Vorkommen::

    return 's' not in word


# Aufruf von der Kommandozeile
# ============================
#
# ::

if __name__ == '__main__':

# Optionen::

    usage = u'%prog [Optionen]\n' + __doc__
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-i', '--infile', dest='infile',
                      help=u'Eingangsdatei ("-" oder "stdin" für '
                      u'Standardeingabe), Vorgabe "../../wortliste"',
                      default='../../wortliste')
    parser.add_option('-o', '--outfile', dest='outfile',
                      help=u'Ausgangsdatei, ("-" oder "stdout" für '
                      u'Standardausgabe) Vorgabe: "words-<language>-Latf.txt"',
                      default='') # wird später ausgefüllt
    parser.add_option('-l', '--language', dest='language',
                      help=u'Sprachvariante (ISO Sprachtag), '
                      u'Vorgabe "de-1901"',
                      default='de-1901')
    parser.add_option('-d', '--drop-homonyms', action="store_true",
                      default=False,
                      help=u'Bei mehrdeutigen Wörtern, die sich nur in '
                      'Lang-S-Schreibung unterscheiden, nimm nur das erste.')

    (options, args) = parser.parse_args()

# Angabe der Sprachvariante nach [BCP47]_ (Reformschreibung 'de' oder
# 'de-1996', Schweiz 'de-CH', ...)::

    lang = options.language

# Iterator::

    if options.infile in ('-', 'stdin'):
        wordfile = (WordEntry(line.rstrip().decode('utf-8'))
                    for line in sys.stdin)
    else:
        wordfile = WordFile(options.infile)

# Ausgabedatei::
    if options.outfile in ('-', 'stdout'):
        outstream = sys.stdout
    else:
        outfile = options.outfile or 'words-' + lang + '-Latf.txt'
        outstream = file(outfile, 'w')


# Hauptschleife
# =============
#
# Konvertiere die Wörter der Trennliste und sortiere die Ergebnisse in
# Listen::

    no_of_words = 0   # Gesamtwortzahl der gewählten Sprache
    completed = []    # Automatisch konvertiert
    irreversible = [] # Rückkonversion ungleich Original (Fehler)
    unkategorisiert = [] # Unterscheidung in Haupt- und Nebentrennstellen fehlt
    offen = [] # Der Algorithmus kann die Schreibweise (noch) nicht ermitteln

# Iteration über alle Zeilen der Wortliste::

    for entry in wordfile:

        word = entry.get(lang)  # Wort mit Trennstellen
        if word is None: # Wort existiert nicht in der Sprachvariante
            continue
        no_of_words += 1

# Vorsortieren
# ------------
#
# Wörter ohne Binnen-s müssen nicht konvertiert werden. Damit wird die
# Wortliste ungefähr um die Hälfte kürzer::

        if 's' not in entry[0][:-1]:
            completed.append(entry[0])
            continue

# Regelbasierte s/ſ-Schreibung::

        lang_s_word = s_ersetzen(word)

# Einsortieren nach Vollständigkeit der Ersetzungen::

        entry.set(lang_s_word, lang) # Rückschreiben von teilweisen Ersetzungen

        if lang_s_word.replace(u'ſ', u's') != word:
            entry.comment = lang_s_word.replace(u'ſ', u's') + u" != " + word
            irreversible.append(entry)
            continue

        if not is_complete(lang_s_word):
            if lang_s_word.find(u's·') != -1:
                unkategorisiert.append(entry)
            else:
                offen.append(entry)
            continue

# Mehrdeutigkeiten [ſ/s] oder [s/ſ] auflösen::

        lang_s_word = join_word(lang_s_word)
        if u'/' in lang_s_word:
            # 1. Alternative:
            completed.append(re.sub(ur'\[(.+)/.+\]', ur'\1', lang_s_word))
            if not options.drop_homonyms:
                completed.append(re.sub(ur'\[.+/(.+)\]', ur'\1', lang_s_word))
        else:
            completed.append(lang_s_word)
        # completed.append(lang_s_word)


# Ausgabe
# =======
#
# Wortliste mit automatisch bestimmter S-Schreibung, ohne Trennstellen::

    outstream.write(u'\n'.join(completed).encode('utf8') + '\n')

# Auswertung
# ==========
#
# ::

    if options.outfile not in ('-', 'stdout'):
        print "# Gesamtwortzahl", lang, no_of_words
        print "# Automatisch konvertiert:", len(completed)
        print "# erkannte Konvertierungsfehler:", len(irreversible)
        for entry in irreversible:
            print unicode(entry).encode('utf8')
        print "# Kategorisierung der Trennstellen fehlt:", len(unkategorisiert)
        for entry in unkategorisiert:
            print unicode(entry).encode('utf8')
        print "# noch offen/unklar:", len(offen)
        for entry in offen:
            print unicode(entry).encode('utf8')


# Diskussion
# ==========
#
# Für gebrochene Schriften gibt es den `ISO Sprachtag`_
#
#   :Latf: Latin (Fraktur variant)
#
# also "Lateinisches Alphabet, gebrochen". Dieser Tag wird and die
# Ausgabedateien angehängt (e.g. "de-1901-Latf", "de-1996-Latf").
#
# .. _ISO Sprachtag: http://www.unicode.org/iso15924/iso15924-codes.html
#
# Statistik
# ---------
#
# Gesamtwortzahl (traditionelle Rechtschreibung): 427746
# Automatisch konvertiert: 427740
# Kategorisierung der Trennstellen fehlt: 0
# noch offen: 6
#
# Die Mehrzahl der Wörter der Trennliste wurde nach den Regeln des Dudens in
# die Schreibung mit langem `S` (ſ) konvertiert (wobei ungefähr die Hälfte der
# Wörter kein kleines `s` enthält womit die Konversion trivial wird).
#
# Für eine beschränke Anzahl offener Fälle wurden Ausnahmeregeln und Ausnahmen
# implementiert.
#
# Das Resultat muß noch auf nicht erfaßte Ausnahmen und Sonderfälle geprüft
# werden. Fehlentscheidungen sind nicht auszuschließen.
#
#
# Offene Fälle
# ------------
#
# Wörter mit identischer Schreibung ohne Lang-S
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Einige mehrdeutige Zusammensetzungen unterscheiden sich in der
# Lang-S-Schreibung, z.B.
#
# * Wach[s/ſ]tube:  Wach-Stube / Wachs-Tube
# * Ga[s/ſ]traſſe:  Gas-Trasse / Gast-Rasse
# * Schiff[ſ/s]tau: Schiffs-Tau / Schiff-Stau
#
# Die Ausgangsdatei schreibt diese mit der "Alternativsyntax" [s/ſ] oder [ſ/s]
# wie in den obigen Beispielen.
#
# Unklare Schreibung
# ~~~~~~~~~~~~~~~~~~
#
# * Ersetztes SZ in reformierter Rechtschreibung, wenn ein Selbstlaut folgt
#   (z.B. "Straſ-ſe" oder "Straſ-se).
#
#   - Während in 1901-er Rechtschreibung die Trennung vor dem "ss" erfolgt
#     (was Ersetzung mit "ſs" impliziert) wäre bei Trennung "wie normales
#     Doppel-S" dann ein rundes S am Silbenanfang.
#
#     Korrekte Fallunterscheidung geht nur bei Betrachtung der Nachbarfelder.
#
# * Tonarten (As-Dur oder Aſ-Dur)
#
#   - Im Fraktur-Duden steht As *in Antiqua* mit rundem s, also
#     keine Aussage zur Schreibung in Fraktur.
#   - Im 1976-er [Duden]_ steht As ohne Unterstreichung des `s`,
#     das wäre Lang-S, obgleich am Wortende!
#
# Quellen
# =======
#
# .. [Duden] `Der Große Duden` 16. Auflage, VEB Bibliographisches Institut
#    Leipzig, 1971
#
#    Kennzeichnet im Stichwortteil rundes s durch Unterstreichen.
#
# .. [wikipedia] Langes s
#    http://de.wikipedia.org/wiki/Langes_s
#
# .. [en.wiktionary.org]
#    http://en.wiktionary.org/wiki/%C5%BF
#
# .. [Typefounder08]
#    http://typefoundry.blogspot.com/2008/01/long-s.html
#
# .. [West06] Andrew West, `The rules for long s`, 2006
#    http://babelstone.blogspot.com/2006/06/rules-for-long-s.html
#
# .. [BCP47]  A. Phillips und M. Davis, (Editoren.),
#    `Tags for Identifying Languages`, http://www.rfc-editor.org/rfc/bcp/bcp47.txt
#
# .. Links:
#
# .. _Wortliste der deutschsprachigen Trennmustermannschaft:
#    http://mirrors.ctan.org/language/hyphenation/dehyph-exptl/projektbeschreibung.pdf
