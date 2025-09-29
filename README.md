# Steam L&M Injector

Application moderne pour ajouter des jeux à Steam via des manifests et lua. Interface graphique améliorée avec navigateur intégré.


<img width="1920" height="1017" alt="Steam Injector V2" src="https://github.com/user-attachments/assets/cae53ab9-4b00-43af-9172-24a12a522ef6" />


##  Fonctionnalités

- **Interface utilisateur** avec design moderne et couleurs thématiques
- **Détection automatique du chemin Steam** sur Windows
- **Gestion des erreurs** avec messages informatifs
- **Téléchargements en arrière-plan** sans bloquer l'interface
- **Indicateurs visuels** de progression et d'état
- **Vérification des dépendances** au démarrage
- **Nettoyage automatique** des fichiers temporaires
- **Aide intégrée** avec raccourcis clavier

### Navigation et Détection
- Navigateur SteamDB intégré avec moteur web complet
- Détection automatique de l'App ID depuis n'importe quelle URL Steam
- Support des URLs multiples : `/app/`, `/apps/`, paramètres `appid=`
- Surveillance en temps réel des changements d'URL

### Interface et Contrôles  
- Interface graphique moderne avec indicateurs visuels
- Raccourcis clavier intuitifs
  
### Installation et Téléchargement
- Téléchargement et extraction automatiques des fichiers nécessaires
- Installation en arrière-plan sans blocage
- Gestion intelligente des permissions
- Configuration automatique des dossiers Steam
- Nettoyage automatique des fichiers temporaires

## 🔧 Prérequis

- **Python 3.8 ou supérieur**
- **Navigateur web** (Chrome/Chromium recommandé pour l'affichage optimal)
- **Compte Steam** avec installation locale
- **Droits administrateur** (recommandé pour l'écriture dans les dossiers Steam)

### Systèmes Supportés
- ✅ Windows 10/11 (x64) - Version .exe disponible
- 🐍 Windows (Python 3.8+)
- 🐍 Linux (Python 3.8+)
- 🐍 macOS (Python 3.8+)

## 📦 Installation

1. **Clonez ou téléchargez** ce dépôt
   ```bash
   git clone https://github.com/votre-repo/steam-injector.git
   cd steam-injector
   ```

2. **Installez les dépendances Python**
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancez l'application**
   ```bash
   python steam_injector.py
   ```

### Installation avec Environnement Virtuel (Recommandé)
```bash
# Création de l'environnement virtuel
python -m venv steam_injector_env

# Activation (Windows)
steam_injector_env\Scripts\activate
# Activation (Linux/macOS)
source steam_injector_env/bin/activate

# Installation des dépendances
pip install -r requirements.txt

# Lancement
python steam_injector.py
```

## 🚀 Utilisation

### Premier Démarrage
1. **Configuration automatique** : L'application détecte automatiquement Steam
2. **Configuration manuelle** : Si nécessaire, indiquez le chemin d'installation
3. **Navigation** : La fenêtre du navigateur Steam s'ouvre automatiquement

### Utilisation Normale
1. **Naviguez** vers la page du jeu Steam que vous souhaitez ajouter
2. **Détection automatique** : L'App ID s'affiche dès que vous êtes sur la page
3. **Installation** : Appuyez sur `Entrée` ou le bouton A de votre manette
4. **Redémarrage** : Redémarrez Steam pour voir le jeu dans votre bibliothèque

### Chemins Steam par Défaut
- **Windows** : `C:\Program Files (x86)\Steam` ou `C:\Program Files\Steam`
- **Linux** : `~/.steam/steam` ou `~/.local/share/Steam`
- **macOS** : `~/Library/Application Support/Steam`

### Clavier
- **Entrée/Espace** : Ajouter le jeu à Steam
- **Échap** : Quitter l'application
- **F1** : Afficher l'aide détaillée
- **F5** : Actualiser le navigateur web
- **Ctrl+Q** : Quitter rapidement

### Souris
- **Clic sur le bouton** : Ajouter le jeu à Steam
- **Redimensionnement** : Glissez les bordures pour ajuster la taille


### Fichiers Générés
- **config.json** : Sauvegarde le chemin Steam et les préférences
- **temp/** : Dossier temporaire pour les téléchargements (auto-nettoyé)
- **logs/** : Historique des installations (si activé)

### v1.0.0
- Version initiale avec support de l'ajout de jeux via manifests et lua
- Interface utilisateur moderne
- Version .exe pour Windows
- Support Python pour Windows, Linux et macOS

##  Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.


## 🙏 Remerciements

- **SPIN0ZAi** pour le dépôt SB_manifest_DB

