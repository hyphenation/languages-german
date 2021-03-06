# -*- coding: utf-8 -*-
#
# This Makefile creates German hyphenation patterns in subdirectories
# $(TRAD) and $(REFO) for traditional and new orthography, respectively.
# Hyphenation patterns for traditional Swiss German are generated in
# directory $(SWISS).
#
# The input data is in $(SRCDIR); the possible targets are `pattern-trad',
# `pattern-refo', and `pattern-swiss'.  If no target (or target `all') is
# given, all patterns for all three targets are built.
#
# SRCDIR (and the other variables) can be easily modified as parameters
# while calling `make', e.g.
#
#   make pattern-trad SRCDIR=~/git/wortliste
#
# If you add one of the (phony) targets `major', `fugen', or `suffix',
# patterns that only use major hyphenation points (`Haupttrennstellen')
# are created.  Example:
#
#   make major pattern-refo
#
# The used directories names are the same as above but with `-major' (etc.)
# appended to the names.
#
# To control the used weights in the major hyphenation patterns, add
# variable `W=N', where `N' gives the quality: value 1 specifies the best
# hyphenation points only, value 2 both the best and second-best points,
# etc.  The default is value 0, using all major hyphenation points.
#
#
#
# Dieses Makefile erzeugt deutsche Trennmuster in den
# Unterverzeichnissen $(TRAD) und $(REFO) für die traditionelle
# bzw. reformierte Rechtschreibung.  Trennmuster für tradionelles
# deutschschweizerisches Deutsch werden Verzeichnis $(SWISS) erzeugt.
#
# Die Eingabedaten werden im Verzeichnis $(SRCDIR) erwartet; die möglichen
# Make-Ziele sind `pattern-trad', `pattern-refo' und `pattern-swiss'.  Wenn
# kein Ziel angegeben ist (oder man das Ziel `all' verwendet), werden alle
# drei Trennmuster erzeugt.
#
# SRCDIR (und die anderen Variablen) kann man leicht beim Aufruf von
# `make' als Parameter modifizieren, z.B.
#
#   make pattern-trad SRCDIR=~/git/wortliste
#
# Wird eines der zusätzlichen (künstlichen) Ziele `major', `fugen' oder
# `suffix' angegeben, werden Haupttrennstellmuster erzeugt.
#
# Beispiel:
#
#   make major pattern-refo
#
# Die verwendeten Verzeichnisnamen sind die gleichen wie oben, allerdings
# mit einem angehängten `-major', `-fugen' bzw. `-suffix'.
#
# Diese Spezialmuster spiegeln die Auszeichnung in der Liste direkt wider.
# Sie haben nicht das Ziel, "gute" Trennungen in Texten zu erzeugen sondern
# sind zum Testen der Konsistenz der Auszeichnung sowie zum "kategorisierten"
# Markieren der Trennstellen neuer Wörter gedacht.
#
# Bei `major' kann die Menge der verwendeten Haupttrennstellen mittels der
# Variable `W=N' (Wichtungs-Schwellwert)
# kontrolliert werden, wo `N' die Qualität angibt: Wert 1 selektiert
# nur die besten Haupttrennstellen, Wert 2 die besten und zweitbesten
# Haupttrennstellen usw.  Der Standardwert für `W' ist 0; er gibt an, dass
# alle Haupttrennstellen verwendet werden sollen.

# Die Ziele `de-Latf' und `de-x-long-s' erzeugen (experimentelle) Wortlisten
# und (Quasi-) Trennmuster für die Wandlung von Wörtern in traditioneller oder
# reformierter Standardorthographie in der Variante mit Unterscheidung von
# langem und runden S (Binnen-S vs. Schluß-S) wie sie im Satz mit gebrochenen
# Schriften benötigt wird. Ein Beispiel für die Anwendung dieser Muster ist
# das Skript `skripte/python/patuse/long_s_conversion.py`

