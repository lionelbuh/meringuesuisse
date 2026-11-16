#!/bin/sh
# Downloads the Google Fonts used by the reel scripts into ./fonts (not committed).
cd "$(dirname "$0")" && mkdir -p fonts && cd fonts
for f in "ofl/cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf" "ofl/cormorantgaramond/CormorantGaramond-Italic%5Bwght%5D.ttf" "ofl/figtree/Figtree%5Bwght%5D.ttf"; do
  o=$(basename "$f" | sed 's/%5B/[/;s/%5D/]/'); [ -f "$o" ] || curl -sS -L -o "$o" "https://raw.githubusercontent.com/google/fonts/main/$f"
done
