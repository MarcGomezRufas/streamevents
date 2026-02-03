# 🎥 StreamEvents

## 💾 Dades Inicials (Fixtures)

📦 Carregar dades inicials (Fixtures)

El projecte inclou fixtures JSON que permeten precarregar usuaris i grups a la base de dades per facilitar les proves i el desenvolupament.

### 🗂 Arxius inclosos

| Arxiu | Model | Descripció |
| :--- | :--- | :--- |
| `01_groups.json` | `auth.group` | Conté els grups bàsics del sistema: Organitzadors, Participants i Moderadors. |
| `02_users.json` | `users.customuser` | Crea usuaris d'exemple i els assigna als seus respectius grups. |

### ⚙️ Com carregar les fixtures

Des de l'arrel del projecte (on es troba l'arxiu `manage.py`), executa les següents comandes:

```bash
# 1️⃣ Carregar grups
python manage.py loaddata fixtures/01_groups.json

# 2️⃣ Carregar usuaris
python manage.py loaddata fixtures/02_users.json
```

### ⚠️ Important:

*   Abans de carregar les fixtures, executa `python manage.py migrate` per aplicar les migracions i crear les col·leccions/taules necessàries.
*   Si estàs utilitzant **MongoDB** amb **Djongo**, la comanda `loaddata` funciona igual que amb qualsevol altra base de dades suportada per Django.
*   Les contrasenyes dels usuaris ja estan xifrades amb `pbkdf2_sha256`.
*   Pots accedir amb els usuaris de prova directament o modificar les seves contrasenyes des del panell d'administració de Django.

## 🧠 Cerca Semàntica

El projecte inclou un sistema de cerca semàntica basat en embeddings i similitud del cosinus.

### 🚀 Com funciona
1. Els usuaris poden cercar en llenguatge natural (ex: "concert de jazz aquest cap de setmana").
2. El sistema converteix la cerca i els esdeveniments en vectors utilitzant el model `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
3. Es retornen els resultats més rellevants.

### 🛠️ Comandos útils
Generar embeddings per a esdeveniments existents:
```bash
python manage.py backfill_event_embeddings
```

## 🌱 Seeds (exemple d'script)
