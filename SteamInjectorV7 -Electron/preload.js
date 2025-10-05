const { contextBridge, ipcRenderer } = require('electron');

// Exposer les APIs au renderer de manière sécurisée
contextBridge.exposeInMainWorld('electronAPI', {
    // Configuration
    getConfig: () => ipcRenderer.invoke('get-config'),
    saveConfig: (config) => ipcRenderer.invoke('save-config', config),

    // Gestion Steam
    selectSteamPath: () => ipcRenderer.invoke('select-steam-path'),
    detectSteam: () => ipcRenderer.invoke('detect-steam'),
    isSteamRunning: () => ipcRenderer.invoke('is-steam-running'),
    closeSteam: () => ipcRenderer.invoke('close-steam'),
    startSteam: () => ipcRenderer.invoke('start-steam'),

    // Téléchargement et installation
    downloadGame: (appId) => ipcRenderer.invoke('download-game', appId),

    // Événements
    onDownloadProgress: (callback) => {
        ipcRenderer.on('download-progress', (event, data) => callback(data));
    },
    removeDownloadProgressListener: () => {
        ipcRenderer.removeAllListeners('download-progress');
    }
});
