# DiscordBot 

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
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

### File Structure
```
DiscordBot/
├── main.py               # Main entry point
├── requirements.txt      # Project dependencies
├── .env                  # Environment variables
├── .github/              # GitHub specific files
├── .gitignore            # Git ignore file
├── .vscode/              # VSCode settings
├── LICENSE               # Apache 2.0 license
├── README.md             # This documentation
└── src/                  # Source code directory
    ├── bot.py            # Core bot functionality
    ├── commands/         # General command modules
    │   ├── ping.py       # Ping command
    │   └── roulette.py   # Roulette game command
    ├── data/             # Data storage directory
    │   ├── audit_log.json # Audit logging data
    │   ├── birthdate.json # User birthdate data
    │   └── games.txt     # Games data
    ├── events/           # Event handling modules
    │   └── birthdate/    # Birthday event handling
    │       └── birthdate.py # Birthday event logic
    ├── moderation/       # Moderation modules
    │   ├── set_audit_log.py # Audit logging functionality
    │   └── set_prefix.py # Prefix setting functionality
    ├── music/            # Music functionality
    │   ├── music.py      # Main music module
    │   ├── handlers/     # Command and event handlers
    │   │   ├── command_handler/ # Music command handlers
    │   │   └── event_handler/    # Music event handlers
    │   ├── services/     # Music services
    │   │   ├── auto_disconnect_service.py
    │   │   ├── controller_service.py
    │   │   └── player_service.py
    │   └── utils/        # Music utilities
    │       ├── controller/ # Music controller
    │       ├── formatter.py # Formatting utilities
    │       ├── queue_manager.py # Queue management
    │       ├── voice_manager.py # Voice connection management
    │       └── youtube.py # YouTube integration
    └── utils/            # General utilities
        └── json_manager.py # JSON data handling
```

### Environment Setup
```bash
# Windows
python -m venv .myenv
.myenv\Scripts\activate

# Linux/macOS
python3 -m venv .myenv
source .myenv/bin/activate
```

### Installation Steps
1. **Prerequisites**:
   - Python 3.8 or higher
   - Git
   - Discord account with a registered application

2. **Clone the repository**:
   ```bash
   git clone https://github.com/JozsefIvanGafo/DiscordBot.git
   cd DiscordBot
   ```

3. **Create and activate virtual environment**:
   ```bash
   # Windows
   python -m venv .myenv
   .myenv\Scripts\activate
   
   # Linux/macOS
   python3 -m venv .myenv
   source .myenv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure the bot**:
   Run the bot for the first time to generate the configuration:
   ```bash
   python main.py
   ```
   The bot will prompt you for:
   - Discord Bot Token
   - Command Prefix
   - Owner ID
   - Guild ID

6. **Run the bot**:
   ```bash
   python main.py
   ```

### Configuration
The bot uses environment variables stored in a `.env` file. When running for the first time, you'll be prompted for:
- **Discord Bot Token**: Obtain from the [Discord Developer Portal](https://discord.com/developers/applications)
- **Command Prefix**: The character(s) that precede text commands (e.g., !, ?, ., etc.)
- **Owner ID**: Your Discord user ID (enable Developer Mode in Discord settings and right-click your name to copy ID)
- **Guild ID**: Your server ID (right-click the server name to copy ID)

### Features
- Modular command system with extension loading
- Support for slash commands and prefix commands
- Automatic environment configuration
- Easy to extend with new features

### Commands
The bot includes the following command categories:

#### General Commands
- `/help` - Displays a list of available commands
- `/ping` - Checks the bot's response time
- `/roulette` - Play a game of roulette

#### Moderation Commands
- `/set_audit_log <channel>` - Sets the channel for audit logging
- `/set_prefix <new_prefix>` - Changes the command prefix

#### Music Commands
- `/play <song>` - Plays a song from YouTube or URL
- `/pause` - Pauses the current song
- `/resume` - Resumes playback
- `/skip` - Skips to the next song in the queue
- `/queue` - Shows the current music queue
- `/stop` - Stops playback and clears the queue
- `/leave` - Disconnects the bot from voice channel
- `/music_channel` - Sets up a dedicated music control channel

#### Event Features
- Birthday announcements - Automatically sends birthday wishes to users

### Extending the Bot
You can create new command modules by adding files to the `src/commands/` directory:

```python
# Example: src/commands/mycommand.py
import discord

class MyCommand(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="mycommand", description="Description of my command")
    async def my_command(self, ctx):
        await ctx.respond("Hello from my custom command!")

def setup(bot):
    bot.add_cog(MyCommand(bot))
