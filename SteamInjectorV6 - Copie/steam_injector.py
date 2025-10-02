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
                           QHBoxLayout, QPushButton, QStatusBar, QSplitter, QComboBox)
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

# ========== SYSTÈME DE TRADUCTIONS ==========
TRANSLATIONS = {
    'fr': {
        'app_title': 'Steam Injector v2.0',
        'back': '← Retour',
        'forward': 'Avant →',
        'refresh': '🔄 Actualiser',
        'home': '🏠 Accueil Steam',
        'restart_steam': '🔄 Redémarrer Steam',
        'config': '⚙️ Configuration',
        'add_to_steam': 'Ajouter à Steam',
        'downloading': 'Téléchargement en cours...',
        'url_label': 'URL: {}',
        'app_id_detected': 'App ID: {} ✓',
        'app_id_not_detected': 'App ID: Non détecté',
        'steam_configured': 'Steam: {}',
        'steam_not_configured': 'Steam: Non configuré',
        'ready_status': 'Prêt - Naviguez vers une page de jeu Steam',
        'instructions': 'Instructions: Naviguez vers un jeu Steam → App ID détecté automatiquement → Cliquez \'Ajouter à Steam\' → Redémarrez Steam',
        'closing_steam': 'Fermeture de Steam...',
        'restarting_steam': 'Redémarrage de Steam...',
        'steam_restarted': 'Steam redémarré avec succès',
        'error_restart': 'Erreur lors du redémarrage: {}',
        'config_required': 'Configuration Steam requise pour redémarrer',
        'cannot_restart_download': 'Impossible de redémarrer Steam pendant un téléchargement',
        'steam_path_detected': 'Steam détecté dans: {}\n\nUtiliser ce chemin?',
        'steam_path_title': 'Chemin Steam détecté',
        'steam_path_input': 'Chemin d\'installation Steam',
        'steam_path_prompt': 'Veuillez entrer le chemin d\'installation de Steam:',
        'error_path': 'Le chemin spécifié n\'existe pas!',
        'error_title': 'Erreur',
        'config_updated': 'Configuration Steam mise à jour',
        'no_app_id': 'Aucun App ID détecté.\nNaviguez vers une page de jeu Steam.',
        'config_required_question': 'Le chemin Steam n\'est pas configuré.\nVoulez-vous le configurer maintenant?',
        'confirmation': 'Confirmation',
        'add_game_confirm': 'Ajouter le jeu avec l\'App ID {} à Steam?\n\nLe jeu sera téléchargé depuis GitHub et installé dans:\n• Manifests: {}\n• Plugins: {}',
        'downloading_app': 'Téléchargement de l\'App ID {} en cours...',
        'install_success': 'Installation terminée avec succès! Vous pouvez maintenant redémarrer Steam.',
        'install_error': 'Erreur lors de l\'installation',
        'game_detected': 'Jeu détecté: App ID {}',
        'navigate_to_game': 'Naviguez vers une page de jeu Steam',
        'help_title': 'Aide - Steam Injector',
        'close_confirmation': 'Un téléchargement est en cours.\nVoulez-vous vraiment quitter?',
        'close_title': 'Fermeture',
        'language': '🌐 Langue',
    },
    'en': {
        'app_title': 'Steam Injector v2.0',
        'back': '← Back',
        'forward': 'Forward →',
        'refresh': '🔄 Refresh',
        'home': '🏠 Steam Home',
        'restart_steam': '🔄 Restart Steam',
        'config': '⚙️ Settings',
        'add_to_steam': 'Add to Steam',
        'downloading': 'Downloading...',
        'url_label': 'URL: {}',
        'app_id_detected': 'App ID: {} ✓',
        'app_id_not_detected': 'App ID: Not detected',
        'steam_configured': 'Steam: {}',
        'steam_not_configured': 'Steam: Not configured',
        'ready_status': 'Ready - Navigate to a Steam game page',
        'instructions': 'Instructions: Navigate to a Steam game → App ID automatically detected → Click \'Add to Steam\' → Restart Steam',
        'closing_steam': 'Closing Steam...',
        'restarting_steam': 'Restarting Steam...',
        'steam_restarted': 'Steam restarted successfully',
        'error_restart': 'Restart error: {}',
        'config_required': 'Steam configuration required to restart',
        'cannot_restart_download': 'Cannot restart Steam during download',
        'steam_path_detected': 'Steam detected at: {}\n\nUse this path?',
        'steam_path_title': 'Steam Path Detected',
        'steam_path_input': 'Steam Installation Path',
        'steam_path_prompt': 'Please enter the Steam installation path:',
        'error_path': 'The specified path does not exist!',
        'error_title': 'Error',
        'config_updated': 'Steam configuration updated',
        'no_app_id': 'No App ID detected.\nNavigate to a Steam game page.',
        'config_required_question': 'Steam path is not configured.\nWould you like to configure it now?',
        'confirmation': 'Confirmation',
        'add_game_confirm': 'Add game with App ID {} to Steam?\n\nThe game will be downloaded from GitHub and installed in:\n• Manifests: {}\n• Plugins: {}',
        'downloading_app': 'Downloading App ID {}...',
        'install_success': 'Installation completed successfully! You can now restart Steam.',
        'install_error': 'Installation error',
        'game_detected': 'Game detected: App ID {}',
        'navigate_to_game': 'Navigate to a Steam game page',
        'help_title': 'Help - Steam Injector',
        'close_confirmation': 'A download is in progress.\nDo you really want to quit?',
        'close_title': 'Closing',
        'language': '🌐 Language',
    },
    'es': {
        'app_title': 'Steam Injector v2.0',
        'back': '← Atrás',
        'forward': 'Adelante →',
        'refresh': '🔄 Actualizar',
        'home': '🏠 Inicio Steam',
        'restart_steam': '🔄 Reiniciar Steam',
        'config': '⚙️ Configuración',
        'add_to_steam': 'Agregar a Steam',
        'downloading': 'Descargando...',
        'url_label': 'URL: {}',
        'app_id_detected': 'App ID: {} ✓',
        'app_id_not_detected': 'App ID: No detectado',
        'steam_configured': 'Steam: {}',
        'steam_not_configured': 'Steam: No configurado',
        'ready_status': 'Listo - Navega a una página de juego de Steam',
        'instructions': 'Instrucciones: Navega a un juego de Steam → App ID detectado automáticamente → Clic en \'Agregar a Steam\' → Reinicia Steam',
        'closing_steam': 'Cerrando Steam...',
        'restarting_steam': 'Reiniciando Steam...',
        'steam_restarted': 'Steam reiniciado con éxito',
        'error_restart': 'Error al reiniciar: {}',
        'config_required': 'Configuración de Steam requerida para reiniciar',
        'cannot_restart_download': 'No se puede reiniciar Steam durante una descarga',
        'steam_path_detected': 'Steam detectado en: {}\n\n¿Usar esta ruta?',
        'steam_path_title': 'Ruta de Steam Detectada',
        'steam_path_input': 'Ruta de Instalación de Steam',
        'steam_path_prompt': 'Por favor ingrese la ruta de instalación de Steam:',
        'error_path': '¡La ruta especificada no existe!',
        'error_title': 'Error',
        'config_updated': 'Configuración de Steam actualizada',
        'no_app_id': 'Ningún App ID detectado.\nNavega a una página de juego de Steam.',
        'config_required_question': 'La ruta de Steam no está configurada.\n¿Desea configurarla ahora?',
        'confirmation': 'Confirmación',
        'add_game_confirm': '¿Agregar juego con App ID {} a Steam?\n\nEl juego se descargará desde GitHub e instalará en:\n• Manifests: {}\n• Plugins: {}',
        'downloading_app': 'Descargando App ID {}...',
        'install_success': '¡Instalación completada con éxito! Ahora puedes reiniciar Steam.',
        'install_error': 'Error de instalación',
        'game_detected': 'Juego detectado: App ID {}',
        'navigate_to_game': 'Navega a una página de juego de Steam',
        'help_title': 'Ayuda - Steam Injector',
        'close_confirmation': 'Una descarga está en progreso.\n¿Realmente desea salir?',
        'close_title': 'Cerrando',
        'language': '🌐 Idioma',
    },
    'de': {
        'app_title': 'Steam Injector v2.0',
        'back': '← Zurück',
        'forward': 'Vorwärts →',
        'refresh': '🔄 Aktualisieren',
        'home': '🏠 Steam Startseite',
        'restart_steam': '🔄 Steam Neustarten',
        'config': '⚙️ Einstellungen',
        'add_to_steam': 'Zu Steam Hinzufügen',
        'downloading': 'Wird heruntergeladen...',
        'url_label': 'URL: {}',
        'app_id_detected': 'App ID: {} ✓',
        'app_id_not_detected': 'App ID: Nicht erkannt',
        'steam_configured': 'Steam: {}',
        'steam_not_configured': 'Steam: Nicht konfiguriert',
        'ready_status': 'Bereit - Navigieren Sie zu einer Steam-Spieleseite',
        'instructions': 'Anleitung: Zu einem Steam-Spiel navigieren → App ID automatisch erkannt → \'Zu Steam Hinzufügen\' klicken → Steam Neustarten',
        'closing_steam': 'Steam wird geschlossen...',
        'restarting_steam': 'Steam wird neugestartet...',
        'steam_restarted': 'Steam erfolgreich neugestartet',
        'error_restart': 'Neustart-Fehler: {}',
        'config_required': 'Steam-Konfiguration erforderlich zum Neustarten',
        'cannot_restart_download': 'Steam kann während eines Downloads nicht neugestartet werden',
        'steam_path_detected': 'Steam erkannt in: {}\n\nDiesen Pfad verwenden?',
        'steam_path_title': 'Steam-Pfad Erkannt',
        'steam_path_input': 'Steam-Installationspfad',
        'steam_path_prompt': 'Bitte geben Sie den Steam-Installationspfad ein:',
        'error_path': 'Der angegebene Pfad existiert nicht!',
        'error_title': 'Fehler',
        'config_updated': 'Steam-Konfiguration aktualisiert',
        'no_app_id': 'Keine App ID erkannt.\nNavigieren Sie zu einer Steam-Spieleseite.',
        'config_required_question': 'Steam-Pfad ist nicht konfiguriert.\nMöchten Sie ihn jetzt konfigurieren?',
        'confirmation': 'Bestätigung',
        'add_game_confirm': 'Spiel mit App ID {} zu Steam hinzufügen?\n\nDas Spiel wird von GitHub heruntergeladen und installiert in:\n• Manifests: {}\n• Plugins: {}',
        'downloading_app': 'App ID {} wird heruntergeladen...',
        'install_success': 'Installation erfolgreich abgeschlossen! Sie können jetzt Steam neustarten.',
        'install_error': 'Installationsfehler',
        'game_detected': 'Spiel erkannt: App ID {}',
        'navigate_to_game': 'Navigieren Sie zu einer Steam-Spieleseite',
        'help_title': 'Hilfe - Steam Injector',
        'close_confirmation': 'Ein Download ist im Gange.\nMöchten Sie wirklich beenden?',
        'close_title': 'Schließen',
        'language': '🌐 Sprache',
    },
}

