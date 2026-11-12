# MarginTracker 📈

[🇪🇸 Español](#español) | [🇬🇧 English](#english)

---

## <a name="español"></a>🇪🇸 Español

### 💡 ¿Para qué sirve MarginTracker?
**MarginTracker** es una aplicación web híbrida diseñada para comercios y emprendedores que necesitan un control operativo ágil de su inventario, costos, impuestos y gastos de envío, combinado con analíticas avanzadas de negocio. 

A diferencia de las hojas de cálculo tradicionales, MarginTracker centraliza la carga de productos, permite la importación masiva mediante archivos Excel/CSV y calcula automáticamente los márgenes de ganancia reales, conectando la operación diaria con herramientas de Business Intelligence.

### 🏗️ Arquitectura y Enfoque Técnico
El proyecto implementa un enfoque híbrido moderno:
* **Capa Operativa (Transaccional):** Desarrollada en **Python (Flask)** conectada a una base de datos relacional en la nube (**MySQL en Aiven**). Maneja el inventario en tiempo real, altas, modificaciones, eliminaciones y procesamiento de planillas con **Pandas**.
* **Capa Analítica (BI):** Integración con **Looker Studio** para la visualización de métricas de rendimiento, proporcionando tableros de control ejecutivos sin sobrecargar el servidor principal.
* **Infraestructura Cloud:** Desplegado en **Render** utilizando un servidor WSGI de alto rendimiento (**Gunicorn**) y variables de entorno seguras.

### ✨ Características Principales
* **CRUD Completo:** Registro, edición y eliminación individual o masiva de productos.
* **Gestión de Costos Detallada:** Control de precio de costo, precio de venta, impuestos y tarifas de envío por artículo.
* **Importación/Exportación Masiva:** Descarga de plantillas estandarizadas en Excel y carga automática de inventario masivo mediante `pandas` y `openpyxl`.
* **Seguridad y Conexión Segura:** Conexión cifrada (SSL) con bases de datos cloud y gestión estricta de credenciales mediante variables de entorno (`python-dotenv` y `urlparse`).

---

## <a name="english"></a>🇬🇧 English

### 💡 What is MarginTracker?
**MarginTracker** is a hybrid web application built for businesses and merchants who need agile operational control over their inventory, costs, taxes, and shipping expenses, coupled with advanced business analytics.

Unlike traditional spreadsheets, MarginTracker streamlines product management, supports bulk data imports via Excel/CSV files, and automatically computes real profit margins, seamlessly bridging daily operations with Business Intelligence tools.

### 🏗️ Architecture & Technical Approach
The project implements a modern hybrid approach:
* **Operational Layer (Transactional):** Built with **Python (Flask)** and backed by a cloud relational database (**Aiven MySQL**). It handles real-time inventory tracking, CRUD operations, and spreadsheet data processing using **Pandas**.
* **Analytical Layer (BI):** Integrated with **Looker Studio** for executive performance reporting and KPI visualization without overloading the core application server.
* **Cloud Infrastructure:** Deployed on **Render** using a high-performance WSGI server (**Gunicorn**) and secure environment variable configurations.

### ✨ Key Features
* **Full CRUD Functionality:** Register, update, and delete individual or multiple inventory items effortlessly.
* **Granular Cost Control:** Track purchase costs, selling prices, local taxes, and shipping fees per product.
* **Mass Import/Export:** Download standardized Excel templates and bulk-upload inventory seamlessly using `pandas` and `openpyxl`.
* **Security & Cloud Readiness:** Encrypted SSL connections to cloud databases and robust environment variable management (`python-dotenv` & `urlparse`).

---

### 🚀 Stack Tecnológico / Tech Stack
* **Backend:** Python, Flask, Gunicorn
* **Base de Datos / Database:** MySQL (Aiven Cloud)
* **Procesamiento de Datos / Data Processing:** Pandas, OpenPyXL
* **Despliegue / Deployment:** Render, Git / GitHub