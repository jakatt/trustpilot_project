# Trustpilot Reviews Analysis Tools

Ce projet contient plusieurs outils Python pour analyser et traiter les avis Trustpilot en utilisant l'API OpenAI.

## 📋 Scripts disponibles

### 1. Reviews_Classification.py
Classifie automatiquement les avis Trustpilot en thèmes principaux.

**Fonctionnalités :**
- Lecture d'avis depuis un fichier Excel
- Classification automatique en thèmes avec OpenAI GPT-4
- Consolidation des thèmes similaires
- Export des résultats avec exemples
- Garantit que le total des comptes ≥ nombre d'avis d'entrée

### 2. explication, reformulation.py
Génère des explications et reformulations pour les avis supprimés de Trustpilot.

**Fonctionnalités :**
- Analyse des raisons de suppression d'avis
- Génération d'explications basées sur les guidelines Trustpilot
- Proposition de reformulations conformes aux guidelines
- Extraction automatique du texte des PDF de guidelines

### 3. focus_on_review_flagging.py
Analyse spécialisée pour les avis signalés.

### 4. focus_on_review_removal.py
Analyse spécialisée pour les avis supprimés.

## 🚀 Installation

1. **Clonez le repository**
```bash
git clone https://github.com/[votre-username]/trustpilot-reviews-analysis.git
cd trustpilot-reviews-analysis
```

2. **Créez un environnement virtuel**
```bash
python3 -m venv venv
source venv/bin/activate  # Sur macOS/Linux
# ou
venv\Scripts\activate     # Sur Windows
```

3. **Installez les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurez votre clé API OpenAI**
Créez un fichier `setvar.env` dans le répertoire racine :
```env
OPENAI_API_KEY=votre_clé_api_openai_ici
```

## 📁 Fichiers requis

Placez ces fichiers dans le répertoire racine avant d'exécuter les scripts :

### Pour Reviews_Classification.py :
- `Trust_Pilot_Reviews.xlsx` : Fichier Excel contenant les avis à analyser
  - Doit avoir une colonne 'text' avec les avis

### Pour explication, reformulation.py :
- `Trustpilot_Dataset.xlsx` : Fichier Excel avec les données d'avis supprimés
  - Doit avoir une feuille 'dataset' avec les colonnes :
    - ID, Company Name, User Name, Detailed Review, Reason for Removal, Star Rating, Company Comment
- `trustpilot_guidelines.pdf` : PDF contenant les guidelines officielles Trustpilot

## 🎯 Usage

### Classification des avis
```bash
python "Reviews_Classification.py"
```
**Sortie :** `Trust_Pilot_Review_Analysis_v2.xlsx`

### Explication et reformulation d'avis supprimés
```bash
python "explication, reformulation.py"
```
**Sortie :** `output_trustpilot.xlsx`

### Analyses spécialisées
```bash
python focus_on_review_flagging.py
python focus_on_review_removal.py
```

## ⚙️ Configuration

### Variables d'environnement (setvar.env)
```env
OPENAI_API_KEY=sk-votre_clé_ici
```

### Paramètres modifiables dans Reviews_Classification.py
- `OPENAI_MODEL` : Modèle OpenAI à utiliser (défaut: "gpt-4-1106-preview")
- `MAX_THEMATICS` : Nombre maximum de thèmes dans le résultat final (défaut: 10)
- `COMMENT_COLUMN` : Nom de la colonne contenant les avis (défaut: 'text')

## 📊 Format des fichiers de sortie

### Trust_Pilot_Review_Analysis_v2.xlsx
- **Theme** : Nom du thème identifié
- **Count** : Nombre d'avis classés dans ce thème
- **Example 1-3** : Exemples d'avis pour ce thème
- **TOTAL** : Ligne de total des comptes

### output_trustpilot.xlsx
- Toutes les colonnes d'origine plus :
- **Explication** : Explication de la suppression de l'avis
- **Nouvelle formulation** : Reformulation proposée conforme aux guidelines

## 🔧 Dépendances

```txt
pandas>=1.5.0
openai>=1.0.0
python-dotenv>=0.19.0
tqdm>=4.64.0
PyPDF2>=3.0.0
openpyxl>=3.0.0
```

## 🛡️ Sécurité

- ❌ **Ne commitez jamais** votre clé API OpenAI
- ❌ **Ne commitez jamais** les fichiers de données contenant des informations privées
- ✅ Utilisez le fichier `.gitignore` fourni
- ✅ Stockez les clés API dans `setvar.env` (exclu du versioning)

## 📝 Exemples d'utilisation

### Analyse rapide de 50 avis
```bash
# Assurez-vous d'avoir Trust_Pilot_Reviews_50.xlsx
python "Reviews_Classification.py"
```

### Traitement d'un dataset complet
```bash
# Avec un fichier Trust_Pilot_Reviews.xlsx plus volumineux
python "Reviews_Classification.py"
```

## 🤝 Contribution

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commitez vos changements (`git commit -am 'Ajoute nouvelle fonctionnalité'`)
4. Pushez vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails.

## ⚠️ Avertissements

- L'utilisation de l'API OpenAI peut engendrer des coûts
- Respectez les limites de taux de l'API OpenAI
- Assurez-vous de respecter les conditions d'utilisation de Trustpilot
- Les données d'avis peuvent contenir des informations personnelles - manipulez avec précaution

## 🆘 Support

Si vous rencontrez des problèmes :
1. Vérifiez que votre clé API OpenAI est valide
2. Vérifiez que les fichiers requis sont présents
3. Consultez les logs d'erreur pour plus de détails
4. Ouvrez une issue sur GitHub avec les détails de l'erreur
