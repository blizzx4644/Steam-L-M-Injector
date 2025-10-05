// Traductions multilingues
const translations = {
    fr: {
        config: 'Configuration',
        steam_path: 'Chemin Steam',
        steam_not_configured: 'Non configuré',
        detect_steam: 'Auto-détection',
        select_steam: 'Parcourir',
        status: 'Statut',
        steam_offline: 'Hors ligne',
        steam_online: 'En ligne',
        app_id: 'App ID',
        actions: 'Actions',
        add_to_steam: 'Ajouter à Steam',
        restart_steam: 'Redémarrer Steam',
        gamepad_connected: 'Manette connectée',
        downloading: 'Téléchargement...',
        instructions: 'Naviguez vers un jeu Steam → App ID détecté automatiquement → Cliquez sur Ajouter à Steam → Redémarrez Steam',
        steam_detected: 'Steam détecté avec succès',
        steam_not_found: 'Steam non trouvé. Veuillez sélectionner manuellement.',
        config_saved: 'Configuration sauvegardée',
        app_detected: 'Jeu détecté : App ID',
        no_app_id: 'Aucun App ID détecté',
        download_success: 'Installation terminée avec succès',
        download_error: 'Erreur lors du téléchargement',
        restart_confirm: 'Voulez-vous redémarrer Steam maintenant ?',
        add_confirm: 'Ajouter le jeu avec l\'App ID',
        closing_steam: 'Fermeture de Steam...',
        starting_steam: 'Démarrage de Steam...',
        steam_restarted: 'Steam redémarré avec succès'
    },
    en: {
        config: 'Configuration',
        steam_path: 'Steam Path',
        steam_not_configured: 'Not configured',
        detect_steam: 'Auto Detect',
        select_steam: 'Browse',
        status: 'Status',
        steam_offline: 'Offline',
        steam_online: 'Online',
        app_id: 'App ID',
        actions: 'Actions',
        add_to_steam: 'Add to Steam',
        restart_steam: 'Restart Steam',
        gamepad_connected: 'Controller Connected',
        downloading: 'Downloading...',
        instructions: 'Navigate to a Steam game → App ID detected automatically → Click Add to Steam → Restart Steam',
        steam_detected: 'Steam detected successfully',
        steam_not_found: 'Steam not found. Please select manually.',
        config_saved: 'Configuration saved',
        app_detected: 'Game detected: App ID',
        no_app_id: 'No App ID detected',
        download_success: 'Installation completed successfully',
        download_error: 'Download error',
        restart_confirm: 'Do you want to restart Steam now?',
        add_confirm: 'Add game with App ID',
        closing_steam: 'Closing Steam...',
        starting_steam: 'Starting Steam...',
        steam_restarted: 'Steam restarted successfully'
    },
    es: {
        config: 'Configuración',
        steam_path: 'Ruta de Steam',
        steam_not_configured: 'No configurado',
        detect_steam: 'Auto-detectar',
        select_steam: 'Explorar',
        status: 'Estado',
        steam_offline: 'Desconectado',
        steam_online: 'Conectado',
        app_id: 'App ID',
        actions: 'Acciones',
        add_to_steam: 'Agregar a Steam',
        restart_steam: 'Reiniciar Steam',
        gamepad_connected: 'Controlador conectado',
        downloading: 'Descargando...',
        instructions: 'Navega a un juego de Steam → App ID detectado automáticamente → Clic en Agregar a Steam → Reinicia Steam',
        steam_detected: 'Steam detectado con éxito',
        steam_not_found: 'Steam no encontrado. Por favor seleccione manualmente.',
        config_saved: 'Configuración guardada',
        app_detected: 'Juego detectado: App ID',
        no_app_id: 'Ningún App ID detectado',
        download_success: 'Instalación completada con éxito',
        download_error: 'Error de descarga',
        restart_confirm: '¿Desea reiniciar Steam ahora?',
        add_confirm: 'Agregar juego con App ID',
        closing_steam: 'Cerrando Steam...',
        starting_steam: 'Iniciando Steam...',
        steam_restarted: 'Steam reiniciado con éxito'
    },
    de: {
        config: 'Einstellungen',
        steam_path: 'Steam-Pfad',
        steam_not_configured: 'Nicht konfiguriert',
        detect_steam: 'Auto-Erkennung',
        select_steam: 'Durchsuchen',
        status: 'Status',
        steam_offline: 'Offline',
        steam_online: 'Online',
        app_id: 'App ID',
        actions: 'Aktionen',
        add_to_steam: 'Zu Steam hinzufügen',
        restart_steam: 'Steam neustarten',
        gamepad_connected: 'Controller verbunden',
        downloading: 'Wird heruntergeladen...',
        instructions: 'Zu einem Steam-Spiel navigieren → App ID automatisch erkannt → Zu Steam hinzufügen klicken → Steam neustarten',
        steam_detected: 'Steam erfolgreich erkannt',
        steam_not_found: 'Steam nicht gefunden. Bitte manuell auswählen.',
        config_saved: 'Konfiguration gespeichert',
        app_detected: 'Spiel erkannt: App ID',
        no_app_id: 'Keine App ID erkannt',
        download_success: 'Installation erfolgreich abgeschlossen',
        download_error: 'Download-Fehler',
        restart_confirm: 'Möchten Sie Steam jetzt neustarten?',
        add_confirm: 'Spiel mit App ID hinzufügen',
        closing_steam: 'Steam wird geschlossen...',
        starting_steam: 'Steam wird gestartet...',
        steam_restarted: 'Steam erfolgreich neugestartet'
    }
};

