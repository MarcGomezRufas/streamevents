## 💾 Fixtures (exemple)

📦 Cargar datos iniciales (Fixtures)

El proyecto incluye fixtures JSON que permiten precargar usuarios y grupos en la base de datos para facilitar las pruebas y el desarrollo.

🗂 Archivos incluidos
Archivo	Modelo	Descripción
01_groups.json	auth.group	Contiene los grupos básicos del sistema: Organitzadors, Participants y Moderadors.
02_users.json	users.customuser	Crea usuarios de ejemplo y los asigna a sus respectivos grupos.
⚙️ Cómo cargar las fixtures

Desde la raíz del proyecto (donde se encuentra el archivo manage.py), ejecuta los siguientes comandos:

# 1️⃣ Cargar grupos
python manage.py loaddata fixtures/01_groups.json

# 2️⃣ Cargar usuarios
python manage.py loaddata fixtures/02_users.json


⚠️ Importante:

Antes de cargar las fixtures, ejecuta python manage.py migrate para aplicar las migraciones y crear las colecciones/tablas necesarias.

Si estás usando MongoDB con Djongo, el comando loaddata funciona igual que con cualquier otra base de datos soportada por Django.

Las contraseñas de los usuarios ya están cifradas con pbkdf2_sha256.

Puedes acceder con los usuarios de prueba directamente o modificar sus contraseñas desde el panel de administración de Django.

## 🌱 Seeds (exemple d'script)