SRCDIR = .
W = 0

DATADIR = $(SRCDIR)/daten
SCRIPTDIR = $(SRCDIR)/skripte
LANGSDIR = $(SCRIPTDIR)/python/lang_s
WORDLIST = wortliste

ifneq ($(findstring major,$(MAKECMDGOALS)),)
  MAJOR = -major
  # A single `-' gets removed; all other combinations of `-', `<', `>',
  # and `=' are converted to a hyphen.
  SEDMAJOR = $(SED) -e '/[=<>-]/!n' \
                    -e 's/---*/=/g' \
                    -e 's/-//g' \
                    -e 's/[=<>][=<>]*/-/g' \
                    -e '/-/!d'
  PERLMAJOR = -g $(W)

  ifeq ($(words $(MAKECMDGOALS)),1)
    major: all
  else
    # This is to suppress the `nothing to be done' warning.
    major:
	    @:
  endif
else ifneq ($(findstring fugen,$(MAKECMDGOALS)),)
  MAJOR = -fugen
  # All combinations of `-', `<', `>', `<=', `=>' get removed,
  # runs of `=' are converted to a hyphen.
  SEDMAJOR = $(SED) -e '/[=<>-]/!n' \
                    -e 's/--*//g' \
                    -e 's/<=*//g' \
                    -e 's/=*>//g' \
                    -e 's/[<>][<>]*//g' \
                    -e 's/[=][=]*/-/g'
  PERLMAJOR = -g $(W)

  ifeq ($(words $(MAKECMDGOALS)),1)
    fugen: all
  else
    # This is to suppress the `nothing to be done' warning.
    fugen:
	    @:
  endif
else ifneq ($(findstring suffix,$(MAKECMDGOALS)),)
  MAJOR = -suffix
  # All combinations of `-', `<', `=' get removed,
  # runs of `>' are converted to a hyphen.
  SEDMAJOR = $(SED) -e '/[=<>-]/!n' \
                    -e 's/-//g' \
                    -e 's/[<=][<=]*//g' \
                    -e 's/[>][>]*/-/g'
  PERLMAJOR = -g $(W)

  ifeq ($(words $(MAKECMDGOALS)),1)
    suffix: all
  else
    # This is to suppress the `nothing to be done' warning.
    suffix:
	    @:
  endif
else
  MAJOR =
  SEDMAJOR = cat
  PERLMAJOR =
endif

TRAD = dehypht-x$(MAJOR)
REFO = dehyphn-x$(MAJOR)
SWISS = dehyphts-x$(MAJOR)
LATF = de-Latf
LONG_S = de-long-s

LC_ENVVARS = LC_COLLATE=de_DE.ISO8859-15 \
             LC_CTYPE=de_DE.ISO8859-15

CAT = cat
CHDIR = cd
COPY = cp
DATE = $(shell date '+%Y-%m-%d')
ECHO = echo
GIT = git
ICONV = iconv -f iso-8859-15 -t utf-8
MKDIR = mkdir -p
PERL = perl
PWD = pwd
PYTHON = python
SED = sed
SH = bash
SORT = $(LC_ENVVARS) sort -d \
       | $(LC_ENVVARS) uniq -i

GIT_VERSION := `$(CHDIR) $(SRCDIR); \
                $(GIT) log --format=%H -1 HEAD --`
TRADFILES = $(TRAD)/$(TRAD)-$(DATE).pat $(TRAD)/$(TRAD)-$(DATE).tex
REFOFILES = $(REFO)/$(REFO)-$(DATE).pat $(REFO)/$(REFO)-$(DATE).tex
SWISSFILES = $(SWISS)/$(SWISS)-$(DATE).pat $(SWISS)/$(SWISS)-$(DATE).tex


override SRCDIR := $(shell cd $(SRCDIR); $(PWD))


all: pattern-trad pattern-refo pattern-swiss

