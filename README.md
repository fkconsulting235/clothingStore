# Virtual Shope

Tienda de ropa en Django: catálogo por categorías, inventario por color/talla, reservas de 24h, pago por depósito/transferencia con comprobante, y contacto directo por WhatsApp con el código de cada prenda.

## Instalación local

```bash
python -m venv venv
venv/Scripts/activate        # en Windows
pip install -r requirements.txt
cp .env.example .env         # y completa tu número de WhatsApp
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abre `http://localhost:8000` para la tienda pública y `http://localhost:8000/panel/` para el **panel del encargado** (subir/editar/eliminar prendas con sus variantes e imágenes, categorías, cuentas bancarias, y ver/confirmar reservas y pedidos). El `createsuperuser` que acabas de crear entra ahí sin nada extra; para un empleado que no deba tener acceso al admin de Django, crea un usuario con `is_staff=True` (y `is_superuser=False`) desde `/admin/auth/user/add/`.

El admin técnico de Django (`http://localhost:8000/admin/`) se mantiene disponible aparte, por si el dueño necesita algo avanzado (usuarios, permisos, etc.) — el día a día de subir ropa se hace desde `/panel/`.

## Variables de entorno (`.env`)

Ver `.env.example`. La importante para que la tienda funcione de verdad:

- `WHATSAPP_NUMBER`: número del negocio en formato internacional sin signos (ej. `50585384179`), usado en los botones de WhatsApp de cada prenda y del pedido.
- `RESERVATION_HOURS`: horas que dura una reserva (24 por defecto).
- `DB_HOST` / `DB_PORT` / `DB_NAME` / `DB_USER` / `DB_PASSWORD`: conexión a Postgres en Supabase (ver sección siguiente). Si `DB_HOST` queda vacío, la tienda usa SQLite local automáticamente.

## Base de datos en Supabase