// Variables globales
let currentLanguage = 'fr';
let config = {};
let currentAppId = null;
let webview;

// Initialisation
document.addEventListener('DOMContentLoaded', async () => {
    webview = document.getElementById('webview');

    // Charger la configuration
    await loadConfig();

    // Configurer les événements
    setupEventListeners();

    // Configurer le webview
    setupWebview();

    // Vérifier le statut de Steam
    checkSteamStatus();
    setInterval(checkSteamStatus, 5000);

    // Écouter les progrès de téléchargement
    window.electronAPI.onDownloadProgress((data) => {
        showProgress(data.message, data.percent);
    });
});

// Charger la configuration
async function loadConfig() {
    config = await window.electronAPI.getConfig();
    currentLanguage = config.language || 'fr';

    // Mettre à jour l'interface
    updateLanguage(currentLanguage);
    updateSteamPathDisplay();

    // Sélectionner la langue dans le dropdown
    document.getElementById('languageSelect').value = currentLanguage;
}

// Mettre à jour l'affichage du chemin Steam
function updateSteamPathDisplay() {
    const display = document.getElementById('steamPathDisplay');
    if (config.steamPath) {
        display.textContent = config.steamPath;
        display.classList.remove('value');
        display.classList.add('value');
    } else {
        display.textContent = t('steam_not_configured');
    }
}

// Fonction de traduction
function t(key) {
    return translations[currentLanguage][key] || key;
}

// Mettre à jour la langue
function updateLanguage(lang) {
    currentLanguage = lang;

    // Mettre à jour tous les éléments avec data-i18n
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        const translated = t(key);

        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            element.placeholder = translated;
        } else {
            element.textContent = translated;
        }
    });

    updateSteamPathDisplay();
}

// Configurer les écouteurs d'événements
function setupEventListeners() {
    // Changement de langue
    document.getElementById('languageSelect').addEventListener('change', async (e) => {
        currentLanguage = e.target.value;
        await window.electronAPI.saveConfig({ language: currentLanguage });
        updateLanguage(currentLanguage);
        showNotification(t('config_saved'));
    });

    // Détecter Steam
    document.getElementById('detectSteamBtn').addEventListener('click', async () => {
        const steamPath = await window.electronAPI.detectSteam();
        if (steamPath) {
            config.steamPath = steamPath;
            await window.electronAPI.saveConfig(config);
            updateSteamPathDisplay();
            showNotification(t('steam_detected'));
        } else {
            showNotification(t('steam_not_found'), 'error');
        }
    });

    // Sélectionner Steam manuellement
    document.getElementById('selectSteamBtn').addEventListener('click', async () => {
        const steamPath = await window.electronAPI.selectSteamPath();
        if (steamPath) {
            config.steamPath = steamPath;
            await window.electronAPI.saveConfig(config);
            updateSteamPathDisplay();
            showNotification(t('config_saved'));
        }
    });

    // Ajouter à Steam
    document.getElementById('addToSteamBtn').addEventListener('click', async () => {
        if (!currentAppId) {
            showNotification(t('no_app_id'), 'error');
            return;
        }

        if (!config.steamPath) {
            showNotification(t('steam_not_configured'), 'error');
            return;
        }

        if (confirm(`${t('add_confirm')} ${currentAppId}?`)) {
            await downloadAndInstallGame(currentAppId);
        }
    });

    // Redémarrer Steam
    document.getElementById('restartSteamBtn').addEventListener('click', async () => {
        if (!config.steamPath) {
            showNotification(t('steam_not_configured'), 'error');
            return;
        }

        if (confirm(t('restart_confirm'))) {
            await restartSteam();
        }
    });

    // Navigation du webview
    document.getElementById('backBtn').addEventListener('click', () => {
        if (webview.canGoBack()) webview.goBack();
    });

    document.getElementById('forwardBtn').addEventListener('click', () => {
        if (webview.canGoForward()) webview.goForward();
    });

    document.getElementById('refreshBtn').addEventListener('click', () => {
        webview.reload();
    });

    document.getElementById('homeBtn').addEventListener('click', () => {
        const homeUrl = document.getElementById('siteSelector').value;
        webview.src = homeUrl;
    });

    // Changement de site
    document.getElementById('siteSelector').addEventListener('change', (e) => {
        webview.src = e.target.value;
    });
}

