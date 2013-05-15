SogBot
======

Per ottenere una lista con solo gli id dei termini a partire dal file *dbpedia.txt* basta digitare il seguente comando:

   awk '{ print $1 }' dbpedia.txt | awk --field-separator '/' '{print $6}' | sed 's/>//' > idlist.txt
