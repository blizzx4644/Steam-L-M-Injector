import os
import sys
import json
import requests
import zipfile
import shutil
import threading
import time
import re
import subprocess
import psutil
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from PyQt6.QtCore import QUrl, QTimer, Qt, QThread, pyqtSignal, QSize
from PyQt6.QtWidgets import (QApplication, QVBoxLayout, QWidget, QMainWindow,
                           QMessageBox, QInputDialog, QProgressBar, QLabel,
                           QHBoxLayout, QPushButton, QStatusBar, QSplitter)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor, QKeySequence, QShortcut

try:
    import win32api
    import win32con
    import win32gui
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

class SteamRestartThread(QThread):
    """Thread pour redémarrer Steam sans bloquer l'interface"""
    status_update = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, steam_path):
        super().__init__()
        self.steam_path = steam_path

    def run(self):
        try:
            self.status_update.emit("Fermeture de Steam...")

            # Méthode plus fiable pour fermer Steam
            steam_closed = self.close_steam()

            if not steam_closed:
                self.status_update.emit("Forçage de la fermeture de Steam...")
                self.force_close_steam()

            # Attendre que Steam se ferme complètement
            self.status_update.emit("Attente de la fermeture complète...")
            time.sleep(3)

            # Vérifier que Steam est bien fermé
            if self.is_steam_running():
                self.status_update.emit("Nettoyage des processus Steam restants...")
                self.force_close_steam()
                time.sleep(2)

            self.status_update.emit("Redémarrage de Steam...")

            # Redémarrer Steam avec différentes méthodes selon l'OS
            success = self.start_steam()

            if success:
                # Vérifier que Steam a bien démarré
                time.sleep(5)
                if self.is_steam_running():
                    self.finished.emit(True, "Steam redémarré avec succès")
                else:
                    self.finished.emit(False, "Steam fermé mais le redémarrage a échoué")
            else:
                self.finished.emit(False, "Impossible de redémarrer Steam")

        except Exception as e:
            self.finished.emit(False, f"Erreur lors du redémarrage: {str(e)}")

    def close_steam(self):
        """Ferme Steam proprement"""
        try:
            if os.name == 'nt':  # Windows
                # Essayer d'abord avec la commande Steam
                steam_exe = os.path.join(self.steam_path, 'steam.exe')
                if os.path.exists(steam_exe):
                    subprocess.run([steam_exe, '-shutdown'], timeout=10)
                    time.sleep(2)
                    return not self.is_steam_running()
            else:  # Linux/macOS
                # Utiliser pkill ou killall
                try:
                    subprocess.run(['pkill', '-f', 'steam'], timeout=5)
                except FileNotFoundError:
                    subprocess.run(['killall', 'steam'], timeout=5)
                time.sleep(2)
                return not self.is_steam_running()
        except Exception as e:
            print(f"Erreur fermeture propre: {e}")

        return False

    def force_close_steam(self):
        """Force la fermeture de tous les processus Steam"""
        try:
            steam_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info.get('name', '').lower()
                    proc_exe = proc_info.get('exe', '').lower()

                    # Identifier les processus Steam
                    if (proc_name and ('steam' in proc_name or 'steamwebhelper' in proc_name)) or \
                       (proc_exe and 'steam' in proc_exe):
                        steam_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

            # Terminer les processus
            for proc in steam_processes:
                try:
                    proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Attendre et forcer si nécessaire
            time.sleep(3)
            for proc in steam_processes:
                try:
                    if proc.is_running():
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        except Exception as e:
            print(f"Erreur fermeture forcée: {e}")

    def start_steam(self):
        """Démarre Steam selon l'OS"""
        try:
            if os.name == 'nt':  # Windows
                steam_exe = os.path.join(self.steam_path, 'steam.exe')
                if os.path.exists(steam_exe):
                    # Utiliser shell=True et détacher le processus
                    subprocess.Popen(f'"{steam_exe}"',
                                   shell=True,
                                   creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
                    return True
                else:
                    # Essayer le raccourci Steam
                    try:
                        subprocess.Popen(['steam://'], shell=True)
                        return True
                    except:
                        return False

            else:  # Linux/macOS
                # Essayer différents chemins
                steam_paths = [
                    os.path.join(self.steam_path, 'steam'),
                    '/usr/bin/steam',
                    '/usr/local/bin/steam',
                    '/opt/steam/steam',
                    '/usr/games/steam'
                ]

                for steam_exe in steam_paths:
                    if os.path.exists(steam_exe):
                        subprocess.Popen([steam_exe],
                                       start_new_session=True,
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL)
                        return True

                # Essayer via le système
                try:
                    subprocess.Popen(['steam'],
                                   start_new_session=True,
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
                    return True
                except FileNotFoundError:
                    return False

        except Exception as e:
            print(f"Erreur démarrage Steam: {e}")
            return False

        return False

    def is_steam_running(self):
        """Vérifie si Steam est en cours d'exécution"""
        try:
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'] and 'steam' in proc.info['name'].lower():
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except:
            return False

class DownloadThread(QThread):
    """Thread pour gérer les téléchargements sans bloquer l'interface"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    progress_percent = pyqtSignal(int)

    def __init__(self, app_id, steam_injector):
        super().__init__()
        self.app_id = app_id
        self.steam_injector = steam_injector

    def run(self):
        try:
            self.progress.emit(f"Téléchargement pour l'App ID: {self.app_id}")
            self.progress_percent.emit(10)

            # Création des dossiers nécessaires
            os.makedirs('temp', exist_ok=True)
            os.makedirs(self.steam_injector.depotcache_path, exist_ok=True)
            os.makedirs(self.steam_injector.plugins_path, exist_ok=True)

            # Construction de l'URL de téléchargement avec fallbacks
            urls_to_try = [
                f"https://codeload.github.com/SPIN0ZAi/SB_manifest_DB/zip/refs/heads/{self.app_id}",
                f"https://github.com/SPIN0ZAi/SB_manifest_DB/archive/refs/heads/{self.app_id}.zip",
                f"https://api.github.com/repos/SPIN0ZAi/SB_manifest_DB/zipball/{self.app_id}"
            ]

            zip_path = os.path.join('temp', f'{self.app_id}.zip')
            download_success = False

            self.progress_percent.emit(20)

            # Essayer différentes URLs
            for i, url in enumerate(urls_to_try):
                try:
                    self.progress.emit(f"Tentative de téléchargement {i+1}/3...")
                    response = requests.get(url, stream=True, timeout=30)
                    response.raise_for_status()

                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0

                    with open(zip_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total_size > 0:
                                    progress = 20 + int((downloaded / total_size) * 40)
                                    self.progress_percent.emit(progress)

                    # Vérifier que le fichier a été téléchargé
                    if os.path.exists(zip_path) and os.path.getsize(zip_path) > 0:
                        download_success = True
                        break

                except requests.RequestException as e:
                    print(f"Échec téléchargement URL {i+1}: {e}")
                    continue

            if not download_success:
                raise Exception(f"Impossible de télécharger les fichiers pour l'App ID {self.app_id}. Le jeu n'est peut-être pas disponible dans la base de données.")

            self.progress.emit("Extraction des fichiers...")
            self.progress_percent.emit(70)

            # Extraction du ZIP avec gestion d'erreurs améliorée
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall('temp')
            except zipfile.BadZipFile:
                raise Exception("Archive corrompue - le jeu n'est peut-être pas disponible")

            # Recherche du dossier extrait avec patterns multiples
            extracted_dir = None
            possible_patterns = [
                f'SB_manifest_DB-{self.app_id}',
                f'SPIN0ZAi-SB_manifest_DB-{self.app_id}',
                f'SB_manifest_DB-main-{self.app_id}',
                self.app_id
            ]

            for item in os.listdir('temp'):
                item_path = os.path.join('temp', item)
                if os.path.isdir(item_path):
                    # Vérifier si le nom correspond à un des patterns
                    for pattern in possible_patterns:
                        if pattern in item or item.endswith(self.app_id):
                            extracted_dir = item_path
                            break
                    if extracted_dir:
                        break

            # Si pas trouvé par pattern, prendre le premier dossier
            if not extracted_dir:
                for item in os.listdir('temp'):
                    item_path = os.path.join('temp', item)
                    if os.path.isdir(item_path) and item != '__pycache__':
                        extracted_dir = item_path
                        break

            if not extracted_dir:
                raise Exception("Dossier extrait non trouvé - structure d'archive inattendue")

            self.progress.emit("Installation des fichiers...")
            self.progress_percent.emit(80)

            # Copie des fichiers vers les dossiers appropriés
            files_copied = 0
            total_files = 0

            # Parcourir récursivement tous les fichiers
            for root, dirs, files in os.walk(extracted_dir):
                for file in files:
                    src_path = os.path.join(root, file)
                    total_files += 1

                    if file.endswith('.manifest'):
                        dst_path = os.path.join(self.steam_injector.depotcache_path, file)
                        try:
                            shutil.copy2(src_path, dst_path)
                            files_copied += 1
                        except Exception as e:
                            print(f"Erreur copie manifest {file}: {e}")

                    elif file.endswith('.lua') or file.endswith('.vdf'):
                        dst_path = os.path.join(self.steam_injector.plugins_path, file)
                        try:
                            shutil.copy2(src_path, dst_path)
                            files_copied += 1
                        except Exception as e:
                            print(f"Erreur copie plugin {file}: {e}")

                    elif file.endswith('.acf'):
                        # Fichiers ACF vont dans steamapps
                        steamapps_path = os.path.join(self.steam_injector.steam_path, 'steamapps')
                        if os.path.exists(steamapps_path):
                            dst_path = os.path.join(steamapps_path, file)
                            try:
                                shutil.copy2(src_path, dst_path)
                                files_copied += 1
                            except Exception as e:
                                print(f"Erreur copie ACF {file}: {e}")

            self.progress_percent.emit(90)

            # Nettoyage des fichiers temporaires
            try:
                shutil.rmtree('temp')
            except Exception as e:
                print(f"Avertissement: Impossible de nettoyer le dossier temp: {e}")

            if files_copied == 0:
                if total_files == 0:
                    raise Exception(f"Aucun fichier trouvé dans l'archive pour l'App ID {self.app_id}. Ce jeu n'est peut-être pas supporté.")
                else:
                    raise Exception(f"Aucun fichier Steam valide trouvé ({total_files} fichiers examinés). Types de fichiers supportés: .manifest, .lua, .vdf, .acf")

            self.progress_percent.emit(100)
            self.finished.emit(True, f"Installation réussie! {files_copied} fichier(s) installé(s) sur {total_files} examiné(s)")

        except requests.RequestException as e:
            self.finished.emit(False, f"Erreur de téléchargement: {str(e)}")
        except zipfile.BadZipFile:
            self.finished.emit(False, f"Archive corrompue pour l'App ID {self.app_id}. Le jeu n'existe peut-être pas dans la base de données.")
        except Exception as e:
            self.finished.emit(False, f"Erreur: {str(e)}")

class WebView(QWebEngineView):
    """Navigateur web intégré avec paramètres optimisés"""

    url_changed_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_settings()
        self.urlChanged.connect(self.on_url_changed)

    def setup_settings(self):
        """Configure les paramètres du navigateur web"""
        settings = self.settings()

        # Paramètres de base
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadIconsForPage, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ErrorPageEnabled, True)

        # Paramètres de sécurité
        settings.setAttribute(QWebEngineSettings.WebAttribute.XSSAuditingEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)

        # Paramètres de performance
        settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)

    def on_url_changed(self, url):
        """Émet le signal quand l'URL change"""
        self.url_changed_signal.emit(url.toString())

class SteamPathDialog:
    """Dialogue pour la configuration du chemin Steam"""

    @staticmethod
    def get_steam_path(parent=None):
        """Demande à l'utilisateur le chemin d'installation de Steam"""
        default_paths = [
            r"C:\Program Files (x86)\Steam",
            r"C:\Program Files\Steam",
            r"D:\Steam",
            os.path.expanduser("~/.steam/steam"),  # Linux
            os.path.expanduser("~/Library/Application Support/Steam")  # macOS
        ]

        # Recherche automatique du chemin Steam
        detected_path = None
        for path in default_paths:
            if os.path.exists(path):
                steam_exe = 'steam.exe' if os.name == 'nt' else 'steam'
                if os.path.exists(os.path.join(path, steam_exe)):
                    detected_path = path
                    break

        if detected_path:
            reply = QMessageBox.question(
                parent,
                'Chemin Steam détecté',
                f'Steam détecté dans: {detected_path}\n\nUtiliser ce chemin?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                return detected_path

        # Demande manuelle du chemin
        path, ok = QInputDialog.getText(
            parent,
            'Chemin d\'installation Steam',
            'Veuillez entrer le chemin d\'installation de Steam:',
            text=detected_path or default_paths[0]
        )

        if ok and path:
            if not os.path.exists(path):
                QMessageBox.warning(parent, 'Erreur', 'Le chemin spécifié n\'existe pas!')
                return None
            return path

        return None

class SteamInjectorWindow(QMainWindow):
    """Fenêtre principale de l'application Steam Injector"""

    def __init__(self):
        super().__init__()

        # Configuration de base
        self.steam_path = ""
        self.depotcache_path = ""
        self.plugins_path = ""
        self.config_file = "config.json"
        self.current_url = "https://steamdb.info"
        self.app_id = ""
        self.download_in_progress = False

        self.setWindowTitle("Steam Injector v2.0")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # Application du thème sombre
        self.apply_dark_theme()

        # Configuration de l'interface
        self.setup_ui()

        # Chargement de la configuration
        self.load_config()

        # Configuration des raccourcis clavier
        self.setup_shortcuts()

        # Timer pour vérifier les mises à jour
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.check_status_reset)
        self.update_timer.start(100)  # Vérification toutes les 100ms

    def apply_dark_theme(self):
        """Applique un thème sombre à l'application"""
        palette = QPalette()

        # Couleurs sombres
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))

        self.setPalette(palette)

    def setup_ui(self):
        """Configure l'interface utilisateur"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Barre d'outils supérieure
        self.setup_toolbar(main_layout)

        # Splitter pour diviser l'écran
        splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(splitter)

        # Navigateur web (partie supérieure)
        self.browser = WebView()
        self.browser.setUrl(QUrl(self.current_url))
        self.browser.url_changed_signal.connect(self.on_url_changed)
        splitter.addWidget(self.browser)

        # Panneau de contrôle (partie inférieure)
        control_panel = self.setup_control_panel()
        splitter.addWidget(control_panel)

        # Proportions du splitter (80% navigateur, 20% contrôles)
        splitter.setSizes([800, 200])

        # Barre de statut
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Prêt - Naviguez vers une page de jeu Steam")

    def setup_toolbar(self, parent_layout):
        """Configure la barre d'outils supérieure"""
        toolbar_layout = QHBoxLayout()

        # Bouton de navigation arrière
        self.back_button = QPushButton("← Retour")
        self.back_button.clicked.connect(lambda: self.browser.back())
        self.back_button.setMaximumWidth(100)
        toolbar_layout.addWidget(self.back_button)

        # Bouton de navigation avant
        self.forward_button = QPushButton("Avant →")
        self.forward_button.clicked.connect(lambda: self.browser.forward())
        self.forward_button.setMaximumWidth(100)
        toolbar_layout.addWidget(self.forward_button)

        # Bouton d'actualisation
        self.refresh_button = QPushButton("🔄 Actualiser")
        self.refresh_button.clicked.connect(lambda: self.browser.reload())
        self.refresh_button.setMaximumWidth(120)
        toolbar_layout.addWidget(self.refresh_button)

        # Bouton Home
        self.home_button = QPushButton("🏠 Accueil Steam")
        self.home_button.clicked.connect(self.go_home)
        self.home_button.setMaximumWidth(150)
        toolbar_layout.addWidget(self.home_button)

        # Espace flexible
        toolbar_layout.addStretch()

        # Bouton de redémarrage Steam
        self.restart_steam_button = QPushButton("🔄 Redémarrer Steam")
        self.restart_steam_button.clicked.connect(self.restart_steam)
        self.restart_steam_button.setMaximumWidth(150)
        self.restart_steam_button.setStyleSheet("""
            QPushButton {
                background-color: #ff6b35;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #e55a2b;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
            }
        """)
        toolbar_layout.addWidget(self.restart_steam_button)

        # Bouton de configuration Steam
        self.config_button = QPushButton("⚙️ Configuration")
        self.config_button.clicked.connect(self.configure_steam_path)
        self.config_button.setMaximumWidth(150)
        toolbar_layout.addWidget(self.config_button)

        parent_layout.addLayout(toolbar_layout)

    def setup_control_panel(self):
        """Configure le panneau de contrôle inférieur"""
        control_widget = QWidget()
        control_widget.setMaximumHeight(200)
        control_widget.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                border-top: 2px solid #0078d4;
                border-radius: 5px;
            }
        """)

        layout = QVBoxLayout(control_widget)
        layout.setContentsMargins(15, 15, 15, 15)

        # Titre
        title_label = QLabel("Steam Injector v2.0")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff; border: none;")
        layout.addWidget(title_label)

        # Layout horizontal pour les informations
        info_layout = QHBoxLayout()

        # Colonne gauche - Informations
        left_layout = QVBoxLayout()

        self.url_label = QLabel("URL: Chargement...")
        self.url_label.setStyleSheet("color: #cccccc; border: none;")
        left_layout.addWidget(self.url_label)

        self.app_id_label = QLabel("App ID: Non détecté")
        self.app_id_label.setStyleSheet("color: #ffcc00; border: none;")
        left_layout.addWidget(self.app_id_label)

        self.steam_path_label = QLabel("Steam: Non configuré")
        self.steam_path_label.setStyleSheet("color: #cccccc; border: none;")
        left_layout.addWidget(self.steam_path_label)

        info_layout.addLayout(left_layout)

        # Colonne droite - Contrôles
        right_layout = QVBoxLayout()

        # Bouton principal d'ajout
        self.add_button = QPushButton("Ajouter à Steam")
        self.add_button.setMinimumHeight(50)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
            }
        """)
        self.add_button.clicked.connect(self.add_to_steam)
        self.add_button.setEnabled(False)
        right_layout.addWidget(self.add_button)

        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #666666;
                border-radius: 5px;
                text-align: center;
                background-color: #2b2b2b;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """)
        right_layout.addWidget(self.progress_bar)

        info_layout.addLayout(right_layout)
        layout.addLayout(info_layout)

        # Instructions
        instructions_label = QLabel(
            "Instructions: Naviguez vers un jeu Steam → App ID détecté automatiquement → "
            "Cliquez 'Ajouter à Steam' → Redémarrez Steam"
        )
        instructions_label.setStyleSheet("color: #aaaaaa; font-size: 11px; border: none;")
        instructions_label.setWordWrap(True)
        layout.addWidget(instructions_label)

        return control_widget

    def setup_shortcuts(self):
        """Configure les raccourcis clavier"""
        # Raccourci pour ajouter à Steam
        add_shortcut = QShortcut(QKeySequence("Return"), self)
        add_shortcut.activated.connect(self.add_to_steam)

        space_shortcut = QShortcut(QKeySequence("Space"), self)
        space_shortcut.activated.connect(self.add_to_steam)

        # Raccourci pour redémarrer Steam
        restart_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        restart_shortcut.activated.connect(self.restart_steam)

        # Raccourci pour actualiser
        refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(lambda: self.browser.reload())

        # Raccourci pour aide
        help_shortcut = QShortcut(QKeySequence("F1"), self)
        help_shortcut.activated.connect(self.show_help)

        # Raccourci pour quitter
        quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        quit_shortcut.activated.connect(self.close)

    def go_home(self):
        """Retourne à la page d'accueil Steam"""
        self.browser.setUrl(QUrl("https://steamdb.info"))

    def restart_steam(self):
        """Redémarre Steam silencieusement"""
        if not self.steam_path:
            self.status_bar.showMessage("Configuration Steam requise pour redémarrer", 3000)
            return

        # Vérifier si un téléchargement est en cours
        if self.download_in_progress:
            self.status_bar.showMessage("Impossible de redémarrer Steam pendant un téléchargement", 3000)
            return

        # Désactiver le bouton pendant le redémarrage
        self.restart_steam_button.setEnabled(False)
        self.restart_steam_button.setText("Redémarrage...")

        # Démarrer le thread de redémarrage
        self.restart_thread = SteamRestartThread(self.steam_path)
        self.restart_thread.status_update.connect(self.update_restart_status)
        self.restart_thread.finished.connect(self.restart_finished)
        self.restart_thread.start()

    def update_restart_status(self, message):
        """Met à jour le statut pendant le redémarrage"""
        self.status_bar.showMessage(message)

    def restart_finished(self, success, message):
        """Appelé quand le redémarrage est terminé"""
        self.restart_steam_button.setEnabled(True)
        self.restart_steam_button.setText("🔄 Redémarrer Steam")

        if success:
            self.status_bar.showMessage(message, 5000)
        else:
            self.status_bar.showMessage(f"Erreur: {message}", 5000)

    def configure_steam_path(self):
        """Ouvre le dialogue de configuration du chemin Steam"""
        new_path = SteamPathDialog.get_steam_path(self)
        if new_path:
            self.steam_path = new_path
            self.setup_steam_paths()
            self.save_config()
            self.update_steam_label()
            self.status_bar.showMessage("Configuration Steam mise à jour", 3000)

    def load_config(self):
        """Charge la configuration depuis le fichier JSON"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.steam_path = config.get('steam_path', '')

                    if self.steam_path and os.path.exists(self.steam_path):
                        self.setup_steam_paths()
                    else:
                        self.ask_steam_path()
            else:
                self.ask_steam_path()
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration: {e}")
            self.ask_steam_path()

        self.update_steam_label()

    def ask_steam_path(self):
        """Demande le chemin Steam au premier démarrage"""
        QTimer.singleShot(1000, self.configure_steam_path)

    def setup_steam_paths(self):
        """Configure les chemins Steam basés sur le chemin principal"""
        if not self.steam_path:
            return

        self.depotcache_path = os.path.join(self.steam_path, 'depotcache')
        self.plugins_path = os.path.join(self.steam_path, 'config', 'stplug-in')

        # Créer aussi le dossier steamapps si nécessaire
        self.steamapps_path = os.path.join(self.steam_path, 'steamapps')

        # Création des dossiers s'ils n'existent pas
        try:
            os.makedirs(self.depotcache_path, exist_ok=True)
            os.makedirs(self.plugins_path, exist_ok=True)
            os.makedirs(self.steamapps_path, exist_ok=True)
            print(f"Dossiers Steam configurés:")
            print(f"  - Depotcache: {self.depotcache_path}")
            print(f"  - Plugins: {self.plugins_path}")
            print(f"  - Steamapps: {self.steamapps_path}")
        except PermissionError:
            QMessageBox.warning(self, "Permissions",
                              "Permissions insuffisantes pour créer les dossiers Steam.\n"
                              "Lancez l'application en tant qu'administrateur.")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors de la création des dossiers: {e}")

    def save_config(self):
        """Sauvegarde la configuration dans le fichier JSON"""
        try:
            config = {
                'steam_path': self.steam_path,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration: {e}")

    def update_steam_label(self):
        """Met à jour l'affichage du chemin Steam"""
        if self.steam_path:
            steam_display = f"Steam: {os.path.basename(self.steam_path)}"
            self.steam_path_label.setStyleSheet("color: #00ff00; border: none;")
        else:
            steam_display = "Steam: Non configuré"
            self.steam_path_label.setStyleSheet("color: #ff6666; border: none;")

        self.steam_path_label.setText(steam_display)

    def on_url_changed(self, url):
        """Appelé quand l'URL du navigateur change"""
        self.current_url = url

        # Mise à jour de l'affichage de l'URL
        display_url = url
        if len(display_url) > 80:
            display_url = display_url[:80] + "..."
        self.url_label.setText(f"URL: {display_url}")

        # Extraction de l'App ID
        new_app_id = self.extract_app_id_from_url(url)

        if new_app_id and new_app_id != self.app_id:
            self.app_id = new_app_id
            self.app_id_label.setText(f"App ID: {self.app_id} ✓")
            self.app_id_label.setStyleSheet("color: #00ff00; border: none;")
            self.add_button.setEnabled(bool(self.steam_path and not self.download_in_progress))
            self.status_bar.showMessage(f"Jeu détecté: App ID {self.app_id}")
        elif not new_app_id and self.app_id:
            self.app_id = ""
            self.app_id_label.setText("App ID: Non détecté")
            self.app_id_label.setStyleSheet("color: #ffcc00; border: none;")
            self.add_button.setEnabled(False)
            self.status_bar.showMessage("Naviguez vers une page de jeu Steam")

    def extract_app_id_from_url(self, url):
        """Extrait l'App ID depuis une URL Steam"""
        try:
            patterns = [
                r'/app/(\d+)',
                r'[?&]appid=(\d+)',
                r'/apps/(\d+)',
            ]

            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)

            return None
        except Exception as e:
            print(f"Erreur lors de l'extraction de l'App ID: {e}")
            return None

    def add_to_steam(self):
        """Lance le processus d'ajout d'un jeu à Steam"""
        if not self.app_id:
            QMessageBox.warning(self, "Erreur", "Aucun App ID détecté.\nNaviguez vers une page de jeu Steam.")
            return

        if self.download_in_progress:
            return

        if not self.steam_path:
            reply = QMessageBox.question(self, "Configuration requise",
                                       "Le chemin Steam n'est pas configuré.\nVoulez-vous le configurer maintenant?")
            if reply == QMessageBox.StandardButton.Yes:
                self.configure_steam_path()
            return

        # Confirmation avant téléchargement
        reply = QMessageBox.question(self, "Confirmation",
                                   f"Ajouter le jeu avec l'App ID {self.app_id} à Steam?\n\n"
                                   f"Le jeu sera téléchargé depuis GitHub et installé dans:\n"
                                   f"• Manifests: {self.depotcache_path}\n"
                                   f"• Plugins: {self.plugins_path}")

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Démarrage du téléchargement
        self.download_in_progress = True
        self.add_button.setEnabled(False)
        self.add_button.setText("Téléchargement en cours...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.download_thread = DownloadThread(self.app_id, self)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.progress_percent.connect(self.progress_bar.setValue)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.start()

        self.status_bar.showMessage(f"Téléchargement de l'App ID {self.app_id} en cours...")

    def update_progress(self, message):
        """Met à jour le message de progression"""
        self.status_bar.showMessage(message)

    def download_finished(self, success, message):
        """Appelé quand le téléchargement est terminé"""
        self.download_in_progress = False
        self.progress_bar.setVisible(False)
        self.add_button.setText("Ajouter à Steam")
        self.add_button.setEnabled(bool(self.app_id and self.steam_path))

        if success:
            self.status_bar.showMessage("Installation terminée avec succès! Vous pouvez maintenant redémarrer Steam.", 8000)

            # Activer le bouton de redémarrage Steam après installation réussie
            self.restart_steam_button.setStyleSheet("""
                QPushButton {
                    background-color: #00ff00;
                    color: black;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #00cc00;
                }
            """)
        else:
            self.status_bar.showMessage("Erreur lors de l'installation", 5000)

    def check_status_reset(self):
        """Vérifie s'il faut réinitialiser le statut"""
        # Cette méthode est appelée périodiquement pour maintenir l'interface à jour
        pass

    def show_help(self):
        """Affiche la fenêtre d'aide"""
        help_text = """
<h3>Steam Injector v2.0 - Aide</h3>

<h4>Utilisation:</h4>
<ul>
<li><b>Naviguer:</b> Utilisez le navigateur intégré pour aller sur une page de jeu Steam</li>
<li><b>Détecter:</b> L'App ID est détecté automatiquement depuis l'URL</li>
<li><b>Installer:</b> Cliquez sur "Ajouter à Steam" ou appuyez sur Entrée</li>
<li><b>Redémarrer:</b> Redémarrez Steam pour voir le jeu dans votre bibliothèque</li>
</ul>

<h4>Raccourcis clavier:</h4>
<ul>
<li><b>Entrée/Espace:</b> Ajouter à Steam</li>
<li><b>Ctrl+R:</b> Redémarrer Steam</li>
<li><b>F5:</b> Actualiser le navigateur</li>
<li><b>F1:</b> Afficher cette aide</li>
<li><b>Ctrl+Q:</b> Quitter l'application</li>
</ul>

<h4>Boutons de navigation:</h4>
<ul>
<li><b>← Retour / Avant →:</b> Navigation dans l'historique</li>
<li><b>🔄 Actualiser:</b> Recharger la page actuelle</li>
<li><b>🏠 Accueil Steam:</b> Retourner au Steam Store</li>
<li><b>🔄 Redémarrer Steam:</b> Fermer et relancer Steam automatiquement</li>
<li><b>⚙️ Configuration:</b> Configurer le chemin Steam</li>
</ul>

<h4>Dépannage:</h4>
<ul>
<li><b>App ID non détecté:</b> Assurez-vous d'être sur une page de jeu Steam valide</li>
<li><b>Erreur de téléchargement:</b> Vérifiez votre connexion Internet</li>
<li><b>Permissions:</b> Lancez en tant qu'administrateur si nécessaire</li>
<li><b>Jeu non visible:</b> Redémarrez complètement Steam</li>
</ul>

<p><b>Note:</b> Cette application télécharge les fichiers depuis GitHub et les installe dans vos dossiers Steam. Assurez-vous que Steam est fermé pendant l'installation.</p>
        """

        msg = QMessageBox(self)
        msg.setWindowTitle("Aide - Steam Injector")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(help_text)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.resize(600, 500)
        msg.exec()

    def closeEvent(self, event):
        """Gère la fermeture de l'application"""
        if self.download_in_progress:
            reply = QMessageBox.question(self, 'Fermeture',
                                       'Un téléchargement est en cours.\nVoulez-vous vraiment quitter?',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return

        # Sauvegarde de la configuration avant fermeture
        self.save_config()

        # Arrêt du thread de redémarrage s'il est actif
        if hasattr(self, 'restart_thread') and self.restart_thread.isRunning():
            self.restart_thread.quit()
            self.restart_thread.wait(2000)

        # Arrêt du thread de téléchargement s'il est actif
        if hasattr(self, 'download_thread') and self.download_thread.isRunning():
            self.download_thread.quit()
            self.download_thread.wait(2000)

        event.accept()


def check_dependencies():
    """Vérifie que toutes les dépendances sont installées"""
    missing_deps = []

    try:
        import requests
    except ImportError:
        missing_deps.append("requests")

    try:
        import psutil
    except ImportError:
        missing_deps.append("psutil")

    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtWebEngineWidgets import QWebEngineView
    except ImportError:
        missing_deps.append("PyQt6 et PyQt6-WebEngine")

    if missing_deps:
        print("❌ Dépendances manquantes:")
        for dep in missing_deps:
            print(f"   • {dep}")
        print("\n💡 Installez les dépendances avec:")
        print("   pip install -r requirements.txt")
        return False

    return True


def check_permissions():
    """Vérifie les permissions d'écriture"""
    if os.name == 'nt':  # Windows
        try:
            import ctypes
            if ctypes.windll.shell32.IsUserAnAdmin():
                print("✅ Droits administrateur détectés")
                return True
            else:
                print("⚠️  Avertissement: Droits administrateur recommandés")
                print("   L'application pourrait ne pas pouvoir écrire dans les dossiers Steam")
                return False
        except:
            print("⚠️  Impossible de vérifier les permissions")
            return False
    else:
        # Linux/macOS - vérification basique
        try:
            test_file = os.path.expanduser("~/test_write_permissions")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            return True
        except:
            print("⚠️  Permissions d'écriture limitées détectées")
            return False


def main():
    """Point d'entrée principal de l'application"""
    try:
        print("🚀 Steam Injector v2.0")
        print("=" * 50)

        print("🔍 Vérification des dépendances...")
        if not check_dependencies():
            input("\n❌ Appuyez sur Entrée pour quitter...")
            return 1

        print("✅ Toutes les dépendances sont installées")

        print("🔐 Vérification des permissions...")
        check_permissions()

        print("🎯 Initialisation de l'application...")

        # Création de l'application Qt
        app = QApplication(sys.argv)
        app.setApplicationName("Steam Injector")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("Steam Injector")

        # Style global pour l'application
        app.setStyle('Fusion')  # Style moderne

        # Création et affichage de la fenêtre principale
        window = SteamInjectorWindow()
        window.show()

        print("✅ Application prête!")
        print("\n💡 Conseils d'utilisation:")
        print("   • Naviguez vers une page de jeu Steam")
        print("   • L'App ID sera détecté automatiquement")
        print("   • Cliquez 'Ajouter à Steam' ou appuyez sur Entrée")
        print("   • Redémarrez Steam pour voir le jeu")
        print("   • Appuyez F1 pour plus d'aide")
        print("-" * 50)

        # Lancement de la boucle d'événements
        return app.exec()

    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l'utilisateur")
        return 0
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("💡 Installez les dépendances avec: pip install -r requirements.txt")
        input("Appuyez sur Entrée pour quitter...")
        return 1
    except Exception as e:
        print(f"💥 Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        input("Appuyez sur Entrée pour quitter...")
        return 1


if __name__ == "__main__":
    sys.exit(main())