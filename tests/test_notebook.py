"""Executa as células de código do notebook com a API do OpenAlex simulada.

Garante que o notebook roda de ponta a ponta na ordem em que está: definições,
extração, indicadores, gráficos e dashboard. Rode com: python tests/test_notebook.py
"""
import json
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))

import matplotlib
matplotlib.use("Agg")

from test_pipeline import work_falso

RAIZ = os.path.join(os.path.dirname(__file__), "..")
NB = os.path.join(RAIZ, "notebooks", "OA_Monitor_Workshop_ConfOA2026.ipynb")

# células que não dá para executar fora do Colab / que fazem download
PULAR_TRECHOS = ("google.colab import files", "IPython.display import HTML")


def main() -> int:
    nb = json.load(open(NB, encoding="utf-8"))
    celulas = [c for c in nb["cells"] if c["cell_type"] == "code"]
    ns: dict = {"__name__": "__main__"}
    random.seed(11)
    executadas = puladas = 0

    with tempfile.TemporaryDirectory() as tmp:
        os.chdir(tmp)
        for i, cel in enumerate(celulas):
            fonte = cel["source"]
            linhas = [l for l in fonte.splitlines() if not l.strip().startswith(("%pip", "!", "# @title"))]
            fonte = "\n".join(linhas)

            if any(t in fonte for t in PULAR_TRECHOS):
                puladas += 1
                continue

            # --- substitui as entradas do formulário e a rede ---
            if "EMAIL = " in fonte:
                fonte = fonte.replace('EMAIL = ""', 'EMAIL = "teste@exemplo.br"')
                fonte = fonte.replace("USAR_API_KEY = True", "USAR_API_KEY = False")
            if "input('Exibir códigos de apoio? (s/n): ')" in fonte:
                fonte = fonte.replace(
                    "resposta = input('Exibir códigos de apoio? (s/n): ')",
                    "resposta = 'n'",
                )
            if "NIVEL_NOVA = input('Contexto" in fonte:
                fonte = (
                    "NIVEL_NOVA = 'pesquisador'\n"
                    "IDENTIFICADOR_NOVA = '0000-0002-8338-1931'\n"
                    "ANO_INICIO_NOVA = 2023\n"
                    "ANO_FIM_NOVA = 2023\n"
                    "SOMENTE_ARTIGOS_NOVA = True\n"
                    "MAX_REGISTROS_NOVA = 40\n"
                    "cliente.get('works', {'filter': 'publication_year:2024', 'per-page': 1, 'select': 'id'})\n"
                    "print('Credenciais existentes do notebook reaproveitadas.')\n"
                    "tipos_nova = ['article', 'review']\n"
                    "filtro_nova = montar_filtro(NIVEL_NOVA, IDENTIFICADOR_NOVA, ANO_INICIO_NOVA, ANO_FIM_NOVA, tipos=tipos_nova)\n"
                )
            if "MAX_REGISTROS = 3000" in fonte:
                fonte = fonte.replace("MAX_REGISTROS = 3000", "MAX_REGISTROS = 400")
            fonte = fonte.replace("display(", "print(")

            try:
                exec(compile(fonte, f"<celula {i}>", "exec"), ns)
            except Exception as exc:
                print(f"\nFALHOU na célula de código #{i}:\n{'-' * 60}\n{fonte[:900]}\n{'-' * 60}")
                raise
            executadas += 1

            # depois de definir o cliente, troca a rede por dados sintéticos
            if "cliente = OpenAlexClient" in fonte:
                _instalar_mock(ns)

        # verificações finais
        assert len(ns["df"]) == 400, len(ns["df"])
        assert ns["painel"]["gerais"]["obras"] == 400
        assert os.path.exists(ns["arquivo_dash"])
        assert os.path.getsize(ns["arquivo_dash"]) > 15000
        assert os.path.exists("indicadores_oa.xlsx")
        assert os.path.exists("specs_vega.json")
        assert len(json.load(open("specs_vega.json"))) == 5
        assert len(os.listdir("figuras")) == 5
        print(f"\n{executadas} células executadas, {puladas} puladas (só rodam no Colab)")
        print("NOTEBOOK OK — roda de ponta a ponta")
    return 0


def _instalar_mock(ns: dict) -> None:
    """Faz OpenAlexClient.get devolver registros sintéticos, sem tocar a rede."""
    contador = {"n": 0}

    def get_falso(self, endpoint, params=None):
        params = params or {}
        if "group_by" in params:
            from collections import Counter
            c = Counter(work_falso(i)["open_access"]["oa_status"] for i in range(500))
            return {"meta": {"count": 500}, "group_by": [{"key": k, "count": v} for k, v in c.items()]}
        if params.get("per-page") == 1:
            return {"meta": {"count": 500}, "results": []}
        n = contador["n"]
        if n >= 500:
            return {"meta": {"count": 500, "next_cursor": None}, "results": []}
        lote = [work_falso(i) for i in range(n, min(n + 200, 500))]
        contador["n"] = n + len(lote)
        return {"meta": {"count": 500, "next_cursor": "prox"}, "results": lote}

    ns["OpenAlexClient"].get = get_falso
    ns["cliente"].pause = 0


if __name__ == "__main__":
    raise SystemExit(main())
