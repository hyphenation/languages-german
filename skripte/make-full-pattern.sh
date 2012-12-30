#!/bin/bash

#
# Dieses Skript generiert deutsche Trennmuster.
#
# Aufruf:
#
#   sh make-full-pattern.sh words.hyphenated german.tr
#
#
# Eingabe: words.hyphenated   Liste von getrennten Wörtern.
#          german.tr          Translationsdatei für patgen.
#
# Ausgabe: pattmp.[1-8]       patgen-Resultate.
#          pattern.[1-8]      Trennmuster -- pattern.8 ist die finale
#                             Trennmusterdatei.
#          pattern.[1-8].log  Log-Dateien.
#          pattern.rules      Die patgen-Parameter in kompakter Form.
#


# Die Parameter für patgen für die Level eins bis acht.

hyph_start_finish[1]='1 1'
hyph_start_finish[2]='2 2'
hyph_start_finish[3]='3 3'
hyph_start_finish[4]='4 4'
hyph_start_finish[5]='5 5'
hyph_start_finish[6]='6 6'
hyph_start_finish[7]='7 7'
hyph_start_finish[8]='8 8'

pat_start_finish[1]='2 5'
pat_start_finish[2]='2 5'
pat_start_finish[3]='2 6'
pat_start_finish[4]='2 6'
pat_start_finish[5]='2 7'
pat_start_finish[6]='2 7'
pat_start_finish[7]='2 13'
pat_start_finish[8]='2 13'

good_bad_thres[1]='1 1 1'
good_bad_thres[2]='1 2 1'
good_bad_thres[3]='1 1 1'
good_bad_thres[4]='1 4 1'
good_bad_thres[5]='1 1 1'
good_bad_thres[6]='1 6 1'
good_bad_thres[7]='1 4 1'
good_bad_thres[8]='1 8 1'


printf "%s\n%s\n%s\n%s" "${hyph_start_finish[1]}" \
                        "${pat_start_finish[1]}" \
                        "${good_bad_thres[1]}" \
                        "y" \
| patgen $1 /dev/null pattern.1 $2 \
| tee pattern.1.log

for i in 2 3 4 5 6 7 8; do
  printf "%s\n%s\n%s\n%s" "${hyph_start_finish[$i]}" \
                          "${pat_start_finish[$i]}" \
                          "${good_bad_thres[$i]}" \
                          "y" \
  | patgen $1 pattern.$(($i-1)) pattern.$i $2 \
  | tee pattern.$i.log
done

rm -f pattern.rules
for i in 1 2 3 4 5 6 7 8; do
  printf "%%   %s | %s | %s\n" "${hyph_start_finish[$i]}" \
                               "${pat_start_finish[$i]}" \
                               "${good_bad_thres[$i]}" \
  >> pattern.rules
done

# eof
