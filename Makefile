# This Makefile creates German hyphenation patterns in subdirectories
# $(OLD) and $(NEW).  

SRCDIR = ~/git/wortliste
WORDLIST = wortliste

OLD = dehypht-x
NEW = dehyphn-x

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
PATTERNS = $(OLD)/$(OLD)-$(DATE).pat $(NEW)/$(NEW)-$(DATE).pat
WRAPPERS = $(OLD)/$(OLD)-$(DATE).tex $(NEW)/$(NEW)-$(DATE).tex


.PHONY: pre tex

all: pre tex

pre:
	$(MKDIR) $(OLD) $(NEW)

tex: $(PATTERNS) $(WRAPPERS)


$(OLD)/pattern.8 $(OLD)/pattern.rules: $(OLD)/words.hyphenated.old
	$(CHDIR) $(OLD); \
          $(SH) $(SRCDIR)/make-full-pattern.sh $(<F) $(SRCDIR)/german.tr

$(OLD)/$(OLD)-$(DATE).pat : $(OLD)/pattern.8 $(OLD)/pattern.rules
	$(CAT) $(SRCDIR)/$(OLD).1 \
          | $(SED) -e "s/@DATE@/$(DATE)/" \
                   -e "s/@GIT_VERSION@/$(GIT_VERSION)/" > $@; \
        $(CAT) $(OLD)/pattern.rules >> $@; \
        $(CAT) $(SRCDIR)/$(OLD).2 >> $@; \
        $(CAT) $(OLD)/pattern.8 \
          | $(ICONV) >> $@; \
        $(CAT) $(SRCDIR)/$(OLD).3 >> $@

$(NEW)/pattern.8 $(NEW)/pattern.rules: $(NEW)/words.hyphenated.new
	$(CHDIR) $(NEW); \
          $(SH) $(SRCDIR)/make-full-pattern.sh $(<F) $(SRCDIR)/german.tr

$(NEW)/$(NEW)-$(DATE).pat: $(NEW)/pattern.8 $(NEW)/pattern.rules
	$(CAT) $(SRCDIR)/$(NEW).1 \
          | $(SED) -e "s/@DATE@/$(DATE)/" \
                   -e "s/@GIT_VERSION@/$(GIT_VERSION)/" > $@; \
        $(CAT) $(NEW)/pattern.rules >> $@; \
        $(CAT) $(SRCDIR)/$(NEW).2 >> $@; \
        $(CAT) $(NEW)/pattern.8 \
          | $(ICONV) >> $@; \
        $(CAT) $(SRCDIR)/$(NEW).3 >> $@

$(OLD)/words.hyphenated.old: $(SRCDIR)/$(WORDLIST)
	$(CAT) $< \
          | $(PERL) $(SRCDIR)/extract-tex-old.pl \
          | $(SORT) > $@

$(NEW)/words.hyphenated.new: $(SRCDIR)/$(WORDLIST)
	$(CAT) $< \
          | $(PERL) $(SRCDIR)/extract-tex-new.pl \
          | $(SORT) > $@

$(OLD)/$(OLD)-$(DATE).tex: $(SRCDIR)/$(OLD).tex.in
	$(CAT) $< \
          | $(SED) -e "s/@DATE@/$(DATE)/" > $@

$(NEW)/$(NEW)-$(DATE).tex: $(SRCDIR)/$(NEW).tex.in
	$(CAT) $< \
          | $(SED) -e "s/@DATE@/$(DATE)/" > $@

# EOF
