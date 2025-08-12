#!/usr/bin/env python3
"""
Script de exemplo para demonstrar o uso do Gerenciador de Pedidos
Este script cria alguns pedidos e grupos de exemplo para testar o sistema
"""

import sqlite3
from datetime import datetime

def criar_exemplos():
    """Cria pedidos e grupos de exemplo no banco de dados"""
    
    # Conectar ao banco de dados
    conn = sqlite3.connect('pedidos.db')
    cursor = conn.cursor()
    
    print("🏈 Criando dados de exemplo para o Gerenciador de Pedidos...")
    
    # Criar grupos de exemplo
    grupos = [
        ("Grupo 1",),
        ("Grupo 2",),
        ("Grupo 3",)
    ]
    
    cursor.executemany('INSERT INTO grupos (nome) VALUES (?)', grupos)
    print("✅ Grupos criados com sucesso!")
    
    # Criar pedidos de exemplo
    pedidos = [
        # Pedidos com FRETE PADRÃO (para grupos)
        ("PED001", "João Silva", "Brasil 2024", "M", "FRETE PADRÃO"),
        ("PED002", "Maria Santos", "Real Madrid", "G", "FRETE PADRÃO"),
        ("PED003", "Pedro Costa", "Barcelona", "P", "FRETE PADRÃO"),
        ("PED004", "Ana Oliveira", "Brasil 2024", "GG", "FRETE PADRÃO"),
        ("PED005", "Carlos Lima", "Manchester United", "M", "FRETE PADRÃO"),
        ("PED006", "Lucia Ferreira", "Brasil 2024", "G", "FRETE PADRÃO"),
        ("PED007", "Roberto Alves", "Bayern Munich", "P", "FRETE PADRÃO"),
        ("PED008", "Fernanda Rocha", "Real Madrid", "M", "FRETE PADRÃO"),
        ("PED009", "Diego Souza", "Barcelona", "GG", "FRETE PADRÃO"),
        ("PED010", "Camila Torres", "Brasil 2024", "P", "FRETE PADRÃO"),
        
        # Pedidos EXPRESSO (envio direto)
        ("PED011", "Ricardo Mendes", "Brasil 2024", "M", "EXPRESSO"),
        ("PED012", "Juliana Costa", "Real Madrid", "G", "EXPRESSO"),
        ("PED013", "Marcelo Silva", "Barcelona", "P", "EXPRESSO"),
        ("PED014", "Patricia Lima", "Manchester United", "GG", "EXPRESSO"),
        ("PED015", "Thiago Santos", "Bayern Munich", "M", "EXPRESSO"),
    ]
    
    cursor.executemany('''
        INSERT INTO pedidos (id_pedido, nome_cliente, produto, tamanho, tipo_frete)
        VALUES (?, ?, ?, ?, ?)
    ''', pedidos)
    print("✅ Pedidos criados com sucesso!")
    
    # Adicionar alguns pedidos aos grupos
    # Grupo 1: 3 pedidos
    cursor.execute('UPDATE pedidos SET grupo_id = 1 WHERE id_pedido IN ("PED001", "PED002", "PED003")')
    
    # Grupo 2: 2 pedidos
    cursor.execute('UPDATE pedidos SET grupo_id = 2 WHERE id_pedido IN ("PED004", "PED005")')
    
    # Grupo 3: 1 pedido
    cursor.execute('UPDATE pedidos SET grupo_id = 3 WHERE id_pedido = "PED006"')
    
    # Marcar Grupo 1 como enviado
    cursor.execute('UPDATE grupos SET enviado = 1 WHERE id = 1')
    
    print("✅ Pedidos organizados em grupos!")
    print("✅ Grupo 1 marcado como enviado!")
    
    # Commit das alterações
    conn.commit()
    conn.close()
    
    print("\n🎉 Dados de exemplo criados com sucesso!")
    print("\n📊 Resumo dos dados criados:")
    print("   • 3 grupos criados")
    print("   • 15 pedidos criados (10 padrão + 5 expresso)")
    print("   • 6 pedidos organizados em grupos")
    print("   • 1 grupo marcado como enviado")
    print("\n🌐 Acesse http://localhost:5000 para ver o sistema funcionando!")

if __name__ == "__main__":
    try:
        criar_exemplos()
    except sqlite3.IntegrityError as e:
        print("⚠️  Erro: Alguns dados já existem no banco.")
        print("   Para recriar os dados, delete o arquivo 'pedidos.db' e execute novamente.")
    except Exception as e:
        print(f"❌ Erro ao criar dados de exemplo: {e}")
        print("   Certifique-se de que a aplicação foi executada pelo menos uma vez.")
