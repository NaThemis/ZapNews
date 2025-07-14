# Sur Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip

# Installation packages Python
pip3 install openai feedparser schedule

#!/bin/bash

# =============================================================================
# Installation Environment Virtuel Python - News Workflow
# =============================================================================

echo "🚀 Installation de l'environnement virtuel Python pour News Workflow"
echo "=================================================================="

# 1. Création du dossier projet
echo "📁 Création du dossier projet..."
mkdir -p ~/zapnews
cd ~/zapnews

# 2. Vérification de Python
echo "🐍 Vérification de Python..."
if command -v python3 &> /dev/null; then
    echo "✅ Python3 trouvé: $(python3 --version)"
else
    echo "❌ Python3 non trouvé. Installation..."
    # Ubuntu/Debian
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv
    # CentOS/RHEL
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3 python3-pip python3-venv
    # MacOS
    elif command -v brew &> /dev/null; then
        brew install python3
    else
        echo "❌ Impossible d'installer Python automatiquement. Installez-le manuellement."
        exit 1
    fi
fi

# 3. Création de l'environnement virtuel
echo "🔧 Création de l'environnement virtuel..."
python3 -m venv zapnews-env

# 4. Activation de l'environnement virtuel
echo "⚡ Activation de l'environnement virtuel..."
source zapnews-env/bin/activate

# Vérification de l'activation
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Environnement virtuel activé: $VIRTUAL_ENV"
else
    echo "❌ Erreur d'activation de l'environnement virtuel"
    exit 1
fi

# 5. Mise à jour de pip
echo "📦 Mise à jour de pip..."
pip install --upgrade pip

# 6. Installation des dépendances
echo "📚 Installation des librairies requises..."

# Création du fichier requirements.txt
cat > requirements.txt << EOF
# News Workflow Dependencies
openai==0.28.1
feedparser==6.0.10
schedule==1.2.0
requests==2.31.0
python-dateutil==2.8.2
beautifulsoup4==4.12.2
lxml==4.9.3
EOF

# Installation des packages
pip install -r requirements.txt

echo ""
echo "📋 Packages installés:"
pip list

# 7. Création du script principal
echo ""
echo "📝 Création du script principal..."

cat > zapnews.py << 'EOF'
#!/usr/bin/env python3