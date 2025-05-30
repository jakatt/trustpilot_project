# Guide de Contribution

Merci de votre intérêt pour contribuer à ce projet ! 🎉

## 🚀 Comment Contribuer

### 1. Fork et Clone
```bash
# Forkez le projet sur GitHub, puis :
git clone https://github.com/VOTRE-USERNAME/trustpilot-reviews-analysis.git
cd trustpilot-reviews-analysis
```

### 2. Configuration de l'environnement
```bash
# Créez un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installez les dépendances
pip install -r requirements.txt

# Configurez les variables d'environnement
cp setvar.env.example setvar.env
# Ajoutez votre clé API OpenAI dans setvar.env
```

### 3. Créez une branche
```bash
git checkout -b feature/ma-nouvelle-fonctionnalite
# ou
git checkout -b fix/correction-bug
```

### 4. Développez
- Écrivez du code propre et commenté
- Suivez les conventions Python (PEP 8)
- Testez vos modifications

### 5. Commit et Push
```bash
git add .
git commit -m "feat: ajoute nouvelle fonctionnalité X"
git push origin feature/ma-nouvelle-fonctionnalite
```

### 6. Pull Request
Ouvrez une Pull Request avec :
- Description claire des changements
- Tests effectués
- Captures d'écran si applicable

## 📋 Types de Contributions

### 🐛 Corrections de bugs
- Documentez le problème
- Proposez une solution
- Testez la correction

### ✨ Nouvelles fonctionnalités
- Discutez d'abord dans une issue
- Respectez l'architecture existante
- Ajoutez de la documentation

### 📚 Documentation
- Améliorez les README
- Ajoutez des exemples
- Corrigez les typos

### 🔧 Améliorations techniques
- Optimisations de performance
- Meilleure gestion d'erreurs
- Refactoring de code

## 📝 Conventions

### Messages de commit
Utilisez le format conventionnel :
```
type(scope): description

feat: ajoute classification par sentiment
fix: corrige bug de parsing PDF
docs: met à jour README
style: formatage du code
refactor: simplifie fonction de consolidation
test: ajoute tests pour classifier_reviews
```

### Style de code
- Utilisez Black pour le formatage : `black .`
- Respectez PEP 8
- Commentez le code complexe
- Noms de variables explicites

### Tests
```bash
# Testez vos changements
python "Reviews_Classification.py"
python "explication, reformulation.py"
```

## 🛡️ Sécurité

**IMPORTANT** : Ne commitez jamais :
- Clés API (`OPENAI_API_KEY`)
- Fichiers de données (`.xlsx`, `.pdf`)
- Variables d'environnement (`.env`)

Vérifiez avant chaque commit :
```bash
git status
git diff --cached
```

## 🎯 Priorités

### High Priority
- [ ] Amélioration gestion d'erreurs API
- [ ] Support pour d'autres modèles OpenAI
- [ ] Tests unitaires
- [ ] Optimisation des coûts API

### Medium Priority
- [ ] Interface graphique simple
- [ ] Export en formats multiples
- [ ] Analyse de sentiment
- [ ] Détection de langue

### Low Priority
- [ ] Intégration avec d'autres plateformes
- [ ] API REST
- [ ] Dashboard web

## 🤝 Code de Conduite

- Soyez respectueux et inclusif
- Aidez les nouveaux contributeurs
- Acceptez les critiques constructives
- Focalisez sur ce qui est mieux pour le projet

## 📞 Questions ?

- Ouvrez une issue pour les questions techniques
- Contactez les mainteneurs pour les questions générales
- Lisez d'abord la documentation existante

Merci pour votre contribution ! 🙏