.PHONY: pattern-trad pattern-refo pattern-swiss major fugen suffix
pattern-trad: $(TRADFILES)
pattern-refo: $(REFOFILES)
pattern-swiss: $(SWISSFILES)

# intermediate targets

# auxiliary targets

.PHONY: words-trad words-refo
words-trad: $(TRAD)/words.hyphenated.trad
words-refo: $(REFO)/words.hyphenated.refo


.PHONY: pre-trad pre-refo pre-swiss
pre-trad:
	$(MKDIR) $(TRAD)
pre-refo:
	$(MKDIR) $(REFO)
pre-swiss:
	$(MKDIR) $(SWISS)

$(TRADFILES) $(TRAD)/words.hyphenated.trad: pre-trad
$(REFOFILES) $(REFO)/words.hyphenated.refo: pre-refo
$(SWISSFILES) $(SWISS)/words.hyphenated.swiss: pre-swiss


# GNU make supports creation of multiple targets by a single
# invocation of a recipe only for pattern rules, thus we have
# to use a `sentinel file' (using `echo' for the time stamp).


$(TRAD)/pattern.8 $(TRAD)/pattern.rules: $(TRAD)/make-full-pattern-trad

$(TRAD)/make-full-pattern-trad: $(TRAD)/words.hyphenated.trad
	$(CHDIR) $(TRAD); \
          $(SH) $(SCRIPTDIR)/make-full-pattern.sh $(<F) $(DATADIR)/german.tr
	$(ECHO) done > $@

$(TRAD)/$(TRAD)-$(DATE).pat: $(TRAD)/pattern.8 $(TRAD)/pattern.rules
	$(CAT) $(DATADIR)/$(TRAD).1 \
          | $(SED) -e "s/@DATE@/$(DATE)/" \
                   -e "s/@GIT_VERSION@/$(GIT_VERSION)/" > $@; \
        $(CAT) $(TRAD)/pattern.rules >> $@; \
        $(CAT) $(DATADIR)/$(TRAD).2 >> $@; \
        $(CAT) $(TRAD)/pattern.8 \
          | $(ICONV) >> $@; \
        $(CAT) $(DATADIR)/$(TRAD).3 >> $@


$(REFO)/pattern.8 $(REFO)/pattern.rules: $(REFO)/make-full-pattern-refo

$(REFO)/make-full-pattern-refo: $(REFO)/words.hyphenated.refo
	$(CHDIR) $(REFO); \
          $(SH) $(SCRIPTDIR)/make-full-pattern.sh $(<F) $(DATADIR)/german.tr
	$(ECHO) done > $@

$(REFO)/$(REFO)-$(DATE).pat: $(REFO)/pattern.8 $(REFO)/pattern.rules
	$(CAT) $(DATADIR)/$(REFO).1 \
          | $(SED) -e "s/@DATE@/$(DATE)/" \
                   -e "s/@GIT_VERSION@/$(GIT_VERSION)/" > $@; \
        $(CAT) $(REFO)/pattern.rules >> $@; \
        $(CAT) $(DATADIR)/$(REFO).2 >> $@; \
        $(CAT) $(REFO)/pattern.8 \
          | $(ICONV) >> $@; \
        $(CAT) $(DATADIR)/$(REFO).3 >> $@


$(SWISS)/pattern.8 $(SWISS)/pattern.rules: $(SWISS)/make-full-pattern-swiss

$(SWISS)/make-full-pattern-swiss: $(SWISS)/words.hyphenated.swiss
	$(CHDIR) $(SWISS); \
          $(SH) $(SCRIPTDIR)/make-full-pattern.sh $(<F) $(DATADIR)/german.tr
	$(ECHO) done > $@

