#!/usr/bin/env python3
"""Ramène chaque terme de taxonomie à une graphie unique, initiale en majuscule.

POURQUOI
La source open data écrit la même entité de trois façons, et les trois atterrissaient
dans le front-matter : « PROVINCE SUD » (libelledirection, brut), « Province Sud »
(libellecollectivite) et « province Sud » (province déduite). Les taxonomies Hugo étant
INSENSIBLES À LA CASSE, elles se replient sur un terme unique dont le libellé affiché
est celui rencontré en premier — c'est-à-dire l'ordre de traitement des pages, qui est
concurrent. Conséquence mesurée le 20/09/2026 : deux constructions du MÊME commit
produisaient 184 fichiers différents, et le libellé de province basculait d'un build à
l'autre, dans le texte du tag comme dans la balise <meta>.

Les valeurs brutes de `libelledirection` ont en plus perdu leurs accents
(« TELECOMMUNICATIONS »). Aucune règle ne les restitue : la table de correspondance vit
dans le moteur (`_CASSE_TAGS` de src/pipeline/main.py) et fait autorité.

REPRISE PONCTUELLE, PAS UNE ÉTAPE DE BUILD
Le moteur normalise désormais à l'écriture, donc toute fiche publiée après le
20/09/2026 est déjà propre. Ce script rattrape les fiches antérieures, UNE FOIS, et le
résultat est commité : le dépôt dit alors la même chose que le site, ce qui ne serait
pas le cas d'une correction appliquée au vol pendant le build.

Usage :
    python3 scripts/normaliser_casse_tags.py [--dry-run]
"""
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
MOTEUR = RACINE.parent / "avps-engine" / "src" / "pipeline"

# Axes de taxonomie du front-matter, tous concernés : `tags` alimente la recherche,
# les autres leurs taxonomies propres (hugo.toml). Normaliser `tags` seul laisserait
# /directions/ en capitales.
CHAMPS = ("tags", "collectivites", "directions", "communes", "provinces", "corps")


def charger_normaliseur():
    """Importe `normaliser_tag` du moteur : une seule table, pas une copie qui dérive."""
    import importlib.util

    chemin = MOTEUR / "main.py"
    if not chemin.exists():
        sys.exit(f"❌ Moteur introuvable : {chemin}\n   Les deux dépôts doivent être côte à côte.")
    sys.path.insert(0, str(MOTEUR))
    import os

    os.environ.setdefault("PROJECT_ID", "avp-engine")
    spec = importlib.util.spec_from_file_location("pipeline_casse", chemin)
    module = importlib.util.module_from_spec(spec)
    sys.modules["pipeline_casse"] = module
    spec.loader.exec_module(module)
    return module.normaliser_tag


def reecrire(texte: str, normaliser) -> tuple[str, int]:
    """Réécrit les seules lignes d'axes. Le reste du fichier n'est pas touché."""
    modifs = 0
    lignes = texte.split("\n")
    for i, ligne in enumerate(lignes):
        m = re.match(r'^(' + "|".join(CHAMPS) + r'): (\[.*\])$', ligne)
        if not m:
            continue
        champ, brut = m.group(1), m.group(2)
        try:
            valeurs = json.loads(brut)
        except json.JSONDecodeError:
            print(f"   ⚠️  {champ} illisible, ligne laissée telle quelle : {brut[:60]}")
            continue
        # `sorted(set(...))` seulement sur `tags`, qui était déjà trié et dédoublonné ;
        # les autres axes gardent leur ordre, l'ordre y a un sens (unique valeur).
        propres = [normaliser(v) for v in valeurs]
        propres = sorted(set(propres)) if champ == "tags" else propres
        neuf = f"{champ}: {json.dumps(propres, ensure_ascii=False)}"
        if neuf != ligne:
            lignes[i] = neuf
            modifs += 1
    return "\n".join(lignes), modifs


def main():
    essai = "--dry-run" in sys.argv
    normaliser = charger_normaliseur()

    fiches = sorted(RACINE.glob("content/*/*.md"))
    touchees = total = 0
    for f in fiches:
        texte = f.read_text(encoding="utf-8")
        neuf, modifs = reecrire(texte, normaliser)
        if modifs:
            touchees += 1
            total += modifs
            if not essai:
                f.write_text(neuf, encoding="utf-8")
    verbe = "seraient modifiées" if essai else "modifiées"
    print(f"✅ {touchees} fiches {verbe} sur {len(fiches)} ({total} lignes d'axes).")


if __name__ == "__main__":
    main()
