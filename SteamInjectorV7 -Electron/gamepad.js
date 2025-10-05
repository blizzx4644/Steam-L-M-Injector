// Gestion des manettes de jeu (Gamepad API)
class GamepadController {
    constructor() {
        this.gamepad = null;
        this.previousButtons = {};
        this.animationFrameId = null;
        this.buttonMappings = {
            0: 'A',      // Button A (Xbox) / Cross (PS)
            1: 'B',      // Button B (Xbox) / Circle (PS)
            2: 'X',      // Button X (Xbox) / Square (PS)
            3: 'Y',      // Button Y (Xbox) / Triangle (PS)
            4: 'LB',     // Left Bumper
            5: 'RB',     // Right Bumper
            6: 'LT',     // Left Trigger
            7: 'RT',     // Right Trigger
            8: 'Back',   // Back/Select
            9: 'Start',  // Start
            12: 'Up',    // D-Pad Up
            13: 'Down',  // D-Pad Down
            14: 'Left',  // D-Pad Left
            15: 'Right'  // D-Pad Right
        };

        this.focusableElements = [];
        this.currentFocusIndex = 0;

        this.init();
    }

    init() {
        // Écouter les événements de connexion/déconnexion
        window.addEventListener('gamepadconnected', (e) => this.onGamepadConnected(e));
        window.addEventListener('gamepaddisconnected', (e) => this.onGamepadDisconnected(e));

        // Démarrer la boucle de polling
        this.startPolling();

        // Initialiser les éléments focusables
        this.updateFocusableElements();

        // Observer les changements dans le DOM
        const observer = new MutationObserver(() => this.updateFocusableElements());
        observer.observe(document.body, { childList: true, subtree: true });
    }

    onGamepadConnected(event) {
        console.log('Gamepad connected:', event.gamepad);
        this.gamepad = event.gamepad;
        this.showGamepadIndicator();
    }

    onGamepadDisconnected(event) {
        console.log('Gamepad disconnected:', event.gamepad);
        this.gamepad = null;
        this.hideGamepadIndicator();
    }

    showGamepadIndicator() {
        const indicator = document.getElementById('gamepadIndicator');
        if (indicator) {
            indicator.classList.add('visible');
        }
    }

    hideGamepadIndicator() {
        const indicator = document.getElementById('gamepadIndicator');
        if (indicator) {
            indicator.classList.remove('visible');
        }
    }

    startPolling() {
        const poll = () => {
            this.updateGamepad();
            this.animationFrameId = requestAnimationFrame(poll);
        };
        poll();
    }

    updateGamepad() {
        // Récupérer l'état actuel des manettes
        const gamepads = navigator.getGamepads();

        if (!gamepads || gamepads.length === 0) return;

        // Utiliser la première manette connectée
        for (let i = 0; i < gamepads.length; i++) {
            if (gamepads[i]) {
                this.gamepad = gamepads[i];
                break;
            }
        }

        if (!this.gamepad) return;

        // Traiter les boutons
        this.gamepad.buttons.forEach((button, index) => {
            const buttonName = this.buttonMappings[index];
            const isPressed = button.pressed;
            const wasPressed = this.previousButtons[index] || false;

            // Détecter les nouveaux appuis (edge detection)
            if (isPressed && !wasPressed) {
                this.onButtonPressed(buttonName, index);
            }

            this.previousButtons[index] = isPressed;
        });

        // Traiter les joysticks pour le scrolling
        if (Math.abs(this.gamepad.axes[1]) > 0.5) {
            this.handleScroll(this.gamepad.axes[1]);
        }
    }

    onButtonPressed(buttonName, index) {
        console.log(`Button pressed: ${buttonName} (${index})`);

        switch(buttonName) {
            case 'A':
                this.pressCurrentElement();
                break;
            case 'B':
                this.goBack();
                break;
            case 'X':
                this.triggerAddToSteam();
                break;
            case 'Y':
                this.triggerRestartSteam();
                break;
            case 'Up':
                this.moveFocus(-1);
                break;
            case 'Down':
                this.moveFocus(1);
                break;
            case 'Left':
                this.navigateWebview('back');
                break;
            case 'Right':
                this.navigateWebview('forward');
                break;
            case 'LB':
                this.scrollPage(-1);
                break;
            case 'RB':
                this.scrollPage(1);
                break;
            case 'Start':
                this.goHome();
                break;
        }
    }