// Configurer le webview
function setupWebview() {
    webview.addEventListener('did-start-loading', () => {
        document.getElementById('refreshBtn').classList.add('loading');
    });

    webview.addEventListener('did-stop-loading', () => {
        document.getElementById('refreshBtn').classList.remove('loading');
    });

    webview.addEventListener('did-navigate', (e) => {
        updateUrlBar(e.url);
        extractAppId(e.url);
    });

    webview.addEventListener('did-navigate-in-page', (e) => {
        updateUrlBar(e.url);
        extractAppId(e.url);
    });
}

// Mettre à jour la barre d'URL
function updateUrlBar(url) {
    document.getElementById('urlInput').value = url;
}

// Extraire l'App ID de l'URL
function extractAppId(url) {
    let appId = null;

    // Steam Store: https://store.steampowered.com/app/XXXXXX/
    const steamStoreMatch = url.match(/store\.steampowered\.com\/app\/(\d+)/);
    if (steamStoreMatch) {
        appId = steamStoreMatch[1];
    }

    // SteamDB: https://steamdb.info/app/XXXXXX/
    const steamDbMatch = url.match(/steamdb\.info\/app\/(\d+)/);
    if (steamDbMatch) {
        appId = steamDbMatch[1];
    }

    // Mettre à jour l'App ID
    if (appId) {
        currentAppId = appId;
        document.getElementById('appIdDisplay').textContent = appId;
        document.getElementById('addToSteamBtn').disabled = false;
        showNotification(`${t('app_detected')} ${appId}`, 'success');
    } else {
        currentAppId = null;
        document.getElementById('appIdDisplay').textContent = '-';
        document.getElementById('addToSteamBtn').disabled = true;
    }
}

// Vérifier le statut de Steam
async function checkSteamStatus() {
    const isRunning = await window.electronAPI.isSteamRunning();
    const indicator = document.getElementById('steamStatus');
    const text = document.getElementById('steamStatusText');

    if (isRunning) {
        indicator.classList.add('online');
        text.textContent = t('steam_online');
    } else {
        indicator.classList.remove('online');
        text.textContent = t('steam_offline');
    }
}

// Télécharger et installer un jeu
async function downloadAndInstallGame(appId) {
    try {
        document.getElementById('addToSteamBtn').disabled = true;
        showProgress(t('downloading'), 0);

        const result = await window.electronAPI.downloadGame(appId);

        hideProgress();

        if (result.success) {
            showNotification(t('download_success'), 'success');
            if (confirm(t('restart_confirm'))) {
                await restartSteam();
            }
        } else {
            showNotification(`${t('download_error')}: ${result.message}`, 'error');
        }
    } catch (error) {
        hideProgress();
        showNotification(`${t('download_error')}: ${error.message}`, 'error');
    } finally {
        document.getElementById('addToSteamBtn').disabled = false;
    }
}

// Redémarrer Steam
async function restartSteam() {
    try {
        showNotification(t('closing_steam'));
        await window.electronAPI.closeSteam();

        await new Promise(resolve => setTimeout(resolve, 3000));

        showNotification(t('starting_steam'));
        await window.electronAPI.startSteam();

        await new Promise(resolve => setTimeout(resolve, 2000));

        showNotification(t('steam_restarted'), 'success');
    } catch (error) {
        showNotification(`${t('download_error')}: ${error.message}`, 'error');
    }
}

// Afficher la barre de progression
function showProgress(message, percent) {
    const container = document.getElementById('progressContainer');
    const text = document.getElementById('progressText');
    const percentText = document.getElementById('progressPercent');
    const fill = document.getElementById('progressFill');

    container.style.display = 'block';
    text.textContent = message;
    percentText.textContent = `${percent}%`;
    fill.style.width = `${percent}%`;
}

// Cacher la barre de progression
function hideProgress() {
    const container = document.getElementById('progressContainer');
    setTimeout(() => {
        container.style.display = 'none';
    }, 2000);
}

// Afficher une notification (toast)
function showNotification(message, type = 'info') {
    // Créer l'élément de notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#0066ff'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        animation: slideInRight 0.3s ease;
        max-width: 300px;
    `;

    document.body.appendChild(notification);

    // Supprimer après 3 secondes
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Ajouter les animations CSS pour les notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
