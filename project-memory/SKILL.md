---
name: project-memory
description: >
  Registra, consolida e recupera o histórico de execução do projeto.
  Ativar automaticamente ao início e fim de qualquer skill (exceto commiter):
  antes de agir → ler estado atual · após agir → gravar o que foi feito.
  Usar também quando o usuário perguntar "o que foi feito?", "onde paramos?",
  "qual o estado do projeto?", "resumo do progresso" ou qualquer variante.
  Funciona como memória compartilhada entre todas as skills do projeto.
---

# PROJECT-MEMORY

ROLE: guardião de estado · registra ações · fornece contexto · detecta conflitos
AUDIENCE: LLMs (outras skills) · humanos (revisão)
PRINCIPLE: append-only · máximo rastreabilidade · mínimo tokens por entrada

---

## ARQUIVOS

```
MEMORY_FILE:   .ai_context/PMEMORY.md    # persistente entre sessões
LOCK_SENTINEL: .ai_context/PMEMORY.lock # evita escrita concorrente
```

Se `MEMORY_FILE` não existir → criar com cabeçalho (ver INIT).

---

## PROTOCOLO DE USO PELAS SKILLS

Toda skill (exceto commiter) DEVE seguir este ciclo:

```
1. READ   → carregar contexto antes de agir
2. ACT    → executar tarefa principal
3. WRITE  → registrar o que foi feito
```

### 1 · READ — antes de agir

```bash
cat .ai_context/PMEMORY.md 2>/dev/null || echo "MEMORY_EMPTY"
```

Extrair do output:
- `CURRENT_STATE:` → qual estado a máquina está
- Últimas 5 entradas de LOG → contexto recente
- `BLOCKED:` → se houver bloqueio ativo, parar e reportar

### 2 · ACT

Executar normalmente. Capturar:
- O que foi feito (resumo ≤ 15 palavras)
- Resultado: `✓ concluído` | `⚠ parcial` | `✗ falhou` | `BLOCKED: <motivo>`
- Artefatos criados/modificados (paths)

### 3 · WRITE — após agir

Chamar a função de escrita (ver WRITE_ENTRY abaixo).

---

## WRITE_ENTRY

Formato de uma entrada de log:

```
[YYYY-MM-DD HH:MM] <SKILL-NAME> · <STATE> · <ação resumida> · <resultado> [· <artefato>]
```

Exemplos:

```
[2025-07-14 10:32] docx-generator · DRAFT · criou relatório-mensal.docx · ✓ concluído · /outputs/relatorio-mensal.docx
[2025-07-14 10:45] pdf-exporter  · EXPORT · tentou exportar PDF · ✗ falhou · erro: fonte ausente
[2025-07-14 11:00] pdf-exporter  · EXPORT · reexportou com fonte fallback · ✓ concluído · /outputs/relatorio.pdf
```

Script de escrita:

```bash
#!/bin/bash
MEMORY=".ai_context/PMEMORY.md"
LOCK=".ai_context/PMEMORY.lock"
ENTRY="$1"   # passar a linha formatada como argumento

# aguardar lock (máx 5s)
for i in $(seq 1 10); do
  [ ! -f "$LOCK" ] && break
  sleep 0.5
done

touch "$LOCK"
echo "$ENTRY" >> "$MEMORY"
rm -f "$LOCK"
```

DENY:
```
✗ editar linha existente
✗ omitir timestamp
✗ omitir nome da skill
✗ omitir resultado (✓ · ⚠ · ✗ · BLOCKED)
```

---

## INIT — estrutura inicial do arquivo

Quando `.ai_context/PMEMORY.md` não existe, criar com:

```markdown
---
name: project-memory-log
description: Log append-only de execuções do projeto.
created: <YYYY-MM-DD>
---

# PROJECT MEMORY LOG

CURRENT_STATE: INIT

## STATE MACHINE

INIT → IN_PROGRESS → REVIEW → DONE|BLOCKED

## LOG
```

---

## READ_SUMMARY — comando para humanos ou skills

Quando uma skill ou o usuário pedir resumo de estado:

```bash
# Últimas N entradas
tail -n 20 .ai_context/PMEMORY.md

# Só bloqueios ativos
grep "BLOCKED" .ai_context/PMEMORY.md | tail -5

# Artefatos produzidos
grep "✓" .ai_context/PMEMORY.md | grep -oP '/outputs/\S+'
```

Output formatado para o usuário:

```
SUMMARY:  <estado atual · última ação · bloqueios ativos|NONE>
ANÁLISE:
  ✓ <concluídos recentes>
  ⚠ <pendências>
  🔴 <bloqueios> [NONE se vazio]
PRÓXIMO:  <STATE sugerido> | AGUARDANDO_INPUT
```

---

## ATUALIZAR CURRENT_STATE

Quando uma skill muda de estado, atualizar a linha `CURRENT_STATE:` no arquivo:

```bash
MEMORY=".ai_context/PMEMORY.md"
NEW_STATE="$1"
# substituir linha CURRENT_STATE (única exceção ao append-only — só esta linha)
sed -i "s/^CURRENT_STATE:.*/CURRENT_STATE: $NEW_STATE/" "$MEMORY"
echo "[$(date '+%Y-%m-%d %H:%M')] project-memory · STATE_CHANGE · → $NEW_STATE · ✓" >> "$MEMORY"
```

---

## STATE MACHINE

```
INIT → IN_PROGRESS → REVIEW → DONE
                  ↘ BLOCKED → IN_PROGRESS (após desbloqueio)
```

GATE.in:  arquivo existe · cabeçalho presente
GATE.out: última entrada tem timestamp · resultado declarado · CURRENT_STATE atualizado → próxima skill pode prosseguir

---

## INTEGRAÇÃO COM sintax-architect

Todas as entradas de log DEVEM obedecer as regras R1–R14 do `sintax-architect`:

```
R2  separar itens inline com ·
R3  transições com →
R4  alternativas com |
R9  arquivo tem frontmatter YAML
R10 nome do arquivo em kebab-case
R14 log append-only · obrigatório no DOD
```

Violação detectada em entrada existente → NÃO editar · adicionar nova entrada com prefixo `⚠ CORRIGIDO:`.

---

## CHECKLIST DE USO (DOD por invocação)

```
PRE:
  [ ] leu MEMORY_FILE antes de agir
  [ ] verificou BLOCKED ativo
  [ ] identificou CURRENT_STATE

POST:
  [ ] escreveu entrada com timestamp
  [ ] resultado declarado (✓ · ⚠ · ✗ · BLOCKED)
  [ ] artefatos listados se existirem
  [ ] CURRENT_STATE atualizado se mudou
```
