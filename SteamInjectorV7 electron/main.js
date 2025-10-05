const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const axios = require('axios');
const AdmZip = require('adm-zip');

let mainWindow;
const CONFIG_FILE = 'config.json';

// Configuration par défaut
let config = {
    steamPath: '',
    language: 'fr'
};

// Charger la configuration
function loadConfig() {
    try {
        if (fs.existsSync(CONFIG_FILE)) {
            const data = fs.readFileSync(CONFIG_FILE, 'utf8');
            config = JSON.parse(data);
        }
    } catch (error) {
        console.error('Erreur de chargement de la config:', error);
    }
}

// Sauvegarder la configuration
function saveConfig() {
    try {
        fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
    } catch (error) {
        console.error('Erreur de sauvegarde de la config:', error);
    }
}

// Créer la fenêtre principale
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1200,
        minHeight: 800,
        frame: true,
        backgroundColor: '#1a1a2e',
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false,
            webviewTag: true
        },
        icon: path.join(__dirname, 'assets/icon.png')
    });

    mainWindow.loadFile('index.html');

    // Ouvrir les DevTools en développement
    // mainWindow.webContents.openDevTools();

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.whenReady().then(() => {
    loadConfig();
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// IPC Handlers

// Obtenir la configuration
ipcMain.handle('get-config', async () => {
    return config;
});

// Sauvegarder la configuration
ipcMain.handle('save-config', async (event, newConfig) => {
    config = { ...config, ...newConfig };
    saveConfig();
    return { success: true };
});

// Sélectionner le chemin Steam
ipcMain.handle('select-steam-path', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openDirectory'],
        title: 'Sélectionner le dossier d\'installation Steam'
    });

    if (!result.canceled && result.filePaths.length > 0) {
        return result.filePaths[0];
    }
    return null;
});

// Détecter automatiquement Steam
ipcMain.handle('detect-steam', async () => {
    const possiblePaths = [
        'C:\\Program Files (x86)\\Steam',
        'C:\\Program Files\\Steam',
        'D:\\Steam',
        'E:\\Steam',
        path.join(process.env.USERPROFILE || '', 'Steam')
    ];

    for (const steamPath of possiblePaths) {
        const steamExe = path.join(steamPath, 'steam.exe');
        if (fs.existsSync(steamExe)) {
            return steamPath;
        }
    }
    return null;
});

// Vérifier si Steam est en cours d'exécution
ipcMain.handle('is-steam-running', async () => {
    return new Promise((resolve) => {
        if (process.platform === 'win32') {
            exec('tasklist', (error, stdout) => {
                if (error) {
                    resolve(false);
                    return;
                }
                resolve(stdout.toLowerCase().includes('steam.exe'));
            });
        } else {
            exec('pgrep steam', (error) => {
                resolve(!error);
            });
        }
    });
});

// Fermer Steam
ipcMain.handle('close-steam', async () => {
    return new Promise((resolve) => {
        if (process.platform === 'win32') {
            const steamExe = path.join(config.steamPath, 'steam.exe');
            exec(`"${steamExe}" -shutdown`, (error) => {
                setTimeout(() => {
                    exec('taskkill /F /IM steam.exe', () => {
                        resolve(true);
                    });
                }, 3000);
            });
        } else {
            exec('pkill -f steam', (error) => {
                resolve(!error);
            });
        }
    });
});

// Démarrer Steam
ipcMain.handle('start-steam', async () => {
    return new Promise((resolve) => {
        if (process.platform === 'win32') {
            const steamExe = path.join(config.steamPath, 'steam.exe');
            exec(`"${steamExe}"`, (error) => {
                resolve(!error);
            });
        } else {
            exec('steam', (error) => {
                resolve(!error);
            });
        }
    });
});

