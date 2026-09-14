#!/bin/bash

if [ "$#" -eq 0 ]; then
    echo "Erro: Nenhum diretório informado."
    echo "Uso: $0 /caminho/para/diretorio1 /caminho/para/diretorio2"
    exit 1
fi

TEMP_DIR=$(mktemp -d)
AGGREGATED_FILE="$TEMP_DIR/contexto_agregado.txt"

echo "Diretório temporário criado em: $TEMP_DIR"
echo "Agregando arquivos..."


for DIR in "$@"; do
    if [ -d "$DIR" ]; then
        # Usa o find para listar apenas arquivos (-type f)
        find "$DIR" -type f | while read -r FILE; do
            echo -e "\n\n========================================" >> "$AGGREGATED_FILE"
            echo "ARQUIVO: $FILE" >> "$AGGREGATED_FILE"
            echo -e "========================================\n" >> "$AGGREGATED_FILE"
            cat "$FILE" >> "$AGGREGATED_FILE" 2>/dev/null

        done
    else
        echo "Aviso: '$DIR' não é um diretório válido ou acessível. Ignorando."
    fi
done

echo -e "\nAgregação concluída! Lendo o contexto agregado:\n"
echo "---------------------------------------------------"
cat "$AGGREGATED_FILE"
echo -e "\n---------------------------------------------------"
echo "O arquivo consolidado está salvo em: $AGGREGATED_FILE"
