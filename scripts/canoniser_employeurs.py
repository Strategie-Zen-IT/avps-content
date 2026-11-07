#!/usr/bin/env python3
"""Un seul libellé par employeur dans les fiches déjà publiées.

POURQUOI
--------
Quand l'open data ne nomme aucun employeur — le cas le plus fréquent pour les communes,
dont `libellecollectivite`, `libelledirection` et `acronymedirection` sont vides — le nom
est lu par le modèle DANS le document. Chaque collectivité écrivant son en-tête à sa
façon, la même entité se retrouve sous plusieurs libellés : autant d'employeurs distincts
pour les taxonomies du site, la carte et le rapport mensuel.

Le moteur canonise désormais à la source (`canoniser_employeur` dans
`avps-engine/src/pipeline/main.py`), donc **toute fiche publiée depuis est déjà propre**.
Ce script ne sert qu'au rattrapage des fiches antérieures.

⚠️ LA TABLE EST LA MÊME DES DEUX CÔTÉS. Elle est recopiée ici depuis le moteur, selon la
convention du dépôt (les Cloud Functions ne partagent pas de paquet commun). Une
divergence ne lèverait aucune erreur : elle laisserait simplement des fiches non
rattrapées. Le script la compare au moteur quand celui-ci est accessible à côté.

CE QU'IL FAIT, ET RIEN D'AUTRE
------------------------------
1. `content/**/*.md` — réécrit les valeurs des clés `collectivite`, `direction`,
   `collectivites`, `directions` et `tags` quand elles figurent dans la table.
2. `data/avps/*.json` — réécrit les mêmes libellés dans le JSON-LD.

Les champs `employeur_sigle` et les chemins de fichiers ne sont PAS touchés : le sigle
sert de clé de regroupement et de nom de logo, et le renommer déplacerait des URL déjà
indexées. Le moteur le recalculera de lui-même à la prochaine republication de l'offre.

IDEMPOTENT
----------
Relançable sans dommage : une fiche déjà propre n'est pas réécrite.

    python3 scripts/canoniser_employeurs.py [--verifier]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
MOTEUR = RACINE.parent / "avps-engine" / "src" / "pipeline" / "main.py"

# ⚠️ RECOPIE de `_LIBELLES_EMPLOYEURS` (avps-engine/src/pipeline/main.py).
# Cette table REGROUPE des entités identiques. Elle ne doit jamais fusionner deux
# personnes morales distinctes : le « Centre d'action communale de Nouméa » est un
# établissement public autonome, et non la Ville de Nouméa.
LIBELLES = {
    # « Kanak » est invariable et s'écrit sans « e ». La graphie « kanake » vient des
    # documents de la collectivité elle-même ; le sigle ADCK le confirme, et la
    # description de ses propres avis écrit correctement « culture kanak ».
    "agence de developpement de la culture kanake":
        "Agence de développement de la culture kanak",
}

# ⚠️ RECOPIE de `COMMUNES_NC`, `_COMMUNES_VILLE` et `_COMMUNES_ARTICLE` (moteur).
# « Ville de », « Mairie de » et « Commune de » désignent la même collectivité : seul le
# nom qui suit compte. « Commune de X » est l'appellation juridique — c'est la commune qui
# recrute, la mairie n'étant que son exécutif. On ne garde « Ville de X » que pour les
# quatre communes qui se nomment ainsi.
COMMUNES = [
    "Bélep", "Boulouparis", "Bourail", "Canala", "Dumbéa", "Farino",
    "Hienghène", "Houaïlou", "Île des Pins", "Kaala-Gomen", "Koné",
    "Kouaoua", "Koumac", "La Foa", "Lifou", "Mont-Dore", "Maré",
    "Moindou", "Nouméa", "Ouégoa", "Ouvéa", "Païta", "Poindimié",
    "Ponérihouen", "Pouébo", "Pouembout", "Poum", "Poya", "Sarraméa",
    "Thio", "Touho", "Voh", "Yaté",
]
COMMUNES_VILLE = {
    "Nouméa": "Ville de Nouméa",
    "Dumbéa": "Ville de Dumbéa",
    "Païta": "Ville de Païta",
    "Mont-Dore": "Ville du Mont-Dore",
}
COMMUNES_ARTICLE = {
    "Ouvéa": "d'",
    "Île des Pins": "de l'",
}

PREFIXE_COMMUNE = re.compile(r"^(?:ville|mairie|commune)\s+(.+)$")
# Essayés TOUS : « La Foa » commence elle-même par un article.
ARTICLES_COMMUNE = ("", "de la ", "de l ", "des ", "du ", "de ", "d ")
# Les clés de front-matter qui portent un nom d'employeur.
CLES_SIMPLES = ("collectivite", "direction")
CLES_LISTES = ("collectivites", "directions", "tags")


def cle_casse(valeur: str) -> str:
    """Même normalisation que `_cle_casse` du moteur : casse, accents, ponctuation."""
    sans = "".join(
        c for c in unicodedata.normalize("NFD", valeur) if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"[^a-z0-9]+", " ", sans.lower()).strip()


INDEX_COMMUNES = {
    **{cle_casse(n): n for n in COMMUNES},
    "le mont dore": "Mont-Dore",
    "l ile des pins": "Île des Pins",
    "iles belep": "Bélep",
}


def libelle_commune(commune: str) -> str:
    if commune in COMMUNES_VILLE:
        return COMMUNES_VILLE[commune]
    return f"Commune {COMMUNES_ARTICLE.get(commune, 'de ')}{commune}"


def canoniser(nom: str) -> str:
    cle = cle_casse(nom)
    if cle in LIBELLES:
        return LIBELLES[cle]
    # ⚠️ Le motif exige un PRÉFIXE : « Centre d'action communale de Nouméa » ne matche
    # pas, et c'est voulu — le CCAS est un établissement public autonome, pas la Ville.
    trouve = PREFIXE_COMMUNE.match(cle)
    if trouve:
        reste = trouve.group(1)
        for article in ARTICLES_COMMUNE:
            if not reste.startswith(article):
                continue
            commune = INDEX_COMMUNES.get(cle_casse(reste[len(article):]))
            if commune:
                return libelle_commune(commune)
    return nom


# Les lettres qui peuvent porter un accent dans le texte réel, alors que la clé de la
# table est désaccentuée.
_VARIANTES = {"a": "aàâä", "e": "eéèêë", "i": "iîï", "o": "oôö", "u": "uùûü", "c": "cç"}


def motif_tolerant(cle: str) -> re.Pattern:
    """Reconnaît un libellé DANS une phrase, quels que soient ses accents et sa casse.

    Le libellé n'apparaît pas que dans les clés du front-matter : il est aussi recopié
    en toutes lettres dans `summary` (« …, basé à Nouméa (Agence de développement de la
    culture kanake). »). Sans ce motif, la clé serait corrigée et la phrase, non.

    Construit depuis la clé désaccentuée : chaque lettre accentuable devient une classe,
    et les espaces acceptent tiret et apostrophe, comme `cle_casse` les y ramène.
    """
    morceaux = []
    for c in cle:
        if c == " ":
            morceaux.append(r"[\s\-']+")
        elif c in _VARIANTES:
            morceaux.append(f"[{_VARIANTES[c]}]")
        else:
            morceaux.append(re.escape(c))
    return re.compile("".join(morceaux), re.IGNORECASE)


MOTIFS = [(motif_tolerant(cle), propre) for cle, propre in LIBELLES.items()]


def canoniser_texte(texte: str) -> str:
    """Réécrit les libellés rencontrés en toutes lettres dans un texte libre."""
    for motif, propre in MOTIFS:
        texte = motif.sub(propre, texte)
    return texte


def verifier_table_du_moteur() -> None:
    """Alerte si la copie a divergé de la table du moteur, quand il est à côté."""
    if not MOTEUR.exists():
        return
    source = MOTEUR.read_text(encoding="utf-8")
    debut = source.index("_LIBELLES_EMPLOYEURS = {")
    # Borné à l'accolade fermante de CETTE table : le bloc allait jusqu'à
    # `canoniser_employeur` et captait au passage `_COMMUNES_ARTICLE`, d'où une
    # divergence annoncée à tort.
    bloc = source[debut:source.index("\n}", debut)]
    attendues = set(re.findall(r'"([^"]+)":\s*\n?\s*"([^"]+)"', bloc))
    ici = set(LIBELLES.items())
    if attendues and attendues != ici:
        print("⚠️ La table diverge de celle du moteur :", file=sys.stderr)
        for e in sorted(attendues - ici):
            print(f"     manque ici : {e}", file=sys.stderr)
        for e in sorted(ici - attendues):
            print(f"     en trop ici : {e}", file=sys.stderr)


def traiter_markdown(chemin: Path) -> bool:
    texte = chemin.read_text(encoding="utf-8")
    original = texte

    for cle in CLES_SIMPLES:
        def _remplacer(m, cle=cle):
            return f'{cle}: "{canoniser(m.group(1))}"'
        texte = re.sub(rf'^{cle}:\s*"([^"]*)"', _remplacer, texte, flags=re.MULTILINE)

    for cle in CLES_LISTES:
        def _liste(m, cle=cle):
            valeurs = re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))
            # Le YAML échappe les guillemets internes : on canonise la valeur DÉSÉCHAPPÉE
            # puis on la ré-échappe, sinon les noms entre guillemets seraient corrompus.
            propres = [canoniser(v.replace('\\"', '"')).replace('"', '\\"') for v in valeurs]
            # Dédoublonnage : deux graphies regroupées ne doivent pas laisser deux entrées.
            uniques = list(dict.fromkeys(propres))
            return f'{cle}: [' + ", ".join(f'"{v}"' for v in uniques) + "]"
        texte = re.sub(rf'^{cle}:\s*\[([^\]]*)\]', _liste, texte, flags=re.MULTILINE)

    # Le libellé se retrouve aussi en toutes lettres dans `summary` et dans le corps.
    texte = canoniser_texte(texte)

    if texte != original:
        chemin.write_text(texte, encoding="utf-8")
        return True
    return False


def traiter_json(chemin: Path) -> bool:
    brut = chemin.read_text(encoding="utf-8")
    try:
        data = json.loads(brut)
    except json.JSONDecodeError:
        print(f"⚠️ JSON illisible, ignoré : {chemin}", file=sys.stderr)
        return False

    change = False

    def parcourir(noeud):
        nonlocal change
        if isinstance(noeud, dict):
            for cle, valeur in noeud.items():
                if isinstance(valeur, str):
                    propre = canoniser(valeur) if cle in ("collectivite", "direction", "name") \
                        else canoniser_texte(valeur)
                    if propre != valeur:
                        noeud[cle] = propre
                        change = True
                else:
                    parcourir(valeur)
        elif isinstance(noeud, list):
            for i, v in enumerate(noeud):
                if isinstance(v, str):
                    propre = canoniser(canoniser_texte(v))
                    if propre != v:
                        noeud[i] = propre
                        change = True
                else:
                    parcourir(v)

    parcourir(data)
    if change:
        chemin.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return change


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--verifier", action="store_true",
                        help="N'écrit rien ; sort en 1 s'il reste un libellé à corriger.")
    args = parser.parse_args()

    verifier_table_du_moteur()

    md = sorted((RACINE / "content").rglob("*.md"))
    js = sorted((RACINE / "data" / "avps").glob("*.json"))

    if args.verifier:
        restants = []
        for f in [*md, *js]:
            texte = f.read_text(encoding="utf-8")
            if any(motif.search(texte) for motif, _ in MOTIFS):
                restants.append(f)
        print(f"🔎 {len(restants)} fichier(s) portent encore un libellé à corriger.")
        for f in restants[:20]:
            print(f"   {f.relative_to(RACINE)}")
        return 1 if restants else 0

    n_md = sum(traiter_markdown(f) for f in md)
    n_js = sum(traiter_json(f) for f in js)
    print(f"✅ {n_md} fiche(s) et {n_js} JSON mis à jour "
          f"(sur {len(md)} fiches et {len(js)} JSON examinés).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
