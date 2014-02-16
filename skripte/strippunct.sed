# wird von prepare-wordlist.sh verwendet.

s/[-'‘"·*+=~«»<>.,:;!\?()_„“@©•—…0-9]/ /g	# ersetzt alle nichtalphabetischen durch Leerzeichen
s/[IVXLDMC.]\{2,\}/ /g		      		# entfernt römische Zahlen
s/ /\n/g	    				# ersetzt Leerzeichen durch Zeilenumbruch
