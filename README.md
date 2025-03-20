# DiscordBot 

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Sponsor](https://img.shields.io/badge/Sponsor-❤️-red.svg)](https://ko-fi.com/jozsef)

## 🌐 Languages / Idiomas / Nyelvek / Langues
- [English 🇬🇧](#english)
- [Español 🇪🇸](#spanish)
- [Magyar 🇭🇺](#hungarian)
- [Français 🇫🇷](#french)

<a id="english"></a>
## 🇬🇧 English

### Description
This is a modular Discord bot built using py-cord with support for both slash commands and traditional prefix commands. The bot includes modules for moderation, music playback, and custom event handling.

### Environment Setup
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/DiscordBot.git
    cd DiscordBot
    ```
2. Set up the virtual environment (see above)
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Run the bot:
    ```bash
    python main.py
    ```
    - The bot will prompt you for the necessary configuration values on first run.

### Configuration
The bot uses environment variables stored in a .env file. When running for the first time, you'll be prompted for:
- Discord Bot Token (from Discord Developer Portal)
- Command Prefix (e.g. !, ?, ., etc.)
- Owner ID (your Discord user ID)
- Guild ID (your server ID)

### Features
- Modular command system with extension loading
- Support for slash commands and prefix commands
- Automatic environment configuration
- Easy to extend with new features

### Commands
Commands are organized in extension modules. Refer to the extension documentation for available commands.

<a id="spanish"></a>
## 🇪🇸 Español

### Descripción
Este es un bot de Discord modular construido usando py-cord con soporte para comandos slash y comandos tradicionales con prefijo. El bot incluye módulos para moderación, reproducción de música y manejo de eventos personalizados.

### Configuración del Entorno
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Instalación
1. Clona el repositorio:
    ```bash
    git clone https://github.com/yourusername/DiscordBot.git
    cd DiscordBot
    ```
2. Configura el entorno virtual (ver arriba)
3. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
4. Ejecuta el bot:
    ```bash
    python main.py
    ```
    - El bot te pedirá los valores de configuración necesarios en la primera ejecución.

### Configuración
El bot utiliza variables de entorno almacenadas en un archivo .env. Al ejecutar por primera vez, se te pedirá:
- Token del Bot de Discord (del Portal de Desarrolladores de Discord)
- Prefijo de Comandos (por ejemplo !, ?, ., etc.)
- ID del Propietario (tu ID de usuario de Discord)
- ID del Servidor (ID de tu servidor)

### Características
- Sistema de comandos modular con carga de extensiones
- Soporte para comandos slash y comandos con prefijo
- Configuración automática del entorno
- Fácil de extender con nuevas funcionalidades

### Comandos
Los comandos están organizados en módulos de extensión. Consulta la documentación de las extensiones para conocer los comandos disponibles.

<a id="hungarian"></a>
## 🇭🇺 Magyar

### Leírás
Ez egy moduláris Discord bot, amely py-cord segítségével készült, és támogatja mind a perjel parancsokat, mind a hagyományos előtag parancsokat. A bot tartalmaz moderációs, zenelejátszó modulokat és egyéni eseménykezelést.

### Környezet beállítása
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Telepítés
1. Klónozd a tárolót:
    ```bash
    git clone https://github.com/yourusername/DiscordBot.git
    cd DiscordBot
    ```
2. Állítsd be a virtuális környezetet (lásd fentebb)
3. Telepítsd a függőségeket:
    ```bash
    pip install -r requirements.txt
    ```
4. Futtasd a botot:
    ```bash
    python main.py
    ```
    - A bot az első futtatáskor kérni fogja a szükséges konfigurációs értékeket.

### Konfiguráció
A bot a .env fájlban tárolt környezeti változókat használja. Az első futtatáskor a következőket kéri:
- Discord Bot Token (a Discord Developer Portalról)
- Parancs előtag (például !, ?, ., stb.)
- Tulajdonos ID (a Discord felhasználói azonosítód)
- Szerver ID (a szervered azonosítója)

### Jellemzők
- Moduláris parancsrendszer bővítmények betöltésével
- Támogatás perjel parancsokhoz és előtag parancsokhoz
- Automatikus környezeti konfiguráció
- Könnyen bővíthető új funkciókkal

### Parancsok
A parancsok bővítménymodulokban vannak szervezve. A rendelkezésre álló parancsokért lásd a bővítmények dokumentációját.

<a id="french"></a>
## 🇫🇷 Français

### Description
C'est un bot Discord modulaire construit en utilisant py-cord avec support pour les commandes slash et les commandes traditionnelles à préfixe. Le bot inclut des modules pour la modération, la lecture de musique et la gestion d'événements personnalisés.

### Configuration de l'environnement
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Installation
1. Cloner le dépôt:
    ```bash
    git clone https://github.com/yourusername/DiscordBot.git
    cd DiscordBot
    ```
2. Configurer l'environnement virtuel (voir ci-dessus)
3. Installer les dépendances:
    ```bash
    pip install -r requirements.txt
    ```
4. Exécuter le bot:
    ```bash
    python bot.py
    ```
    - Le bot vous demandera les valeurs de configuration nécessaires lors de la première exécution.

### Configuration
Le bot utilise des variables d'environnement stockées dans un fichier .env. Lors de la première exécution, il vous sera demandé:
- Token du Bot Discord (du Portail Développeur Discord)
- Préfixe de Commande (par exemple !, ?, ., etc.)
- ID du Propriétaire (votre ID utilisateur Discord)
- ID du Serveur (ID de votre serveur)

### Fonctionnalités
- Système de commandes modulaire avec chargement d'extensions
- Support pour les commandes slash et les commandes à préfixe
- Configuration automatique de l'environnement
- Facile à étendre avec de nouvelles fonctionnalités

### Commandes
Les commandes sont organisées dans des modules d'extension. Consultez la documentation des extensions pour les commandes disponibles.

## License / Licencia / Licenc / Licence
This project is licensed under the MIT License - see the LICENSE file for details.