```

<a id="spanish"></a>
## 🇪🇸 Español

### Descripción
Este es un bot de Discord modular construido usando py-cord con soporte para comandos slash y comandos tradicionales con prefijo. El bot incluye módulos para moderación, reproducción de música y manejo de eventos personalizados.

### Estructura de Archivos
```
DiscordBot/
├── main.py               # Punto de entrada principal
├── requirements.txt      # Dependencias del proyecto
├── .env                  # Variables de entorno
├── .github/              # Archivos específicos de GitHub
├── .gitignore            # Archivo de exclusión de Git
├── .vscode/              # Configuraciones de VSCode
├── LICENSE               # Licencia Apache 2.0
├── README.md             # Esta documentación
└── src/                  # Directorio de código fuente
    ├── bot.py            # Funcionalidad principal del bot
    ├── commands/         # Módulos de comandos generales
    │   ├── ping.py       # Comando ping
    │   └── roulette.py   # Comando de juego de ruleta
    ├── data/             # Directorio de almacenamiento de datos
    │   ├── audit_log.json # Datos de registro de auditoría
    │   ├── birthdate.json # Datos de cumpleaños de usuarios
    │   └── games.txt     # Datos de juegos
    ├── events/           # Módulos de manejo de eventos
    │   └── birthdate/    # Manejo de eventos de cumpleaños
    │       └── birthdate.py # Lógica de eventos de cumpleaños
    ├── moderation/       # Módulos de moderación
    │   ├── set_audit_log.py # Funcionalidad de registro de auditoría
    │   └── set_prefix.py # Funcionalidad de configuración de prefijo
    ├── music/            # Funcionalidad de música
    │   ├── music.py      # Módulo principal de música
    │   ├── handlers/     # Manejadores de comandos y eventos
    │   │   ├── command_handler/ # Manejadores de comandos de música
    │   │   └── event_handler/    # Manejadores de eventos de música
    │   ├── services/     # Servicios de música
    │   │   ├── auto_disconnect_service.py
    │   │   ├── controller_service.py
    │   │   └── player_service.py
    │   └── utils/        # Utilidades de música
    │       ├── controller/ # Controlador de música
    │       ├── formatter.py # Utilidades de formato
    │       ├── queue_manager.py # Gestión de cola
    │       ├── voice_manager.py # Gestión de conexión de voz
    │       └── youtube.py # Integración con YouTube
    └── utils/            # Utilidades generales
        └── json_manager.py # Manejo de datos JSON
```

### Configuración del Entorno
```bash
# Windows
python -m venv .myenv
.myenv\Scripts\activate

# Linux/macOS
python3 -m venv .myenv
source .myenv/bin/activate
```

### Pasos de Instalación
1. **Prerrequisitos**:
   - Python 3.8 o superior
   - Git
   - Cuenta de Discord con una aplicación registrada

2. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/JozsefIvanGafo/DiscordBot.git
   cd DiscordBot
   ```

3. **Crear y activar el entorno virtual**:
   ```bash
   # Windows
   python -m venv .myenv
   .myenv\Scripts\activate
   
   # Linux/macOS
   python3 -m venv .myenv
   source .myenv/bin/activate
   ```

4. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configurar el bot**:
   Ejecuta el bot por primera vez para generar la configuración:
   ```bash
   python main.py
   ```
   El bot te pedirá:
   - Token de Bot de Discord
   - Prefijo de Comandos
   - ID del Propietario
   - ID del Servidor

6. **Ejecutar el bot**:
   ```bash
   python main.py
   ```

