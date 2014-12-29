#!/usr/local/bin/bash
for genre in drama entertainment comedy
do
  echo "handling" $genre
  python nitroradical.py ${genre} > ../iplayercast/json/${genre}.json
done
