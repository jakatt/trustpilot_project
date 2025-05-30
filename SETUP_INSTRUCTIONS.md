# Instructions pour les utilisateurs

## Configuration initiale

1. **Clonez le repository :**
```bash
git clone https://github.com/[votre-username]/[nom-du-repo].git
cd [nom-du-repo]
```

2. **Créez un environnement virtuel :**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Installez les dépendances :**
```bash
pip install -r requirements.txt
```

4. **Configurez votre clé API :**
```bash
cp setvar.env.example setvar.env
# Puis éditez setvar.env avec votre vraie clé API OpenAI
```

## Fichiers de données requis

Vous devez ajouter ces fichiers dans le répertoire racine :

### Pour Reviews_Classification.py :
- `Trust_Pilot_Reviews.xlsx` : Votre fichier Excel avec les avis
  - Doit contenir une colonne 'text' avec les avis à analyser

### Pour explication, reformulation.py :
- `Trustpilot_Dataset.xlsx` : Fichier Excel avec les données d'avis supprimés
- `trustpilot_guidelines.pdf` : PDF des guidelines Trustpilot

**⚠️ Important :** Ces fichiers de données ne sont pas inclus dans le repository pour des raisons de confidentialité.

## Exécution

Une fois la configuration terminée :

```bash
# Pour classifier les avis
python "Reviews_Classification.py"

# Pour analyser les avis supprimés
python "explication, reformulation.py"
```
