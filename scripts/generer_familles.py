#!/usr/bin/env python3
"""Régénère data/familles_couleurs.yml et data/familles_rome.yml.

Source de vérité : le référentiel RESPNC versionné dans le moteur
(`avps-engine/src/pipeline/ref/famille-code-rome.csv`). Les deux dépôts partagent ce
référentiel — c'est lui qui définit à la fois l'arborescence du site
(`content/{famille}/`) et l'énumération qui contraint l'extraction Gemini. Le
régénérer ici évite de recopier 41 libellés à la main, ce qui était précisément le
point faible de la chaîne d'origine (un enum de directions recopié dans 4 specs).

Usage :
    python3 scripts/generer_familles.py [chemin/vers/famille-code-rome.csv]
"""
import csv
import pathlib
import sys

DEFAUT_CSV = "../avps-engine/src/pipeline/ref/famille-code-rome.csv"

# Une couleur par domaine ROME. Doit rester alignée avec COULEURS_DOMAINE_ROME de
# avps-engine/src/pipeline/schema.py, qui s'en sert pour la palette des bannières.
COULEURS = {
    "A": "#4C8C4A",  # Agriculture, mer, espaces verts
    "E": "#7A5195",  # Imprimerie
    "G": "#EF7B45",  # Restauration collective / hôtellerie
    "H": "#B54A6B",  # Laboratoire
    "I": "#1F6F8B",  # Infrastructures, transports, télécoms, aviation
    "J": "#009CAB",  # Santé
    "K": "#3D5A80",  # Services à la population et à la collectivité
    "M": "#C8963E",  # Support (finances, RH, SI, fiscalité)
}
DEFAUT = "#6B7280"

ENTETE = """# ⚙️ FICHIER GÉNÉRÉ — ne pas éditer à la main.
#
# Source : avps-engine/src/pipeline/ref/famille-code-rome.csv (référentiel RESPNC,
# 41 familles de métiers de la fonction publique calédonienne).
# Régénérer avec : python3 scripts/generer_familles.py
#
"""

SORTIES = (
    (
        "data/familles_couleurs.yml",
        "# Une couleur par DOMAINE ROME (1re lettre du code), et non par famille : 41 couleurs\n"
        "# ne se distinguent pas à l'œil, les 8 domaines du référentiel si.\n"
        "# ⚠️ PALETTE PROVISOIRE — à remplacer par la charte d'avps.nc. Les mêmes valeurs sont\n"
        "# dans avps-engine/src/pipeline/schema.py (palette des bannières) : garder alignées.\n",
        lambda rome: COULEURS.get(rome[:1], DEFAUT),
    ),
    (
        "data/familles_rome.yml",
        "# Code ROME de rattachement de chaque famille. Trois codes sont partagés par deux\n"
        "# familles (K1201, K1402, K2501) : c'est normal, la famille est la clé, pas le ROME.\n",
        lambda rome: rome,
    ),
)


def main() -> int:
    chemin = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else DEFAUT_CSV)
    if not chemin.exists():
        print(f"❌ Référentiel introuvable : {chemin}", file=sys.stderr)
        print("   Passez son chemin en argument si le moteur n'est pas dans le dossier voisin.", file=sys.stderr)
        return 1

    with open(chemin, encoding="utf-8-sig") as fh:
        familles = sorted(
            (ligne["id_famille"].strip(), ligne["code_rome"].strip())
            for ligne in csv.DictReader(fh)
            if ligne.get("id_famille")
        )

    if not familles:
        print(f"❌ Aucune famille lue dans {chemin}", file=sys.stderr)
        return 1

    for fichier, commentaire, valeur in SORTIES:
        lignes = [ENTETE + commentaire, "familles:"]
        lignes += [f'  "{famille}": "{valeur(rome)}"' for famille, rome in familles]
        pathlib.Path(fichier).write_text("\n".join(lignes) + "\n", encoding="utf-8")
        print(f"✅ {fichier} — {len(familles)} familles")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
