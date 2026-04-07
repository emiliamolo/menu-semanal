# 🥗 MiMenu: Gestión Inteligente de Alimentación

**MiMenu** es una plataforma web completa para la organización nutricional. Permite a los usuarios crear, gestionar y compartir planes alimentarios de forma dinámica y segura.

---

## 🚀 Demo
Puedes acceder a la aplicación en vivo aquí:  
👉 **[Ver Demo en Vivo](https://mi-menu.up.railway.app/)**


---

## ✨ Características Principales

* **📅 Planificación Flexible:** Creación de múltiples menús semanales totalmente editables por día y tipo de comida.
* **👥 Comunidad y Privacidad:** Sistema de recetas con visibilidad configurable (Públicas/Privadas). Explora recetas de otros usuarios o gestiona tu propio recetario personal.
* **📄 Exportación y Compartición:** Generación automática de menús en formato **PDF** y envío directo a través de **WhatsApp**.
* **🔐 Seguridad Avanzada:** Recuperación de cuenta mediante tokens temporales y hashing de contraseñas.
* **☁️ Cloud Ready:** Configuración optimizada para despliegue continuo en **Railway** con persistencia de datos.

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
| :--- | :--- |
| **Backend** | Python 3.x + Flask |
| **Base de Datos** | SQLite3 (con volumen persistente en disco) |
| **Frontend** | HTML5, CSS3, Jinja2 |
| **Infraestructura** | Gunicorn, Railway |
| **Servicios Externos** | Resend API (Email Delivery) |

---

## 📁 Estructura del Proyecto

```text
├── app/
│   ├── static/          # Recursos estáticos (CSS, JS, imágenes)
│   ├── templates/       # Vistas dinámicas en Jinja2
│   ├── models.py        # Definición de esquemas y lógica de DB
│   ├── routes.py        # Controladores y gestión de endpoints
│   ├── database.py      # Configuración de conexión
│   └── helpers.py       # Funciones de soporte y utilidades
├── db/
│   └── recetas.db       # Base de datos local (SQLite)
├── requirements.txt     # Listado de dependencias
└── run.py               # Punto de entrada de la aplicación