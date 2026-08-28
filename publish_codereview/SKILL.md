---
name: publish-codereview
description: Publica achados de uma code review (do skill code-reviewer ou de uma análise ad-hoc) como uma review formal no GitHub via `gh api`, comentário por arquivo/linha, com veredito explícito. Ative quando o usuário pedir para "publicar a review", "postar os comentários no PR", "abrir request changes", "comentar arquivo por arquivo".
triggers: ["publicar review", "postar review", "publish review", "request changes no PR", "comentar no PR arquivo por arquivo", "post inline comments"]
---

ROLE: publish-codereview
PRINCIPLE: publicar review é uma ação visível, assinada com a identidade do usuário, para terceiros — nunca publicar sem confirmação explícita do escopo e do veredito. Comentário por arquivo/linha, nunca um bloco único ("burst shot"), a menos que o usuário peça o contrário.

ESCOPO: este skill NÃO analisa código — ele publica achados que já existem na conversa (gerados pelo skill `code-reviewer`, pelo `code-review`, ou por uma comparação/análise ad-hoc). Se não houver achados prontos, rodar a análise primeiro (outro skill) antes de invocar este.

PIPELINE:

  1. INPUT RESOLUTION
     - Achados: reaproveitar da conversa — nunca re-analisar do zero se já existem achados aprovados.
     - Alvo: PR number + `owner/repo` (via URL informada, ou branch atual + `gh repo view --json owner,name`).
     - Idioma do corpo publicado: default en-US (times e PRs em inglês), independente do idioma da conversa — só perguntar se ambíguo.
     - Veredito (event da review): se o usuário não disser explicitamente, inferir do gate de severidade (ver VERDICT MAPPING) e SEMPRE confirmar antes de publicar.

  2. PRE-FLIGHT (sempre antes de montar qualquer JSON)
     - `gh auth status` → confirmar a identidade que vai assinar a review.
     - `gh pr view <n> --repo <owner>/<repo> --json headRefOid,reviews,comments` → obter `commit_id` do head e checar reviews/comentários já existentes, para não duplicar feedback já dado por outro reviewer.
     - `gh repo clone <owner>/<repo> <tmp-dir> -- --depth 1 --branch <headRefName>` (ou `gh api repos/.../contents/<path>` por arquivo) → obter o conteúdo EXATO de cada arquivo na revisão do PR.

  3. LINE MAPPING (por achado, obrigatório antes de escrever o comentário)
     - Localizar a linha exata no arquivo clonado (`cat -n <file>` / `grep -n`) — nunca estimar ou reaproveitar número de linha do diff bruto sem checar contra o arquivo real.
     - A linha DEVE pertencer ao diff do PR (linha adicionada `+` ou linha de contexto dentro de um hunk) — GitHub rejeita/perde o anchor de comentário em linhas fora do range visível do diff.
     - `side`: "RIGHT" para linha na versão nova (padrão, cobre a quase totalidade dos casos); "LEFT" só quando o achado é sobre uma linha removida.

  4. COMMENT TEMPLATE (um comentário por achado — nunca agrupar achados distintos)
     ```
     **<título em negrito, uma frase, a alegação central>**
     ```<diff ou linguagem do arquivo>
     <before/after ou trecho sugerido, quando aplicável>
     ```
     <1–3 frases: por que importa / o que quebra ou piora se não for corrigido — nunca "considere X" sem o porquê>
     ```
     - Comentário adaptado ao contexto local do arquivo — nunca um template genérico copiado sem ajuste entre arquivos diferentes.

  5. PAYLOAD & CONFIRMATION GATE
     - Montar JSON: `{commit_id, event, body (resumo geral, 1–3 frases, tom construtivo), comments: [{path, line, side, body}, ...]}`.
     - Validar com `jq . <payload>.json >/dev/null` antes de qualquer chamada de rede.
     - Apresentar ao usuário (via pergunta direta, ou AskUserQuestion se houver ambiguidade real) o veredito + a lista de achados que entrarão na review, antes de publicar — mesmo que o usuário já tenha pedido a ação antes na conversa: cada publish é uma nova confirmação se o payload mudou desde a última vez (achados incluídos/excluídos, idioma, veredito).

  6. EXECUTE
     ```
     gh api repos/<owner>/<repo>/pulls/<number>/reviews -X POST --input <payload>.json
     ```
     - Reportar a `html_url` retornada como confirmação final de que a review foi publicada.

  7. FALLBACK (sem comentários inline)
     - Se o usuário pedir explicitamente um resumo único (não arquivo por arquivo), usar `gh pr review <n> --repo <owner>/<repo> --request-changes --body-file <resumo>.md` em vez do passo 5/6 — mais simples, mas perde o anchoring por linha.

VERDICT MAPPING (quando o veredito não vier explícito do usuário):
  - Existe achado 🔴/bloqueante → event: REQUEST_CHANGES
  - Só existem achados 🟡/🟢 (melhorias, não bloqueantes) → perguntar ao usuário entre COMMENT e APPROVE; nunca assumir aprovação silenciosa
  - Nenhum achado sobrevive → perguntar se aprova (APPROVE) ou só comenta (COMMENT); nunca publicar REQUEST_CHANGES vazio

GUARDS & RESTRIÇÕES:
  - NUNCA publicar sem `gh auth status` confirmado e sem confirmação explícita do payload final (achados, veredito, idioma).
  - NUNCA inventar número de linha — sempre derivado do arquivo real checado no head SHA do PR (passo 2/3).
  - NUNCA agrupar múltiplos achados distintos em um único comentário "resumo" quando o pedido for arquivo por arquivo/linha por linha.
  - NUNCA reaproveitar ou duplicar comentários já postados por outro reviewer no mesmo PR (checado no PRE-FLIGHT).
  - NUNCA fazer merge, aprovar CI, forçar push, ou qualquer ação além de publicar a review pedida.
  - NUNCA traduzir o corpo da review para o idioma da conversa se o padrão do repositório/time for outro — perguntar apenas se genuinamente ambíguo.

GATE.out:
  payload=validado(jq) · linhas=confirmadas-no-arquivo-real(head SHA) · veredito=confirmado-pelo-usuário · duplicidade=checada(reviews/comments existentes) · gh-auth=ok
  → review publicada, retornar html_url · STATE:DONE
  else → STATE:BLOCKED (pedir a informação faltante antes de qualquer chamada de escrita)
