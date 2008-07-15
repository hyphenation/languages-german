# This Makefile creates German hyphenation patterns in subdirectories
# $(TRAD) and $(REFO).  

SRCDIR = ~/git/wortliste
WORDLIST = wortliste

TRAD = dehypht-x
REFO = dehyphn-x

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
PATTERNS = $(TRAD)/$(TRAD)-$(DATE).pat $(REFO)/$(REFO)-$(DATE).pat
WRAPPERS = $(TRAD)/$(TRAD)-$(DATE).tex $(REFO)/$(REFO)-$(DATE).tex


.PHONY: pre-trad pre-refo tex

all: pre tex

pre-trad:
	$(MKDIR) $(TRAD)
pre-refo:
	$(MKDIR) $(REFO)

tex: $(PATTERNS) $(WRAPPERS)

# auxiliary targets

words-trad: pre-trad $(TRAD)/words.hyphenated.trad
words-refo: pre-refo $(REFO)/words.hyphenated.refo


$(TRAD)/pattern.8 $(TRAD)/pattern.rules: $(TRAD)/words.hyphenated.trad
	$(CHDIR) $(TRAD); \
          $(SH) $(SRCDIR)/make-full-pattern.sh $(<F) $(SRCDIR)/german.tr

$(TRAD)/$(TRAD)-$(DATE).pat : $(TRAD)/pattern.8 $(TRAD)/pattern.rules
	$(CAT) $(SRCDIR)/$(TRAD).1 \
          | $(SED) -e "s/@DATE@/$(DATE)/" \
                   -e "s/@GIT_VERSION@/$(GIT_VERSION)/" > $@; \
        $(CAT) $(TRAD)/pattern.rules >> $@; \
        $(CAT) $(SRCDIR)/$(TRAD).2 >> $@; \
        $(CAT) $(TRAD)/pattern.8 \
          | $(ICONV) >> $@; \
        $(CAT) $(SRCDIR)/$(TRAD).3 >> $@

$(REFO)/pattern.8 $(REFO)/pattern.rules: $(REFO)/words.hyphenated.refo
	$(CHDIR) $(REFO); \
          $(SH) $(SRCDIR)/make-full-pattern.sh $(<F) $(SRCDIR)/german.tr

$(REFO)/$(REFO)-$(DATE).pat: $(REFO)/pattern.8 $(REFO)/pattern.rules
	$(CAT) $(SRCDIR)/$(REFO).1 \
          | $(SED) -e "s/@DATE@/$(DATE)/" \
                   -e "s/@GIT_VERSION@/$(GIT_VERSION)/" > $@; \
        $(CAT) $(REFO)/pattern.rules >> $@; \
        $(CAT) $(SRCDIR)/$(REFO).2 >> $@; \
        $(CAT) $(REFO)/pattern.8 \
          | $(ICONV) >> $@; \
        $(CAT) $(SRCDIR)/$(REFO).3 >> $@

$(TRAD)/words.hyphenated.trad: $(SRCDIR)/$(WORDLIST)
	$(CAT) $< \
          | $(PERL) $(SRCDIR)/extract-tex-trad.pl \
          | $(SORT) > $@

$(REFO)/words.hyphenated.refo: $(SRCDIR)/$(WORDLIST)
	$(CAT) $< \
          | $(PERL) $(SRCDIR)/extract-tex-refo.pl \
          | $(SORT) > $@

$(TRAD)/$(TRAD)-$(DATE).tex: $(SRCDIR)/$(TRAD).tex.in
	$(CAT) $< \
          | $(SED) -e "s/@DATE@/$(DATE)/" > $@

$(REFO)/$(REFO)-$(DATE).tex: $(SRCDIR)/$(REFO).tex.in
	$(CAT) $< \
          | $(SED) -e "s/@DATE@/$(DATE)/" > $@

# EOF