// Télécharger et installer un jeu
ipcMain.handle('download-game', async (event, appId) => {
    try {
        // Créer les dossiers nécessaires
        const tempDir = path.join(__dirname, 'temp');
        if (!fs.existsSync(tempDir)) {
            fs.mkdirSync(tempDir);
        }

        const depotcachePath = path.join(config.steamPath, 'depotcache');
        const stplugInPath = path.join(config.steamPath, 'config', 'stplug-in');
        const steamappsPath = path.join(config.steamPath, 'steamapps');

        if (!fs.existsSync(depotcachePath)) {
            fs.mkdirSync(depotcachePath, { recursive: true });
        }
        if (!fs.existsSync(stplugInPath)) {
            fs.mkdirSync(stplugInPath, { recursive: true });
        }

        // Télécharger le fichier ZIP depuis GitHub
        const urls = [
            `https://codeload.github.com/SPIN0ZAi/SB_manifest_DB/zip/refs/heads/${appId}`,
            `https://github.com/SPIN0ZAi/SB_manifest_DB/archive/refs/heads/${appId}.zip`,
            `https://api.github.com/repos/SPIN0ZAi/SB_manifest_DB/zipball/${appId}`
        ];

        let zipPath = path.join(tempDir, `${appId}.zip`);
        let downloaded = false;

        for (let i = 0; i < urls.length; i++) {
            try {
                event.sender.send('download-progress', {
                    message: `Tentative de téléchargement ${i + 1}/${urls.length}...`,
                    percent: 20
                });

                const response = await axios.get(urls[i], {
                    responseType: 'arraybuffer',
                    timeout: 60000
                });

                fs.writeFileSync(zipPath, response.data);

                // Vérifier que le fichier existe et n'est pas vide
                if (fs.existsSync(zipPath) && fs.statSync(zipPath).size > 0) {
                    downloaded = true;
                    break;
                }
            } catch (error) {
                console.error(`Échec téléchargement depuis ${urls[i]}:`, error.message);
            }
        }

        if (!downloaded) {
            throw new Error(`Impossible de télécharger les fichiers pour l'App ID ${appId}. Le jeu n'existe peut-être pas dans la base de données.`);
        }

        event.sender.send('download-progress', { message: 'Extraction des fichiers...', percent: 60 });

        // Extraire le ZIP
        const zip = new AdmZip(zipPath);
        zip.extractAllTo(tempDir, true);

        // Trouver le dossier extrait
        let extractedDir = null;
        const possiblePatterns = [
            `SB_manifest_DB-${appId}`,
            `SPIN0ZAi-SB_manifest_DB-${appId}`,
            `SB_manifest_DB-main-${appId}`,
            appId
        ];

        const tempContents = fs.readdirSync(tempDir);
        for (const item of tempContents) {
            const itemPath = path.join(tempDir, item);
            if (fs.statSync(itemPath).isDirectory() && item !== appId) {
                // Vérifier si le nom correspond à un pattern
                for (const pattern of possiblePatterns) {
                    if (item.includes(pattern) || item.endsWith(appId)) {
                        extractedDir = itemPath;
                        break;
                    }
                }
                if (extractedDir) break;
            }
        }

        // Si pas trouvé avec les patterns, prendre le premier dossier
        if (!extractedDir) {
            for (const item of tempContents) {
                const itemPath = path.join(tempDir, item);
                if (fs.statSync(itemPath).isDirectory() && item !== '__pycache__') {
                    extractedDir = itemPath;
                    break;
                }
            }
        }

        if (!extractedDir) {
            throw new Error('Dossier extrait introuvable - structure d\'archive inattendue');
        }

        event.sender.send('download-progress', { message: 'Installation des fichiers...', percent: 75 });

        // Parcourir récursivement et copier selon l'extension
        let filesCopied = 0;
        let totalFiles = 0;

        function walkDirectory(dir) {
            const files = fs.readdirSync(dir);

            for (const file of files) {
                const filePath = path.join(dir, file);
                const stats = fs.statSync(filePath);

                if (stats.isDirectory()) {
                    walkDirectory(filePath);
                } else {
                    totalFiles++;

                    try {
                        // Copier les fichiers .manifest dans Steam\depotcache
                        if (file.endsWith('.manifest')) {
                            const destPath = path.join(depotcachePath, file);
                            fs.copyFileSync(filePath, destPath);
                            filesCopied++;
                            console.log(`Copied manifest: ${file} -> ${destPath}`);
                        }
                        // Copier les fichiers .lua dans Steam\config\stplug-in
                        else if (file.endsWith('.lua')) {
                            const destPath = path.join(stplugInPath, file);
                            fs.copyFileSync(filePath, destPath);
                            filesCopied++;
                            console.log(`Copied lua: ${file} -> ${destPath}`);
                        }
                    } catch (error) {
                        console.error(`Erreur lors de la copie de ${file}:`, error.message);
                    }
                }
            }
        }

        walkDirectory(extractedDir);

        event.sender.send('download-progress', { message: 'Nettoyage...', percent: 95 });

        // Nettoyer
        try {
            fs.rmSync(extractedDir, { recursive: true, force: true });
            fs.unlinkSync(zipPath);
        } catch (error) {
            console.warn('Impossible de nettoyer le dossier temp:', error.message);
        }

        if (filesCopied === 0) {
            if (totalFiles === 0) {
                throw new Error(`Aucun fichier trouvé dans l'archive pour l'App ID ${appId}. Ce jeu n'est peut-être pas supporté.`);
            } else {
                throw new Error(`Aucun fichier Steam valide trouvé (${totalFiles} fichiers examinés). Types supportés: .manifest, .lua`);
            }
        }

        event.sender.send('download-progress', { message: 'Installation terminée!', percent: 100 });

        return {
            success: true,
            message: `Installation réussie ! ${filesCopied} fichier(s) installé(s) sur ${totalFiles} examinés.`
        };
    } catch (error) {
        console.error('Erreur download-game:', error);
        return { success: false, message: error.message };
    }
});

// Fonction helper pour copier récursivement
function copyRecursiveSync(src, dest) {
    if (!fs.existsSync(dest)) {
        fs.mkdirSync(dest, { recursive: true });
    }

    const entries = fs.readdirSync(src, { withFileTypes: true });

    for (const entry of entries) {
        const srcPath = path.join(src, entry.name);
        const destPath = path.join(dest, entry.name);

        if (entry.isDirectory()) {
            copyRecursiveSync(srcPath, destPath);
        } else {
            fs.copyFileSync(srcPath, destPath);
        }
    }
}