La tienda usa Postgres (vía Supabase) en vez de SQLite cuando `DB_HOST` está configurado en `.env` — ver `virtualshope/settings.py`. Los datos de conexión salen de tu proyecto en [supabase.com](https://supabase.com/dashboard) → **Project Settings → Database → Connect** (usa el **Session pooler**, funciona igual de bien en redes IPv4 que la conexión directa):

```bash
DB_HOST=aws-0-xx-xxxx-x.pooler.supabase.com
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres.xxxxxxxxxxxx
DB_PASSWORD=tu-contraseña-de-la-base-de-datos
```

Con eso configurado, corre las migraciones para crear las tablas en Supabase y crea tu superusuario ahí (es una base nueva, no comparte datos con tu SQLite local):

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo   # opcional, solo si quieres datos de ejemplo
```

## Cómo se cobra: depósito/transferencia con comprobante

En vez de una pasarela de tarjeta (no hay ninguna con registro simple para un negocio informal en Nicaragua — se investigó Stripe, PayPal, Mercado Pago y PayPhone antes de llegar a esta solución), el pago funciona así:

1. El cliente llena sus datos en "Comprar ahora" y ve las **cuentas bancarias** del negocio (banco, número, a nombre de quién).
2. Hace su depósito o transferencia por su cuenta, y sube una **foto o captura del comprobante** directo en el sitio.
3. El pedido queda "Pendiente" en `/panel/pedidos/`, con el comprobante visible con un clic ("Ver foto").
4. El encargado revisa el comprobante y hace clic en **"Marcar como pagado"** — ahí (y solo ahí) se descuenta el stock de verdad y, si el pedido venía de una reserva, esta pasa a "Convertida en pedido".

**Antes de lanzar la tienda, edita las cuentas bancarias de ejemplo** que vienen sembradas (`BAC Credomatic` / `Banco LAFISE` con datos de relleno) desde `/panel/cuentas-bancarias/` — ponlas con tus números reales, o desactiva/elimina las que no uses. También puedes agregar más cuentas ahí mismo, sin tocar código.

Cuando el negocio crezca y quieras automatizar esto con una pasarela de verdad, lo más realista para Nicaragua es gestionarlo directo con un banco local (ej. BAC Credomatic) para una cuenta de comercio — eso requiere trámite propio con el banco, no algo que se resuelva desde el código.

## Liberar reservas vencidas

Las reservas de 24h se calculan en tiempo real (el stock disponible ya descarta las reservas vencidas), pero para mantener el panel limpio conviene correr esto cada pocos minutos (cron del hosting, tarea programada de Windows, etc.):

```bash
python manage.py expire_reservations
```

## Estructura del proyecto

- `apps/catalog`: categorías, prendas, variantes (color/talla/stock) e imágenes.
- `apps/reservations`: reserva de 24h sin necesidad de cuenta (nombre + teléfono).
- `apps/orders`: pedidos, cuentas bancarias, y el flujo de comprobante de pago.
- `apps/dashboard`: panel del encargado (`/panel/`) para subir prendas, gestionar cuentas bancarias, confirmar pagos y ver reservas/pedidos, sin pasar por `/admin/`.
- `apps/core`: layout base y utilidades compartidas.
- `templates/`: todas las plantillas del sitio (Tailwind CSS vía CDN, paleta neutra).

## Desplegar en Render

El proyecto ya está listo para producción: `gunicorn` como servidor WSGI, `whitenoise` para servir los archivos estáticos (CSS/JS/imágenes del sitio), y ajustes de seguridad que se activan solos cuando `DEBUG=False`.

1. **Sube el proyecto a GitHub** (Render despliega desde un repo conectado, no permite subir una carpeta directo).
2. En [render.com](https://dashboard.render.com) → **New → Web Service** → conecta tu repositorio.
3. Configura:
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command**: `gunicorn virtualshope.wsgi:application`
4. Variables de entorno (Render → tu servicio → **Environment**) — las mismas de tu `.env` local, más estas dos nuevas:
   - `DJANGO_SECRET_KEY`: una nueva y real (no la de desarrollo). Génerala con `python -c "import secrets; print(secrets.token_urlsafe(50))"`.
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: el dominio que te da Render (ej. `mi-tienda.onrender.com`)
   - `CSRF_TRUSTED_ORIGINS`: `https://mi-tienda.onrender.com` (con `https://`, si no los formularios del sitio van a fallar por CSRF)
   - `DB_HOST` / `DB_PORT` / `DB_NAME` / `DB_USER` / `DB_PASSWORD`: los mismos de Supabase
   - `WHATSAPP_NUMBER`, `STORE_NAME`, `STORE_CURRENCY`, `RESERVATION_HOURS`, `TIME_ZONE`: igual que en tu `.env`
5. Deploy. Cuando termine, entra a `https://tu-dominio.onrender.com/panel/` con tu usuario admin (el mismo que ya existe en Supabase, porque la base de datos es la misma).

**Sobre las fotos subidas (prendas y comprobantes de pago)**: por ahora el proyecto guarda esos archivos en el disco del propio servicio de Render, el cual **se borra en cada despliegue o reinicio** (es la opción gratis). Para una demo está bien; cuando el negocio ya esté pagando, agrega un **Persistent Disk** en la configuración del servicio en Render (unos $1/mes por GB) montado en la carpeta `media/` y las fotos dejan de perderse — no requiere ningún cambio de código, solo configurarlo en el dashboard de Render.

## Desplegar en cPanel (sin terminal/SSH)

Si tu hosting es cPanel con **Setup Python App** (CloudLinux Python Selector) pero sin acceso a Terminal/SSH, el proyecto ya está preparado para eso: `passenger_wsgi.py` corre las migraciones, recolecta los archivos estáticos y crea el superusuario automáticamente cada vez que la app arranca — no hace falta ejecutar ningún comando a mano. La base de datos usa MySQL (`PyMySQL`, no requiere compilar nada) en vez de SQLite/Postgres.

1. **Crea la base de datos en cPanel** (si no lo hiciste ya): **MySQL Databases** → crea una base y un usuario, asígnale todos los privilegios. Anota el nombre de la base y del usuario — cPanel les pone el prefijo de tu cuenta automáticamente (ej. `cpaneluser_tienda` y `cpaneluser_tiendauser`). El host casi siempre es `localhost`.

2. **Crea la aplicación de Python**: en cPanel → **Setup Python App** → **Create Application**. Elige la versión de Python más reciente disponible (3.11+), define el **App Root** (una carpeta nueva, ej. `tienda_kei`) y el dominio/subdominio donde vivirá la tienda. No toques ninguna app existente que no sea esta.

3. **Sube el código a esa carpeta**, sin usar terminal:
   - Si tu cPanel tiene **Git Version Control**: apunta a tu repositorio de GitHub y clónalo directo en el **App Root** que creaste en el paso 2.
   - Si no: descarga el proyecto como `.zip` desde GitHub (botón verde **Code → Download ZIP**), súbelo con **File Manager** a esa misma carpeta, y usa la opción **Extract** del File Manager para descomprimirlo ahí.

4. **Variables de entorno**: en la pantalla de **Setup Python App**, edita la aplicación y agrega en la sección de variables de entorno (mismos nombres que tu `.env`):
   ```
   DJANGO_SECRET_KEY=（genera una nueva con el comando de la sección de Render）
   DEBUG=False
   ALLOWED_HOSTS=tu-dominio.com
   CSRF_TRUSTED_ORIGINS=https://tu-dominio.com
   DB_ENGINE=mysql
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=cpaneluser_tienda
   DB_USER=cpaneluser_tiendauser
   DB_PASSWORD=la-contraseña-que-pusiste-en-mysql-databases
   WHATSAPP_NUMBER=50585384179
   STORE_NAME=Tienda K E I
   STORE_CURRENCY=usd
   RESERVATION_HOURS=24
   TIME_ZONE=America/Guatemala
   DJANGO_SUPERUSER_USERNAME=admin
   DJANGO_SUPERUSER_EMAIL=tu-correo@ejemplo.com
   DJANGO_SUPERUSER_PASSWORD=una-contraseña-segura
   ```

5. **Instala las dependencias sin terminal**: en la misma pantalla de la aplicación, cPanel detecta el `requirements.txt` del proyecto y muestra un botón para instalarlo (a veces aparece como **"Run Pip Install"** junto al archivo detectado). Dale clic ahí — así se instalan Django, gunicorn/passenger, PyMySQL, etc. dentro del entorno virtual que cPanel ya creó.

6. **Reinicia la aplicación** (botón de reiniciar/restart en la misma pantalla) y entra a tu dominio. La primera carga va a tardar un poco más de lo normal porque `passenger_wsgi.py` corre las migraciones y crea el superusuario en ese momento; después de eso ya es instantáneo. Entra a `/panel/login/` con el usuario y contraseña que pusiste en `DJANGO_SUPERUSER_USERNAME`/`DJANGO_SUPERUSER_PASSWORD`.

**Si algo no carga**, cPanel guarda un log de errores de Passenger en la misma pantalla de "Setup Python App" (o en un archivo `stderr.log` dentro del App Root) — ahí se ve el motivo exacto si algo falla.