$(SWISS)/$(SWISS)-$(DATE).pat: $(SWISS)/pattern.8 $(SWISS)/pattern.rules
	$(CAT) $(DATADIR)/$(SWISS).1 \
          | $(SED) -e "s/@DATE@/$(DATE)/" \
                   -e "s/@GIT_VERSION@/$(GIT_VERSION)/" > $@; \
        $(CAT) $(SWISS)/pattern.rules >> $@; \
        $(CAT) $(DATADIR)/$(SWISS).2 >> $@; \
        $(CAT) $(SWISS)/pattern.8 \
          | $(ICONV) >> $@; \
        $(CAT) $(DATADIR)/$(SWISS).3 >> $@


$(TRAD)/words.hyphenated.trad: $(SRCDIR)/$(WORDLIST)
	$(CAT) $< \
          | $(PERL) $(SCRIPTDIR)/extract-tex.pl -l -t $(PERLMAJOR) \
          | $(SEDMAJOR) \
          | $(SORT) > $@

$(REFO)/words.hyphenated.refo: $(SRCDIR)/$(WORDLIST)
	$(CAT) $< \
          | $(PERL) $(SCRIPTDIR)/extract-tex.pl -l $(PERLMAJOR) \
          | $(SEDMAJOR) \
          | $(SORT) > $@

$(SWISS)/words.hyphenated.swiss: $(SRCDIR)/$(WORDLIST)
	$(CAT) $< \
          | $(PERL) $(SCRIPTDIR)/extract-tex.pl -l -s $(PERLMAJOR) \
          | $(SEDMAJOR) \
          | $(SORT) > $@


$(TRAD)/$(TRAD)-$(DATE).tex: $(DATADIR)/$(TRAD).tex.in
	$(CAT) $< \
          | $(SED) -e "s/@DATE@/$(DATE)/" > $@

$(REFO)/$(REFO)-$(DATE).tex: $(DATADIR)/$(REFO).tex.in
	$(CAT) $< \
          | $(SED) -e "s/@DATE@/$(DATE)/" > $@

$(SWISS)/$(SWISS)-$(DATE).tex: $(DATADIR)/$(SWISS).tex.in
	$(CAT) $< \
          | $(SED) -e "s/@DATE@/$(DATE)/" > $@

# Listen und Patterns de-Latf (deutsch, Latin script, fraktur;
# Orthographie für Satz mit gebrochenen Schriften und rundem und langem S)

# Wortlisten mit Langem-S: gemischt, de-1901 (alt), de-1996 (reform)

$(LATF)/words-de-Latf.txt: wortliste $(LANGSDIR)/s2long-s.py
	$(MKDIR) $(LATF)
	$(PYTHON) $(LANGSDIR)/s2long-s.py --drop-homonyms \
	   -l "de-1901,de-1996" -i wortliste -o $(LATF)/words-de-Latf.txt

$(LATF)/words-de-1901-Latf.txt: wortliste $(LANGSDIR)/s2long-s.py
	$(MKDIR) $(LATF)
	$(PYTHON) $(LANGSDIR)/s2long-s.py --drop-homonyms -l de-1901 \
	   -i wortliste -o $(LATF)/words-de-1901-Latf.txt

$(LATF)/words-de-1996-Latf.txt: wortliste $(LANGSDIR)/s2long-s.py
	$(PYTHON) $(LANGSDIR)/s2long-s.py  --drop-homonyms -l de-1996 \
	    -i wortliste -o $(LATF)/words-de-1996-Latf.txt

# de-Latf...: Variante mit Quasi-Trennstellen nach rund-s (aus-sagen)

.PHONY: de-Latf de-1901-Latf de-1996-Latf

de-Latf: $(LATF)/de-Latf.pat

$(LATF)/words-de-Latf.hyphenated: $(LATF)/words-de-Latf.txt
	$(PYTHON) $(LANGSDIR)/de_Latf_quasihyph.py < $< > $@

