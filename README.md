<div align="center">

# Steam Injector

### Modern Electron application for Steam Lua and Manifest management


</div>


##  Features

### Core Functionality
- **Integrated Web Browser** - Browse Steam Store and SteamDB directly in the app
- **Automatic App ID Detection** - Automatically detects Steam game App IDs from URLs
- **Background Downloads** - Downloads and installs games from GitHub repository
- **Smart Steam Management** - Automatically restarts Steam after installation

### User Experience
- **Experimental Gamepad Support** - Control the entire app with Xbox/PlayStation controllers
- **Multi-language** - Available in French, English, Spanish, and German
- **Modern UI** - Clean, minimalist design with smooth transitions

### Technical
- Built with **Electron 28** for cross-platform desktop experience
- **Chromium-based** web browsing for optimal compatibility
- **IPC architecture** for secure communication

---

##  Requirements

- **Node.js** v16 or higher
- **npm** or **yarn**
- **Steam** installed on your system
- **Windows 10/11** (Linux/macOS support planned)

---

##  Installation

Or simply in the [releases](https://github.com/blizzx4644/Steam-L-M-Injector/releases)

### Option 1: From Source

1. **Clone the repository**
   ```bash
   git clone https://github.com/blizzx4644/Steam-L-M-Injector.git
   cd steam-injector
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Run the application**
   ```bash
   npm start
   ```

### Option 2: Quick Start (Windows)

Simply double-click `start.bat` - it will automatically:
- Check for Node.js installation
- Install dependencies if needed
- Launch the application

### Option 3: Build Executable

Create a standalone executable:
```bash
npm run build
```
The `.exe` file will be generated in the `dist/` folder.

---

##  Usage

### Initial Setup

1. **Launch the application**
2. Click **"Auto Detect"** to find your Steam installation
3. If detection fails, use **"Browse"** to manually select your Steam folder

### Adding a Game

1. **Navigate** to a game page on Steam Store or SteamDB
2. The **App ID** will be detected automatically
3. Click **"Add to Steam"**
4. Wait for download and installation to complete
5. Click **"Restart Steam"** to see the game in your library

### Supported File Types

The application automatically handles:
- **`.manifest`** files → `Steam\depotcache\`
- **`.lua`** files → `Steam\config\stplug-in\`

---

##  Gamepad Support (Experimental)

### Button Mapping

| Button | Action |
|--------|--------|
| **A** (Xbox) / **✕** (PS) | Select highlighted element |
| **B** (Xbox) / **○** (PS) | Back |
| **X** (Xbox) / **□** (PS) | Add to Steam |
| **Y** (Xbox) / **△** (PS) | Restart Steam |
| **D-Pad Up/Down** | Navigate UI elements |
| **D-Pad Left/Right** | Web navigation (Back/Forward) |
| **LB/RB** | Scroll page |
| **Start** | Home |
| **Left Stick** | Scroll page |

### Connection

1. Connect your controller before launching the app
2. The controller indicator will appear when detected
3. Use D-Pad to navigate and A button to select

---

##  Languages

Available languages:
- 🇫🇷 **Français** (French)
- 🇬🇧 **English**
- 🇪🇸 **Español** (Spanish)
- 🇩🇪 **Deutsch** (German)

Change language via the dropdown in the top-right corner.

---

##  Tech Stack

- **[Electron](https://www.electronjs.org/)** - Desktop application framework
- **[Node.js](https://nodejs.org/)** - JavaScript runtime
- **[Axios](https://axios-http.com/)** - HTTP client for downloads
- **[AdmZip](https://www.npmjs.com/package/adm-zip)** - ZIP file extraction
- **Gamepad API** - Native controller support
- **WebView** - Integrated web browsing

---

##  Project Structure

```
steam-injector/
├── main.js              # Main Electron process
├── preload.js           # IPC bridge (secure)
├── renderer.js          # UI logic & translations
├── gamepad.js           # Controller support
├── index.html           # User interface
├── styles.css           # Modern CSS styling
├── package.json         # Dependencies
├── start.bat            # Windows launcher
└── README.md            # This file
```

---

##  Troubleshooting

### Steam Not Detected

**Solution:**
- Verify Steam is installed
- Use **"Browse"** button to manually select Steam folder
- Folder must contain `steam.exe`

### Download Fails

**Possible causes:**
- No internet connection
- Game doesn't exist in the `SPIN0ZAi/SB_manifest_DB` repository
- Firewall blocking download

**Solutions:**
1. Check your internet connection
2. Try a different game
3. Temporarily disable antivirus

### Steam Won't Restart

**Solution:**
1. Open Task Manager (`Ctrl+Shift+Esc`)
2. End all "Steam" processes
3. Manually restart Steam
4. Verify Steam path in settings

### Gamepad Not Detected

**Solutions:**
1. Disconnect and reconnect controller
2. Restart the application
3. Check controller in Windows Settings → Devices
4. Test with [HTML5 Gamepad Tester](https://hardwaretester.com/gamepad)


---

##  Acknowledgments

- **[SPIN0ZAi](https://github.com/SPIN0ZAi/SB_manifest_DB)** - For the game manifest database
- **Electron Community** - For the excellent framework



[Report Bug](https://github.com/yourusername/steam-injector/issues) • [Request Feature](https://github.com/yourusername/steam-injector/issues)

</div>

