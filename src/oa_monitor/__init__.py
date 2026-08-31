"""OA_monitor — indicadores de Ciência Aberta com dados do OpenAlex.

Material do workshop "Monitorando a Ciência Aberta", ConfOA 2026.
"""

from .api import OpenAlexClient, OpenAlexError
from .config import Credentials
from .dashboard import gerar_dashboard
from .extract import (
    OA_STATUS_ORDEM,
    OA_STATUS_ROTULO,
    extrair_works,
    montar_filtro,
    normalizar_orcid,
    normalizar_ror,
    resumo_rapido,
)
from .indicators import painel_completo
from .vega import salvar_specs, todas_as_specs

__version__ = "1.0.0"

__all__ = [
    "Credentials",
    "OpenAlexClient",
    "OpenAlexError",
    "montar_filtro",
    "extrair_works",
    "resumo_rapido",
    "normalizar_ror",
    "normalizar_orcid",
    "painel_completo",
    "todas_as_specs",
    "salvar_specs",
    "gerar_dashboard",
    "OA_STATUS_ORDEM",
    "OA_STATUS_ROTULO",
    "__version__",
]
