# 📦 Installing npm (Node Package Manager)

Since you have Node.js but npm is missing, here are several ways to install npm:

## 🚀 Quick Solutions

### Option 1: Reinstall Node.js with npm (Recommended)
1. **Download Node.js** from [https://nodejs.org/](https://nodejs.org/)
2. **Choose the LTS version** (includes npm)
3. **Run the installer** - it will install both Node.js and npm
4. **Restart your terminal/command prompt**

### Option 2: Install npm separately
```bash
# Windows (using PowerShell as Administrator)
Set-ExecutionPolicy Unrestricted -Scope CurrentUser -Force
npm install -g npm@latest

# macOS/Linux
curl -qL https://www.npmjs.org/install.sh | sh
```

### Option 3: Use Yarn instead of npm
```bash
# Install Yarn globally
npm install -g yarn

# Then use yarn instead of npm
yarn install
yarn start
```

## 🔧 Manual Installation

### Windows
1. **Download Node.js installer** from [nodejs.org](https://nodejs.org/)
2. **Run installer as Administrator**
3. **Make sure "npm package manager" is checked** during installation
4. **Restart your system**

### macOS
```bash
# Using Homebrew
brew install node

# Using MacPorts
sudo port install nodejs
```

### Linux (Ubuntu/Debian)
```bash
# Update package list
sudo apt update

# Install Node.js and npm
sudo apt install nodejs npm

# Verify installation
node --version
npm --version
```

### Linux (CentOS/RHEL/Fedora)
```bash
# Install Node.js and npm
sudo yum install nodejs npm
# or for newer versions:
sudo dnf install nodejs npm
```

## 🐛 Troubleshooting

### If npm is still not found after installation:
1. **Check PATH environment variable**
2. **Restart your terminal/command prompt**
3. **Restart your computer**

### Windows PATH check:
1. **Open System Properties** → **Environment Variables**
2. **Check if these paths exist in PATH:**
   - `C:\Program Files\nodejs\`
   - `%APPDATA%\npm`

### macOS/Linux PATH check:
```bash
echo $PATH
which node
which npm
```

## ✅ Verification

After installation, verify everything works:
```bash
node --version
npm --version
```

## 🎯 Alternative: Use Yarn

If npm continues to cause issues, you can use Yarn instead:

```bash
# Install Yarn
npm install -g yarn

# Use Yarn commands
yarn install    # instead of npm install
yarn start      # instead of npm start
```

## 🆘 Still Having Issues?

1. **Check Node.js installation**: `node --version`
2. **Check npm installation**: `npm --version`
3. **Try reinstalling Node.js completely**
4. **Use Yarn as an alternative**

---

**💡 Tip**: The easiest solution is usually to download the Node.js installer from [nodejs.org](https://nodejs.org/) which includes both Node.js and npm. 