### Configuración
El bot utiliza variables de entorno almacenadas en un archivo `.env`. Al ejecutar por primera vez, se te pedirá:
- **Token del Bot de Discord**: Obtén del [Portal de Desarrolladores de Discord](https://discord.com/developers/applications)
- **Prefijo de Comandos**: Los caracteres que preceden a los comandos de texto (por ejemplo, !, ?, ., etc.)
- **ID del Propietario**: Tu ID de usuario de Discord (habilita el Modo Desarrollador en la configuración de Discord y haz clic derecho en tu nombre para copiar el ID)
- **ID del Servidor**: ID de tu servidor (haz clic derecho en el nombre del servidor para copiar el ID)

### Características
- Sistema de comandos modular con carga de extensiones
- Soporte para comandos slash y comandos con prefijo
- Configuración automática del entorno
- Fácil de extender con nuevas funcionalidades

### Comandos
El bot incluye las siguientes categorías de comandos:

#### Comandos Generales
- `/help` - Muestra una lista de comandos disponibles
- `/ping` - Comprueba el tiempo de respuesta del bot
- `/roulette` - Juega una partida de ruleta

#### Comandos de Moderación
- `/set_audit_log <canal>` - Establece el canal para registro de auditoría
- `/set_prefix <nuevo_prefijo>` - Cambia el prefijo de comandos

#### Comandos de Música
- `/play <canción>` - Reproduce una canción de YouTube o URL
- `/pause` - Pausa la canción actual
- `/resume` - Reanuda la reproducción
- `/skip` - Salta a la siguiente canción en la cola
- `/queue` - Muestra la cola de música actual
- `/stop` - Detiene la reproducción y limpia la cola
- `/leave` - Desconecta el bot del canal de voz
- `/music_channel` - Configura un canal dedicado para control de música

#### Características de Eventos
- Anuncios de cumpleaños - Envía automáticamente felicitaciones a los usuarios

### Extendiendo el Bot
Puedes crear nuevos módulos de comandos añadiendo archivos al directorio `src/commands/`:

```python
# Ejemplo: src/commands/micomando.py
import discord

class MiComando(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="micomando", description="Descripción de mi comando")
    async def mi_comando(self, ctx):
        await ctx.respond("¡Hola desde mi comando personalizado!")

def setup(bot):
    bot.add_cog(MiComando(bot))
```

<a id="hungarian"></a>
## 🇭🇺 Magyar

### Leírás
Ez egy moduláris Discord bot, amely py-cord segítségével készült, és támogatja mind a perjel parancsokat, mind a hagyományos előtag parancsokat. A bot tartalmaz moderációs, zenelejátszó modulokat és egyéni eseménykezelést.

### Fájl Szerkezet
```
DiscordBot/
├── main.py               # Fő belépési pont
├── requirements.txt      # Projekt függőségek
├── .env                  # Környezeti változók
├── .github/              # GitHub-specifikus fájlok
├── .gitignore            # Git kizárási fájl
├── .vscode/              # VSCode beállítások
├── LICENSE               # Apache 2.0 licenc
├── README.md             # Ez a dokumentáció
└── src/                  # Forráskód könyvtár
    ├── bot.py            # Alapvető bot funkcionalitás
    ├── commands/         # Általános parancsi modulok
    │   ├── ping.py       # Ping parancs
    │   └── roulette.py   # Rulett játék parancs
    ├── data/             # Adattárolási könyvtár
    │   ├── audit_log.json # Audit naplózási adatok
    │   ├── birthdate.json # Felhasználói születésnapi adatok
    │   └── games.txt     # Játék adatok
    ├── events/           # Eseménykezelő modulok
    │   └── birthdate/    # Születésnapi eseménykezelés
    │       └── birthdate.py # Születésnapi esemény logika
    ├── moderation/       # Moderációs modulok
    │   ├── set_audit_log.py # Audit naplózási funkcionalitás
    │   └── set_prefix.py # Előtag beállítási funkcionalitás
    ├── music/            # Zenei funkcionalitás
    │   ├── music.py      # Fő zenei modul
    │   ├── handlers/     # Parancs- és eseménykezelők
    │   │   ├── command_handler/ # Zene parancskezelők
    │   │   └── event_handler/    # Zenei eseménykezelők
    │   ├── services/     # Zenei szolgáltatások
    │   │   ├── auto_disconnect_service.py
    │   │   ├── controller_service.py
    │   │   └── player_service.py
    │   └── utils/        # Zenei segédprogramok
    │       ├── controller/ # Zenei vezérlő
    │       ├── formatter.py # Formázási segédprogramok
    │       ├── queue_manager.py # Sorkezelés
    │       ├── voice_manager.py # Hangkapcsolat kezelés
    │       └── youtube.py # YouTube integráció
    └── utils/            # Általános segédprogramok
        └── json_manager.py # JSON adatkezelés
```

### Környezet beállítása
```bash
# Windows
python -m venv .myenv
.myenv\Scripts\activate

# Linux/macOS
python3 -m venv .myenv
source .myenv/bin/activate
```

### Telepítési Lépések
1. **Előfeltételek**:
   - Python 3.8 vagy újabb
   - Git
   - Discord fiók regisztrált alkalmazással

2. **Klónozd a tárolót**:
   ```bash
   git clone https://github.com/JozsefIvanGafo/DiscordBot.git
   cd DiscordBot
   ```

3. **Hozz létre és aktiválj virtuális környezetet**:
   ```bash
   # Windows
   python -m venv .myenv
   .myenv\Scripts\activate
   
   # Linux/macOS
   python3 -m venv .myenv
   source .myenv/bin/activate
   ```

4. **Telepítsd a függőségeket**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Konfiguráld a botot**:
   Futtasd a botot először a konfiguráció létrehozásához:
   ```bash
   python main.py
   ```
   A bot a következőket kéri:
   - Discord Bot Token
   - Parancs Előtag
   - Tulajdonos ID
   - Szerver ID

6. **Futtasd a botot**:
   ```bash
   python main.py
   ```

### Konfiguráció
A bot a `.env` fájlban tárolt környezeti változókat használja. Az első futtatáskor a következőket kéri:
- **Discord Bot Token**: A [Discord Developer Portal](https://discord.com/developers/applications)-ról szerezhető be
- **Parancs Előtag**: A szöveges parancsokat megelőző karakter(ek) (például !, ?, ., stb.)
- **Tulajdonos ID**: A Discord felhasználói azonosítód (engedélyezd a Fejlesztői Módot a Discord beállításaiban, majd jobb kattintás a nevedre az ID másolásához)
- **Szerver ID**: A szervered azonosítója (jobb kattintás a szerver nevére az ID másolásához)

### Jellemzők
- Moduláris parancsrendszer bővítmények betöltésével
- Támogatás perjel parancsokhoz és előtag parancsokhoz
- Automatikus környezeti konfiguráció
- Könnyen bővíthető új funkciókkal

### Parancsok
A bot a következő parancskategóriákat tartalmazza:

#### Általános Parancsok
- `/help` - Megjeleníti az elérhető parancsok listáját
- `/ping` - Ellenőrzi a bot válaszidejét
- `/roulette` - Rulettjáték játszása

#### Moderációs Parancsok
- `/set_audit_log <csatorna>` - Beállítja a csatornát az audit naplózáshoz
- `/set_prefix <új_előtag>` - Megváltoztatja a parancs előtagot

#### Zene Parancsok
- `/play <dal>` - Lejátszik egy dalt YouTube-ról vagy URL-ről
- `/pause` - Szünetelteti az aktuális dalt
- `/resume` - Folytatja a lejátszást
- `/skip` - A következő dalra ugrik a sorban
- `/queue` - Megjeleníti az aktuális zenei sort
- `/stop` - Leállítja a lejátszást és törli a sort
- `/leave` - Lecsatlakoztatja a botot a hangcsatornáról
- `/music_channel` - Beállít egy dedikált zenei vezérlő csatornát

#### Esemény Funkciók
- Születésnapi köszöntések - Automatikusan küld születésnapi jókívánságokat a felhasználóknak

### Bot Bővítése
Új parancsmodulokat hozhatsz létre a `src/commands/` könyvtárhoz való fájlok hozzáadásával:

```python
# Példa: src/commands/sajatparancs.py
import discord

class SajatParancs(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="sajatparancs", description="Saját parancs leírása")
    async def sajat_parancs(self, ctx):
        await ctx.respond("Üdvözlet a saját parancsomból!")

def setup(bot):
    bot.add_cog(SajatParancs(bot))
```

<a id="french"></a>
## 🇫🇷 Français

### Description
C'est un bot Discord modulaire construit en utilisant py-cord avec support pour les commandes slash et les commandes traditionnelles à préfixe. Le bot inclut des modules pour la modération, la lecture de musique et la gestion d'événements personnalisés.

### Structure des Fichiers
```
DiscordBot/
├── main.py               # Point d'entrée principal
├── requirements.txt      # Dépendances du projet
├── .env                  # Variables d'environnement
├── .github/              # Fichiers spécifiques à GitHub
├── .gitignore            # Fichier d'exclusion Git
├── .vscode/              # Paramètres VSCode
├── LICENSE               # Licence Apache 2.0
├── README.md             # Cette documentation
└── src/                  # Répertoire de code source
    ├── bot.py            # Fonctionnalité principale du bot
    ├── commands/         # Modules de commandes générales
    │   ├── ping.py       # Commande ping
    │   └── roulette.py   # Commande de jeu de roulette
    ├── data/             # Répertoire de stockage de données
    │   ├── audit_log.json # Données de journalisation d'audit
    │   ├── birthdate.json # Données d'anniversaire des utilisateurs
    │   └── games.txt     # Données de jeux
    ├── events/           # Modules de gestion d'événements
    │   └── birthdate/    # Gestion d'événements d'anniversaire
    │       └── birthdate.py # Logique d'événements d'anniversaire
    ├── moderation/       # Modules de modération
    │   ├── set_audit_log.py # Fonctionnalité de journalisation d'audit
    │   └── set_prefix.py # Fonctionnalité de définition de préfixe
    ├── music/            # Fonctionnalité musicale
    │   ├── music.py      # Module musical principal
    │   ├── handlers/     # Gestionnaires de commandes et d'événements
    │   │   ├── command_handler/ # Gestionnaires de commandes musicales
    │   │   └── event_handler/    # Gestionnaires d'événements musicaux
    │   ├── services/     # Services musicaux
    │   │   ├── auto_disconnect_service.py
    │   │   ├── controller_service.py
    │   │   └── player_service.py
    │   └── utils/        # Utilitaires musicaux
    │       ├── controller/ # Contrôleur musical
    │       ├── formatter.py # Utilitaires de formatage
    │       ├── queue_manager.py # Gestion de file d'attente
    │       ├── voice_manager.py # Gestion de connexion vocale
    │       └── youtube.py # Intégration YouTube
    └── utils/            # Utilitaires généraux
        └── json_manager.py # Gestion de données JSON
```

### Configuration de l'environnement
```bash
# Windows
python -m venv .myenv
.myenv\Scripts\activate

# Linux/macOS
python3 -m venv .myenv
source .myenv/bin/activate
```

### Étapes d'Installation
1. **Prérequis**:
   - Python 3.8 ou supérieur
   - Git
   - Compte Discord avec une application enregistrée

2. **Cloner le dépôt**:
   ```bash
   git clone https://github.com/JozsefIvanGafo/DiscordBot.git
   cd DiscordBot
   ```

3. **Créer et activer l'environnement virtuel**:
   ```bash
   # Windows
   python -m venv .myenv
   .myenv\Scripts\activate
   
   # Linux/macOS
   python3 -m venv .myenv
   source .myenv/bin/activate
   ```

4. **Installer les dépendances**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configurer le bot**:
   Exécutez le bot pour la première fois pour générer la configuration:
   ```bash
   python main.py
   ```
   Le bot vous demandera:
   - Token du Bot Discord
   - Préfixe de Commande
   - ID du Propriétaire
   - ID du Serveur

6. **Exécuter le bot**:
   ```bash
   python main.py
   ```

### Configuration
Le bot utilise des variables d'environnement stockées dans un fichier `.env`. Lors de la première exécution, il vous sera demandé:
- **Token du Bot Discord**: Obtenir depuis le [Portail Développeur Discord](https://discord.com/developers/applications)
- **Préfixe de Commande**: Les caractères qui précèdent les commandes textuelles (par exemple !, ?, ., etc.)
- **ID du Propriétaire**: Votre ID utilisateur Discord (activez le Mode Développeur dans les paramètres Discord et faites un clic droit sur votre nom pour copier l'ID)
- **ID du Serveur**: ID de votre serveur (clic droit sur le nom du serveur pour copier l'ID)

### Fonctionnalités
- Système de commandes modulaire avec chargement d'extensions
- Support pour les commandes slash et les commandes à préfixe
- Configuration automatique de l'environnement
- Facile à étendre avec de nouvelles fonctionnalités

### Commandes
Le bot inclut les catégories de commandes suivantes:

#### Commandes Générales
- `/help` - Affiche une liste des commandes disponibles
- `/ping` - Vérifie le temps de réponse du bot
- `/roulette` - Jouer une partie de roulette

#### Commandes de Modération
- `/set_audit_log <canal>` - Définit le canal pour la journalisation d'audit
- `/set_prefix <nouveau_préfixe>` - Change le préfixe de commande

#### Commandes de Musique
- `/play <chanson>` - Joue une chanson depuis YouTube ou URL
- `/pause` - Met en pause la chanson actuelle
- `/resume` - Reprend la lecture
- `/skip` - Passe à la chanson suivante dans la file d'attente
- `/queue` - Affiche la file d'attente musicale actuelle
- `/stop` - Arrête la lecture et vide la file d'attente
- `/leave` - Déconnecte le bot du canal vocal
- `/music_channel` - Configure un canal dédié au contrôle de la musique

#### Fonctionnalités d'Événements
- Annonces d'anniversaire - Envoie automatiquement des vœux d'anniversaire aux utilisateurs

### Extension du Bot
Vous pouvez créer de nouveaux modules de commandes en ajoutant des fichiers au répertoire `src/commands/`:

```python
# Exemple: src/commands/macommande.py
import discord

class MaCommande(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="macommande", description="Description de ma commande")
    async def ma_commande(self, ctx):
        await ctx.respond("Bonjour depuis ma commande personnalisée!")

def setup(bot):
    bot.add_cog(MaCommande(bot))
```

## License / Licencia / Licenc / Licence
This project is licensed under the Apache 2.0 License - see the LICENSE file for details.