"""
Kalkulator podatkowy JDG - aplikacja FastAPI.

Punkt startowy aplikacji backendowej.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.calculator import router as calculator_router


# Inicjalizacja aplikacji
app = FastAPI(
    title="Kalkulator Podatkowy JDG",
    description=(
        "Aplikacja do porównania form opodatkowania dla jednoosobowej działalności gospodarczej (JDG) w Polsce.\n\n"
        "**UWAGA:** Aplikacja ma charakter informacyjny i symulacyjny. "
        "Nie stanowi doradztwa podatkowego i nie zastępuje księgowego ani interpretacji indywidualnej.\n\n"
        "Rok podatkowy: 2025"
    ),
    version="1.0.0",
    contact={
        "name": "Kalkulator Podatkowy JDG",
    },
)

# CORS - pozwól na requesty z frontendu
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # W produkcji zmienić na konkretne domeny
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rejestracja routerów
app.include_router(calculator_router, prefix="/api", tags=["Kalkulator"])


@app.get("/", tags=["Health"])
async def root():
    """
    Health check endpoint.

    Returns
    -------
    dict
        Status aplikacji i podstawowe informacje.
    """
    return {
        "status": "ok",
        "message": "Kalkulator Podatkowy JDG API",
        "version": "1.0.0",
        "tax_year": 2025,
        "note": "Aplikacja ma charakter informacyjny i symulacyjny. Nie stanowi doradztwa podatkowego.",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Dodatkowy health check endpoint.

    Returns
    -------
    dict
        Status zdrowia aplikacji.
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
