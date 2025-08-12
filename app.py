from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, flash
import sqlite3
import csv
import io
from datetime import datetime
import os
import pandas as pd
try:
    import chardet
    CHARDET_AVAILABLE = True
except ImportError:
    CHARDET_AVAILABLE = False

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Necessário para flash messages

# Configuração do banco de dados
DATABASE = 'pedidos.db'

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Tabela de pedidos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_pedido TEXT UNIQUE NOT NULL,
            nome_cliente TEXT NOT NULL,
            produto TEXT NOT NULL,
            tamanho TEXT NOT NULL,
            tipo_frete TEXT NOT NULL,
            grupo_id INTEGER,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (grupo_id) REFERENCES grupos (id)
        )
    ''')
    
    # Tabela de grupos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grupos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            codigo_rastreio TEXT,
            enviado BOOLEAN DEFAULT 0,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela para dados completos dos pedidos importados
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos_completos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_pedido TEXT UNIQUE NOT NULL,
            email TEXT,
            data_pedido TEXT,
            status_pedido TEXT,
            status_pagamento TEXT,
            status_envio TEXT,
            moeda TEXT,
            subtotal REAL,
            desconto REAL,
            valor_frete REAL,
            total REAL,
            nome_comprador TEXT,
            cpf_cnpj TEXT,
            telefone TEXT,
            nome_entrega TEXT,
            telefone_entrega TEXT,
            endereco TEXT,
            numero TEXT,
            complemento TEXT,
            bairro TEXT,
            cidade TEXT,
            codigo_postal TEXT,
            estado TEXT,
            pais TEXT,
            forma_entrega TEXT,
            forma_pagamento TEXT,
            cupom_desconto TEXT,
            anotacoes_comprador TEXT,
            anotacoes_vendedor TEXT,
            data_pagamento TEXT,
            data_envio TEXT,
            nome_produto TEXT,
            valor_produto REAL,
            data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Adicionar coluna codigo_rastreio se não existir
    try:
        cursor.execute('ALTER TABLE grupos ADD COLUMN codigo_rastreio TEXT')
        print("Coluna codigo_rastreio adicionada à tabela grupos")
    except sqlite3.OperationalError:
        print("Coluna codigo_rastreio já existe na tabela grupos")
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Retorna uma conexão com o banco de dados"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Página principal - Dashboard"""
    conn = get_db_connection()
    
    # Buscar grupos com pedidos
    grupos = conn.execute('''
        SELECT g.*, COUNT(p.id) as total_pedidos
        FROM grupos g
        LEFT JOIN pedidos p ON g.id = p.grupo_id
        GROUP BY g.id
        ORDER BY g.id
    ''').fetchall()
    
    # Buscar pedidos expresso
    pedidos_expresso = conn.execute('''
        SELECT * FROM pedidos 
        WHERE tipo_frete = 'EXPRESSO' 
        ORDER BY data_criacao DESC
    ''').fetchall()
    
    # Buscar pedidos por grupo
    pedidos_por_grupo = {}
    for grupo in grupos:
        pedidos = conn.execute('''
            SELECT * FROM pedidos 
            WHERE grupo_id = ? 
            ORDER BY data_criacao
        ''', (grupo['id'],)).fetchall()
        pedidos_por_grupo[grupo['id']] = pedidos
    
    conn.close()
    
    return render_template('index.html', 
                         grupos=grupos, 
                         pedidos_expresso=pedidos_expresso,
                         pedidos_por_grupo=pedidos_por_grupo)

@app.route('/importar_csv', methods=['GET', 'POST'])
def importar_csv():
    """Importar pedidos de arquivo CSV"""
    if request.method == 'POST':
        if 'arquivo' not in request.files:
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
        
        arquivo = request.files['arquivo']
        if arquivo.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
        
        if arquivo and arquivo.filename.endswith('.csv'):
            try:
                # Detectar codificação automaticamente se chardet estiver disponível
                if CHARDET_AVAILABLE:
                    arquivo.seek(0)
                    raw_data = arquivo.read()
                    arquivo.seek(0)
                    
                    # Detectar codificação
                    result = chardet.detect(raw_data)
                    detected_encoding = result['encoding']
                    confidence = result['confidence']
                    
                    print(f"Codificação detectada: {detected_encoding} (confiança: {confidence:.2f})")
                    
                    # Tentar usar a codificação detectada
                    try:
                        # Primeiro tentar com separador padrão (vírgula)
                        df = pd.read_csv(arquivo, encoding=detected_encoding, on_bad_lines='skip', quoting=csv.QUOTE_ALL)
                        print(f"Arquivo lido com sucesso usando codificação detectada: {detected_encoding}")
                    except (UnicodeDecodeError, pd.errors.ParserError) as e:
                        print(f"Falha com codificação detectada e separador padrão: {e}")
                        try:
                            # Tentar com separador ponto e vírgula
                            arquivo.seek(0)
                            df = pd.read_csv(arquivo, encoding=detected_encoding, sep=';', on_bad_lines='skip', quoting=csv.QUOTE_ALL)
                            print(f"Arquivo lido com sucesso usando codificação detectada e separador ';': {detected_encoding}")
                        except (UnicodeDecodeError, pd.errors.ParserError) as e2:
                            print(f"Falha com codificação detectada e separador ';': {e2}")
                            df = None
                else:
                    df = None
                
                # Se a detecção automática falhou ou não está disponível, tentar codificações comuns
                if df is None:
                    encodings = ['utf-8', 'iso-8859-1', 'windows-1252', 'latin1', 'cp1252']
                    
                    for encoding in encodings:
                        try:
                            arquivo.seek(0)  # Voltar ao início do arquivo
                            df = pd.read_csv(arquivo, encoding=encoding, on_bad_lines='skip', quoting=csv.QUOTE_ALL)
                            print(f"Arquivo lido com sucesso usando codificação: {encoding}")
                            break
                        except (UnicodeDecodeError, pd.errors.ParserError) as e:
                            print(f"Falha com codificação {encoding}: {e}")
                            continue
                
                if df is None:
                    # Tentar métodos alternativos de leitura
                    print("Tentando métodos alternativos de leitura...")
                    
                    # Método 1: Tentar com engine='python' (mais flexível)
                    for encoding in ['utf-8', 'iso-8859-1', 'windows-1252']:
                        try:
                            arquivo.seek(0)
                            df = pd.read_csv(arquivo, encoding=encoding, engine='python', on_bad_lines='skip')
                            print(f"Arquivo lido com sucesso usando engine='python' e codificação: {encoding}")
                            break
                        except Exception as e:
                            print(f"Falha com engine='python' e codificação {encoding}: {e}")
                            continue
                    
                    # Método 2: Tentar com separador diferente
                    if df is None:
                        for encoding in ['utf-8', 'iso-8859-1', 'windows-1252']:
                            try:
                                arquivo.seek(0)
                                df = pd.read_csv(arquivo, encoding=encoding, sep=';', on_bad_lines='skip')
                                print(f"Arquivo lido com sucesso usando separador ';' e codificação: {encoding}")
                                break
                            except Exception as e:
                                print(f"Falha com separador ';' e codificação {encoding}: {e}")
                                continue
                    
                    # Método 3: Tentar ler linha por linha para debug
                    if df is None:
                        print("Tentando análise linha por linha para debug...")
                        try:
                            arquivo.seek(0)
                            linhas = arquivo.readlines()
                            print(f"Total de linhas no arquivo: {len(linhas)}")
                            print("Primeiras 3 linhas:")
                            for i, linha in enumerate(linhas[:3]):
                                print(f"Linha {i+1}: {linha[:100]}...")
                        except Exception as e:
                            print(f"Erro ao ler linhas: {e}")
                
                if df is None:
                    flash('Não foi possível ler o arquivo CSV. Verifique se o arquivo está em um formato válido. Tente salvar como "CSV UTF-8" no Excel.', 'error')
                    return redirect(request.url)
                
                # Debug: Mostrar informações sobre o DataFrame
                print(f"DataFrame carregado com sucesso!")
                print(f"Shape: {df.shape}")
                print(f"Colunas: {list(df.columns)}")
                print(f"Primeiras 2 linhas:")
                print(df.head(2))
                
                # Se o DataFrame tem apenas uma coluna, tentar separar por ponto e vírgula
                if len(df.columns) == 1:
                    print("Detectado arquivo com separador ';'. Tentando separar colunas...")
                    try:
                        # Pegar a primeira coluna e separar por ponto e vírgula
                        primeira_coluna = df.columns[0]
                        df = df[primeira_coluna].str.split(';', expand=True)
                        
                        # Definir os nomes das colunas baseado na primeira linha
                        if len(df.columns) >= 33:  # Verificar se tem pelo menos 33 colunas
                            # Mapear as colunas principais que precisamos (45 colunas do arquivo real)
                            colunas_mapeadas = [
                                'Número do Pedido', 'E-mail', 'Data', 'Status do Pedido', 
                                'Status do Pagamento', 'Status do Envio', 'Moeda', 'Subtotal', 
                                'Desconto', 'Valor do Frete', 'Total', 'Nome do comprador', 
                                'CPF / CNPJ', 'Telefone', 'Nome para a entrega', 'Telefone para a entrega', 
                                'Endereço', 'Número', 'Complemento', 'Bairro', 'Cidade', 
                                'Código postal', 'Estado', 'País', 'Forma de Entrega', 
                                'Forma de Pagamento', 'Cupom de Desconto', 'Anotações do Comprador', 
                                'Anotações do Vendedor', 'Data de pagamento', 'Data de envío', 
                                'Nome do Produto', 'Valor do Produto', 'Quantidade Comprada',
                                'SKU', 'Canal', 'Código de rastreio do envio', 
                                'Identificador da transação no meio de pagamento', 'Identificador do pedido',
                                'Produto Fisico', 'Pessoa que registrou a venda', 'Local de venda',
                                'Vendedor', 'Data e hora do cancelamento', 'Motivo do cancelamento'
                            ]
                            
                            # Se o arquivo tem mais colunas, adicionar as extras
                            if len(df.columns) > 45:
                                colunas_extras = [f'Coluna_{i}' for i in range(45, len(df.columns))]
                                colunas_mapeadas.extend(colunas_extras)
                            
                            df.columns = colunas_mapeadas
                            print(f"Colunas separadas com sucesso! Total de colunas: {len(df.columns)}")
                            print(f"Primeiras 10 colunas: {list(df.columns[:10])}")
                        else:
                            print(f"Arquivo tem {len(df.columns)} colunas, mas esperamos pelo menos 33")
                    except Exception as e:
                        print(f"Erro ao separar colunas: {e}")
                
                # Verificar se as colunas necessárias existem
                colunas_esperadas = [
                    'Número do Pedido', 'E-mail', 'Data', 'Status do Pedido', 
                    'Status do Pagamento', 'Status do Envio', 'Moeda', 'Subtotal', 
                    'Desconto', 'Valor do Frete', 'Total', 'Nome do comprador', 
                    'CPF / CNPJ', 'Telefone', 'Nome para a entrega', 'Telefone para a entrega', 
                    'Endereço', 'Número', 'Complemento', 'Bairro', 'Cidade', 
                    'Código postal', 'Estado', 'País', 'Forma de Entrega', 
                    'Forma de Pagamento', 'Cupom de Desconto', 'Anotações do Comprador', 
                    'Anotações do Vendedor', 'Data de pagamento', 'Data de envío', 
                    'Nome do Produto', 'Valor do Produto'
                ]
                
                # Verificar colunas faltantes
                colunas_faltantes = [col for col in colunas_esperadas if col not in df.columns]
                if colunas_faltantes:
                    flash(f'Colunas faltantes no CSV: {", ".join(colunas_faltantes)}', 'error')
                    return redirect(request.url)
                
                conn = get_db_connection()
                pedidos_importados = 0
                pedidos_duplicados = 0
                erros = 0
                
                print(f"Total de linhas no DataFrame: {len(df)}")
                print(f"Processando {len(df)} linhas...")
                
                linhas_processadas = 0
                linhas_puladas = 0
                
                # Agrupar linhas por número do pedido
                pedidos_agrupados = {}
                
                for index, row in df.iterrows():
                    try:
                        # Debug: mostrar algumas linhas para verificar
                        if index < 5:
                            print(f"Processando linha {index + 1}: Número do Pedido = '{row['Número do Pedido']}'")
                        
                        # Verificar se é uma linha válida (não vazia)
                        numero_pedido = str(row['Número do Pedido']).strip()
                        if pd.isna(row['Número do Pedido']) or numero_pedido == '' or numero_pedido == 'nan':
                            linhas_puladas += 1
                            if index < 10:  # Mostrar apenas as primeiras 10 linhas puladas
                                print(f"Linha {index + 1} pulada: número do pedido vazio ou inválido")
                            continue
                        
                        linhas_processadas += 1
                        
                        # Agrupar por número do pedido
                        if numero_pedido not in pedidos_agrupados:
                            pedidos_agrupados[numero_pedido] = []
                        pedidos_agrupados[numero_pedido].append(row)
                        
                    except Exception as e:
                        erros += 1
                        print(f"Erro ao processar linha {index + 1}: {e}")
                
                print(f"Total de pedidos únicos encontrados: {len(pedidos_agrupados)}")
                
                # Processar cada pedido agrupado
                for numero_pedido, linhas_pedido in pedidos_agrupados.items():
                    try:
                        # Pegar a primeira linha que tem todos os dados
                        linha_principal = linhas_pedido[0]
                        
                        # Debug
                        if len(pedidos_agrupados) <= 20:  # Mostrar apenas se tiver poucos pedidos
                            print(f"Processando pedido {numero_pedido} com {len(linhas_pedido)} produtos")
                        
                        # Preparar dados base do pedido (da primeira linha)
                        dados_base = {
                            'numero_pedido': str(linha_principal['Número do Pedido']).strip(),
                            'email': str(linha_principal['E-mail']).strip() if pd.notna(linha_principal['E-mail']) else '',
                            'data_pedido': str(linha_principal['Data']).strip() if pd.notna(linha_principal['Data']) else '',
                            'status_pedido': str(linha_principal['Status do Pedido']).strip() if pd.notna(linha_principal['Status do Pedido']) else '',
                            'status_pagamento': str(linha_principal['Status do Pagamento']).strip() if pd.notna(linha_principal['Status do Pagamento']) else '',
                            'status_envio': str(linha_principal['Status do Envio']).strip() if pd.notna(linha_principal['Status do Envio']) else '',
                            'moeda': str(linha_principal['Moeda']).strip() if pd.notna(linha_principal['Moeda']) else '',
                            'subtotal': float(linha_principal['Subtotal']) if pd.notna(linha_principal['Subtotal']) and str(linha_principal['Subtotal']).strip() != '' else 0.0,
                            'desconto': float(linha_principal['Desconto']) if pd.notna(linha_principal['Desconto']) and str(linha_principal['Desconto']).strip() != '' else 0.0,
                            'valor_frete': float(linha_principal['Valor do Frete']) if pd.notna(linha_principal['Valor do Frete']) and str(linha_principal['Valor do Frete']).strip() != '' else 0.0,
                            'total': float(linha_principal['Total']) if pd.notna(linha_principal['Total']) and str(linha_principal['Total']).strip() != '' else 0.0,
                            'nome_comprador': str(linha_principal['Nome do comprador']).strip() if pd.notna(linha_principal['Nome do comprador']) else '',
                            'cpf_cnpj': str(linha_principal['CPF / CNPJ']).strip() if pd.notna(linha_principal['CPF / CNPJ']) else '',
                            'telefone': str(linha_principal['Telefone']).strip() if pd.notna(linha_principal['Telefone']) else '',
                            'nome_entrega': str(linha_principal['Nome para a entrega']).strip() if pd.notna(linha_principal['Nome para a entrega']) else '',
                            'telefone_entrega': str(linha_principal['Telefone para a entrega']).strip() if pd.notna(linha_principal['Telefone para a entrega']) else '',
                            'endereco': str(linha_principal['Endereço']).strip() if pd.notna(linha_principal['Endereço']) else '',
                            'numero': str(linha_principal['Número']).strip() if pd.notna(linha_principal['Número']) else '',
                            'complemento': str(linha_principal['Complemento']).strip() if pd.notna(linha_principal['Complemento']) else '',
                            'bairro': str(linha_principal['Bairro']).strip() if pd.notna(linha_principal['Bairro']) else '',
                            'cidade': str(linha_principal['Cidade']).strip() if pd.notna(linha_principal['Cidade']) else '',
                            'codigo_postal': str(linha_principal['Código postal']).strip() if pd.notna(linha_principal['Código postal']) else '',
                            'estado': str(linha_principal['Estado']).strip() if pd.notna(linha_principal['Estado']) else '',
                            'pais': str(linha_principal['País']).strip() if pd.notna(linha_principal['País']) else '',
                            'forma_entrega': str(linha_principal['Forma de Entrega']).strip() if pd.notna(linha_principal['Forma de Entrega']) else '',
                            'forma_pagamento': str(linha_principal['Forma de Pagamento']).strip() if pd.notna(linha_principal['Forma de Pagamento']) else '',
                            'cupom_desconto': str(linha_principal['Cupom de Desconto']).strip() if pd.notna(linha_principal['Cupom de Desconto']) else '',
                            'anotacoes_comprador': str(linha_principal['Anotações do Comprador']).strip() if pd.notna(linha_principal['Anotações do Comprador']) else '',
                            'anotacoes_vendedor': str(linha_principal['Anotações do Vendedor']).strip() if pd.notna(linha_principal['Anotações do Vendedor']) else '',
                            'data_pagamento': str(linha_principal['Data de pagamento']).strip() if pd.notna(linha_principal['Data de pagamento']) else '',
                            'data_envio': str(linha_principal['Data de envío']).strip() if pd.notna(linha_principal['Data de envío']) else ''
                        }
                        
                        # Determinar tipo de frete baseado na forma de entrega
                        tipo_frete = 'EXPRESSO' if 'expresso' in dados_base['forma_entrega'].lower() else 'FRETE PADRÃO'
                        
                        # Processar cada linha do pedido (cada produto)
                        for i, linha in enumerate(linhas_pedido):
                            try:
                                # Pegar dados do produto desta linha
                                nome_produto = str(linha['Nome do Produto']).strip() if pd.notna(linha['Nome do Produto']) else ''
                                valor_produto = float(linha['Valor do Produto']) if pd.notna(linha['Valor do Produto']) and str(linha['Valor do Produto']).strip() != '' else 0.0
                                
                                # Criar ID único para cada produto do pedido
                                id_produto = f"{numero_pedido}_{i+1}" if i > 0 else numero_pedido
                                
                                # Inserir na tabela de pedidos completos
                                try:
                                    conn.execute('''
                                        INSERT INTO pedidos_completos (
                                            numero_pedido, email, data_pedido, status_pedido, status_pagamento,
                                            status_envio, moeda, subtotal, desconto, valor_frete, total,
                                            nome_comprador, cpf_cnpj, telefone, nome_entrega, telefone_entrega,
                                            endereco, numero, complemento, bairro, cidade, codigo_postal,
                                            estado, pais, forma_entrega, forma_pagamento, cupom_desconto,
                                            anotacoes_comprador, anotacoes_vendedor, data_pagamento,
                                            data_envio, nome_produto, valor_produto
                                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    ''', (
                                        id_produto, dados_base['email'], dados_base['data_pedido'],
                                        dados_base['status_pedido'], dados_base['status_pagamento'], dados_base['status_envio'],
                                        dados_base['moeda'], dados_base['subtotal'], dados_base['desconto'], dados_base['valor_frete'],
                                        dados_base['total'], dados_base['nome_comprador'], dados_base['cpf_cnpj'], dados_base['telefone'],
                                        dados_base['nome_entrega'], dados_base['telefone_entrega'], dados_base['endereco'],
                                        dados_base['numero'], dados_base['complemento'], dados_base['bairro'], dados_base['cidade'],
                                        dados_base['codigo_postal'], dados_base['estado'], dados_base['pais'], dados_base['forma_entrega'],
                                        dados_base['forma_pagamento'], dados_base['cupom_desconto'], dados_base['anotacoes_comprador'],
                                        dados_base['anotacoes_vendedor'], dados_base['data_pagamento'], dados_base['data_envio'],
                                        nome_produto, valor_produto
                                    ))
                                except sqlite3.IntegrityError:
                                    # Produto já existe, pular
                                    pedidos_duplicados += 1
                                    continue
                                
                                # Extrair tamanho do nome do produto
                                tamanho = 'M'  # Tamanho padrão
                                if nome_produto:
                                    # Tentar extrair tamanho do nome do produto
                                    tamanhos = ['PP', 'P', 'M', 'G', 'GG', 'XG', 'XXG']
                                    for t in tamanhos:
                                        if t in nome_produto.upper():
                                            tamanho = t
                                            break
                                
                                # Criar pedido no sistema principal
                                try:
                                    conn.execute('''
                                        INSERT INTO pedidos (id_pedido, nome_cliente, produto, tamanho, tipo_frete)
                                        VALUES (?, ?, ?, ?, ?)
                                    ''', (
                                        id_produto,
                                        dados_base['nome_comprador'],
                                        nome_produto,
                                        tamanho,
                                        tipo_frete
                                    ))
                                    pedidos_importados += 1
                                except sqlite3.IntegrityError:
                                    pedidos_duplicados += 1
                                
                            except Exception as e:
                                erros += 1
                                print(f"Erro ao processar produto {i+1} do pedido {numero_pedido}: {e}")
                        
                    except Exception as e:
                        erros += 1
                        print(f"Erro ao processar pedido {numero_pedido}: {e}")
                        

                
                conn.commit()
                conn.close()
                
                print(f"Resumo do processamento:")
                print(f"- Total de linhas no DataFrame: {len(df)}")
                print(f"- Linhas processadas: {linhas_processadas}")
                print(f"- Linhas puladas: {linhas_puladas}")
                print(f"- Pedidos importados: {pedidos_importados}")
                print(f"- Pedidos duplicados: {pedidos_duplicados}")
                print(f"- Erros: {erros}")
                
                flash(f'Importação concluída! {pedidos_importados} pedidos importados, {pedidos_duplicados} duplicados, {erros} erros.', 'success')
                return redirect(url_for('index'))
                
            except Exception as e:
                flash(f'Erro ao processar arquivo: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Arquivo deve ser CSV', 'error')
            return redirect(request.url)
    
    return render_template('importar_csv.html')

@app.route('/pedidos_importados')
def pedidos_importados():
    """Visualizar pedidos importados do CSV"""
    conn = get_db_connection()
    pedidos = conn.execute('''
        SELECT * FROM pedidos_completos 
        ORDER BY data_importacao DESC
    ''').fetchall()
    conn.close()
    
    return render_template('pedidos_importados.html', pedidos=pedidos)

@app.route('/pedido/<pedido_id>/detalhes')
def detalhes_pedido(pedido_id):
    """Ver detalhes completos de um pedido importado"""
    conn = get_db_connection()
    pedido = conn.execute('''
        SELECT * FROM pedidos_completos 
        WHERE numero_pedido = ?
    ''', (pedido_id,)).fetchone()
    conn.close()
    
    if not pedido:
        flash('Pedido não encontrado', 'error')
        return redirect(url_for('pedidos_importados'))
    
    return render_template('detalhes_pedido.html', pedido=pedido)

@app.route('/pedido/novo', methods=['GET', 'POST'])
def novo_pedido():
    """Criar novo pedido"""
    if request.method == 'POST':
        id_pedido = request.form['id_pedido']
        nome_cliente = request.form['nome_cliente']
        produto = request.form['produto']
        tamanho = request.form['tamanho']
        tipo_frete = request.form['tipo_frete']
        
        conn = get_db_connection()
        
        try:
            conn.execute('''
                INSERT INTO pedidos (id_pedido, nome_cliente, produto, tamanho, tipo_frete)
                VALUES (?, ?, ?, ?, ?)
            ''', (id_pedido, nome_cliente, produto, tamanho, tipo_frete))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            conn.close()
            return "Erro: ID do pedido já existe!", 400
    
    return render_template('novo_pedido.html')

@app.route('/grupo/novo', methods=['GET', 'POST'])
def novo_grupo():
    """Criar novo grupo"""
    if request.method == 'POST':
        nome = request.form['nome']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO grupos (nome) VALUES (?)', (nome,))
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))
    
    return render_template('novo_grupo.html')

@app.route('/grupo/<int:grupo_id>/adicionar_pedido', methods=['GET', 'POST'])
def adicionar_pedido_grupo(grupo_id):
    """Adicionar pedido a um grupo"""
    conn = get_db_connection()
    
    if request.method == 'POST':
        pedido_id = request.form['pedido_id']
        
        # Verificar se o grupo tem menos de 5 pedidos
        count = conn.execute('SELECT COUNT(*) FROM pedidos WHERE grupo_id = ?', (grupo_id,)).fetchone()[0]
        if count >= 5:
            conn.close()
            return "Erro: Grupo já tem 5 pedidos!", 400
        
        # Verificar se o pedido existe e é do tipo padrão
        pedido = conn.execute('SELECT * FROM pedidos WHERE id_pedido = ?', (pedido_id,)).fetchone()
        if not pedido:
            conn.close()
            return "Erro: Pedido não encontrado!", 404
        
        if pedido['tipo_frete'] != 'FRETE PADRÃO':
            conn.close()
            return "Erro: Apenas pedidos com FRETE PADRÃO podem ser adicionados a grupos!", 400
        
        # Adicionar pedido ao grupo
        conn.execute('UPDATE pedidos SET grupo_id = ? WHERE id_pedido = ?', (grupo_id, pedido_id))
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))
    
    # Buscar pedidos disponíveis (sem grupo e com frete padrão)
    pedidos_disponiveis = conn.execute('''
        SELECT * FROM pedidos 
        WHERE grupo_id IS NULL AND tipo_frete = 'FRETE PADRÃO'
        ORDER BY data_criacao
    ''').fetchall()
    
    grupo = conn.execute('SELECT * FROM grupos WHERE id = ?', (grupo_id,)).fetchone()
    conn.close()
    
    return render_template('adicionar_pedido_grupo.html', 
                         grupo=grupo, 
                         pedidos_disponiveis=pedidos_disponiveis)

@app.route('/grupo/<int:grupo_id>/remover_pedido/<pedido_id>')
def remover_pedido_grupo(grupo_id, pedido_id):
    """Remover pedido de um grupo"""
    conn = get_db_connection()
    conn.execute('UPDATE pedidos SET grupo_id = NULL WHERE id_pedido = ?', (pedido_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/grupo/<int:grupo_id>/marcar_enviado', methods=['GET', 'POST'])
def marcar_grupo_enviado(grupo_id):
    """Marcar grupo como enviado com código de rastreio"""
    try:
        conn = get_db_connection()
        
        # Verificar se o grupo existe
        grupo = conn.execute('SELECT * FROM grupos WHERE id = ?', (grupo_id,)).fetchone()
        if not grupo:
            flash('Grupo não encontrado', 'error')
            conn.close()
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            codigo_rastreio = request.form.get('codigo_rastreio', '').strip()
            
            try:
                # Marcar como enviado e salvar código de rastreio
                conn.execute('UPDATE grupos SET enviado = 1, codigo_rastreio = ? WHERE id = ?', (codigo_rastreio, grupo_id))
                conn.commit()
                flash(f'Grupo "{grupo["nome"]}" marcado como enviado! Código de rastreio: {codigo_rastreio}', 'success')
            except Exception as e:
                flash(f'Erro ao marcar grupo como enviado: {str(e)}', 'error')
            finally:
                conn.close()
            
            return redirect(url_for('index'))
        
        conn.close()
        return render_template('marcar_enviado_rastreio.html', grupo=grupo)
    except Exception as e:
        flash(f'Erro interno: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/grupo/<int:grupo_id>/marcar_nao_enviado')
def marcar_grupo_nao_enviado(grupo_id):
    """Marcar grupo como não enviado"""
    conn = get_db_connection()
    
    # Verificar se o grupo existe
    grupo = conn.execute('SELECT * FROM grupos WHERE id = ?', (grupo_id,)).fetchone()
    if not grupo:
        flash('Grupo não encontrado', 'error')
        conn.close()
        return redirect(url_for('index'))
    
    try:
        # Marcar como não enviado e limpar código de rastreio
        conn.execute('UPDATE grupos SET enviado = 0, codigo_rastreio = NULL WHERE id = ?', (grupo_id,))
        conn.commit()
        flash(f'Grupo "{grupo["nome"]}" marcado como pendente!', 'success')
    except Exception as e:
        flash(f'Erro ao marcar grupo como pendente: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('index'))

@app.route('/buscar_pedido', methods=['GET', 'POST'])
def buscar_pedido():
    """Buscar pedido por ID"""
    if request.method == 'POST':
        id_pedido = request.form['id_pedido']
        
        conn = get_db_connection()
        pedido = conn.execute('''
            SELECT p.*, g.nome as nome_grupo 
            FROM pedidos p 
            LEFT JOIN grupos g ON p.grupo_id = g.id 
            WHERE p.id_pedido = ?
        ''', (id_pedido,)).fetchone()
        conn.close()
        
        return render_template('buscar_pedido.html', pedido=pedido)
    
    return render_template('buscar_pedido.html', pedido=None)

@app.route('/exportar_csv')
def exportar_csv():
    """Exportar dados para CSV"""
    conn = get_db_connection()
    
    # Buscar todos os dados
    grupos = conn.execute('SELECT * FROM grupos ORDER BY id').fetchall()
    pedidos = conn.execute('''
        SELECT p.*, g.nome as nome_grupo 
        FROM pedidos p 
        LEFT JOIN grupos g ON p.grupo_id = g.id 
        ORDER BY p.grupo_id, p.data_criacao
    ''').fetchall()
    
    conn.close()
    
    # Criar arquivo CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Cabeçalho
    writer.writerow(['TIPO', 'ID_PEDIDO', 'CLIENTE', 'PRODUTO', 'TAMANHO', 'FRETE', 'GRUPO', 'ENVIADO', 'DATA'])
    
    # Pedidos em grupos
    for pedido in pedidos:
        if pedido['grupo_id']:
            grupo = next((g for g in grupos if g['id'] == pedido['grupo_id']), None)
            enviado = "SIM" if grupo and grupo['enviado'] else "NÃO"
            writer.writerow([
                'GRUPO',
                pedido['id_pedido'],
                pedido['nome_cliente'],
                pedido['produto'],
                pedido['tamanho'],
                pedido['tipo_frete'],
                pedido['nome_grupo'] or '',
                enviado,
                pedido['data_criacao']
            ])
    
    # Pedidos expresso
    for pedido in pedidos:
        if pedido['tipo_frete'] == 'EXPRESSO':
            writer.writerow([
                'EXPRESSO',
                pedido['id_pedido'],
                pedido['nome_cliente'],
                pedido['produto'],
                pedido['tamanho'],
                pedido['tipo_frete'],
                '',
                'N/A',
                pedido['data_criacao']
            ])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'pedidos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/pedido/<pedido_id>/editar', methods=['GET', 'POST'])
def editar_pedido(pedido_id):
    """Editar pedido existente"""
    conn = get_db_connection()
    
    if request.method == 'POST':
        nome_cliente = request.form['nome_cliente']
        produto = request.form['produto']
        tamanho = request.form['tamanho']
        tipo_frete = request.form['tipo_frete']
        
        conn.execute('''
            UPDATE pedidos 
            SET nome_cliente = ?, produto = ?, tamanho = ?, tipo_frete = ?
            WHERE id_pedido = ?
        ''', (nome_cliente, produto, tamanho, tipo_frete, pedido_id))
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))
    
    pedido = conn.execute('SELECT * FROM pedidos WHERE id_pedido = ?', (pedido_id,)).fetchone()
    conn.close()
    
    if not pedido:
        return "Pedido não encontrado!", 404
    
    return render_template('editar_pedido.html', pedido=pedido)

@app.route('/pedido/<pedido_id>/excluir')
def excluir_pedido(pedido_id):
    """Excluir um pedido"""
    conn = get_db_connection()
    
    # Verificar se o pedido existe
    pedido = conn.execute('SELECT * FROM pedidos WHERE id_pedido = ?', (pedido_id,)).fetchone()
    if not pedido:
        flash('Pedido não encontrado', 'error')
        conn.close()
        return redirect(url_for('index'))
    
    try:
        # Excluir o pedido
        conn.execute('DELETE FROM pedidos WHERE id_pedido = ?', (pedido_id,))
        
        # Também excluir da tabela de pedidos completos se existir
        conn.execute('DELETE FROM pedidos_completos WHERE numero_pedido = ?', (pedido_id,))
        
        conn.commit()
        flash(f'Pedido {pedido_id} excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir pedido: {str(e)}', 'error')
    finally:
        conn.close()
    
    # Verificar se há um parâmetro 'next' para redirecionamento
    next_page = request.args.get('next')
    if next_page and next_page.startswith('/'):
        return redirect(next_page)
    else:
        return redirect(url_for('index'))

@app.route('/grupo/<int:grupo_id>/excluir')
def excluir_grupo(grupo_id):
    """Excluir um grupo e todos os seus pedidos"""
    conn = get_db_connection()
    
    # Verificar se o grupo existe
    grupo = conn.execute('SELECT * FROM grupos WHERE id = ?', (grupo_id,)).fetchone()
    if not grupo:
        flash('Grupo não encontrado', 'error')
        conn.close()
        return redirect(url_for('index'))
    
    try:
        # Primeiro, remover todos os pedidos do grupo (não excluir os pedidos, apenas desassociar)
        conn.execute('UPDATE pedidos SET grupo_id = NULL WHERE grupo_id = ?', (grupo_id,))
        
        # Depois excluir o grupo
        conn.execute('DELETE FROM grupos WHERE id = ?', (grupo_id,))
        
        conn.commit()
        flash(f'Grupo "{grupo["nome"]}" excluído com sucesso! Os pedidos foram mantidos.', 'success')
    except Exception as e:
        flash(f'Erro ao excluir grupo: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('index'))

@app.route('/grupo/<int:grupo_id>/editar_rastreio', methods=['GET', 'POST'])
def editar_rastreio_grupo(grupo_id):
    """Editar código de rastreio de um grupo"""
    conn = get_db_connection()
    
    # Verificar se o grupo existe
    grupo = conn.execute('SELECT * FROM grupos WHERE id = ?', (grupo_id,)).fetchone()
    if not grupo:
        flash('Grupo não encontrado', 'error')
        conn.close()
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        codigo_rastreio = request.form.get('codigo_rastreio', '').strip()
        
        try:
            conn.execute('UPDATE grupos SET codigo_rastreio = ? WHERE id = ?', (codigo_rastreio, grupo_id))
            conn.commit()
            flash(f'Código de rastreio do grupo "{grupo["nome"]}" atualizado com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao atualizar código de rastreio: {str(e)}', 'error')
        finally:
            conn.close()
        
        return redirect(url_for('index'))
    
    conn.close()
    return render_template('editar_rastreio_grupo.html', grupo=grupo)

@app.route('/pedidos_importados/<pedido_id>/excluir')
def excluir_pedido_importado(pedido_id):
    """Excluir um pedido importado (tanto da tabela completa quanto da simplificada)"""
    conn = get_db_connection()
    
    # Verificar se o pedido existe na tabela de pedidos completos
    pedido = conn.execute('SELECT * FROM pedidos_completos WHERE numero_pedido = ?', (pedido_id,)).fetchone()
    if not pedido:
        flash('Pedido não encontrado', 'error')
        conn.close()
        return redirect(url_for('pedidos_importados'))
    
    try:
        # Excluir da tabela de pedidos completos
        conn.execute('DELETE FROM pedidos_completos WHERE numero_pedido = ?', (pedido_id,))
        
        # Excluir da tabela de pedidos simplificados
        conn.execute('DELETE FROM pedidos WHERE id_pedido = ?', (pedido_id,))
        
        conn.commit()
        flash(f'Pedido {pedido_id} excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir pedido: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('pedidos_importados'))

@app.route('/limpar_todos_dados')
def limpar_todos_dados():
    """Limpar todos os dados do banco (pedidos e grupos)"""
    conn = get_db_connection()
    
    try:
        # Limpar todas as tabelas
        conn.execute('DELETE FROM pedidos')
        conn.execute('DELETE FROM grupos')
        conn.execute('DELETE FROM pedidos_completos')
        
        # Resetar os contadores de auto-incremento
        conn.execute('DELETE FROM sqlite_sequence WHERE name IN ("pedidos", "grupos", "pedidos_completos")')
        
        conn.commit()
        flash('Todos os dados foram excluídos com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao limpar dados: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('index'))

@app.route('/pedidos_disponiveis')
def pedidos_disponiveis():
    """Visualizar todos os pedidos disponíveis (sem grupo)"""
    conn = get_db_connection()
    
    # Buscar pedidos sem grupo
    pedidos_sem_grupo = conn.execute('''
        SELECT * FROM pedidos 
        WHERE grupo_id IS NULL
        ORDER BY data_criacao DESC
    ''').fetchall()
    
    # Separar por tipo de frete
    pedidos_padrao = [p for p in pedidos_sem_grupo if p['tipo_frete'] == 'FRETE PADRÃO']
    pedidos_expresso = [p for p in pedidos_sem_grupo if p['tipo_frete'] == 'EXPRESSO']
    
    conn.close()
    
    return render_template('pedidos_disponiveis.html', 
                         pedidos_padrao=pedidos_padrao,
                         pedidos_expresso=pedidos_expresso)

@app.route('/todos_pedidos')
def todos_pedidos():
    """Visualizar todos os pedidos do sistema"""
    conn = get_db_connection()
    
    # Buscar todos os pedidos com informações do grupo
    todos_pedidos = conn.execute('''
        SELECT p.*, g.nome as nome_grupo, g.enviado as grupo_enviado
        FROM pedidos p 
        LEFT JOIN grupos g ON p.grupo_id = g.id
        ORDER BY p.data_criacao DESC
    ''').fetchall()
    
    # Buscar grupos disponíveis para ações em lote
    grupos_disponiveis = conn.execute('''
        SELECT g.*, COUNT(p.id) as total_pedidos
        FROM grupos g
        LEFT JOIN pedidos p ON g.id = p.grupo_id
        GROUP BY g.id
        HAVING COUNT(p.id) < 5
        ORDER BY g.id
    ''').fetchall()
    
    # Separar por tipo de frete
    pedidos_padrao = [p for p in todos_pedidos if p['tipo_frete'] == 'FRETE PADRÃO']
    pedidos_expresso = [p for p in todos_pedidos if p['tipo_frete'] == 'EXPRESSO']
    
    # Estatísticas
    total_pedidos = len(todos_pedidos)
    pedidos_em_grupos = len([p for p in todos_pedidos if p['grupo_id'] is not None])
    pedidos_sem_grupo = total_pedidos - pedidos_em_grupos
    grupos_enviados = len([p for p in todos_pedidos if p['grupo_enviado'] == 1])
    
    conn.close()
    
    return render_template('todos_pedidos.html', 
                         todos_pedidos=todos_pedidos,
                         pedidos_padrao=pedidos_padrao,
                         pedidos_expresso=pedidos_expresso,
                         total_pedidos=total_pedidos,
                         pedidos_em_grupos=pedidos_em_grupos,
                         pedidos_sem_grupo=pedidos_sem_grupo,
                         grupos_enviados=grupos_enviados,
                         grupos_disponiveis=grupos_disponiveis)

@app.route('/acoes_lote', methods=['POST'])
def acoes_lote():
    """Executar ações em lote nos pedidos selecionados"""
    conn = get_db_connection()
    
    if request.method == 'POST':
        acao = request.form.get('acao')
        pedidos_selecionados = request.form.getlist('pedidos_selecionados')
        
        if not pedidos_selecionados:
            flash('Nenhum pedido selecionado!', 'warning')
            conn.close()
            return redirect(url_for('todos_pedidos'))
        
        try:
            if acao == 'excluir':
                # Excluir pedidos selecionados
                for pedido_id in pedidos_selecionados:
                    # Excluir da tabela de pedidos
                    conn.execute('DELETE FROM pedidos WHERE id_pedido = ?', (pedido_id,))
                    # Excluir da tabela de pedidos completos se existir
                    conn.execute('DELETE FROM pedidos_completos WHERE numero_pedido = ?', (pedido_id,))
                
                conn.commit()
                flash(f'{len(pedidos_selecionados)} pedido(s) excluído(s) com sucesso!', 'success')
                
            elif acao == 'remover_grupos':
                # Remover pedidos de seus grupos
                for pedido_id in pedidos_selecionados:
                    conn.execute('UPDATE pedidos SET grupo_id = NULL WHERE id_pedido = ?', (pedido_id,))
                
                conn.commit()
                flash(f'{len(pedidos_selecionados)} pedido(s) removido(s) de seus grupos!', 'success')
                
            elif acao == 'mover_grupo':
                # Mover pedidos para um grupo específico
                grupo_id = request.form.get('grupo_destino')
                if grupo_id:
                    # Verificar se o grupo existe
                    grupo = conn.execute('SELECT * FROM grupos WHERE id = ?', (grupo_id,)).fetchone()
                    if grupo:
                        # Verificar se o grupo tem espaço (máximo 5 pedidos)
                        count = conn.execute('SELECT COUNT(*) FROM pedidos WHERE grupo_id = ?', (grupo_id,)).fetchone()[0]
                        if count + len(pedidos_selecionados) <= 5:
                            for pedido_id in pedidos_selecionados:
                                # Verificar se é pedido padrão
                                pedido = conn.execute('SELECT * FROM pedidos WHERE id_pedido = ?', (pedido_id,)).fetchone()
                                if pedido and pedido['tipo_frete'] == 'FRETE PADRÃO':
                                    conn.execute('UPDATE pedidos SET grupo_id = ? WHERE id_pedido = ?', (grupo_id, pedido_id))
                            
                            conn.commit()
                            flash(f'{len(pedidos_selecionados)} pedido(s) movido(s) para o grupo!', 'success')
                        else:
                            flash('Grupo não tem espaço suficiente! Máximo 5 pedidos por grupo.', 'error')
                    else:
                        flash('Grupo não encontrado!', 'error')
                else:
                    flash('Grupo de destino não especificado!', 'error')
            
        except Exception as e:
            flash(f'Erro ao executar ação: {str(e)}', 'error')
        finally:
            conn.close()
    
    return redirect(url_for('todos_pedidos'))

if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0', port=5000)
