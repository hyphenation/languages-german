# This Makefile creates German hyphenation patterns in subdirectories
# $(OLD) and $(NEW).  

SRCDIR = ~/git/wortliste
WORDLIST = $(SRCDIR)/wortliste

OLD = dehypht-x
NEW = dehyphn-x

LC_ENVVARS = LC_COLLATE=de_DE.ISO8859-1 \
             LC_CTYPE=de_DE.ISO8859-1
SORT = $(LC_ENVVARS) sort -d \
       | $(LC_ENVVARS) uniq -i
MKDIR = mkdir -p
CHDIR = cd
COPY = cp
SH = sh
CAT = cat
PERL = perl
ICONV = iconv -f latin1 -t utf8


.PHONY: pre patterns

all: pre patterns

pre:
	$(MKDIR) $(OLD) $(NEW)

patterns: $(OLD)/$(OLD).pattern.latin1 $(NEW)/$(NEW).pattern.latin1 \
          $(OLD)/$(OLD).pattern.utf8 $(NEW)/$(NEW).pattern.utf8


$(OLD)/$(OLD).pattern.latin1: $(OLD)/words.hyphenated.old
	$(CHDIR) $(OLD); \
          $(SH) $(SRCDIR)/make-full-pattern.sh $(<F) $(SRCDIR)/german.tr; \
          $(COPY) pattern.8 $(@F); \
          $(CHDIR) ..

$(OLD)/$(OLD).pattern.utf8: $(OLD)/$(OLD).pattern.latin1
	$(CAT) $< \
          | $(ICONV) \
          > $@

$(NEW)/$(NEW).pattern.latin1: $(NEW)/words.hyphenated.new
	$(CHDIR) $(NEW); \
          $(SH) $(SRCDIR)/make-full-pattern.sh $(<F) $(SRCDIR)/german.tr; \
          $(COPY) pattern.8 $(@F); \
          $(CHDIR) ..

$(NEW)/$(NEW).pattern.utf8: $(NEW)/$(NEW).pattern.latin1
	$(CAT) $< \
          | $(ICONV) \
          > $@

$(OLD)/words.hyphenated.old: $(WORDLIST)
	$(CAT) $< \
          | $(PERL) $(SRCDIR)/extract-tex-old.pl \
          | $(SORT) \
          > $@

$(NEW)/words.hyphenated.new: $(WORDLIST)
	$(CAT) $< \
          | $(PERL) $(SRCDIR)/extract-tex-new.pl \
          | $(SORT) \
          > $@

# EOF
