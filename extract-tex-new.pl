#! /usr/bin/perl -w
#
# extract-tex-new.pl
#
# Dieses Perl-Skript extrahiert aus der `wortliste'-Datei eine Eingabedatei
# für Patgen, und zwar für die neue deutsche Rechtschreibung.
#
# Aufruf:  perl extract-tex-new.pl < wortliste > input.patgen

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
  $zeile = $feld[3] if defined $feld[3] && $feld[3] ne "---";
  $zeile = $feld[4] if defined $feld[4] && $feld[4] ne "---";
  $zeile = $feld[6] if defined $feld[6] && $feld[6] ne "---";
  next if $zeile eq "---";

  # entferne Doppeldeutigkeiten ganz
  next if $zeile =~ /[\[\]]/;
  # entferne Markierungen für schlechte Trennungen
  $zeile =~ s/\.//g;
  print "$zeile\n";
}

# eof
