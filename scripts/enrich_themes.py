#!/usr/bin/env python3
"""Ajoute `themes:` au front-matter des fiches d'AVP qui n'en ont pas.

Lancé au build (deploy_site.yaml), juste après enrich_descriptions.py et avant `hugo`.
Le grand thème d'une offre est une fonction pure de sa famille de métier : la table est
`data/familles_themes.yml`, générée par scripts/generer_familles.py. Le calculer ici
plutôt que dans le moteur couvre d'un coup toutes les fiches déjà publiées et les
archives, sans republication ; le jour où le moteur écrira lui-même `themes:`, ce script
ne touchera plus ces fiches (il ne complète que ce qui manque).

Alimente la taxonomie `themes` (hugo.toml) : une page par thème, cible des liens de la
légende de la carte.

Sans dépendance hors bibliothèque standard : le YAML des données est lu par expression
régulière, il est plat et généré (une ligne `"famille": "thème"` par entrée).
"""
import os
import re
import sys

CONTENT = "content"
TABLE = os.path.join("data", "familles_themes.yml")
THEME_DEFAUT = "Autres métiers"


def charger_table(chemin: str) -> dict:
    table = {}
    with open(chemin, encoding="utf-8") as fh:
        for ligne in fh:
            m = re.match(r'^\s+"((?:[^"\\]|\\.)*)":\s+"((?:[^"\\]|\\.)*)"\s*$', ligne)
            if m:
                table[m.group(1).replace('\\"', '"')] = m.group(2).replace('\\"', '"')
    return table


def familles_du_front_matter(fm: str) -> list:
    m = re.search(r'^familles:\s*\[(.*)\]\s*$', fm, re.MULTILINE)
    if not m:
        return []
    return [f.replace('\\"', '"') for f in re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))]


def main() -> int:
    if not os.path.exists(TABLE):
        print(f"❌ Table introuvable : {TABLE}", file=sys.stderr)
        return 1
    table = charger_table(TABLE)
    if not table:
        print(f"❌ Table vide : {TABLE}", file=sys.stderr)
        return 1

    ajoutes = deja = sans_famille = 0
    inconnues = set()
    for racine, _dirs, fichiers in os.walk(CONTENT):
        if racine == CONTENT:
            continue  # les pages éditoriales vivent à la racine : jamais d'AVP là
        for nom in fichiers:
            if not nom.endswith(".md") or nom == "_index.md":
                continue
            chemin = os.path.join(racine, nom)
            with open(chemin, encoding="utf-8") as fh:
                contenu = fh.read()
            parts = contenu.split("---", 2)
            if len(parts) < 3:
                continue
            fm, corps = parts[1], parts[2]
            if re.search(r"^themes:", fm, re.MULTILINE):
                deja += 1
                continue
            familles = familles_du_front_matter(fm)
            if not familles:
                sans_famille += 1
                continue
            themes = []
            for f in familles:
                t = table.get(f)
                if t is None:
                    inconnues.add(f)
                    t = THEME_DEFAUT
                if t not in themes:
                    themes.append(t)
            ligne = "themes: [" + ", ".join('"' + t.replace('"', '\\"') + '"' for t in themes) + "]"
            # Juste sous `familles:`, pour que le front-matter reste lisible.
            fm = re.sub(r"^(familles:.*)$", lambda m: m.group(1) + "\n" + ligne, fm, count=1, flags=re.MULTILINE)
            with open(chemin, "w", encoding="utf-8") as fh:
                fh.write(f"---{fm}---{corps}")
            ajoutes += 1

    print(f"🏷️ Thèmes : {ajoutes} fiche(s) complétée(s), {deja} déjà renseignée(s), {sans_famille} sans famille.")
    if inconnues:
        print(f"⚠️ Familles absentes de {TABLE} (thème « {THEME_DEFAUT} ») : {sorted(inconnues)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