    updateFocusableElements() {
        // Récupérer tous les éléments focusables
        this.focusableElements = Array.from(document.querySelectorAll(
            'button:not(:disabled), a[href], input:not(:disabled), select:not(:disabled), [tabindex]:not([tabindex="-1"])'
        )).filter(el => {
            // Filtrer les éléments invisibles
            const style = window.getComputedStyle(el);
            return style.display !== 'none' && style.visibility !== 'hidden';
        });
    }

    moveFocus(direction) {
        if (this.focusableElements.length === 0) return;

        // Retirer le focus actuel
        if (this.focusableElements[this.currentFocusIndex]) {
            this.focusableElements[this.currentFocusIndex].style.outline = '';
        }

        // Calculer le nouvel index
        this.currentFocusIndex = (this.currentFocusIndex + direction + this.focusableElements.length) % this.focusableElements.length;

        // Appliquer le nouveau focus
        const element = this.focusableElements[this.currentFocusIndex];
        if (element) {
            element.style.outline = '3px solid #0066ff';
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    pressCurrentElement() {
        const element = this.focusableElements[this.currentFocusIndex];
        if (element) {
            // Créer un effet visuel
            element.style.transform = 'scale(0.95)';
            setTimeout(() => {
                element.style.transform = '';
            }, 100);

            // Cliquer sur l'élément
            element.click();
        }
    }

    goBack() {
        const backBtn = document.getElementById('backBtn');
        if (backBtn) {
            backBtn.click();
        }
    }

    goHome() {
        const homeBtn = document.getElementById('homeBtn');
        if (homeBtn) {
            homeBtn.click();
        }
    }

    triggerAddToSteam() {
        const addBtn = document.getElementById('addToSteamBtn');
        if (addBtn && !addBtn.disabled) {
            // Effet visuel
            addBtn.style.transform = 'scale(0.95)';
            setTimeout(() => {
                addBtn.style.transform = '';
            }, 100);
            addBtn.click();
        }
    }

    triggerRestartSteam() {
        const restartBtn = document.getElementById('restartSteamBtn');
        if (restartBtn) {
            // Effet visuel
            restartBtn.style.transform = 'scale(0.95)';
            setTimeout(() => {
                restartBtn.style.transform = '';
            }, 100);
            restartBtn.click();
        }
    }

    navigateWebview(direction) {
        const webview = document.getElementById('webview');
        if (!webview) return;

        if (direction === 'back' && webview.canGoBack()) {
            webview.goBack();
        } else if (direction === 'forward' && webview.canGoForward()) {
            webview.goForward();
        }
    }

    scrollPage(direction) {
        const webview = document.getElementById('webview');
        if (webview) {
            webview.executeJavaScript(`window.scrollBy(0, ${direction * 300})`);
        }
    }

    handleScroll(axisValue) {
        // Utiliser le joystick gauche (axe Y) pour scroller
        const webview = document.getElementById('webview');
        if (webview) {
            const scrollAmount = axisValue * 10;
            webview.executeJavaScript(`window.scrollBy(0, ${scrollAmount})`);
        }
    }

    destroy() {
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
        }
        window.removeEventListener('gamepadconnected', this.onGamepadConnected);
        window.removeEventListener('gamepaddisconnected', this.onGamepadDisconnected);
    }
}

// Initialiser le contrôleur de manette quand le DOM est prêt
let gamepadController;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        gamepadController = new GamepadController();
    });
} else {
    gamepadController = new GamepadController();
}

// Nettoyer à la fermeture
window.addEventListener('beforeunload', () => {
    if (gamepadController) {
        gamepadController.destroy();
    }
});
