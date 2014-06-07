#! /usr/bin/perl -w
#
# extract-tex.pl
#
# Dieses Perl-Skript extrahiert einfache Wortlisten aus der
# »wortliste«-Datenbank, die beispielsweise als Eingabedateien für »patgen«
# verwendet werden können.
#
# Aufruf:  perl extract-tex.pl [Optionen...] < wortliste > input.patgen
#
# Die »wortliste«-Datei muss in UTF-8 kodiert sein.
#
# Optionen
# --------
#
# -t
# -s  Option »-t« wählt die traditionelle deutsche Rechtschreibung aus,
#     Option »-s« die traditionelle (deutsch)schweizerische Rechtschreibung.
#     Wenn weder »-s« noch »-t« gesetzt ist, wird die reformierte deutsche
#     Rechtschreibung ausgewählt.
#
# -x  Ignoriere Optionen »-g« und »-u« und gebe die sprachspezifischen
#     Felder unbearbeitet aus.
#
# -g  Gib Wörter mit gewichteten Trennstellen aus; Wörter mit »·« werden
#     ignoriert.  Optional kann ein ganzzahliges Argument angegeben werden:
#     Wert 0 gibt alle gewichtete Trennstellen aus inklusive »-« (das ist
#     der Standardwert), Wert 1 nur die Trennstellen mit der höchsten
#     Wichtung (ohne »-«), Wert 2 die Trennstellen mit der höchsten und
#     zweithöchsten Wichtung (ohne »-«), usw.
#
#     Beachte, dass bei nahe beieinanderstehenden Trennstellen derzeit keine
#     zusätzliche Wichtung vorgenommen wird.  Beispielsweise ist in dem Wort
#
#       ab<be<ru-fen
#
#     die Trennung »abbe-rufen« schlecht, weil ganz nahe der optimalen
#     Trennstelle (nach »ab«).  Das Skript gibt trotzdem diese Trennstelle
#     als zweitbeste aus.
#
# -u  Verhindere die Ausgabe von Wörtern mit Markern für unerwünschte
#     Trennungen (z.B. »An-al.pha-bet«).
#
# -v  Verhindere die Ausgabe von Versalformen, wo »ß« durch »ss« ersetzt
#     ist.
#
# -l  Konvertiere die Ausgabe von UTF-8 nach latin-9 (wie von »patgen«
#     benötigt).

use strict;
use warnings;
use English '-no_match_vars';
use utf8;                              # String-Literals direkt als UTF-8.
use Getopt::Long qw(:config bundling);


my ($opt_g, $opt_l, $opt_s, $opt_t, $opt_u, $opt_v, $opt_x);
$opt_g = -1;

GetOptions("g:i" => \$opt_g,
           "l"   => \$opt_l,
           "s"   => \$opt_s,
           "t"   => \$opt_t,
           "u"   => \$opt_u,
           "v"   => \$opt_v,
           "x"   => \$opt_x);


my $prog = $0;
$prog =~ s@.*/@@;


# Kodierung:
binmode(STDIN, ":encoding(utf8)");

if ($opt_l) {
  binmode(STDOUT, ":encoding(latin9)");
}
else {
  binmode(STDOUT, ":encoding(utf8)");
}


sub entferne_marker {
  my $arg = shift;
  $arg =~ s/[-=<>·]//g;
  return $arg;
}


