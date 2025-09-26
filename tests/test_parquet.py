#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrae los textos (chunks) de un Parquet de embeddings y los exporta a JSONL/CSV.

Uso:
  python test_parquet.py "C:/ruta/al/archivo.parquet" --verbose \
      --out-jsonl chunks.jsonl --out-csv chunks.csv
"""

import argparse
import json
import sys
from pathlib import Path
import pandas as pd
import ast

# -------------------- Helpers --------------------

def coerce_text(cell):
    """
    Normaliza la columna 'texts' a str:
    - Si viene como lista (p.ej., ['texto']), toma el primer elemento
    - Si es bytes, decodifica a utf-8
    - None -> ""
    - Cualquier otro tipo -> str(cell)
    """
    if cell is None:
        return ""
    if isinstance(cell, (list, tuple)):
        return coerce_text(cell[0]) if cell else ""
    if isinstance(cell, bytes):
        try:
            return cell.decode("utf-8", errors="ignore")
        except Exception:
            return str(cell)
    return str(cell)

def coerce_metadata(cell):
    """
    Normaliza 'metadatas' a dict:
    - dict -> dict
    - str JSON o repr de dict -> parsea (json.loads o ast.literal_eval)
    - None -> {}
    - Resto -> {"_raw": str(cell)}
    """
    if cell is None:
        return {}
    if isinstance(cell, dict):
        return cell
    if isinstance(cell, (bytes, bytearray)):
        try:
            cell = cell.decode("utf-8", errors="ignore")
        except Exception:
            cell = str(cell)
    if isinstance(cell, str):
        s = cell.strip()
        if not s:
            return {}
        try:
            return json.loads(s)
        except Exception:
            try:
                return ast.literal_eval(s)
            except Exception:
                return {"_raw": s}
    try:
        return dict(cell)  # por si es Mapping
    except Exception:
        return {"_raw": str(cell)}

def get_m(meta: dict, key: str, default=None):
    if not isinstance(meta, dict):
        return default
    return meta.get(key, default)

# -------------------- Main --------------------

def main():
    ap = argparse.ArgumentParser(
        description="Extrae y ordena chunks (texto) desde un Parquet de embeddings."
    )
    ap.add_argument("input", help="Ruta al archivo .parquet")
    ap.add_argument("--out-jsonl", default="chunks.jsonl",
                    help="Salida JSONL (por defecto: chunks.jsonl)")
    ap.add_argument("--out-csv", default=None,
                    help="Salida CSV opcional (ej: chunks.csv)")
    ap.add_argument("--sample", type=int, default=None,
                    help="Limitar a N filas (opcional, para depuración)")
    ap.add_argument("--verbose", action="store_true",
                    help="Imprime un preview en consola")
    args = ap.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"ERROR: no existe {in_path}", file=sys.stderr)
        sys.exit(1)

    # ✅ Lectura simple con tipos Python (evita scalars/clases internas de PyArrow)
    try:
        df = pd.read_parquet(in_path, engine="pyarrow")
    except Exception:
        # Fallback al engine por defecto si pyarrow no está disponible
        df = pd.read_parquet(in_path)

    if df.empty:
        print("El Parquet no tiene filas.", file=sys.stderr)

    # Mapeo case-insensitive de columnas típicas
    colmap = {c.lower(): c for c in df.columns}
    id_col      = colmap.get("ids") or colmap.get("id")
    texts_col   = colmap.get("texts") or colmap.get("text")
    meta_col    = colmap.get("metadatas") or colmap.get("metadata")

    if texts_col is None:
        print("ERROR: no encontré columna 'texts' o 'text' en el Parquet.", file=sys.stderr)
        print(f"Columnas disponibles: {list(df.columns)}", file=sys.stderr)
        sys.exit(2)

    # Normaliza textos y metadatos
    df["_text"] = df[texts_col].apply(coerce_text)
    if meta_col:
        df["_meta"] = df[meta_col].apply(coerce_metadata)
    else:
        df["_meta"] = [{} for _ in range(len(df))]

    # Campos útiles desde metadata (si existen)
    df["_chunk_index"] = df["_meta"].apply(lambda m: get_m(m, "chunk_index"))
    df["_source"] = df["_meta"].apply(
        lambda m: get_m(m, "source",
                 get_m(m, "SOURCE",
                 get_m(m, "file_path",
                 get_m(m, "path"))))
    )

    # Orden sugerido: source y chunk_index
    sort_cols = []
    if "_source" in df.columns: sort_cols.append("_source")
    if df["_chunk_index"].notna().any(): sort_cols.append("_chunk_index")
    if sort_cols:
        df = df.sort_values(sort_cols, kind="stable")

    # Preview
    if args.verbose:
        show_cols = [c for c in (id_col, "_source", "_chunk_index", "_text") if c is not None]
        for _, r in df[show_cols].head(5).iterrows():
            snippet = (r["_text"][:120] + "…") if len(r["_text"]) > 120 else r["_text"]
            _id = r[id_col] if id_col else "(sin id)"
            print(f"- id={_id}  src={r.get('_source')}  idx={r.get('_chunk_index')}  txt='{snippet}'")

    # Exporta JSONL
    out_jsonl = Path(args.out_jsonl)
    n = 0
    with out_jsonl.open("w", encoding="utf-8") as f:
        iterable = df[[c for c in (id_col, "_text", "_meta", "_source", "_chunk_index") if c is not None]]
        if args.sample:
            iterable = iterable.head(args.sample)
        for _, row in iterable.iterrows():
            obj = {
                "id": str(row[id_col]) if id_col else None,
                "text": row["_text"],
                "metadata": row["_meta"],
                "source": row["_source"],
                "chunk_index": row["_chunk_index"],
            }
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
            n += 1
    print(f"✓ JSONL escrito con {n} chunks → {out_jsonl}")

    # Exporta CSV opcional
    if args.out_csv:
        out_csv = Path(args.out_csv)
        export_df = df.copy()
        if id_col:
            export_df = export_df.rename(columns={id_col: "id"})
        export_df = export_df.rename(columns={"_source": "source", "_chunk_index": "chunk_index", "_text": "text"})
        cols = [c for c in ("id", "source", "chunk_index", "text") if c in export_df.columns]
        export_df = export_df[cols]
        if args.sample:
            export_df = export_df.head(args.sample)
        # Evita saltos de línea que rompan el CSV
        export_df["text"] = export_df["text"].astype(str).replace({r"\r?\n": " "}, regex=True)
        export_df.to_csv(out_csv, index=False, encoding="utf-8-sig")
        print(f"✓ CSV escrito → {out_csv}")

    # Resumen por documento
    try:
        grouped = df.groupby("_source", dropna=False)
        print("≈ Reconstrucción por documento (conteo de chunks):")
        for src, g in grouped:
            label = src if src else "(sin source)"
            print(f"  - {label}: {len(g)} chunks")
    except Exception:
        pass

if __name__ == "__main__":
    main()
