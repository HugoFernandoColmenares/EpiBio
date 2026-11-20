"""Descarga la tabla de MGnify y los metadatos de la ENA (sin claves)."""
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

import httpx
import pandas as pd

MGNIFY = "https://www.ebi.ac.uk/metagenomics/api/v1"
ENA = "https://www.ebi.ac.uk/ena/portal/api/filereport"

ESTUDIO = "MGYS00006080"
PROYECTO = "PRJNA693108"
TABLA = "SRP302406_taxonomy_abundances_SSU_v5.0.tsv"

RAW = Path("data/raw")


def _get(url: str, params: dict | None = None) -> str:
    """Cliente HTTP con timeout y User-Agent identificable."""
    with httpx.Client(timeout=60, headers={"User-Agent": "epibio/0.1"}) as client:
        r = client.get(url, params=params, follow_redirects=True)
        r.raise_for_status()
        return r.text


def descargar_tabla(destino: Path = RAW) -> Path:
    destino.mkdir(parents=True, exist_ok=True)
    url = f"{MGNIFY}/studies/{ESTUDIO}/pipelines/5.0/file/{TABLA}"
    ruta = destino / TABLA
    ruta.write_text(_get(url), encoding="utf-8")
    _anotar(destino, url)
    return ruta


def descargar_metadatos(destino: Path = RAW) -> Path:
    destino.mkdir(parents=True, exist_ok=True)
    params = {
        "accession": PROYECTO,
        "result": "read_run",
        "fields": "run_accession,sample_alias,sample_title,library_strategy,read_count",
        "format": "tsv",
    }
    texto = _get(ENA, params)
    meta = pd.read_csv(StringIO(texto), sep="\t")
    # El proyecto mezcla amplicones 16S y metagenomas (WGS); la tabla SSU es de amplicones.
    meta = meta[meta["library_strategy"] == "AMPLICON"]
    ruta = destino / "metadatos_ena.tsv"
    meta.to_csv(ruta, sep="\t", index=False)
    _anotar(destino, f"{ENA}?accession={PROYECTO}")
    return ruta


def _anotar(destino: Path, url: str) -> None:
    """Bitácora de procedencia: MGnify reprocesa estudios y la tabla puede cambiar."""
    ahora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open(destino / "DESCARGAS.txt", "a", encoding="utf-8") as f:
        f.write(f"{ahora}\t{url}\n")


if __name__ == "__main__":
    print(descargar_tabla())
    print(descargar_metadatos())
