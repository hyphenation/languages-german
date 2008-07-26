#! /usr/bin/perl -w
#
# extract-tex-refo.pl
#
# Dieses Perl-Skript extrahiert aus der `wortliste'-Datei eine Eingabedatei
# für Patgen, und zwar für die reformierte deutsche Rechtschreibung.
#
# Aufruf:  perl extract-tex-refo.pl < wortliste > input.patgen

use strict;

my $prog = $0;
$prog =~ s@.*/@@;

while (<>) {
  chop;
  next if /^#/;

  my @feld = split(';');
  next if $#feld < 0;

  # Felder 2, 4, 5 und 7
  my $zeile = $feld[1];
  $zeile = $feld[3] if defined $feld[3] && $feld[3] ne "-4-";
  $zeile = $feld[4] if defined $feld[4] && $feld[4] ne "-5-";
  $zeile = $feld[6] if defined $feld[6] && $feld[6] ne "-7-";
  next if $zeile eq "-2-";

  # entferne Doppeldeutigkeiten
  $zeile =~ s/\[-*(.*?)-*\|.*?\]/$1/g;
  # entferne Markierungen für schlechte Trennungen
  $zeile =~ s/\.//g;

  print "$zeile\n";
}

# eof
