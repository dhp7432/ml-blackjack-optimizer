# Configure WSL as Default Terminal

## Method 1: Cursor/VS Code Settings (Recommended)
The `.vscode/settings.json` file has been created to set WSL as default.

## Method 2: Windows Terminal Settings
1. Open **Windows Terminal**
2. Press `Ctrl + ,` (Settings)
3. Go to **Startup** tab
4. Set **Default profile** to your WSL distribution (e.g., "Ubuntu")

## Method 3: Global Windows Terminal Config
Add this to your Windows Terminal `settings.json`:

```json
{
    "defaultProfile": "{2c4de342-38b7-51cf-b940-2309a097f518}",
    "profiles": {
        "defaults": {},
        "list": [
            {
                "guid": "{2c4de342-38b7-51cf-b940-2309a097f518}",
                "hidden": false,
                "name": "Ubuntu",
                "source": "Windows.Terminal.Wsl"
            }
        ]
    }
}
```

## Method 4: Environment Variable
Set in Windows:
```cmd
setx COMSPEC "wsl.exe"
```

## Method 5: PowerShell Profile
Add to your PowerShell profile:
```powershell
# Auto-launch WSL
wsl
```

## Verification Commands
Test in your terminal:
```bash
# Check if you're in WSL
uname -a
# Should show Linux kernel info

# Check distribution
cat /etc/os-release
# Shows your Linux distribution

# Check current shell
echo $SHELL
# Should show /bin/bash or /bin/zsh
```

## WSL-Specific Python Setup
```bash
# Install Python in WSL
sudo apt update
sudo apt install python3 python3-pip

# Install required packages
pip3 install tkinter pandas openpyxl pyinstaller

# Navigate to your project (Windows drives are mounted under /mnt/)
cd /mnt/c/Users/Huy/Desktop/udemy/"python fullstack"

# Run your Python applications
python3 main.py
```

## Path Translation
- Windows: `C:\Users\Huy\Desktop\udemy\python fullstack`
- WSL: `/mnt/c/Users/Huy/Desktop/udemy/"python fullstack"`

## Common WSL Commands
```bash
# See all WSL distributions
wsl --list --verbose

# Set default distribution
wsl --set-default Ubuntu

# Restart WSL
wsl --shutdown
wsl

# Run Windows commands from WSL
cmd.exe /c "echo Hello from Windows"
powershell.exe -c "Get-Process"
```
