#!/usr/bin/awk -f
#
# Dieses Skript liest eine DIFF-Datei der Patgen-Eingabelisten (siehe
# Skript diff-patgen-input.sh) und zerlegt sie in Wörter,
#
#  * die neu hinzugefügt,
#  * die entfernt,
#  * deren Trennung korrigiert und
#  * deren Klein- und Großschreibung korrigiert
#
# wurde.  Die Wörter werden in Dateien der Form <Eingabedatei>.<ext>
# gespeichert.  <ext> ist entsprechend 'added', 'removed', 'case' oder
# 'hyph'.  Beim Aufruf des Skripts muss die Variable 'ftr' mit dem Namen
# der Translate-Datei für Patgen vorbelegt werden:
#   gawk -v ftr=<translate datei> ...



# Translate a string to lower case characters as defined by the rules in
# the translate file.
function tr_tolower(s) {
    l = length(s)
    trs = ""
    for (i=1; i<=l; ++i) {
        ch = substr(s, i, 1)
        if (tr[ch] == "") {
            printf("%s", "Error: Bad character '" ch "' in string " s " (" FILENAME ", line " FNR ")\n") > "/dev/stderr"
            error = 1
            exit
        }
        trs = trs tr[ch]
    }
    return trs
}



# Normalize a word.
#   * Remove hyphens.
#   * All lower case.
function normalize_word(word) {
    gsub("-", "", word)
    word = tr_tolower(word)
    return word
}



# Output all words of a class (added, removed, ...) to a file.  Output
# number of words in class on command-line.
function output_word_class(clarr, clname) {
    fname = fdiff "." clname
    i = 0
    # Create output file and output word class unsorted.
    printf "" > fname ".unsort"
    for (word in clarr) {
        ++i
        print(clarr[word]) >> fname ".unsort"
    }
    print(clname ": " i)
    # Sort output file on shell.
    system("LC_COLLATE=de_DE.ISO8859-15 LC_CTYPE=de_DE.ISO8859-15 sort -f " fname ".unsort > " fname)
    system("rm -f " fname ".unsort")
}



# Read translate file via getline and build translate table used for
# validating and normalizing words.  A word is valid, if it consists
# entirely of characters that are indices in table tr.
function read_translate_file(ftr) {
    # Switch to fixed-width field splitting mode.  The separator in
    # translate files is not known in advance and can change from line
    # to line.
    FIELDWIDTHS = "1 1 1 1 1 1 1"
    # Skip first line containing hyphenation minima and hyphenation
    # characters.
    getline < ftr
    # The hyphen is a valid character.
    tr["-"] = "-"
    # NR and FNR aren't updated when reading a file via getline.  So we
    # count lines manually.
    ln = 1
    # Read lines from translate file.
    while (getline < ftr > 0) {
        ++ln
        # Skip comments (column 1 == column 2).
        if ($1 != $2) {
            # Determine number of columns on line.
            cols = 0
            while ($(cols+1) != "") {
                cols++
            }
            # Ignore trailing separators.
            while ((cols > 0) && ($cols == $1)) {
                cols--
            }
            # Check character translation table format.  Check if
            # separators are all equal to that in column 1.
            for (i=3; i<=cols; i=i+2) {
                if ($i != $1) {
                    printf("%s", "Error: Bad character translation table in file " ftr ", line " ln "\n") > "/dev/stderr"
                    error = 1
                    exit
                }
            }
            # Store characters in translation table.
            for (i=2; i<=cols; i=i+2)
                tr[$i] = $2
        }
    }
#    print(ln " lines from translation file " ftr " read OK.")
#    for (ch in tr)
#        print(ch, tr[ch])
    # Reset regular field splitting mode.
    FS = FS
    return
}



# First, read translate file, whose name is defined in variable ftr on the
# command line.
BEGIN {
    # Check if translate file name is set.
    if (ftr == "") {
        printf("%s", "Error: Translate file name missing!\nPlease set-up variable 'ftr' like: gawk -v ftr=<translate file> ...\n") > "/dev/stderr"
        error = 1
        exit
    }
    # Read translate file and build translate table.
    read_translate_file(ftr)
}



# Read DIFF file's added lines.
/^> / {
    # Store added word in field with:
    #   key = <normalized word>,
    #   value = <patgen input word>.
    # A normalized word is lower case only with hyphens removed.  Example:
    #   word_in["tafelsilber"] = "Ta-fel-sil-ber"
    k = normalize_word($2)
    v = $2
    word_in[k] = v
}
# Read DIFF file's removed lines.
/^< / {
    # Store removed word with:
    #   key = <normalized word>,
    #   value = <patgen input word>.
    # A normalized word is lower case only with hyphens removed.  Example:
    #   word_out["tafelsilber"] = "Ta-fel-sil-ber"
    k = normalize_word($2)
    v = $2
    word_out[k] = v
}



END {
    if (error) {
        exit error
    }
    for (word in word_in) {
        if (word in word_out) {
            # Changed word.
            # Check for case changes only.
            lword_in = tr_tolower(word_in[word])
            lword_out = tr_tolower(word_out[word])
            if (lword_in == lword_out) {
                # Case change only.
                CaSe[word] = word_in[word]
            }
            else {
                # Hyphenation corrected.
                hyph[word] = word_in[word]
            }
        }
        else {
            # Added word.
            added[word] = word_in[word]
        }
    }
    for (word in word_out) {
        if (word in word_in) {
            # Changed word.
            # Already processed in above loop.
        }
        else {
            # Removed word.
            removed[word] = word_out[word]
        }
    }
    # Save input file name.
    fdiff = FILENAME
    # Output results.
    print("Processed file " fdiff ".")
    output_word_class(added, "added")
    output_word_class(removed, "removed")
    output_word_class(hyph, "hyph")
    output_word_class(CaSe, "case")
}
