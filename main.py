from fastapi import FastAPI, HTTPException, Depends, Header, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from pydantic import BaseModel
import stripe, os
from dotenv import load_dotenv

app = FastAPI(
    title="API FERREMAS DUOC",
    description="AAAAAAAAA LOCURA A LAS 3 AM",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

API_BASE = os.getenv("API_BASE")
FIXED_TOKEN = os.getenv("TOKEN_FIJO")
VENDOR_ALLOW_TOKEN = os.getenv("TOKEN_VENDEDOR_PERMITIDO")
VENDOR_DENY_TOKEN = os.getenv("TOKEN_VENDEDOR_DENEGADO")
FX_API_KEY = os.getenv("TOKEN_FXRATESAPI")
stripe.api_key = os.getenv("CLAVE_SECRETA_STRIPE")

# Usuarios permitidos
usuarios_autorizados = [
    {"usuario": "javier_thompson", "contrasena": "aONF4d6aNBIxRjlgjBRRzrS", "rol": "admin"},
    {"usuario": "ignacio_tapia", "contrasena": "f7rWChmQS1JYfThT", "rol": "maintainer"},
    {"usuario": "stripe_sa", "contrasena": "dzkQqDL9XZH33YDzhmsf", "rol": "service_account"},
    {"usuario": "Admin", "contrasena": "1234", "rol": "admin"},
]

class ProductoPago(BaseModel):
    id: str
    nombre: str
    precio: int
    cantidad: int
    moneda: str

# Función para verificar token general
def verificar_token_general(x_authentication: str = Header(None, alias="x-authentication")):
    if x_authentication != FIXED_TOKEN:
        raise HTTPException(403, "Token inválido")
    return x_authentication

# Función para verificar token de vendedor
def verificar_token_vendedor(x_vendor_token: str = Header(None, alias="x-vendor-token")):
    if x_vendor_token != VENDOR_ALLOW_TOKEN:
        raise HTTPException(403, "No tienes permiso para este recurso")
    return x_vendor_token

async def obtener_desde_api(path: str, token: str):
    headers = {"x-authentication": token}
    async with httpx.AsyncClient() as cliente:
        respuesta = await cliente.get(f"{API_BASE}{path}", headers=headers)
        return JSONResponse(status_code=respuesta.status_code, content=respuesta.json())

async def enviar_a_api_post(path: str, datos: dict, token: str):
    headers = {"x-authentication": token}
    async with httpx.AsyncClient() as cliente:
        respuesta = await cliente.post(f"{API_BASE}{path}", json=datos, headers=headers)
        return JSONResponse(status_code=respuesta.status_code, content=respuesta.json())
async def enviar_a_api_put(path: str, headers: dict):
    async with httpx.AsyncClient() as cliente:
        respuesta = await cliente.put(f"{API_BASE}{path}", headers=headers)
        return JSONResponse(status_code=respuesta.status_code, content=respuesta.json())

@app.post("/autenticacion", tags=["Auth"])
async def login_usuario(credenciales: dict):
    usuario = credenciales.get("user")
    contrasena = credenciales.get("password")
    for u in usuarios_autorizados:
        if u["usuario"] == usuario and u["contrasena"] == contrasena:
            token_vendedor = VENDOR_DENY_TOKEN if u["rol"] == "service_account" else VENDOR_ALLOW_TOKEN
            return {"token": FIXED_TOKEN, "rol": u["rol"], "vendorToken": token_vendedor}
    raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
@app.get("/currency", tags=["Divisas"])
async def convertir_divisa(
    moneda_origen: str = Query(..., min_length=3, max_length=3),
    moneda_destino: str = Query(..., min_length=3, max_length=3)
):
    url_fx = f"https://fxratesapi.com/api/latest?base={moneda_origen.upper()}&symbols={moneda_destino.upper()}&api_key={FX_API_KEY}"
    async with httpx.AsyncClient() as cliente:
        respuesta = await cliente.get(url_fx)
    if respuesta.status_code != 200:
        raise HTTPException(status_code=502, detail="Error al obtener tasa de cambio FXRatesAPI")
    datos = respuesta.json()
    tasa = datos.get("rates", {}).get(moneda_destino.upper())
    if tasa is None:
        raise HTTPException(status_code=400, detail="Código de moneda inválido")
    return {"rate": tasa}

@app.post("/create-checkout-session", tags=["Stripe"])
async def crear_sesion_pago(items: list[ProductoPago]):
    try:
        line_items = [{
            "price_data": {
                "currency": item.moneda,
                "unit_amount": item.precio,
                "product_data": {"name": item.nombre}
            },
            "quantity": item.cantidad
        } for item in items]

        sesion_pago = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=line_items,
            success_url="https://tusitio.com/success",
            cancel_url="https://tusitio.com/cancel"
            "https://docs.stripe.com/payments/checkout/custom-success-page?payment-ui=stripe-hosted",
        )
        return {"url": sesion_pago.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/config", tags=["Stripe"])
async def obtener_clave_publica_stripe():
    clave_publica = os.getenv("CLAVE_PUBLICA_STRIPE")
    if not clave_publica:
        raise HTTPException(status_code=500, detail="Clave pública de Stripe no configurada")
    return {"publicKey": clave_publica}

# Endpoints para artículos
@app.get("/data/articulos", tags=["Articulos"])
async def listar_articulos(token: str = Depends(verificar_token_general)):
    return await obtener_desde_api("/data/articulos", token)

@app.get("/data/articulos/{articulo_id}", tags=["Articulos"])
async def obtener_articulo(articulo_id: str, token: str = Depends(verificar_token_general)):
    return await obtener_desde_api(f"/data/articulos/{articulo_id}", token)

# Endpoints para sucursales
@app.get("/data/sucursales", tags=["Sucursales"])
async def listar_sucursales(token: str = Depends(verificar_token_general)):
    return await obtener_desde_api("/data/sucursales", token)

@app.get("/data/sucursales/{sucursal_id}", tags=["Sucursales"])
async def obtener_sucursal(sucursal_id: str, token: str = Depends(verificar_token_general)):
    return await obtener_desde_api(f"/data/sucursales/{sucursal_id}", token)

# Endpoints para vendedores
@app.get("/data/vendedores", tags=["Vendedores"])
async def listar_vendedores(token: str = Depends(verificar_token_general), vendor_token: str = Depends(verificar_token_vendedor)):
    return await obtener_desde_api("/data/vendedores", token)

@app.get("/data/vendedores/{vendedor_id}", tags=["Vendedores"])
async def obtener_vendedor(vendedor_id: str, token: str = Depends(verificar_token_general), vendor_token: str = Depends(verificar_token_vendedor)):
    return await obtener_desde_api(f"/data/vendedores/{vendedor_id}", token)

# Endpoint para actualizar venta de artículo
@app.put("/data/articulos/venta/{articulo_id}", tags=["Ventas"])
async def actualizar_venta(articulo_id: str, cantidad: int = Query(...), token: str = Depends(verificar_token_general)):
    return await enviar_a_api_put(f"/data/articulos/venta/{articulo_id}?cantidad={cantidad}", headers={"x-authentication": token})

# Endpoint para crear nuevo pedido
@app.post("/data/pedidos/nuevo", tags=["Pedidos"])
async def crear_pedido(datos_pedido: dict, token: str = Depends(verificar_token_general)):
    return await enviar_a_api_post("/data/pedidos/nuevo", datos_pedido, token)

# Endpoint novedades
@app.get("/data/articulos/novedades", tags=["Articulos"])
async def listar_novedades(token: str = Depends(verificar_token_general)):
    return await obtener_desde_api("/data/articulos/novedades", token)

# Endpoint promociones
@app.get("/data/articulos/promociones", tags=["Articulos"])
async def listar_promociones(token: str = Depends(verificar_token_general)):
    return await obtener_desde_api("/data/articulos/promociones", token)

# Endpoint contacto vendedor (POST)
@app.post("/data/contacto/vendedor", tags=["Contacto"])
async def contacto_vendedor(mensaje: dict, token: str = Depends(verificar_token_general)):
    return await enviar_a_api_post("/data/contacto/vendedor", mensaje, token)
