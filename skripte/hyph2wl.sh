LC_COLLATE=de_DE.UTF8

sed 's/^.*$/&;&/'\
| sed 's/[-=·\.\|]\+\(.*;\)/\1/g'\
| sed 's/[-=·\.\|]\+\(.*;\)/\1/g'\
| sed 's/[-=·\.\|]\+\(.*;\)/\1/g'\
| sed 's/[-=·\.\|]\+\(.*;\)/\1/g'\
| sed 's/[-=·\.\|]\+\(.*;\)/\1/g'\
| sed 's/[-=·\.\|]\+\(.*;\)/\1/g'\
| sed 's/[-=·\.\|]\+\(.*;\)/\1/g'\
| sed 's/-/·/g'
