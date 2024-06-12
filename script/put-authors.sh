#!/bin/bash

# Gehe ins Verzeichnis des Git-Repos
cd ../gesture_glide

# Funktion zum Hinzufügen von Autoren zu einer Datei
add_authors_to_file() {
  file=$1
  authors=$(git log --format='%an' "$file" | sort | uniq)
  authors_list=$(echo "$authors" | tr '\n' ',' | sed 's/,$//')
  if [[ ! -z "$authors_list" ]]; then
    echo -e "# Autoren: $authors_list\n$(cat "$file")" > "$file"
  fi
}

# Iteriere über alle Dateien im Repo
for file in $(git ls-files); do
  if [[ -f $file ]]; then
    add_authors_to_file "$file"
  fi
done