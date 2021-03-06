# Repositorium *wortliste* – Übersicht

<!-- Diese Datei kann mit 

       $ pandoc -t html5 -so index.html index.md

 nach HTML konvertiert werden.-->

Das Repositorium enthält:  

1. Eine Wortliste als Grundlage für die Generierung von Trennmustern nebst 
   einiger Neben- und Sonderlisten.  
2. Einen Mechanismus zur Generierung von Trennmustern aus den Wortlisten.  
3. Einige Skripte zur Arbeit mit den Wortlisten.  
4. Das LaTeX-Paket *dehyph-exptl*.  

Allgemeine Informationen zu diesem Projekt finden sich im [Projekt-Wiki] und in
der [Trennmusterliste]. 

## Verzeichnisstruktur und Dokumentation
  
 [wortliste]  
  + [daten]  
  + [dehyph-exptl]  
  + [dokumente]  
  + [skripte]  
  &nbsp;&nbsp;+ [lua]  
  &nbsp;&nbsp;+ [python]  

Die meisten Verzeichnisse enthalten eine MANIFEST-Datei, in der die einzelnen
enthaltenen Dateien aufgeführt und kurz erläutert sind. Das Format der
Wortliste ist in [README.wortliste] beschrieben. Eine kurze Anleitung für
die Erstellung und Einrichtung neuer Trennmuster findet sich in
[new-patterns]. Das LaTeX-Paket im Verzeichnis [dehyph-exptl] erzeugt bei
seiner Installation eine eigene Dokumentation, die über

<pre>
    $ texdoc dehyph-exptl
</pre>

zugänglich ist.


[projekt-wiki]: http://projekte.dante.de/Trennmuster
[trennmusterliste]: https://lists.dante.de/mailman/listinfo/trennmuster
[wortliste]: ../
[daten]: ../daten
[dehyph-exptl]: ../dehyph-exptl/
[dokumente]: ../dokumente
[skripte]: ../skripte
[python]: ../skripte/python
[lua]: ../skripte/lua
[README.wortliste]: README.wortliste
[new-patterns]: new-patterns
[dehyph-exptl]: ../dehyph-exptl/
