# Politique de Sécurité

## 🔒 Informations Sensibles

### ⚠️ NE JAMAIS COMMITER :

1. **Clés API** :
   - `OPENAI_API_KEY`
   - Toute autre clé d'authentification

2. **Fichiers de données** :
   - `*.xlsx` (contiennent des données d'avis privées)
   - `*.pdf` (guidelines propriétaires)
   - `setvar.env` (contient les clés API)

3. **Données personnelles** :
   - Noms d'utilisateurs
   - Avis complets
   - Informations d'entreprises

### ✅ Bonnes Pratiques :

1. **Utilisez le fichier `.gitignore`** fourni
2. **Vérifiez avant chaque commit** :
   ```bash
   git status
   git diff --cached
   ```
3. **Utilisez `setvar.env.example`** comme modèle
4. **Stockez les clés API localement** uniquement

## 🛡️ Configuration Sécurisée

### Variables d'environnement :
```bash
# Copiez le fichier exemple
cp setvar.env.example setvar.env

# Éditez avec vos vraies valeurs
nano setvar.env
```

### Vérification avant publication :
```bash
# Vérifiez qu'aucun fichier sensible n'est tracké
git ls-files | grep -E '\.(env|xlsx|pdf)$'

# Cette commande ne doit rien retourner !
```

## 🚨 En cas de fuite accidentelle

Si vous avez accidentellement commité des informations sensibles :

1. **Arrêtez immédiatement** de pousser vers le repository distant
2. **Révoque immédiatement** toutes les clés API exposées
3. **Nettoyez l'historique Git** :
   ```bash
   # Pour le dernier commit seulement
   git reset --hard HEAD~1
   
   # Pour un fichier spécifique dans l'historique
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch nom-du-fichier' \
   --prune-empty --tag-name-filter cat -- --all
   ```
4. **Générez de nouvelles clés API**

## 📞 Contact

En cas de problème de sécurité, contactez immédiatement le mainteneur du projet.
