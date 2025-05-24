# FerreMas

🛠️ API FERREMAS DUOC

Versión: 1.0.0
Descripción: API de integración para la empresa FERREMAS, desarrollada con FastAPI. Implementa autenticación, autorización basada en roles (RBAC), operaciones CRUD, integración con Stripe para pagos, y consulta de tasas de cambio con FXRatesAPI.
📦 Tecnologías

    FastAPI

    MongoDB (mediante API externa)

    Stripe

    FXRatesAPI

    httpx

    Python 3.11+

    Vercel (Frontend) + Railway (Backend)

🔐 Autenticación y Autorización
Tipos de autenticación:

    Token de autenticación general: x-authentication

    Token de vendedor: x-vendor-token

Roles soportados (RBAC):

    admin

    maintainer

    service_account

🚀 Endpoints Principales
🔒 Auth

    POST /autenticacion: Iniciar sesión y obtener tokens.

🛒 Artículos

    GET /data/articulos: Listar todos los productos.

    GET /data/articulos/{id}: Obtener producto por ID.

    GET /data/articulos/novedades: Productos marcados como novedades.

    GET /data/articulos/promociones: Productos en promoción.

    POST /data/articulos: Agregar producto (requiere rol).

    PUT /data/articulos/venta/{id}?cantidad=: Actualizar stock tras venta.

🏬 Sucursales

    GET /data/sucursales: Obtener todas las sucursales.

    GET /data/sucursales/{id}: Detalle de una sucursal.

🧑‍💼 Vendedores

    GET /data/vendedores: Listar todos los vendedores.

    GET /data/vendedores/{id}: Detalle de un vendedor.

    GET /data/vendedores/porSucursal?sucursal_Id={id}: Vendedores por sucursal.

📦 Pedidos

    POST /data/pedidos/nuevo: Crear pedido (mono o multiproducto).

📩 Contacto

    POST /data/contacto/vendedor: Solicitar contacto con vendedor.

💰 Stripe

    POST /create-checkout-session: Crear sesión de pago.

    GET /config: Obtener clave pública de Stripe.

💱 Conversión de Divisas

    GET /currency?moneda_origen=CLP&moneda_destino=USD: Conversión CLP/USD o USD/CLP mediante FXRatesAPI.

🧪 Casos de uso cubiertos

    ✅ Como cliente, puedo mirar detalles de una sucursal.

    ✅ Como cliente, puedo obtener productos en promoción.

    ✅ Como mantenedor, puedo agregar productos al catálogo.

    ✅ Como administrador, puedo ver a mis vendedores.

    ✅ Como cliente, puedo realizar una compra.

⚙️ Variables de entorno

Asegúrate de definir estas variables en .env:

API_BASE=https://ea2p2assets-production.up.railway.app
TOKEN_FIJO=SaGrP9ojGS39hU9ljqbXxQ==
TOKEN_VENDEDOR_PERMITIDO=token_autorizado
TOKEN_VENDEDOR_DENEGADO=token_denegado
CLAVE_SECRETA_STRIPE=sk_test_xxxxxxxxxxxxx
CLAVE_PUBLICA_STRIPE=pk_test_xxxxxxxxxxxxx
TOKEN_FXRATESAPI=tu_token_de_fxratesapi

📁 Estructura del Proyecto

📦 ferremas-api
 ┣ 📄 main.py          # Archivo principal FastAPI
 ┣ 📄 .env             # Variables de entorno
 ┗ 📄 README.md        # Documentación del proyecto

📌 Notas

    El proyecto usa CORS libre para pruebas, se recomienda restringirlo en producción.

    Se puede extender el manejo de usuarios y autenticación usando OAuth2 o JWT para producción.
