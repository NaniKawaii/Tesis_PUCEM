"""Servidor web (FastAPI). Expone la API REST y sirve la interfaz en /.

Ejecutar:  python -m telescopio.servidor [--config archivo.json] [--puerto 8000]
"""

from __future__ import annotations

import argparse
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .config import Config, cargar_config
from .correccion import TIPOS
from .sistema import Telescopio

ESTATICOS = Path(__file__).parent / "static"


class PeticionReferencia(BaseModel):
    azimut: float = 0.0
    altitud: float = 0.0


class PeticionGoto(BaseModel):
    objeto: str
    usar_ia: bool = True


class PeticionAjuste(BaseModel):
    eje: str
    grados: float


class PeticionSeguimiento(BaseModel):
    activo: bool


class PeticionEntrenar(BaseModel):
    tipo: str = "red_neuronal"


def crear_app(cfg: Config | None = None, telescopio: Telescopio | None = None) -> FastAPI:
    tel = telescopio or Telescopio(cfg or Config())

    @asynccontextmanager
    async def ciclo_de_vida(_app):
        yield
        tel.cerrar()  # deshabilita los drivers al apagar el servidor

    app = FastAPI(title="Telescopio automatizado", version="0.1.0", lifespan=ciclo_de_vida)
    app.state.telescopio = tel

    def ejecutar(funcion, *args, **kwargs):
        """Convierte los errores del sistema en respuestas HTTP 400 con el mensaje."""
        try:
            return funcion(*args, **kwargs)
        except (ValueError, KeyError, RuntimeError) as e:
            raise HTTPException(status_code=400, detail=str(e).strip("'\""))

    @app.get("/api/estado")
    def estado():
        return tel.estado()

    @app.get("/api/objetos")
    def objetos():
        return tel.lista_objetos()

    @app.post("/api/referenciar")
    def referenciar(p: PeticionReferencia):
        ejecutar(tel.referenciar, p.azimut, p.altitud)
        return tel.estado()

    @app.post("/api/goto")
    def goto(p: PeticionGoto):
        return ejecutar(tel.goto, p.objeto, p.usar_ia)

    @app.post("/api/ajustar")
    def ajustar(p: PeticionAjuste):
        ejecutar(tel.ajustar, p.eje, p.grados)
        return tel.estado()

    @app.post("/api/centrado")
    def centrado():
        return ejecutar(tel.confirmar_centrado)

    @app.post("/api/seguimiento")
    def seguimiento(p: PeticionSeguimiento):
        ejecutar(tel.seguimiento, p.activo)
        return tel.estado()

    @app.post("/api/detener")
    def detener():
        tel.detener()
        return tel.estado()

    @app.post("/api/ia/entrenar")
    def entrenar(p: PeticionEntrenar):
        if p.tipo not in TIPOS:
            raise HTTPException(400, f"Tipo de modelo inválido. Opciones: {', '.join(TIPOS)}")
        return ejecutar(tel.entrenar_ia, p.tipo)

    @app.post("/api/ia/desactivar")
    def desactivar_ia():
        tel.desactivar_ia()
        return tel.estado()

    @app.get("/")
    def inicio():
        return FileResponse(ESTATICOS / "index.html")

    app.mount("/static", StaticFiles(directory=ESTATICOS), name="static")
    return app


def main() -> None:
    import uvicorn

    parser = argparse.ArgumentParser(description="Servidor del telescopio automatizado")
    parser.add_argument("--config", help="archivo JSON de configuración")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--puerto", type=int, default=8000)
    args = parser.parse_args()
    uvicorn.run(crear_app(cargar_config(args.config)), host=args.host, port=args.puerto)


if __name__ == "__main__":
    main()
