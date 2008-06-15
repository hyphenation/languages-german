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
PATTERNS = $(OLD)/$(OLD)-$(DATE).tex $(NEW)/$(NEW)-$(DATE).tex
WRAPPERS = $(OLD)/$(OLD).tex $(NEW)/$(NEW).tex


.PHONY: pre tex

all: pre tex

pre:
	$(MKDIR) $(OLD) $(NEW)

tex: $(PATTERNS) $(WRAPPERS)


$(OLD)/$(OLD)-$(DATE).tex: $(OLD)/words.hyphenated.old
	$(CHDIR) $(OLD); \
          $(SH) $(SRCDIR)/make-full-pattern.sh $(<F) $(SRCDIR)/german.tr; \
          $(CAT) $(SRCDIR)/$(OLD).1 \
            | $(SED) -e "s/@DATE@/$(DATE)/" \
                     -e "s/@GIT_VERSION@/$(GIT_VERSION)/" > $(@F); \
          $(CAT) pattern.rules >> $(@F); \
          $(CAT) $(SRCDIR)/$(OLD).2 >> $(@F); \
          $(CAT) pattern.8 \
            | $(ICONV) >> $(@F); \
          $(CAT) $(SRCDIR)/$(OLD).3 >> $(@F)

$(NEW)/$(NEW)-$(DATE).tex: $(NEW)/words.hyphenated.new
	$(CHDIR) $(NEW); \
          $(SH) $(SRCDIR)/make-full-pattern.sh $(<F) $(SRCDIR)/german.tr; \
          $(CAT) $(SRCDIR)/$(NEW).1 \
            | $(SED) -e "s/@DATE@/$(DATE)/" \
                     -e "s/@GIT_VERSION@/$(GIT_VERSION)/" > $(@F); \
          $(CAT) pattern.rules >> $(@F); \
          $(CAT) $(SRCDIR)/$(NEW).2 >> $(@F); \
          $(CAT) pattern.8 \
            | $(ICONV) >> $(@F); \
          $(CAT) $(SRCDIR)/$(NEW).3 >> $(@F)

$(OLD)/words.hyphenated.old: $(SRCDIR)/$(WORDLIST)
	$(CAT) $< \
          | $(PERL) $(SRCDIR)/extract-tex-old.pl \
          | $(SORT) > $@

$(NEW)/words.hyphenated.new: $(SRCDIR)/$(WORDLIST)
	$(CAT) $< \
          | $(PERL) $(SRCDIR)/extract-tex-new.pl \
          | $(SORT) > $@

$(OLD)/$(OLD).tex: $(SRCDIR)/$(OLD).tex.in
	$(CAT) $< \
          | $(SED) -e "s/@DATE@/$(DATE)/" > $@

$(NEW)/$(NEW).tex: $(SRCDIR)/$(NEW).tex.in
	$(CAT) $< \
          | $(SED) -e "s/@DATE@/$(DATE)/" > $@

# EOF
