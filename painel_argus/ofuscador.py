# ofuscador_c.py

import re
import base64
import random
import string
import json
from typing import List, Dict, Tuple
import argparse
from pathlib import Path

# --- FUNÇÕES AUXILIARES DE GERAÇÃO DE NOME ---
def _gerar_nome_ofuscado(tamanho: int = 4) -> str:
    """Gera um nome aleatório e sem sentido (começa com letra)."""
    primeira_letra = random.choice(string.ascii_letters)
    resto = ''.join(random.choices(string.ascii_letters + string.digits, k=max(0, tamanho - 1)))
    return primeira_letra + resto

# --- FUNÇÃO DE DECODIFICAÇÃO C (Para Inclusão no Código C) ---
def _obter_funcao_decodificadora() -> str:
    """Retorna o código C da função de decodificação Base64."""
    return r"""
// Funcao de Decodificacao Base64 (Inserida para Obfuscacao)
static const char B64_T[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

char* decodificar_b64(const char* input) {
    size_t len = strlen(input);
    if (len == 0) return strdup("");
    size_t out_len = len / 4 * 3;
    if (len >= 1 && input[len - 1] == '=') out_len--;
    if (len >= 2 && input[len - 2] == '=') out_len--;

    char* output = (char*)malloc(out_len + 1);
    if (!output) return NULL;
    output[out_len] = '\0';
    int i = 0, j = 0;
    while (i < (int)len) {
        int val = 0;
        for (int k = 0; k < 4 && i + k < (int)len; k++) {
            val <<= 6;
            char c = input[i + k];
            int b64_index = -1;
            if (c >= 'A' && c <= 'Z') b64_index = c - 'A';
            else if (c >= 'a' && c <= 'z') b64_index = c - 'a' + 26;
            else if (c >= '0' && c <= '9') b64_index = c - '0' + 52;
            else if (c == '+') b64_index = 62;
            else if (c == '/') b64_index = 63;
            else if (c == '=') { val >>= 6; break; }
            if (b64_index != -1) { val |= b64_index; } else { val >>= 6; break;}
        }
        if (j < (int)out_len) output[j++] = (val >> 16) & 0xFF;
        if (j < (int)out_len) output[j++] = (val >> 8) & 0xFF;
        if (j < (int)out_len) output[j++] = val & 0xFF;
        i += 4;
    }
    return output;
}
"""

# --- FUNÇÃO EXPOSTA PARA O MENU ---

def ofuscar_codigo_c_hibrido(codigo: str) -> Tuple[str, Dict[str, str], Dict[str, str]]:
    """
    Função principal que aplica ofuscação de strings (Base64) e renomeação.
    Retorna: (codigo_ofuscado, mapa_b64, mapa_renomeacao)
    """

    palavras_chave_c = set([
        "auto", "break", "case", "char", "const", "continue", "default", "do",
        "double", "else", "enum", "extern", "float", "for", "goto", "if",
        "int", "long", "register", "return", "short", "signed", "sizeof",
        "static", "struct", "switch", "typedef", "union", "unsigned",
        "void", "volatile", "while", "main", "printf", "scanf", "malloc", "free", 
        "size_t", "NULL", "strdup", "include", "define", "ifdef", "ifndef", "endif", 
        "pragma", "error", "decodificar_b64", "B64_T", "strlen", "WSADATA", "SOCKET",
        "WSASocket", "WSAStartup", "WSACleanup", "inet_addr", "gethostbyname",
        "CreateProcess", "STARTUPINFO", "PROCESS_INFORMATION", "WaitForSingleObject",
        "closesocket", "CreateProcess", "HANDLE", "DWORD", "SOCKADDR"
    ])

    # 1. Obfuscação de Strings Literais (Base64)
    strings_encontrados: List[str] = re.findall(r'"((?:[^"\\]|\\.)*)"', codigo)
    mapa_b64: Dict[str, str] = {}
    for original in sorted(list(set(strings_encontrados)), key=len, reverse=True):
        if original == "": continue
        original_bytes = original.encode('utf-8')
        b64_encoded = base64.b64encode(original_bytes).decode('utf-8')
        nova_chamada = f'decodificar_b64("{b64_encoded}")'
        # Substitui APENAS as ocorrências exatas de literais (usa lookarounds)
        codigo = re.sub(r'(?<![A-Za-z0-9_])"' + re.escape(original) + r'"(?![A-Za-z0-9_])', nova_chamada, codigo)
        mapa_b64[original] = b64_encoded

    # 2. Inserir a função decodificadora e headers (garante que as headers necessárias existam)
    headers_necessarios = "#include <stdlib.h>\n#include <string.h>\n#include <stdio.h>\n\n"
    # Remove possíveis duplicatas de std headers antes de inserir (não remove windows/other headers)
    codigo = re.sub(r'#include\s+<(stdio|stdlib|string)\.h>\s*\n', '', codigo)
    codigo = headers_necessarios + _obter_funcao_decodificadora() + "\n" + codigo

    # 3. Renomeação de Identificadores
    identificador_regex = re.compile(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b')
    todos_identificadores: List[str] = identificador_regex.findall(codigo)

    identificadores_a_renomear = sorted(list(set(
        id for id in todos_identificadores if id not in palavras_chave_c
    )), key=len, reverse=True)

    mapa_renomeacao: Dict[str, str] = {}
    for identificador in identificadores_a_renomear:
        if identificador not in mapa_renomeacao:
            novo_nome = _gerar_nome_ofuscado(random.randint(2, 6))
            while novo_nome in mapa_renomeacao.values() or novo_nome in palavras_chave_c:
                novo_nome = _gerar_nome_ofuscado(random.randint(2, 6))
            mapa_renomeacao[identificador] = novo_nome

    # Aplica renomeações com boundary-aware substituição
    for original, ofuscado in mapa_renomeacao.items():
        codigo = re.sub(r'(?<![A-Za-z0-9_])' + re.escape(original) + r'(?![A-Za-z0-9_])', ofuscado, codigo)

    return codigo, mapa_b64, mapa_renomeacao

# Entrypoint CLI para compatibilidade com execução via subprocess
def main():
    parser = argparse.ArgumentParser(description="Ofuscador de código C (gera chamadas base64 + renomeação)")
    parser.add_argument('--input', '-i', help='Arquivo C de entrada (opcional).')
    parser.add_argument('--output', '-o', help='Arquivo C de saída (opcional).')
    parser.add_argument('--maps', '-m', help='Arquivo JSON para salvar mapas (opcional).')
    args = parser.parse_args()

    if args.input:
        in_path = Path(args.input)
        if not in_path.exists():
            print(f"Arquivo de entrada não encontrado: {in_path}", file=sys.stderr)
            raise SystemExit(2)
        codigo = in_path.read_text(encoding='utf-8')
    else:
        # se chamado sem input, não faz nada (útil ao importar)
        print("Nenhum arquivo de entrada fornecido. Saindo.", file=sys.stderr)
        return

    codigo_ofuscado, mapa_b64, mapa_renomeacao = ofuscar_codigo_c_hibrido(codigo)

    if args.output:
        Path(args.output).write_text(codigo_ofuscado, encoding='utf-8')
    else:
        print(codigo_ofuscado)

    if args.maps:
        with Path(args.maps).open('w', encoding='utf-8') as f:
            json.dump({'b64': mapa_b64, 'renomeacao': mapa_renomeacao}, f, indent=2, ensure_ascii=False)

    # Indica sucesso
    return

if __name__ == "__main__":
    import sys
    main()