while (<>) {
  next if /^#/;
  chop;

  # Entferne Kommentare.
  s/#.*$//;

  # Entferne Leerzeichen aller Art.
  s/\s+//g;

  my @feld = split(';');
  next if $#feld < 1;

  # reformiert:           Felder 2, 4, 5, 7
  # traditionell:         Felder 2, 3, 5, 6
  # traditionell Schweiz: Felder 2, 3, 5, 6, 8
  #
  # Beachte: Feld n hat Index n-1.
  my $zeile = $feld[1];
  $zeile = $feld[2] if defined $feld[2]
                       && $feld[2] ne "-3-" && ($opt_t || $opt_s);
  $zeile = $feld[3] if defined $feld[3]
                       && $feld[3] ne "-4-" && !($opt_t || $opt_s);
  $zeile = $feld[4] if defined $feld[4]
                       && $feld[4] ne "-5-" && !$opt_v;
  $zeile = $feld[5] if defined $feld[5]
                       && $feld[5] ne "-6-" && ($opt_t || $opt_s) && !$opt_v;
  $zeile = $feld[6] if defined $feld[6]
                       && $feld[6] ne "-7-" && !($opt_t || $opt_s) && !$opt_v;
  $zeile = $feld[7] if defined $feld[7]
                       && $feld[7] ne "-8-" && $opt_s && !$opt_v;

  next if $zeile eq "-2-";

  if (!$opt_x) {
    # Entferne spezielle Trennungen.
    $zeile =~ s|\{ (.*?) / .*? \}|$1|gx;

    # Entferne Doppeldeutigkeiten.
    $zeile =~ s|\[ (.*?) / .*? \]|entferne_marker($1)|egx;

    # Ausgabe von Wörtern mit unerwünschten Trennungen?
    next if $zeile =~ /\./ and $opt_u;

    # Entferne Markierungen für unerwünschte Trennungen.
    $zeile =~ s/[·<>=-]* \.+ [·<>=-]*//gx;

    # Ausgabe von Wörtern mit ungewichteten Trennstellen?
    next if $zeile =~ /·/ and $opt_g >= 0;

    if ($opt_g > 0) {
      # Berechne Wichtungen.  Wir verwenden folgende Werte:
      #
      #   -2   Wortteil
      #   -1   -
      #    0   <, >
      #    1   =
      #    2   ==, <=, =>
      #    3   ===, <==, ==>
      #    ...
      #
      # Bei mehrfachem Auftreten von »<« hat das am meisten links stehende
      # den höchsten Rang.  Bei mehrfachem Auftreten von »>« hat das am
      # meisten rechts stehende den höchsten Rang.  Beispiel:
      #
      #   Mit<ver<ant-wort>lich>keit
      #      ^                 ^
      #
      # Das bezieht sich auch auf Ketten mit »=>« u.ä:
      #
      #   Ei-gen=wirt>schaft=>lich>keit
      #                           ^

      my $g;
      my $m;
      my ($r, $r_vorher);
      my ($w, $w_vorher);

      # Wir zerlegen mit `split' unter Beibehaltung der Begrenzer.
      my @zerlegung = split /([<>=-]+)/, $zeile;

      # Wir speichern Wichtung und Rang als Felder.
      my @wichtung = (-2) x ($#zerlegung + 1);
      my @rang = (0) x ($#zerlegung + 1);

      # Erster Durchgang: Ermittle Wichtungswerte.

      # Wir starten bei erstem Marker (mit Index 1).
      foreach my $i (1 .. ($#zerlegung - 1)) {
        # Ignoriere Nicht-Marker.
        next if not $i % 2;

        $m = $zerlegung[$i];

        if ($m =~ /^-$/) {
          $w = -1;
        }
        elsif ($m =~ /^[<>]$/) {
          $w = 0;
        }
        elsif ($m =~ /^=$/) {
          $w = 1;
        }
        elsif ($m =~ /( ==*>? | <?=*= )/x) {
          $w = length($1);
        }
        else {
          warn "Zeile $INPUT_LINE_NUMBER:"
               . " unbekannter Marker »$m« behandelt als »-«\n";
          $w = -1;
        }

        $wichtung[$i] = $w;
      }

      # Zweiter Durchgang: Adjustiere Wichtung von »<« und »>«.

      # Behandle »<« von rechts nach links gehend.
      $w_vorher = -2;
      foreach my $i (reverse(1 .. ($#zerlegung - 1))) {
        # Ignoriere Nicht-Marker.
        next if not $i % 2;

        if (index ($zerlegung[$i], "<") >= 0) {
          # Hat der rechte Marker in einer Kette von »<« eine höhere
          # Wichtung, wird diese übernommen.
          $w = $wichtung[$i];

          if ($w_vorher >= $w) {
            $wichtung[$i] = $w_vorher;
          }
          else {
            $w_vorher = $w;
          }
        }
        # »-«-Marker zwischen zwei »<« ändert nicht deren Wichtung.
        elsif ($zerlegung[$i] ne "-") {
          $w_vorher = -2;
        }
      }

      # Behandle »>« von links nach rechts gehend.
      $w_vorher = -2;
      foreach my $i (1 .. ($#zerlegung - 1)) {
        # Ignoriere Nicht-Marker.
        next if not $i % 2;

        if (index ($zerlegung[$i], ">") >= 0) {
          # Hat der linke Marker in einer Kette von »>« eine höhere
          # Wichtung, wird diese übernommen.
          $w = $wichtung[$i];

          if ($w_vorher >= $w) {
            $wichtung[$i] = $w_vorher;
          }
          else {
            $w_vorher = $w;
          }
        }
        # »-«-Marker zwischen zwei »>« ändert nicht deren Wichtung.
        elsif ($zerlegung[$i] ne "-") {
          $w_vorher = -2;
        }
      }

      # Dritter Durchgang: Ermittle Rang von »<« und »>«.

      # Behandle »<« von links nach rechts gehend.
      $r = 0;
      foreach my $i (1 .. ($#zerlegung - 1)) {
        # Ignoriere Nicht-Marker.
        next if not $i % 2;

        if (index ($zerlegung[$i], "<") >= 0) {
          $rang[$i] = $r--;
        }
        # »-«-Marker zwischen zwei »<« ändert nicht den Rang.
        elsif ($zerlegung[$i] ne "-") {
          $r = 0;
        }
      }

      # Behandle »>« von rechts nach links gehend.
      $r = 0;
      foreach my $i (reverse(1 .. ($#zerlegung - 1))) {
        # Ignoriere Nicht-Marker.
        next if not $i % 2;

        if (index ($zerlegung[$i], ">") >= 0) {
          $rang[$i] = $r--;
        }
        # »-«-Marker zwischen zwei »>« ändert nicht den Rang.
        elsif ($zerlegung[$i] ne "-") {
          $r = 0;
        }
      }

      # Sortiere Indexfeld für Marker mit absteigender Wichtung.
      my @wichtungsindices =
        sort {
          # Benutze Rang für Sekundärsortierung.
          if ($wichtung[$a] == $wichtung[$b]) {
            -($rang[$a] <=> $rang[$b]);
          }
          else {
            -($wichtung[$a] <=> $wichtung[$b]);
          }
        } (0 .. $#zerlegung);

      # Entferne Trennstellen unter Berücksichtigung des Arguments von »-g«.
      $g = 0;
      $w_vorher = -2;
      $r_vorher = 0;

      foreach my $i (@wichtungsindices) {
        # Alle Wortteile haben einen geraden Index und sind stets am Schluß
        # von @wichtungsindices.
        last if not $i % 2;

        $w = $wichtung[$i];
        $r = $rang[$i];

        if ($w_vorher == $w) {
          $g++ if $r_vorher != $r;
        }
        else {
          $g++;
        }

        $w_vorher = $w;
        $r_vorher = $r;

        # Entferne Trennung mit zu geringer Wichtung.
        $zerlegung[$i] = "" if $g > $opt_g || $w < 0;
      }

      $zeile = join '', @zerlegung;
    }
    elsif ($opt_g < 0) {
      # Reduziere Trennstellenmarker zu »-«.
      $zeile =~ s/[·<>=-]+/-/g;
    }
  }

  print "$zeile\n";
}

# eof