class SteamRestartThread(QThread):
    """Thread pour redémarrer Steam sans bloquer l'interface"""
    status_update = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, steam_path):
        super().__init__()
        self.steam_path = steam_path

    def run(self):
        try:
            self.status_update.emit("Closing Steam...")
            steam_closed = self.close_steam()

            if not steam_closed:
                self.status_update.emit("Forcing Steam closure...")
                self.force_close_steam()

            self.status_update.emit("Waiting for complete closure...")
            time.sleep(3)

            if self.is_steam_running():
                self.status_update.emit("Cleaning remaining Steam processes...")
                self.force_close_steam()
                time.sleep(2)

            self.status_update.emit("Restarting Steam...")
            success = self.start_steam()

            if success:
                time.sleep(5)
                if self.is_steam_running():
                    self.finished.emit(True, "Steam restarted successfully")
                else:
                    self.finished.emit(False, "Steam closed but restart failed")
            else:
                self.finished.emit(False, "Unable to restart Steam")

        except Exception as e:
            self.finished.emit(False, f"Restart error: {str(e)}")

    def close_steam(self):
        try:
            if os.name == 'nt':
                steam_exe = os.path.join(self.steam_path, 'steam.exe')
                if os.path.exists(steam_exe):
                    subprocess.run([steam_exe, '-shutdown'], timeout=10)
                    time.sleep(2)
                    return not self.is_steam_running()
            else:
                try:
                    subprocess.run(['pkill', '-f', 'steam'], timeout=5)
                except FileNotFoundError:
                    subprocess.run(['killall', 'steam'], timeout=5)
                time.sleep(2)
                return not self.is_steam_running()
        except Exception as e:
            print(f"Clean close error: {e}")
        return False

    def force_close_steam(self):
        try:
            steam_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info.get('name', '').lower()
                    proc_exe = proc_info.get('exe', '').lower()

                    if (proc_name and ('steam' in proc_name or 'steamwebhelper' in proc_name)) or \
                       (proc_exe and 'steam' in proc_exe):
                        steam_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

            for proc in steam_processes:
                try:
                    proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            time.sleep(3)
            for proc in steam_processes:
                try:
                    if proc.is_running():
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        except Exception as e:
            print(f"Force close error: {e}")

    def start_steam(self):
        try:
            if os.name == 'nt':
                steam_exe = os.path.join(self.steam_path, 'steam.exe')
                if os.path.exists(steam_exe):
                    subprocess.Popen(f'"{steam_exe}"',
                                   shell=True,
                                   creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
                    return True
                else:
                    try:
                        subprocess.Popen(['steam://'], shell=True)
                        return True
                    except:
                        return False
            else:
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

                try:
                    subprocess.Popen(['steam'],
                                   start_new_session=True,
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
                    return True
                except FileNotFoundError:
                    return False

        except Exception as e:
            print(f"Steam start error: {e}")
            return False
        return False

    def is_steam_running(self):
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
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    progress_percent = pyqtSignal(int)

    def __init__(self, app_id, steam_injector):
        super().__init__()
        self.app_id = app_id
        self.steam_injector = steam_injector

    def run(self):
        try:
            self.progress.emit(f"Downloading for App ID: {self.app_id}")
            self.progress_percent.emit(10)

            os.makedirs('temp', exist_ok=True)
            os.makedirs(self.steam_injector.depotcache_path, exist_ok=True)
            os.makedirs(self.steam_injector.plugins_path, exist_ok=True)

            urls_to_try = [
                f"https://codeload.github.com/SPIN0ZAi/SB_manifest_DB/zip/refs/heads/{self.app_id}",
                f"https://github.com/SPIN0ZAi/SB_manifest_DB/archive/refs/heads/{self.app_id}.zip",
                f"https://api.github.com/repos/SPIN0ZAi/SB_manifest_DB/zipball/{self.app_id}"
            ]

            zip_path = os.path.join('temp', f'{self.app_id}.zip')
            download_success = False

            self.progress_percent.emit(20)

            for i, url in enumerate(urls_to_try):
                try:
                    self.progress.emit(f"Download attempt {i+1}/3...")
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

                    if os.path.exists(zip_path) and os.path.getsize(zip_path) > 0:
                        download_success = True
                        break

                except requests.RequestException as e:
                    print(f"Download failed URL {i+1}: {e}")
                    continue

            if not download_success:
                raise Exception(f"Unable to download files for App ID {self.app_id}. The game may not be available in the database.")

            self.progress.emit("Extracting files...")
            self.progress_percent.emit(70)

            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall('temp')
            except zipfile.BadZipFile:
                raise Exception("Corrupted archive - game may not be available")

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
                    for pattern in possible_patterns:
                        if pattern in item or item.endswith(self.app_id):
                            extracted_dir = item_path
                            break
                    if extracted_dir:
                        break

            if not extracted_dir:
                for item in os.listdir('temp'):
                    item_path = os.path.join('temp', item)
                    if os.path.isdir(item_path) and item != '__pycache__':
                        extracted_dir = item_path
                        break

            if not extracted_dir:
                raise Exception("Extracted folder not found - unexpected archive structure")

            self.progress.emit("Installing files...")
            self.progress_percent.emit(80)

            files_copied = 0
            total_files = 0

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
                            print(f"Error copying manifest {file}: {e}")

                    elif file.endswith('.lua') or file.endswith('.vdf'):
                        dst_path = os.path.join(self.steam_injector.plugins_path, file)
                        try:
                            shutil.copy2(src_path, dst_path)
                            files_copied += 1
                        except Exception as e:
                            print(f"Error copying plugin {file}: {e}")

                    elif file.endswith('.acf'):
                        steamapps_path = os.path.join(self.steam_injector.steam_path, 'steamapps')
                        if os.path.exists(steamapps_path):
                            dst_path = os.path.join(steamapps_path, file)
                            try:
                                shutil.copy2(src_path, dst_path)
                                files_copied += 1
                            except Exception as e:
                                print(f"Error copying ACF {file}: {e}")

            self.progress_percent.emit(90)

            try:
                shutil.rmtree('temp')
            except Exception as e:
                print(f"Warning: Cannot clean temp folder: {e}")

            if files_copied == 0:
                if total_files == 0:
                    raise Exception(f"No files found in archive for App ID {self.app_id}. This game may not be supported.")
                else:
                    raise Exception(f"No valid Steam files found ({total_files} files examined). Supported file types: .manifest, .lua, .vdf, .acf")

            self.progress_percent.emit(100)
            self.finished.emit(True, f"Installation successful! {files_copied} file(s) installed from {total_files} examined")

        except requests.RequestException as e:
            self.finished.emit(False, f"Download error: {str(e)}")
        except zipfile.BadZipFile:
            self.finished.emit(False, f"Corrupted archive for App ID {self.app_id}. The game may not exist in the database.")
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")

class WebView(QWebEngineView):
    url_changed_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_settings()
        self.urlChanged.connect(self.on_url_changed)

    def setup_settings(self):
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadIconsForPage, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ErrorPageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.XSSAuditingEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)

    def on_url_changed(self, url):
        self.url_changed_signal.emit(url.toString())

class SteamPathDialog:
    @staticmethod
    def get_steam_path(parent=None, lang='en'):
        t = TRANSLATIONS[lang]
        default_paths = [
            r"C:\Program Files (x86)\Steam",
            r"C:\Program Files\Steam",
            r"D:\Steam",
            os.path.expanduser("~/.steam/steam"),
            os.path.expanduser("~/Library/Application Support/Steam")
        ]

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
                t['steam_path_title'],
                t['steam_path_detected'].format(detected_path),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                return detected_path

        path, ok = QInputDialog.getText(
            parent,
            t['steam_path_input'],
            t['steam_path_prompt'],
            text=detected_path or default_paths[0]
        )

        if ok and path:
            if not os.path.exists(path):
                QMessageBox.warning(parent, t['error_title'], t['error_path'])
                return None
            return path

        return None

class SteamInjectorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.steam_path = ""
        self.depotcache_path = ""
        self.plugins_path = ""
        self.config_file = "config.json"
        self.current_url = "https://steamdb.info"
        self.app_id = ""
        self.download_in_progress = False
        self.current_language = 'en'  # Langue par défaut
        self.available_sites = {
            'SteamDB': 'https://steamdb.info',
            'Steam Store': 'https://store.steampowered.com'
        }

        self.setWindowTitle(self.t('app_title'))
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        self.apply_dark_theme()
        self.setup_ui()
        self.load_config()
        self.setup_shortcuts()

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.check_status_reset)
        self.update_timer.start(100)

    def t(self, key):
        """Fonction helper pour obtenir une traduction"""
        return TRANSLATIONS[self.current_language].get(key, key)

    def change_language(self, lang_code):
        """Change la langue de l'interface"""
        if lang_code in TRANSLATIONS:
            self.current_language = lang_code
            self.save_config()
            self.update_ui_texts()

    def update_ui_texts(self):
        """Met à jour tous les textes de l'interface"""
        self.setWindowTitle(self.t('app_title'))
        self.back_button.setText(self.t('back'))
        self.forward_button.setText(self.t('forward'))
        self.refresh_button.setText(self.t('refresh'))
        self.home_button.setText(self.t('home'))
        self.restart_steam_button.setText(self.t('restart_steam'))
        self.config_button.setText(self.t('config'))

        if not self.download_in_progress:
            self.add_button.setText(self.t('add_to_steam'))

        self.update_steam_label()

        if self.app_id:
            self.app_id_label.setText(self.t('app_id_detected').format(self.app_id))
        else:
            self.app_id_label.setText(self.t('app_id_not_detected'))

        if not self.download_in_progress:
            self.status_bar.showMessage(self.t('ready_status'))
            
        # Mettre à jour le texte des instructions
        if hasattr(self, 'instructions_label'):
            self.instructions_label.setText(self.t('instructions'))

    def apply_dark_theme(self):
        palette = QPalette()
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
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        self.setup_toolbar(main_layout)

        splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(splitter)

        self.browser = WebView()
        self.browser.setUrl(QUrl(self.current_url))
        self.browser.url_changed_signal.connect(self.on_url_changed)
        splitter.addWidget(self.browser)

        control_panel = self.setup_control_panel()
        splitter.addWidget(control_panel)

        splitter.setSizes([800, 200])

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(self.t('ready_status'))

    def setup_toolbar(self, parent_layout):
        toolbar_layout = QHBoxLayout()

        # Site selection dropdown
        self.site_combobox = QComboBox()
        for site_name in self.available_sites:
            self.site_combobox.addItem(site_name)
        self.site_combobox.currentTextChanged.connect(self.on_site_changed)
        toolbar_layout.addWidget(self.site_combobox)

        self.back_button = QPushButton(self.t('back'))
        self.back_button.clicked.connect(lambda: self.browser.back())
        self.back_button.setMaximumWidth(100)
        toolbar_layout.addWidget(self.back_button)

        self.forward_button = QPushButton(self.t('forward'))
        self.forward_button.clicked.connect(lambda: self.browser.forward())
        self.forward_button.setMaximumWidth(100)
        toolbar_layout.addWidget(self.forward_button)

        self.refresh_button = QPushButton(self.t('refresh'))
        self.refresh_button.clicked.connect(lambda: self.browser.reload())
        self.refresh_button.setMaximumWidth(120)
        toolbar_layout.addWidget(self.refresh_button)

        self.home_button = QPushButton(self.t('home'))
        self.home_button.clicked.connect(self.go_home)
        self.home_button.setMaximumWidth(150)
        toolbar_layout.addWidget(self.home_button)

        toolbar_layout.addStretch()

        # Sélecteur de langue
        self.language_label = QLabel(self.t('language'))
        self.language_label.setStyleSheet("color: white; padding-right: 5px;")
        toolbar_layout.addWidget(self.language_label)

        self.language_combo = QComboBox()
        self.language_combo.addItem("🇫🇷 Français", "fr")
        self.language_combo.addItem("🇬🇧 English", "en")
        self.language_combo.addItem("🇪🇸 Español", "es")
        self.language_combo.addItem("🇩🇪 Deutsch", "de")
        self.language_combo.setMaximumWidth(150)
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        toolbar_layout.addWidget(self.language_combo)

        self.restart_steam_button = QPushButton(self.t('restart_steam'))
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

        self.config_button = QPushButton(self.t('config'))
        self.config_button.clicked.connect(self.configure_steam_path)
        self.config_button.setMaximumWidth(150)
        toolbar_layout.addWidget(self.config_button)

        parent_layout.addLayout(toolbar_layout)

    def on_site_changed(self, site_name):
        """Appelé quand l'utilisateur change de site"""
        if site_name in self.available_sites:
            self.current_url = self.available_sites[site_name]
            self.browser.setUrl(QUrl(self.current_url))

    def on_language_changed(self, index):
        """Appelé quand l'utilisateur change de langue"""
        lang_code = self.language_combo.itemData(index)
        if lang_code and lang_code != self.current_language:
            self.change_language(lang_code)

    def setup_control_panel(self):
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

        title_label = QLabel(self.t('app_title'))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff; border: none;")
        layout.addWidget(title_label)

        info_layout = QHBoxLayout()

        left_layout = QVBoxLayout()

        self.url_label = QLabel(self.t('url_label').format("Loading..."))
        self.url_label.setStyleSheet("color: #cccccc; border: none;")
        left_layout.addWidget(self.url_label)

        self.app_id_label = QLabel(self.t('app_id_not_detected'))
        self.app_id_label.setStyleSheet("color: #ffcc00; border: none;")
        left_layout.addWidget(self.app_id_label)

        self.steam_path_label = QLabel(self.t('steam_not_configured'))
        self.steam_path_label.setStyleSheet("color: #cccccc; border: none;")
        left_layout.addWidget(self.steam_path_label)

        info_layout.addLayout(left_layout)

        right_layout = QVBoxLayout()

        self.add_button = QPushButton(self.t('add_to_steam'))
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

        self.instructions_label = QLabel(self.t('instructions'))
        self.instructions_label.setStyleSheet("color: #aaaaaa; font-size: 11px; border: none;")
        self.instructions_label.setWordWrap(True)
        layout.addWidget(self.instructions_label)

        return control_widget

    def setup_shortcuts(self):
        add_shortcut = QShortcut(QKeySequence("Return"), self)
        add_shortcut.activated.connect(self.add_to_steam)

        space_shortcut = QShortcut(QKeySequence("Space"), self)
        space_shortcut.activated.connect(self.add_to_steam)

        restart_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        restart_shortcut.activated.connect(self.restart_steam)

        refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(lambda: self.browser.reload())

        help_shortcut = QShortcut(QKeySequence("F1"), self)
        help_shortcut.activated.connect(self.show_help)

        quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        quit_shortcut.activated.connect(self.close)

    def go_home(self):
        """Retourne à la page d'accueil"""
        self.browser.setUrl(QUrl(self.current_url))

    def restart_steam(self):
        if not self.steam_path:
            self.status_bar.showMessage(self.t('config_required'), 3000)
            return

        if self.download_in_progress:
            self.status_bar.showMessage(self.t('cannot_restart_download'), 3000)
            return

        self.restart_steam_button.setEnabled(False)
        self.restart_steam_button.setText("...")

        self.restart_thread = SteamRestartThread(self.steam_path)
        self.restart_thread.status_update.connect(self.update_restart_status)
        self.restart_thread.finished.connect(self.restart_finished)
        self.restart_thread.start()

    def update_restart_status(self, message):
        self.status_bar.showMessage(message)

    def restart_finished(self, success, message):
        self.restart_steam_button.setEnabled(True)
        self.restart_steam_button.setText(self.t('restart_steam'))

        if success:
            self.status_bar.showMessage(self.t('steam_restarted'), 5000)
        else:
            self.status_bar.showMessage(self.t('error_restart').format(message), 5000)

    def configure_steam_path(self):
        new_path = SteamPathDialog.get_steam_path(self, self.current_language)
        if new_path:
            self.steam_path = new_path
            self.setup_steam_paths()
            self.save_config()
            self.update_steam_label()
            self.status_bar.showMessage(self.t('config_updated'), 3000)

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.steam_path = config.get('steam_path', '')
                    self.current_language = config.get('language', 'fr')

                    # Mettre à jour le sélecteur de langue
                    for i in range(self.language_combo.count()):
                        if self.language_combo.itemData(i) == self.current_language:
                            self.language_combo.setCurrentIndex(i)
                            break

                    if self.steam_path and os.path.exists(self.steam_path):
                        self.setup_steam_paths()
                    else:
                        self.ask_steam_path()
            else:
                self.ask_steam_path()
        except Exception as e:
            print(f"Config load error: {e}")
            self.ask_steam_path()

        self.update_steam_label()

    def ask_steam_path(self):
        QTimer.singleShot(1000, self.configure_steam_path)

    def setup_steam_paths(self):
        if not self.steam_path:
            return

        self.depotcache_path = os.path.join(self.steam_path, 'depotcache')
        self.plugins_path = os.path.join(self.steam_path, 'config', 'stplug-in')
        self.steamapps_path = os.path.join(self.steam_path, 'steamapps')

        try:
            os.makedirs(self.depotcache_path, exist_ok=True)
            os.makedirs(self.plugins_path, exist_ok=True)
            os.makedirs(self.steamapps_path, exist_ok=True)
            print(f"Steam folders configured:")
            print(f"  - Depotcache: {self.depotcache_path}")
            print(f"  - Plugins: {self.plugins_path}")
            print(f"  - Steamapps: {self.steamapps_path}")
        except PermissionError:
            QMessageBox.warning(self, "Permissions",
                              "Insufficient permissions to create Steam folders.\n"
                              "Run the application as administrator.")
        except Exception as e:
            QMessageBox.warning(self, self.t('error_title'), f"Error creating folders: {e}")

    def save_config(self):
        try:
            config = {
                'steam_path': self.steam_path,
                'language': self.current_language,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Config save error: {e}")

    def update_steam_label(self):
        if self.steam_path:
            steam_display = self.t('steam_configured').format(os.path.basename(self.steam_path))
            self.steam_path_label.setStyleSheet("color: #00ff00; border: none;")
        else:
            steam_display = self.t('steam_not_configured')
            self.steam_path_label.setStyleSheet("color: #ff6666; border: none;")

        self.steam_path_label.setText(steam_display)

    def on_url_changed(self, url):
        """Appelé quand l'URL de la page change"""
        try:
            # Handle both QUrl and string URL inputs
            if hasattr(url, 'toString'):  # QUrl object
                url_str = url.toString()
            else:  # string
                url_str = str(url)
                
            self.current_url = url_str
            
            # Mettre à jour la sélection du site en fonction de l'URL actuelle
            for site_name, site_url in self.available_sites.items():
                if site_url in url_str:
                    index = self.site_combobox.findText(site_name)
                    if index >= 0 and index != self.site_combobox.currentIndex():
                        self.site_combobox.blockSignals(True)
                        self.site_combobox.setCurrentIndex(index)
                        self.site_combobox.blockSignals(False)
                    break
            
            # Update URL label with truncation if needed
            display_url = url_str[:100] + '...' if len(url_str) > 100 else url_str
            self.url_label.setText(self.t('url_label').format(display_url))
            
            # Extraire l'App ID de l'URL
            new_app_id = self.extract_app_id_from_url(url_str)
            if new_app_id != self.app_id:
                self.app_id = new_app_id
                if self.app_id:
                    self.app_id_label.setText(self.t('app_id_detected').format(self.app_id))
                    self.add_button.setEnabled(True)
                else:
                    self.app_id_label.setText(self.t('app_id_not_detected'))
                    self.add_button.setEnabled(False)
                    
        except Exception as e:
            print(f"Error in on_url_changed: {str(e)}")
            # Continue with default behavior on error
            self.add_button.setEnabled(False)
            self.status_bar.showMessage(self.t('navigate_to_game'))

    def extract_app_id_from_url(self, url):
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
            print(f"App ID extraction error: {e}")
            return None

    def add_to_steam(self):
        if not self.app_id:
            QMessageBox.warning(self, self.t('error_title'), self.t('no_app_id'))
            return

        if self.download_in_progress:
            return

        if not self.steam_path:
            reply = QMessageBox.question(self, self.t('confirmation'),
                                       self.t('config_required_question'))
            if reply == QMessageBox.StandardButton.Yes:
                self.configure_steam_path()
            return

        reply = QMessageBox.question(self, self.t('confirmation'),
                                   self.t('add_game_confirm').format(
                                       self.app_id,
                                       self.depotcache_path,
                                       self.plugins_path))

        if reply != QMessageBox.StandardButton.Yes:
            return

        self.download_in_progress = True
        self.add_button.setEnabled(False)
        self.add_button.setText(self.t('downloading'))
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.download_thread = DownloadThread(self.app_id, self)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.progress_percent.connect(self.progress_bar.setValue)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.start()

        self.status_bar.showMessage(self.t('downloading_app').format(self.app_id))

    def update_progress(self, message):
        self.status_bar.showMessage(message)

    def download_finished(self, success, message):
        self.download_in_progress = False
        self.progress_bar.setVisible(False)
        self.add_button.setText(self.t('add_to_steam'))
        self.add_button.setEnabled(bool(self.app_id and self.steam_path))

        if success:
            self.status_bar.showMessage(self.t('install_success'), 8000)
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
            self.status_bar.showMessage(self.t('install_error'), 5000)

    def check_status_reset(self):
        pass

    def show_help(self):
        help_text = f"""
<h3>{self.t('app_title')} - {self.t('help_title')}</h3>
<p><b>Shortcuts / Raccourcis / Atajos / Tastenkombinationen:</b></p>
<ul>
<li><b>Enter/Space:</b> Add to Steam</li>
<li><b>Ctrl+R:</b> Restart Steam</li>
<li><b>F5:</b> Refresh browser</li>
<li><b>F1:</b> Help</li>
<li><b>Ctrl+Q:</b> Quit</li>
</ul>
        """

        msg = QMessageBox(self)
        msg.setWindowTitle(self.t('help_title'))
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(help_text)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.resize(600, 400)
        msg.exec()

    def closeEvent(self, event):
        if self.download_in_progress:
            reply = QMessageBox.question(self, self.t('close_title'),
                                       self.t('close_confirmation'),
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return

        self.save_config()

        if hasattr(self, 'restart_thread') and self.restart_thread.isRunning():
            self.restart_thread.quit()
            self.restart_thread.wait(2000)

        if hasattr(self, 'download_thread') and self.download_thread.isRunning():
            self.download_thread.quit()
            self.download_thread.wait(2000)

        event.accept()


def check_dependencies():
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
        missing_deps.append("PyQt6 and PyQt6-WebEngine")

    if missing_deps:
        print("Missing dependencies:")
        for dep in missing_deps:
            print(f"   • {dep}")
        print("\nInstall dependencies with:")
        print("   pip install -r requirements.txt")
        return False

    return True


def check_permissions():
    if os.name == 'nt':
        try:
            import ctypes
            if ctypes.windll.shell32.IsUserAnAdmin():
                print("Administrator rights detected")
                return True
            else:
                print("Warning: Administrator rights recommended")
                return False
        except:
            print("Cannot check permissions")
            return False
    else:
        try:
            test_file = os.path.expanduser("~/test_write_permissions")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            return True
        except:
            print("Limited write permissions detected")
            return False


def main():
    try:
        print("Steam Injector v2.0 - Multilingual")
        print("=" * 50)

        print("Checking dependencies...")
        if not check_dependencies():
            input("\nPress Enter to quit...")
            return 1

        print("All dependencies installed")

        print("Checking permissions...")
        check_permissions()

        print("Initializing application...")

        app = QApplication(sys.argv)
        app.setApplicationName("Steam Injector")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("Steam Injector")

        app.setStyle('Fusion')

        window = SteamInjectorWindow()
        window.show()

        print("Application ready!")
        print("\nSupported languages:")
        print("   • Français (FR)")
        print("   • English (EN)")
        print("   • Español (ES)")
        print("   • Deutsch (DE)")
        print("-" * 50)

        return app.exec()

    except KeyboardInterrupt:
        print("\nStopped by user")
        return 0
    except ImportError as e:
        print(f"Import error: {e}")
        print("Install dependencies with: pip install -r requirements.txt")
        input("Press Enter to quit...")
        return 1
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to quit...")
        return 1


if __name__ == "__main__":
    sys.exit(main())