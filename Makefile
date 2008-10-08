# This Makefile creates German hyphenation patterns in subdirectories
# $(TRAD) and $(REFO) for traditional and new ortography, respectively.
# Hyphenation patterns for traditional Swiss German is generated in
# directory $(SWISS).
#
# The input data is in $(SRCDIR).

SRCDIR = ~/git/wortliste
DATADIR = $(SRCDIR)/daten
WORDLIST = wortliste

TRAD = dehypht-x
REFO = dehyphn-x
SWISS = dehyphts-x

LC_ENVVARS = LC_COLLATE=de_DE.ISO8859-1 \
             LC_CTYPE=de_DE.ISO8859-1

CAT = cat
CHDIR = cd
COPY = cp
DATE = $(shell date '+%Y-%m-%d')
ECHO = echo
GIT = git
ICONV = iconv -f latin1 -t utf8
MKDIR = mkdir -p
PERL = perl
SED = sed
SH = sh
SORT = $(LC_ENVVARS) sort -d \
       | $(LC_ENVVARS) uniq -i

GIT_VERSION := `$(CHDIR) $(SRCDIR); \
                $(GIT) log --pretty=oneline -1 $(WORDLIST) \
                | $(SED) 's/ .*//'`
TRADFILES = $(TRAD)/$(TRAD)-$(DATE).pat $(TRAD)/$(TRAD)-$(DATE).tex
REFOFILES = $(REFO)/$(REFO)-$(DATE).pat $(REFO)/$(REFO)-$(DATE).tex
SWISSFILES = $(SWISS)/$(SWISS)-$(DATE).pat $(SWISS)/$(SWISS)-$(DATE).tex



all: pattern-trad pattern-refo pattern-swiss

.PHONY: pattern-trad pattern-refo pattern-swiss
pattern-trad: $(TRADFILES)
pattern-refo: $(REFOFILES)
pattern-swiss: $(SWISSFILES)

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
          $(SH) $(SRCDIR)/make-full-pattern.sh $(<F) $(SRCDIR)/german.tr
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
          $(SH) $(SRCDIR)/make-full-pattern.sh $(<F) $(SRCDIR)/german.tr
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
          $(SH) $(SRCDIR)/make-full-pattern.sh $(<F) $(SRCDIR)/german.tr
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
          | $(PERL) $(SRCDIR)/extract-tex-trad.pl \
          | $(SORT) > $@

$(REFO)/words.hyphenated.refo: $(SRCDIR)/$(WORDLIST)
	$(CAT) $< \
          | $(PERL) $(SRCDIR)/extract-tex-refo.pl \
          | $(SORT) > $@

$(SWISS)/words.hyphenated.swiss: $(SRCDIR)/$(WORDLIST)
	$(CAT) $< \
          | $(PERL) $(SRCDIR)/extract-tex-swisstrad.pl \
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

# EOF
