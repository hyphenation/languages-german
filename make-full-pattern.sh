#!/bin/sh

#
# Dieses Skript generiert deutsche Trennmuster.
#
# Aufruf:  sh make-full-pattern.sh words.hyphenated german.tr
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


# Die Parameter für patgen.

LEVEL1_HYPH_START_FINISH="1 1"
LEVEL2_HYPH_START_FINISH="2 2"
LEVEL3_HYPH_START_FINISH="3 3"
LEVEL4_HYPH_START_FINISH="4 4"
LEVEL5_HYPH_START_FINISH="5 5"
LEVEL6_HYPH_START_FINISH="6 6"
LEVEL7_HYPH_START_FINISH="7 7"
LEVEL8_HYPH_START_FINISH="8 8"

LEVEL1_PAT_START_FINISH="2 5"
LEVEL2_PAT_START_FINISH="2 5"
LEVEL3_PAT_START_FINISH="2 6"
LEVEL4_PAT_START_FINISH="2 6"
LEVEL5_PAT_START_FINISH="2 7"
LEVEL6_PAT_START_FINISH="2 7"
LEVEL7_PAT_START_FINISH="2 9"
LEVEL8_PAT_START_FINISH="2 9"

LEVEL1_GOOD_BAD_THRES="1 1 1"
LEVEL2_GOOD_BAD_THRES="1 1 1"
LEVEL3_GOOD_BAD_THRES="1 1 1"
LEVEL4_GOOD_BAD_THRES="1 1 1"
LEVEL5_GOOD_BAD_THRES="1 1 1"
LEVEL6_GOOD_BAD_THRES="1 1 1"
LEVEL7_GOOD_BAD_THRES="1 4 1"
LEVEL8_GOOD_BAD_THRES="1 4 1"


echo "$LEVEL1_HYPH_START_FINISH
$LEVEL1_PAT_START_FINISH
$LEVEL1_GOOD_BAD_THRES
y" | patgen $1 /dev/null pattern.1 $2 | tee pattern.1.log

for i in 2 3 4 5 6 7 8; do
  HSF=LEVEL${i}_HYPH_START_FINISH
  PSF=LEVEL${i}_PAT_START_FINISH
  GBT=LEVEL${i}_GOOD_BAD_THRES
  echo "${!HSF}
${!PSF}
${!GBT}
y" | patgen $1 pattern.$(($i-1)) pattern.$i $2 | tee pattern.$i.log
done

rm -f pattern.rules
for i in 1 2 3 4 5 6 7 8; do
  HSF=LEVEL${i}_HYPH_START_FINISH
  PSF=LEVEL${i}_PAT_START_FINISH
  GBT=LEVEL${i}_GOOD_BAD_THRES
  echo "%   ${!HSF} | ${!PSF} | ${!GBT}" >> pattern.rules
done

# eof
