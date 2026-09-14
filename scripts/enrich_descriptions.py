"""Complète le champ `description` du front-matter des fiches d'AVP.

Lancé au build (voir .github/workflows/deploy_site.yaml), avant `hugo`. Le champ sert
aux méta-descriptions et aux aperçus de partage : quand le moteur ne l'a pas rempli, on
le reconstruit depuis le corps de la fiche.

⚠️ La version d'origine de ce script portait une liste de 6 dossiers en dur
(« commercial-et-clientele », « telecommunications »…) — des slugs de familles de métiers
qui n'existaient même plus dans le contenu, si bien que le script ne traitait plus
aucun fichier en silence. Ici les dossiers sont les 41 familles RESPNC, découvertes à
l'exécution : on parcourt donc l'arborescence au lieu d'énumérer.
"""
import os
import re

content_dir = "content"

# Dossiers à ne pas parcourir : les archives (fiches closes, figées) et les pages
# éditoriales, qui ont leur propre description rédigée à la main.
DOSSIERS_EXCLUS = {"archives"}

def extract_desc(body, summary):
    # Search for the context / description section in body
    match = re.search(r"## 📝 Description du poste & Contexte\s+(.*?)(?=\n##|$)", body, re.DOTALL)
    if match:
        desc = match.group(1).strip()
        # Remove markdown bold/italics or multiple line breaks
        desc = re.sub(r"\s+", " ", desc)
        if len(desc) > 30:
            return desc
    if summary:
        return summary
    return "Description non disponible."

print("✍️ Enrichissement des descriptions AVP...")

updated_count = 0

categories = sorted(
    d for d in os.listdir(content_dir)
    if os.path.isdir(os.path.join(content_dir, d)) and d not in DOSSIERS_EXCLUS
)
print(f"📂 {len(categories)} famille(s) de métier trouvée(s) dans {content_dir}/")

for category in categories:
    cat_dir = os.path.join(content_dir, category)

    for filename in os.listdir(cat_dir):
        if not filename.endswith(".md") or filename == "_index.md":
            continue
            
        file_path = os.path.join(cat_dir, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue
            
        frontmatter = parts[1]
        body = parts[2]
        
        # Check if description field is already present
        desc_match = re.search(r"^description:\s*", frontmatter, re.MULTILINE)
        if desc_match:
            # Let's check if it has a non-empty value
            val_match = re.search(r"^description:\s*\"?([^\n\"]+)\"?", frontmatter, re.MULTILINE)
            if val_match and len(val_match.group(1).strip()) > 10:
                # Description already exists and is valid
                continue
                
        # Get summary and extract a rich description
        summary_match = re.search(r"^summary:\s*\"?([^\n\"]+)\"?", frontmatter, re.MULTILINE)
        summary = summary_match.group(1).strip() if summary_match else None
        
        desc = extract_desc(body.strip(), summary)
        
        # Escape double quotes for YAML double-quoted string
        escaped_desc = desc.replace('"', '\\"')
        
        # Add description to frontmatter
        # We can clean up existing description line if it was empty/invalid
        if desc_match:
            # Remove existing description line
            frontmatter = re.sub(r"^description:.*?\n", "", frontmatter, flags=re.MULTILINE)
            
        # Append description before the end of frontmatter
        new_frontmatter = frontmatter.rstrip() + f'\ndescription: "{escaped_desc}"\n'
        
        new_content = f"---{new_frontmatter}---{body}"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
            
        print(f"✅ {category}/{filename} : description ajoutée/enrichie")
        updated_count += 1

print(f"🎉 Terminé. {updated_count} fichiers AVP mis à jour avec une description riche.")
