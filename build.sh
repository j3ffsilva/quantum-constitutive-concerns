#!/usr/bin/env bash
set -euo pipefail

TEX="${1:-main.tex}"
BASENAME="${TEX%.tex}"
OUTDIR="out"

if [[ ! -f "$TEX" ]]; then
  echo "Erro: arquivo '$TEX' não encontrado." >&2
  exit 1
fi

echo "Compilando $TEX..."
latexmk -pdf -bibtex -output-directory="$OUTDIR" "$TEX"

echo "Movendo artefatos para a raiz..."
cp "$OUTDIR/$BASENAME.pdf" "./$BASENAME.pdf"
cp "$OUTDIR/$BASENAME.log" "./$BASENAME.log"

echo "Limpando temporários em $OUTDIR/..."
latexmk -output-directory="$OUTDIR" -c "$TEX"
rm -f "$OUTDIR/$BASENAME.bbl" \
       "$OUTDIR/$BASENAME.fdb_latexmk" \
       "$OUTDIR/$BASENAME.fls" \
       "$OUTDIR/$BASENAME.synctex.gz" \
       "$OUTDIR/$BASENAME.pdf"

echo "Pronto. PDF e log disponíveis na raiz."
