#! /usr/bin/perl -w
#
# extract-tex-swisstrad.pl
#
# Dieses Perl-Skript extrahiert aus der `wortliste'-Datei eine Eingabedatei
# für Patgen, und zwar für die traditionelle (deutsch)schweizerische
# Rechtschreibung.
#
# Aufruf:  perl extract-tex-swisstrad.pl [-g] [-u] < wortliste > input.patgen
#
# Option `-g' bewirkt die Ausgabe von Wörtern mit gewichteten Trennstellen;
# Wörter mit `·' werden ignoriert.
#
# Option `-u' verhindert die Ausgabe von Wörtern mit Markern für
# unerwünschte Trennungen (z.B. `An-al.pha-bet').
#
# Konstrukte, die spezielle Trennungen (`{.../...}') und Doppeldeutigkeiten
# (`[.../...]') anzeigen, werden immer entfernt.

use strict;
use utf8;         # String-Literals direkt als UTF-8
use Getopt::Std;
getopts('gu');

our ($opt_g, $opt_u);

my $prog = $0;
$prog =~ s@.*/@@;

# Kodierung:
binmode(STDIN, ":encoding(utf8)"); # Eingabe (wortliste) in UTF-8
binmode(STDOUT, ":latin1");        # patgen expects a Latin-1 encoded file

while (<>) {
  chop;
  next if /^#/;

  # entferne Kommentare
  s/#.*$//;

  # entferne Leerzeichen aller Art
  s/\s+//g;

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
  $zeile =~ s|\{(.*?)/.*?\}|$1|g;
  # entferne Doppeldeutigkeiten;
  $zeile =~ s;\[[-=|·]*(.*?)[-=|·]*/.*?\];$1;g;

  # Ausgabe von Wörtern mit unerwünschten Trennungen?
  next if $zeile =~ /[._]/ and $opt_u;
  # entferne Markierungen für unerwünschte Trennungen
  $zeile =~ s/[._]//g;

  # Ausgabe von Wörtern mit ungewichteten Trennstellen?
  next if $zeile =~ /·/ and $opt_g;
  # reduziere Trennstellenmarker zu `-', falls gewollt
  $zeile =~ s/[·|=-]+/-/g if not $opt_g;

  print "$zeile\n";
}

# eof
