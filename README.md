# GameBase

Catálogo interactivo de videojuegos con emulador integrado, búsqueda en tiempo real, fichas enriquecidas desde IGDB y asistente de IA.

> Trabajo Práctico 3 — Práctica Profesional Integrador · Grupo 3

---

## Tabla de contenidos

- [Demo y diseño](#demo-y-diseño)
- [Features](#features)
- [Tecnologías](#tecnologías)
- [Arquitectura](#arquitectura)
- [Levantar el proyecto](#levantar-el-proyecto)
- [Variables de entorno](#variables-de-entorno)
- [Correr los tests](#correr-los-tests)
- [Estructura del proyecto](#estructura-del-proyecto)
- [APIs externas](#apis-externas)
- [Deploy en Render](#deploy-en-render)
- [Links del proyecto](#links-del-proyecto)

---

## Demo y diseño

| Recurso | Link |
|---|---|
| Diseño Figma | https://www.figma.com/design/zlhrbHjXVQvIa3nRkl8iRL/Inventario-Juegos |
| Trello | https://trello.com/b/QW7cn5ch/ppi2-tp3-grupo-3 |
| Minuta | https://docs.google.com/document/d/17HYPCR3TJa0am82yZSlufUNVLnFlhk4Aqx6s1UgLBwo |
| Casos de uso | https://1drv.ms/x/c/07dec0e241a74c12/EXz3a8nMl-ZJqRXkyb43fmgBuCqGcIaZBigk9U7oZ97UzA |
| Texto descriptivo | https://docs.google.com/document/d/11Qe2bSqGOx7W_UvtJo15sN2sc5ofwtq_bZfuXuOqs0I |

---

## Features

### Biblioteca
- **16.598 juegos** cargados desde el dataset VGSales al primer inicio
- **Estanterías por plataforma** (NES, SNES, GB, GBA, N64, PS, PS2, Genesis, DS, Atari 2600)
- **Buscador unificado en tiempo real** — un solo campo para nombre, plataforma, género y año (ej: `mario 1985`); los resultados aparecen 350ms después de tipear, sin necesidad de apretar Enter
- **"Ver todo"** por plataforma con paginación incremental ("cargar más")
- **Portadas lazy**: cuando una tarjeta sin imagen entra al viewport, la app consulta IGDB en segundo plano y muestra la portada al instante (máx. 3 llamadas simultáneas); el resultado queda guardado en la DB para la próxima visita

### Ficha de juego
- Datos enriquecidos desde IGDB: portada HD, descripción, puntuaciones de crítica y usuarios, modos de juego, calificación de edad (ESRB/PEGI)
- **Descripción traducida al español** con DeepL (resultado cacheado en `Summary_ES` para no repetir llamadas)
- Galería de capturas con lightbox
- Trailer de YouTube embebido
- Personajes del juego con foto
- Ficha técnica: desarrolladora, editora, motor, saga, ventas globales
- **Juegos similares** desde el catálogo propio (mismo género + plataforma, clickeables para navegar directo a su ficha)
- También conocido como (nombres alternativos de IGDB)

### Favoritos y perfil
- Marcar/desmarcar favoritos con ★ desde cualquier tarjeta o ficha
- **Página de perfil** accesible desde el nombre de usuario, con grilla de juegos guardados
- Favoritos persistidos en `localStorage`

### Emulador
- Sección dedicada con soporte para ROMs de NES vía **EmulatorJS**
- Incluye 3 juegos homebrew listos para jugar (Pentablocat, BladeBuster, Desert Escape)
- **Juego demo** jugable sin ROM externa (colección de monedas con D-pad)
- Detección de ROM faltante con instrucción para agregarla
- Guardar/cargar estados, pantalla completa, controles por teclado y touch

### Asistente IA
- **Chat flotante** (FAB) conectado a Google Gemini 2.5 Flash
- Responde preguntas sobre juegos, consolas y épocas del catálogo

### Autenticación
- Login con **Google OAuth** (django-allauth)
- Registro e inicio de sesión tradicional con usuario y contraseña
- Todas las vistas protegidas: redirige al login si no está autenticado

---

## Tecnologías

### Backend
| Tecnología | Uso |
|---|---|
| Python 3.11+ | Lenguaje principal |
| Django 4.2 | Framework web, ORM, sistema de plantillas |
| django-allauth | Autenticación social (Google OAuth) |
| Gunicorn | Servidor WSGI para producción |
| WhiteNoise | Servicio de archivos estáticos en producción |
| SQLite | Base de datos en desarrollo |
| PostgreSQL | Base de datos en producción (Render) |
| dj-database-url | Configuración de DB via `DATABASE_URL` |
| python-dotenv / python-decouple | Manejo de variables de entorno |

### Frontend
| Tecnología | Uso |
|---|---|
| React 18 (CDN) | UI reactiva, sin paso de build |
| Babel Standalone 7 | Transpilación de JSX en el navegador |
| CSS custom (pixel art) | Diseño retro inspirado en Game Boy |
| EmulatorJS | Emulación de ROMs en el navegador |

### APIs externas
| API | Uso |
|---|---|
| IGDB (Twitch) | Portadas, descripciones, screenshots, ratings, similares |
| DeepL (Free) | Traducción de descripciones al español |
| Google Gemini 2.5 Flash | Asistente IA de chat |

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                        Browser                          │
│                                                         │
│   React 18 (CDN) + Babel Standalone                     │
│   ┌──────────┬─────────────┬────────────┬───────────┐   │
│   │ gb-utils │gb-components│ gb-detail  │gb-emulator│   │
│   └──────────┴─────────────┴────────────┴───────────┘   │
│   ┌─────────────────────────────────────────────────┐   │
│   │                   gb-app (App + TopBar)          │   │
│   └─────────────────────────────────────────────────┘   │
│   ┌─────────────────────────────────────────────────┐   │
│   │                gb-chat (vanilla JS)              │   │
│   └─────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/JSON
┌────────────────────▼────────────────────────────────────┐
│                    Django 4.2                           │
│                                                         │
│  views/api.py  (solo HTTP: parseo + JsonResponse)       │
│       │                                                 │
│       ├── services/game_service.py                      │
│       │     search_games(), get_shelves(), game_dict()  │
│       │                                                 │
│       ├── services/igdb_service.py                      │
│       │     get_enriched_game()                         │
│       │     _get_db_similar_games()  ← fallback DB      │
│       │                                                 │
│       └── services/chat_service.py                      │
│             get_chat_reply()                            │
│                                                         │
│  igdb_api.py   (cliente IGDB + caché de token Twitch)   │
│  deepl_translate.py  (cliente DeepL)                    │
│                                                         │
│  models.py: Juego (16.598 registros VGSales)            │
└─────────────┬───────────────────────────────────────────┘
              │
    ┌─────────▼────────────────────────────────────┐
    │  Base de datos                               │
    │  SQLite (dev) · PostgreSQL (producción)      │
    └─────────┬────────────────────────────────────┘
              │
    ┌─────────▼──────────────────────────────┐
    │   APIs externas                        │
    │   IGDB · DeepL · Google Gemini         │
    └────────────────────────────────────────┘
```

### Principios de diseño
- **Separación de responsabilidades**: las vistas no tienen lógica de negocio; la lógica vive en `services/`
- **Frontend modular**: el JS está dividido en 6 archivos estáticos cargados secuencialmente; sin bundler ni paso de build
- **Caché de datos externos**: el token de Twitch, las portadas y las traducciones se persisten en la DB para no repetir llamadas

---

## Levantar el proyecto

### Requisitos previos
- Python 3.11 o superior
- pip

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/<tu-usuario>/PPI3-INTEGRADOR.git
cd PPI3-INTEGRADOR/djangoback/tp3_crud

# 2. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
# Copiar el ejemplo y completar con tus claves (ver sección siguiente)
cp .env.example .env

# 5. Crear la base de datos y cargar el dataset
python manage.py migrate
# Los 16.598 juegos se importan automáticamente en el primer inicio

# 6. Levantar el servidor de desarrollo
python manage.py runserver
```

Abrí http://127.0.0.1:8000 en el navegador.

> **Nota:** Al primer inicio el servidor carga el dataset VGSales desde `apps/juego/fixtures/vgsales.json`. Puede tardar unos segundos.

---

## Variables de entorno

Crear el archivo `.env` en `djangoback/tp3_crud/` (ver `.env.example`):

```env
# Django
SECRET_KEY=tu_secret_key_de_django
DEBUG=True

# Base de datos (opcional en desarrollo — sin esta variable usa SQLite local)
# DATABASE_URL=postgresql://user:pass@host/dbname

# IGDB / Twitch — https://api.igdb.com (crear app en dev.twitch.tv)
TWITCH_CLIENT_ID=tu_client_id
TWITCH_CLIENT_SECRET=tu_client_secret

# DeepL (plan Free) — https://www.deepl.com/pro#developer
DEEPL_API_KEY=tu_clave_deepl

# Google Gemini — https://aistudio.google.com/app/apikey
GEMINI_API_KEY=tu_clave_gemini

# Google OAuth — https://console.cloud.google.com/apis/credentials
GOOGLE_CLIENT_ID=tu_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu_client_secret
```

### Obtener las claves

| Clave | Dónde obtenerla | Plan mínimo |
|---|---|---|
| `TWITCH_CLIENT_ID` / `SECRET` | [dev.twitch.tv](https://dev.twitch.tv) → crear aplicación | Gratuito |
| `DEEPL_API_KEY` | [deepl.com/pro](https://www.deepl.com/pro#developer) | Free (500.000 chars/mes) |
| `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com/app/apikey) | Gratuito |
| `GOOGLE_CLIENT_ID` / `SECRET` | Google Cloud Console → Credenciales OAuth | Gratuito |

> **Importante:** Sin `TWITCH_CLIENT_ID` y `TWITCH_CLIENT_SECRET` las fichas de juego no cargarán datos de IGDB. El resto de la app funciona normalmente.

---

## Correr los tests

Los tests se ubican en `apps/juego/test_*.py` y usan la base de datos en memoria. No requieren conexión a internet ni claves de API (las dependencias externas están mockeadas).

```bash
# Desde djangoback/tp3_crud/

# Todos los tests
python manage.py test apps.juego.test_game_service apps.juego.test_igdb_service apps.juego.test_chat_service apps.juego.test_views

# Por módulo
python manage.py test apps.juego.test_game_service   # búsqueda, estantes, game_dict
python manage.py test apps.juego.test_igdb_service   # enriquecimiento IGDB, similares DB
python manage.py test apps.juego.test_chat_service   # servicio de chat Gemini
python manage.py test apps.juego.test_views          # capa HTTP / endpoints

# Con detalle de cada test
python manage.py test apps.juego --verbosity=2
```

### Cobertura

| Archivo | Tests | Qué cubre |
|---|---|---|
| `test_game_service.py` | 21 | `game_dict`, `search_games`, `get_shelves` |
| `test_igdb_service.py` | 19 | Enriquecimiento, caché de traducción, similares DB, persistencia |
| `test_chat_service.py` | 7 | Validaciones, clave faltante, integración Gemini (mockeada) |
| `test_views.py` | 16 | Autenticación, códigos HTTP, modo búsqueda vs estantes |

---

## Estructura del proyecto

```
PPI3-INTEGRADOR/
├── render.yaml                     # Configuración de deploy en Render
├── djangoback/
│   └── tp3_crud/
│       ├── manage.py
│       ├── requirements.txt
│       ├── .env.example            # Plantilla de variables de entorno
│       ├── build.sh                # Script de build para Render
│       │
│       ├── tp3_crud/               # Configuración Django
│       │   ├── settings.py         # DB: SQLite en dev, PostgreSQL en prod (DATABASE_URL)
│       │   ├── urls.py
│       │   └── wsgi.py
│       │
│       ├── apps/juego/             # App principal
│       │   ├── models.py           # Modelo Juego (VGSales + campos IGDB)
│       │   ├── igdb_api.py         # Cliente IGDB con caché de token Twitch
│       │   ├── deepl_translate.py  # Cliente DeepL
│       │   │
│       │   ├── services/           # Lógica de negocio (sin HTTP)
│       │   │   ├── game_service.py     # Búsqueda y estantes
│       │   │   ├── igdb_service.py     # Enriquecimiento + similares DB
│       │   │   └── chat_service.py     # Respuestas Gemini
│       │   │
│       │   ├── views/              # Capa HTTP (parseo + respuesta)
│       │   │   ├── api.py          # Endpoints JSON (juegos, ficha, chat)
│       │   │   └── auth.py         # Login / registro
│       │   │
│       │   ├── templates/
│       │   │   ├── gamebase.html   # Shell de la SPA React
│       │   │   ├── login.html
│       │   │   └── register.html
│       │   │
│       │   ├── fixtures/
│       │   │   └── vgsales.json    # Dataset de 16.598 juegos
│       │   │
│       │   ├── migrations/
│       │   ├── management/commands/
│       │   │   └── fetch_shelf_covers.py  # Poblar portadas en batch
│       │   │
│       │   └── test_*.py           # Tests unitarios por módulo
│       │
│       └── static/
│           ├── css/
│           │   ├── gb-hifi.css     # Estilos base (pixel art / Game Boy)
│           │   └── gb-app.css      # Estilos de componentes React
│           ├── js/
│           │   ├── gb-utils.js     # Paletas, íconos, helpers, cola de portadas lazy
│           │   ├── gb-components.js # Card (con lazy cover), Shelf, Library, Catalog, Profile
│           │   ├── gb-detail.js    # Componente ficha de juego
│           │   ├── gb-emulator.js  # Emulador (demo + EmulatorJS)
│           │   ├── gb-app.js       # TopBar, App, buscador unificado
│           │   └── gb-chat.js      # Chat FAB (vanilla JS)
│           ├── img/
│           │   └── favicon.svg
│           └── roms/               # Archivos ROM (.nes)
```

---

## APIs externas

### IGDB (Twitch)
Proveedor principal de metadatos de juegos.

- **Autenticación:** OAuth2 client_credentials (token cacheado en memoria y en `twitch_token.json`)
- **Datos obtenidos:** portada, descripción, screenshots, trailers, personajes, juegos similares, calificaciones, modos de juego, sagas, motores, ratings de edad (ESRB/PEGI)
- **Estrategia de búsqueda:** primero por ID exacto; si no hay ID, búsqueda exacta por nombre, con fallback fuzzy
- **Endpoint:** `https://api.igdb.com/v4/games`
- **Documentación:** https://api-docs.igdb.com

### DeepL
Traducción automática de descripciones al español.

- **Plan:** Free (500.000 caracteres/mes)
- **Caché:** el resultado se guarda en `Summary_ES` del modelo para no re-traducir
- **Endpoint:** `https://api-free.deepl.com/v2/translate`
- **Documentación:** https://developers.deepl.com/docs

### Google Gemini 2.5 Flash
Motor del asistente IA de chat.

- **SDK:** `google-genai` (Python)
- **Modelo:** `gemini-2.5-flash`
- **Documentación:** https://ai.google.dev/docs

### EmulatorJS
Emulación de consolas retro en el navegador.

- **CDN:** `https://cdn.emulatorjs.org/stable/data/`
- **Núcleos soportados:** `nes` (en uso), `snes`, `gb`, `gbc`, `gba`, `segaMD`, `n64`, `psx`
- **Documentación:** https://emulatorjs.org/docs

---

## Deploy en Render

El proyecto está configurado para deploy automático en [Render](https://render.com) usando `render.yaml`.

### Variables de entorno requeridas en Render

| Variable | Valor |
|---|---|
| `SECRET_KEY` | Clave secreta de Django |
| `DEBUG` | `False` |
| `DATABASE_URL` | Internal URL de la base PostgreSQL de Render |
| `TWITCH_CLIENT_ID` | Client ID de Twitch |
| `TWITCH_CLIENT_SECRET` | Client Secret de Twitch |
| `DEEPL_API_KEY` | Clave DeepL |
| `GEMINI_API_KEY` | Clave Gemini |
| `GOOGLE_CLIENT_ID` | Client ID de Google OAuth |
| `GOOGLE_CLIENT_SECRET` | Client Secret de Google OAuth |

### Base de datos en Render
Crear una base PostgreSQL gratuita en Render → copiar la **Internal Database URL** → pegarla como `DATABASE_URL` en las variables del servicio web.

El sistema detecta `DATABASE_URL` automáticamente y usa PostgreSQL en producción, SQLite en desarrollo.

### Build
El archivo `build.sh` ejecuta:
```bash
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

### Poblar portadas en producción
Dado que el plan gratuito de Render no incluye shell interactiva, conectarse a la DB de Render desde local usando la **External Database URL**:

```powershell
$env:DATABASE_URL="postgresql://...external-url..."
$env:TWITCH_CLIENT_ID="tu_client_id"
$env:TWITCH_CLIENT_SECRET="tu_client_secret"
python manage.py fetch_shelf_covers
```

### Configurar Google OAuth en producción
Agregar el redirect URI de producción en Google Cloud Console → Credenciales → OAuth 2.0:
```
https://<tu-app>.onrender.com/accounts/google/login/callback/
```

---

## Agregar ROMs

1. Copiar el archivo `.nes` a `djangoback/tp3_crud/static/roms/`
2. Agregar una entrada al array `EMULABLES` en `static/js/gb-emulator.js`:

```js
{
  id: "emu-mi-juego",
  name: "Nombre del juego",
  platform: "NES",
  image_url: "https://url-de-la-portada.jpg",
  pal_idx: 3,
  rom: "/static/roms/mi-juego.nes",
  core: "nes",
}
```

> Solo incluir ROMs de dominio público o homebrew. No distribuir ROMs con copyright.

---

## Comandos de gestión

```bash
# Poblar portadas de los juegos en las estanterías principales (desde IGDB)
python manage.py fetch_shelf_covers

# Solo las primeras N por plataforma
python manage.py fetch_shelf_covers --limit 10
```

---

## Links del proyecto

| Recurso | Link |
|---|---|
| Diseño Figma | https://www.figma.com/design/zlhrbHjXVQvIa3nRkl8iRL/Inventario-Juegos |
| Trello | https://trello.com/b/QW7cn5ch/ppi2-tp3-grupo-3 |
| Minuta | https://docs.google.com/document/d/17HYPCR3TJa0am82yZSlufUNVLnFlhk4Aqx6s1UgLBwo |
| Casos de uso | https://1drv.ms/x/c/07dec0e241a74c12/EXz3a8nMl-ZJqRXkyb43fmgBuCqGcIaZBigk9U7oZ97UzA |
| Texto descriptivo | https://docs.google.com/document/d/11Qe2bSqGOx7W_UvtJo15sN2sc5ofwtq_bZfuXuOqs0I |
