"""Teste do pipeline com registros sintéticos no formato bruto do OpenAlex.

Não faz chamada de rede: valida o achatamento, os indicadores, as specs Vega e
a geração do dashboard. Rode com:  python tests/test_pipeline.py
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pandas as pd

from oa_monitor.dashboard import gerar_dashboard
from oa_monitor.extract import OA_STATUS_ORDEM, achatar_work, montar_filtro, normalizar_ror
from oa_monitor.indicators import painel_completo
from oa_monitor.vega import todas_as_specs

random.seed(7)


def work_falso(i: int) -> dict:
    status = random.choice(OA_STATUS_ORDEM)
    ano = random.choice([2020, 2021, 2022, 2023, 2024])
    pagou = status in ("gold", "hybrid") and random.random() < 0.6
    return {
        "id": f"https://openalex.org/W{i}",
        "doi": f"https://doi.org/10.1234/x{i}",
        "title": f"Obra {i}",
        "publication_year": ano,
        "publication_date": f"{ano}-06-01",
        "type": "article",
        "language": "pt",
        "cited_by_count": random.randint(0, 90),
        "fwci": round(random.uniform(0, 3), 2),
        "is_retracted": False,
        "open_access": {
            "is_oa": status != "closed",
            "oa_status": status,
            "oa_url": None if status == "closed" else "https://ex.org/pdf",
            "any_repository_has_fulltext": status == "green" or random.random() < 0.2,
        },
        "apc_list": {"value_usd": 2000} if status in ("gold", "hybrid") else {},
        "apc_paid": {"value_usd": random.choice([900, 1800, 2400]), "provenance": "doaj"} if pagou else {},
        "primary_location": {
            "source": {
                "id": "https://openalex.org/S1",
                "display_name": random.choice(["Rev. A", "Rev. B", "Rev. C"]),
                "issn_l": "1234-5678",
                "type": "journal",
                "host_organization_name": random.choice(["Elsevier", "SciELO", "Springer"]),
                "is_in_doaj": status in ("gold", "diamond"),
                "is_oa": status in ("gold", "diamond"),
            }
        },
        "best_oa_location": {"version": "publishedVersion", "source": {"type": "journal"}},
        "locations_count": 2,
        "authorships": [
            {"institutions": [{"display_name": "UFSC", "country_code": "BR"}]},
            {"institutions": [{"display_name": "IBICT", "country_code": "BR"}]},
        ],
        "primary_topic": {
            "display_name": "Bibliometria",
            "field": {"display_name": random.choice(["Social Sciences", "Medicine", "Engineering"])},
        },
    }


def main() -> int:
    # --- filtros ---
    assert normalizar_ror("041akq887") == "https://ror.org/041akq887"
    assert normalizar_ror("https://ror.org/041AKQ887") == "https://ror.org/041akq887"
    assert "publication_year:2020-2024" in montar_filtro("pais", "BR", 2020, 2024)
    try:
        normalizar_ror("banana")
    except ValueError:
        pass
    else:
        raise AssertionError("ROR inválido deveria falhar")

    # --- achatamento ---
    df = pd.DataFrame([achatar_work(work_falso(i)) for i in range(600)])
    df["oa_status_rotulo"] = df["oa_status"]
    df["ano"] = df["ano"].astype("Int64")
    for c in ("apc_cobrado_usd", "apc_pago_usd", "fwci"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    assert len(df) == 600 and df["oa_status"].isin(OA_STATUS_ORDEM).all()

    # --- indicadores ---
    p = painel_completo(df)
    g = p["gerais"]
    assert 0 <= g["taxa_oa"] <= 100
    assert abs(p["distribuicao_oa"]["percentual"].sum() - 100) < 0.5
    for ano, grupo in p["serie_anual_status"].groupby("ano"):
        assert abs(grupo["percentual"].sum() - 100) < 0.5, ano
    assert (p["serie_anual_oa"]["taxa_oa"] <= 100).all()
    assert p["apc_anual"]["apc_total_usd"].sum() > 0
    assert len(p["citacoes_status"]) > 0
    print("indicadores gerais:", json.dumps(g, ensure_ascii=False))

    # --- vazio não quebra ---
    vazio = painel_completo(pd.DataFrame())
    assert vazio["gerais"] == {} and vazio["distribuicao_oa"].empty

    # --- specs Vega ---
    specs = todas_as_specs(p)
    assert set(specs) == {"distribuicao", "serie_oa", "composicao", "apc", "citacoes"}
    for nome, s in specs.items():
        json.dumps(s)  # serializável
        assert s["$schema"].endswith("vega/v5.json"), nome
        assert s["marks"] and s["scales"], nome
        # nunca dois eixos de medida
        eixos_medida = [a for a in s["axes"] if a.get("title")]
        assert len(eixos_medida) <= 1, f"{nome} tem mais de um eixo de medida"
    print("specs vega ok:", ", ".join(specs))

    # --- dashboard ---
    import tempfile
    saida = os.path.join(tempfile.mkdtemp(), "dashboard_teste.html")
    gerar_dashboard(p, "Teste OA_monitor", "dados sintéticos", saida)
    txt = open(saida, encoding="utf-8").read()
    assert "vega.min.js" in txt and "c-distribuicao" in txt and len(txt) > 20000
    print(f"dashboard ok: {len(txt):,} bytes")

    print("\nTODOS OS TESTES PASSARAM")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