$(LATF)/de-Latf.pat: $(LATF)/words-de-Latf.hyphenated
	$(CHDIR) $(LATF); \
          $(SH) $(SCRIPTDIR)/make-full-pattern.sh $(<F) $(DATADIR)/de-Latf.tr
	$(CAT) $(LATF)/pattern.8 | $(ICONV) >> $@;

de-1901-Latf: $(LATF)/de-1901-Latf.pat

$(LATF)/words-de-1901-Latf.hyphenated: $(LATF)/words-de-1901-Latf.txt
	$(PYTHON) $(LANGSDIR)/de_Latf_quasihyph.py < $< > $@

$(LATF)/de-1901-Latf.pat: $(LATF)/words-de-1901-Latf.hyphenated
	$(CHDIR) $(LATF); \
          $(SH) $(SCRIPTDIR)/make-full-pattern.sh $(<F) $(DATADIR)/de-Latf.tr
	$(CAT) $(LATF)/pattern.8 | $(ICONV) >> $@;

de-1996-Latf: $(LATF)/de-1996-Latf.pat

$(LATF)/words-de-1996-Latf.hyphenated: $(LATF)/words-de-1996-Latf.txt
	$(PYTHON) $(LANGSDIR)/de_Latf_quasihyph.py < $< > $@

$(LATF)/de-1996-Latf.pat: $(LATF)/words-de-1996-Latf.hyphenated
	$(CHDIR) $(LATF); \
          $(SH) $(SCRIPTDIR)/make-full-pattern.sh $(<F) $(DATADIR)/de-Latf.tr
	$(CAT) $(LATF)/pattern.8 | $(ICONV) >> $@;

# long-s: Variante mit Quasi-Trennstellen nach Lang-S (auss-agen)

.PHONY: de-x-long-s de-1901-x-long-s de-1996-x-long-s

de-x-long-s: $(LONG_S)/de-x-long-s.pat

$(LONG_S)/words-de-x-long-s.hyphenated: $(LATF)/words-de-Latf.txt
	$(MKDIR) $(LONG_S)
	$(PYTHON) $(LANGSDIR)/long_s_quasihyph.py < $< > $@

$(LONG_S)/de-x-long-s.pat: $(LONG_S)/words-de-x-long-s.hyphenated
	$(CHDIR) $(LONG_S); \
          $(SH) $(SCRIPTDIR)/make-full-pattern.sh $(<F) $(DATADIR)/de-Latf.tr
	$(CAT) $(LONG_S)/pattern.8 | $(ICONV) >> $@;

de-1901-x-long-s: $(LONG_S)/de-1901-x-long-s.pat

$(LONG_S)/words-de-1901-x-long-s.hyphenated: $(LATF)/words-de-1901-Latf.txt
	$(MKDIR) $(LONG_S)
	$(PYTHON) $(LANGSDIR)/long_s_quasihyph.py < $< > $@

$(LONG_S)/de-1901-x-long-s.pat: $(LONG_S)/words-de-1901-x-long-s.hyphenated
	$(CHDIR) $(LONG_S); \
          $(SH) $(SCRIPTDIR)/make-full-pattern.sh $(<F) $(DATADIR)/de-Latf.tr
	$(CAT) $(LONG_S)/pattern.8 | $(ICONV) >> $@;

de-1996-x-long-s: $(LONG_S)/de-1996-x-long-s.pat

$(LONG_S)/words-de-1996-x-long-s.hyphenated: $(LATF)/words-de-1996-Latf.txt
	$(MKDIR) $(LONG_S)
	$(PYTHON) $(LANGSDIR)/long_s_quasihyph.py < $< > $@

$(LONG_S)/de-1996-x-long-s.pat: $(LONG_S)/words-de-1996-x-long-s.hyphenated
	$(CHDIR) $(LONG_S); \
          $(SH) $(SCRIPTDIR)/make-full-pattern.sh $(<F) $(DATADIR)/de-Latf.tr
	$(CAT) $(LONG_S)/pattern.8 | $(ICONV) >> $@;

# EOF
