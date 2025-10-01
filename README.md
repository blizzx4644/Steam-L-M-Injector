# Steam L&M Injector

Modern application for adding games to Steam via manifests and lua. Enhanced graphical interface with integrated browser.


<img width="1920" height="1017" alt="Steam Injector V2" src="https://github.com/user-attachments/assets/cae53ab9-4b00-43af-9172-24a12a522ef6" />



##  Features

- **Multilingual interface** with support for English, French, Spanish, and German
- **User interface** with modern design and themed colors
- **Automatic Steam path detection** on Windows
- **Error handling** with informative messages
- **Background downloads** without blocking the interface
- **Visual indicators** for progress and status
- **Dependency verification** at startup
- **Automatic cleanup** of temporary files
- **Integrated help** with keyboard shortcuts
- **Steam restart functionality** with automatic process management
- **Multiple site support** with dropdown selector (SteamDB, Steam Store)

### Navigation and Detection
- Integrated browser with full web engine
- Automatic App ID detection from any Steam URL
- Support for multiple URLs: `/app/`, `/apps/`, `appid=` parameters
- Real-time monitoring of URL changes
- Site switching between SteamDB and Steam Store

### Interface and Controls  
- Modern graphical interface with visual indicators
- Intuitive keyboard shortcuts
- Language selector with flag icons
- Dark theme with custom styling
- Responsive layout with resizable panels
  
### Installation and Download
- Automatic download and extraction of necessary files
- Background installation without blocking
- Intelligent permission management
- Automatic Steam folder configuration
- Automatic cleanup of temporary files
- Support for .manifest, .lua, .vdf, and .acf files
- Multi-URL fallback system for reliable downloads

### Steam Management
- One-click Steam restart functionality
- Automatic Steam process detection and closure
- Force kill capability for stuck processes
- Automatic Steam relaunch after restart
- Status updates during restart process

## 🔧 Requirements

- **Python 3.8 or higher**
- **Web browser** (Chrome/Chromium recommended for optimal display)
- **Steam account** with local installation
- **Administrator rights** (recommended for writing to Steam folders)

### Supported Systems
- ✅ Windows 10/11 (x64) - .exe version available
- 🐍 Windows (Python 3.8+)
- 🐍 Linux (Python 3.8+)
- 🐍 macOS (Python 3.8+)

## 🌐 Supported Languages

- 🇫🇷 French (Français)
- 🇬🇧 English
- 🇪🇸 Spanish (Español)
- 🇩🇪 German (Deutsch)

Switch languages anytime using the dropdown menu in the toolbar.

## 📦 Installation

You can now use the .bat and .sh scripts provided in V2 (the most recent) to automatically install Python and its dependencies. (There is a .zip file containing the .py files, requirements.txt, and installation scripts.)

1. **Clone or download** this repository
   ```bash
   git clone https://github.com/your-repo/steam-injector.git
   cd steam-injector
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the application**
   ```bash
   python steam_injector.py
   ```

### Installation with Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv steam_injector_env

# Activation (Windows)
steam_injector_env\Scripts\activate
# Activation (Linux/macOS)
source steam_injector_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch
python steam_injector.py
```

## 🚀 Usage

### First Launch
1. **Automatic configuration**: The application automatically detects Steam
2. **Manual configuration**: If necessary, specify the installation path
3. **Language selection**: Choose your preferred language from the toolbar
4. **Navigation**: The browser window opens automatically

### Normal Usage
1. **Select site**: Choose between SteamDB or Steam Store from the dropdown menu
2. **Navigate** to the Steam game page you want to add
3. **Automatic detection**: The App ID displays as soon as you're on the page
4. **Installation**: Press `Enter` or click "Add to Steam" button
5. **Restart**: Click "Restart Steam" button or restart manually to see the game in your library

### Steam Restart Feature
- **One-click restart**: Use the "🔄 Restart Steam" button in the toolbar
- **Automatic process management**: The application handles closing and reopening Steam
- **Status updates**: Real-time feedback during the restart process
- **Safety checks**: Cannot restart during active downloads
- **Multi-platform support**: Works on Windows, Linux, and macOS

### Default Steam Paths
- **Windows**: `C:\Program Files (x86)\Steam` or `C:\Program Files\Steam`
- **Linux**: `~/.steam/steam` or `~/.local/share/Steam`
- **macOS**: `~/Library/Application Support/Steam`

### Keyboard Shortcuts
- **Enter/Space**: Add game to Steam
- **Ctrl+R**: Restart Steam
- **F5**: Refresh web browser
- **F1**: Display detailed help
- **Ctrl+Q**: Quick quit

### Mouse Controls
- **Click on button**: Add game to Steam
- **Dropdown menus**: Switch sites or change language
- **Resize**: Drag borders to adjust window size


### Generated Files
- **config.json**: Saves Steam path, language preference, and settings
- **temp/**: Temporary folder for downloads (auto-cleaned)
- **logs/**: Installation history (if enabled)

## 📋 File Support

The application automatically handles and installs the following file types:
- **.manifest** files → Steam depotcache folder
- **.lua** files → Steam plugins folder
- **.vdf** files → Steam plugins folder
- **.acf** files → Steam steamapps folder

## 🔄 Version History

### v2.0.0
- Added multilingual support (English, French, Spanish, German)
- Implemented Steam restart functionality
- Added multiple site support (SteamDB, Steam Store)
- Enhanced UI with language selector
- Improved process management for Steam
- Better error handling and status updates
- Added force-close capability for stuck Steam processes
- Improved download reliability with multi-URL fallback
- Enhanced visual feedback during operations

### v1.0.0
- Initial version with support for adding games via manifests and lua
- Modern user interface
- Version .exe for Windows
- Python support for Windows, Linux, and macOS


## 🙏 Acknowledgments

- **SPIN0ZAi** for the SB_manifest_DB repository

## ⚠️ Notes

- Administrator rights are recommended for full functionality
- The application requires an active internet connection for downloads
- Steam must be installed on your system
- Some games may not be available in the database
