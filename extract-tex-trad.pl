#! /usr/bin/perl -w
#
# extract-tex-trad.pl
#
# Dieses Perl-Skript extrahiert aus der `wortliste'-Datei eine Eingabedatei
# für Patgen, und zwar für die traditionelle deutsche Rechtschreibung.
#
# Aufruf:  perl extract-tex-trad.pl < wortliste > input.patgen

use strict;

my $prog = $0;
$prog =~ s@.*/@@;

while (<>) {
  chop;
  next if /^#/;

  my @feld = split(';');
  next if $#feld < 0;

  # Felder 2, 3, 5, 6 und 8
  my $zeile = $feld[1];
  $zeile = $feld[2] if defined $feld[2] && $feld[2] ne "-3-";
  $zeile = $feld[4] if defined $feld[4] && $feld[4] ne "-5-";
  $zeile = $feld[5] if defined $feld[5] && $feld[5] ne "-6-";
  $zeile = $feld[7] if defined $feld[7] && $feld[7] ne "-8-";
  next if $zeile eq "-2-";

  # entferne spezielle Trennungen
  $zeile =~ s/\{(.*?)\|.*?\}/$1/g;
  # entferne Doppeldeutigkeiten
  $zeile =~ s/\[-*(.*?)-*\|.*?\]/$1/g;
  # entferne Markierungen für schlechte Trennungen
  $zeile =~ s/\.//g;

  print "$zeile\n";
}

# eof
