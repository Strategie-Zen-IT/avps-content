#!/usr/bin/env python3
"""Retire les restes du code ROME des fiches déjà publiées.

CONTEXTE
--------
Le code ROME a été **retiré du site le 01/10/2026**, pas corrigé : il était faux
pour 24 familles sur 41 (constaté le 30/09/2026 — « Postes et télécommunications »
pointait sur `I1306`, le code des frigoristes). Un code unique par famille RESPNC
n'a de toute façon pas de sens : une famille regroupe plusieurs métiers.

Le moteur a cessé de l'émettre à cette date, donc **toute fiche publiée depuis est
déjà propre**. Ce script ne sert qu'au rattrapage des fiches antérieures.

CE QU'IL FAIT, ET RIEN D'AUTRE
------------------------------
1. `content/**/*.md` — retire du front-matter le commentaire
   « 💼 Classification ROME officielle » et les clés `code_rome` / `libelle_rome`.
2. `data/avps/*.json` — retire `occupationalCategory` à l'intérieur de
   `relevantOccupation`, qui portait le `CategoryCode` ROME.

⚠️ NE PAS confondre avec `JobPosting.occupationalCategory` à la racine du JSON : ce
champ-là porte les **familles RESPNC** et doit rester. Le script ne touche que celui
imbriqué dans `relevantOccupation`.

IDEMPOTENT
----------
Relançable sans dommage : une fiche déjà propre n'est pas réécrite. C'est ce qui
permet de le passer après un `git pull` sans se demander ce qui a déjà été fait.

    python3 scripts/retirer_code_rome.py [--verifier]

`--verifier` ne modifie rien et sort en code 1 s'il reste du ROME.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent

# Le bloc à retirer dans le front-matter : son commentaire, les deux clés, et la
# ligne vide qui le précédait. On accepte l'absence du commentaire — certaines
# fiches anciennes ne l'ont pas.
_BLOC_ROME = re.compile(
    r"\n?^# 💼 Classification ROME officielle\n"
    r"(?:^code_rome:.*\n)?"
    r"(?:^libelle_rome:.*\n)?",
    re.MULTILINE,
)
_CLES_SEULES = re.compile(r"^(?:code_rome|libelle_rome):.*\n", re.MULTILINE)


def nettoyer_markdown(chemin: pathlib.Path) -> bool:
    """Renvoie True si le fichier a été modifié."""
    texte = chemin.read_text(encoding="utf-8")
    sortie = _CLES_SEULES.sub("", _BLOC_ROME.sub("\n", texte))
    if sortie == texte:
        return False
    chemin.write_text(sortie, encoding="utf-8")
    return True


def nettoyer_json(chemin: pathlib.Path) -> bool:
    """Renvoie True si le fichier a été modifié.

    On relit et réécrit le JSON tel quel (indentation de 2, non-ASCII conservé),
    pour ne pas reformater tout le fichier et produire un diff illisible.
    """
    brut = chemin.read_text(encoding="utf-8")
    donnees = json.loads(brut)
    occupation = donnees.get("relevantOccupation")
    if not isinstance(occupation, dict) or "occupationalCategory" not in occupation:
        return False

    del occupation["occupationalCategory"]
    # Même mise en forme que le moteur : 2 espaces, accents conservés, et le
    # fichier se termine sans saut de ligne comme ce qu'il écrit.
    chemin.write_text(
        json.dumps(donnees, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return True


def parcourir(verifier: bool) -> int:
    restes = []
    modifies_md = modifies_json = 0

    for chemin in sorted((RACINE / "content").rglob("*.md")):
        texte = chemin.read_text(encoding="utf-8")
        if "code_rome" not in texte and "libelle_rome" not in texte:
            continue
        if verifier:
            restes.append(chemin)
        elif nettoyer_markdown(chemin):
            modifies_md += 1

    for chemin in sorted((RACINE / "data" / "avps").glob("*.json")):
        try:
            donnees = json.loads(chemin.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"  ⚠️ {chemin.name} illisible : {e}")
            continue
        occupation = donnees.get("relevantOccupation")
        if not isinstance(occupation, dict) or "occupationalCategory" not in occupation:
            continue
        if verifier:
            restes.append(chemin)
        elif nettoyer_json(chemin):
            modifies_json += 1

    if verifier:
        if restes:
            print(f"✋ {len(restes)} fichiers portent encore du ROME. Exemples :")
            for c in restes[:5]:
                print(f"   {c.relative_to(RACINE)}")
            return 1
        print("✅ Aucun reste de ROME.")
        return 0

    print(f"✅ {modifies_md} fiches Markdown et {modifies_json} JSON nettoyés.")
    return 0


if __name__ == "__main__":
    sys.exit(parcourir("--verifier" in sys.argv))
