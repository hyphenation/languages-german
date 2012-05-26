#!/usr/bin/awk -f
#
# Dieses Skript liest eine DIFF-Datei der Patgen-Eingabelisten (siehe
# Skript patgen-list-diff.sh) und zerlegt sie in Wörter,
#
#  * die neu hinzugefügt,
#  * die entfernt,
#  * deren Trennung korrigiert und
#  * deren Klein- und Großschreibung korrigiert
#
# wurde.  Die Wörter werden in Dateien der Form <Eingabedatei>.<ext>
# gespeichert.  <ext> ist entsprechend 'added', 'removed', 'case' oder
# 'hyph'.


/^> / {
    # Save diff input file name.
    fdiff = FILENAME
    # Store added word in field with:
    #   key = <normalized word>,
    #   value = <patgen input word>.
    # A normalized word is lower case only with hyphens removed.  Example:
    #   word_in["tafelsilber"] = "Ta-fel-sil-ber"
    v = $2
    k = v
    gsub("-", "", k)
    k = tolower(k)
    word_in[k] = v
}
/^< / {
    # Save diff input file name.
    fdiff = FILENAME
    # Store removed word with:
    #   key = <normalized word>,
    #   value = <patgen input word>.
    # A normalized word is lower case only with hyphens removed.  Example:
    #   word_out["tafelsilber"] = "Ta-fel-sil-ber"
    v = $2
    k = v
    gsub("-", "", k)
    k = tolower(k)
    word_out[k] = v
}

END {
    for (word in word_in) {
        if (word in word_out) {
            # Changed word.
            # Check for case changes only.
            lword_in = tolower(word_in[word])
            lword_out = tolower(word_out[word])
            if (lword_in == lword_out) {
                # Case change only.
                case[word] = word_in[word]
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
    for (word in added)
        print(added[word]) >> fdiff".added"
    for (word in removed)
        print(removed[word]) >> fdiff".removed"
    for (word in hyph)
        print(hyph[word]) >> fdiff".hyph"
    for (word in case)
        print(case[word]) >> fdiff".case"
}
