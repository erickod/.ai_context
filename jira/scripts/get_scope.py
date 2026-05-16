#!/usr/bin/env python3
"""
get_scope.py — Busca resumo e descrição de uma issue do Jira Cloud.

Uso:
    python get_scope.py <ISSUE_KEY>

Exemplo:
    python get_scope.py LEND-7146

Variáveis de ambiente requeridas:
    JIRA_SERVER_URL   — ex: https://empresa.atlassian.net
    JIRA_USER_EMAIL   — ex: dev@empresa.com
    JIRA_API_TOKEN    — API Token gerado em id.atlassian.com
"""

import json
import os
import sys

from jira.exceptions import JIRAError

from jira import JIRA

# ---------------------------------------------------------------------------
# Constantes de erro
# ---------------------------------------------------------------------------

ERR_NOT_FOUND = "NOT_FOUND"
ERR_AUTH_FAILED = "AUTH_FAILED"
ERR_CONNECTION_ERROR = "CONNECTION_ERROR"
ERR_UNKNOWN = "UNKNOWN"


# ---------------------------------------------------------------------------
# Helpers de output
# ---------------------------------------------------------------------------


def _output(payload: dict) -> None:
    """Serializa e imprime o payload JSON no stdout."""
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _success(key: str, summary: str, description: str | None) -> None:
    _output(
        {
            "key": key,
            "summary": summary,
            "description": description,
            "status": "ok",
        }
    )


def _error(key: str, code: str, message: str) -> None:
    _output(
        {
            "key": key,
            "status": "error",
            "error_code": code,
            "message": message,
        }
    )


# ---------------------------------------------------------------------------
# Conexão e busca
# ---------------------------------------------------------------------------


def _build_client() -> JIRA:
    """
    Instancia o cliente Jira a partir das variáveis de ambiente.
    Lança ValueError se alguma variável obrigatória estiver ausente.
    Lança JIRAError em falha de autenticação/conexão.
    """
    server_url = os.environ.get("JIRA_SERVER_URL", "").strip()
    email = os.environ.get("JIRA_USER_EMAIL", "").strip()
    api_token = os.environ.get("JIRA_API_TOKEN", "").strip()

    missing = [
        v
        for v, val in [
            ("JIRA_SERVER_URL", server_url),
            ("JIRA_USER_EMAIL", email),
            ("JIRA_API_TOKEN", api_token),
        ]
        if not val
    ]

    if missing:
        raise ValueError(f"Variáveis de ambiente ausentes: {', '.join(missing)}")

    return JIRA(server=server_url, basic_auth=(email, api_token))


def get_task_scope(issue_key: str) -> None:
    """
    Busca os campos 'summary' e 'description' da issue e imprime JSON no stdout.
    Todos os caminhos de erro também resultam em JSON estruturado (nunca levantam).
    """
    issue_key = issue_key.strip().upper()

    # Validação mínima do formato da chave (ex: PROJ-123)
    if "-" not in issue_key:
        _error(
            issue_key,
            ERR_NOT_FOUND,
            f"Formato de chave inválido: '{issue_key}'. Esperado: PROJETO-123.",
        )
        return

    # Conexão
    try:
        client = _build_client()
    except ValueError as exc:
        _error(issue_key, ERR_AUTH_FAILED, str(exc))
        return
    except JIRAError as exc:
        # status_code 401/403 → autenticação; outros → conexão
        if exc.status_code in (401, 403):
            _error(
                issue_key,
                ERR_AUTH_FAILED,
                f"Credenciais inválidas ou sem permissão. ({exc.text})",
            )
        else:
            _error(
                issue_key,
                ERR_CONNECTION_ERROR,
                f"Falha ao conectar ao Jira: {exc.text}",
            )
        return
    except Exception as exc:
        _error(issue_key, ERR_CONNECTION_ERROR, f"Erro inesperado na conexão: {exc}")
        return

    # Busca da issue
    try:
        issue = client.issue(issue_key, fields=["summary", "description"])
    except JIRAError as exc:
        if exc.status_code == 404:
            _error(issue_key, ERR_NOT_FOUND, f"Issue '{issue_key}' não encontrada.")
        elif exc.status_code in (401, 403):
            _error(
                issue_key,
                ERR_AUTH_FAILED,
                f"Sem permissão para ler '{issue_key}'. ({exc.text})",
            )
        else:
            _error(
                issue_key,
                ERR_UNKNOWN,
                f"Erro da API Jira (HTTP {exc.status_code}): {exc.text}",
            )
        return
    except Exception as exc:
        _error(issue_key, ERR_UNKNOWN, f"Erro inesperado: {exc}")
        return

    _success(
        key=issue.key,
        summary=issue.fields.summary,
        description=issue.fields.description,  # pode ser None
    )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(
            "Uso: python get_scope.py <ISSUE_KEY>\n"
            "Exemplo: python get_scope.py LEND-7146",
            file=sys.stderr,
        )
        sys.exit(1)

    get_task_scope(sys.argv[1])
