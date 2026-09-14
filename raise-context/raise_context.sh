for DIR in "$@"; do
    if [ -d "$DIR" ]; then
        find "$DIR" -type f \
            -not -path '*/.git/*' \
            -not -path '*/node_modules/*' \
            -print0 | sort -z | while IFS= read -r -d '' FILE; do
                if grep -Iq . "$FILE" 2>/dev/null; then
                    {
                        echo -e "\n\n========================================"
                        echo "ARQUIVO: $FILE"
                        echo -e "========================================\n"
                        cat "$FILE"
                    } >> "$AGGREGATED_FILE"
                else
                    echo "Pulando binário: $FILE" >&2
                fi
            done
    else
        echo "Aviso: '$DIR' não é um diretório válido ou acessível. Ignorando." >&2
    fi
done
