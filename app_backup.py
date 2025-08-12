from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Configuração do banco de dados
DATABASE = 'pedidos.db'

def init_db():
    """Inicializa o banco de dados"""
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
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de grupos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grupos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            enviado BOOLEAN DEFAULT 0,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Cria uma conexão com o banco de dados"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Página inicial"""
    try:
        conn = get_db_connection()
        
        # Estatísticas
        total_pedidos = conn.execute('SELECT COUNT(*) FROM pedidos').fetchone()[0]
        pedidos_em_grupos = conn.execute('SELECT COUNT(*) FROM pedidos WHERE grupo_id IS NOT NULL').fetchone()[0]
        total_grupos = conn.execute('SELECT COUNT(*) FROM grupos').fetchone()[0]
        grupos_enviados = conn.execute('SELECT COUNT(*) FROM grupos WHERE enviado = 1').fetchone()[0]
        
        # Grupos
        grupos = conn.execute('''
            SELECT g.*, COUNT(p.id) as total_pedidos
            FROM grupos g
            LEFT JOIN pedidos p ON g.id = p.grupo_id
            GROUP BY g.id
            ORDER BY g.id
        ''').fetchall()
        
        # Pedidos expresso
        pedidos_expresso = conn.execute('''
            SELECT * FROM pedidos 
            WHERE tipo_frete = 'EXPRESSO' 
            ORDER BY data_criacao DESC
        ''').fetchall()
        
        conn.close()
        
        return render_template('index.html', 
                             total_pedidos=total_pedidos,
                             pedidos_em_grupos=pedidos_em_grupos,
                             total_grupos=total_grupos,
                             grupos_enviados=grupos_enviados,
                             grupos=grupos,
                             pedidos_expresso=pedidos_expresso)
    except Exception as e:
        return f"Erro: {str(e)}", 500

@app.route('/novo_pedido', methods=['GET', 'POST'])
def novo_pedido():
    """Adicionar novo pedido"""
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
            flash('Pedido adicionado com sucesso!', 'success')
        except sqlite3.IntegrityError:
            flash('ID do pedido já existe!', 'error')
        finally:
            conn.close()
        
        return redirect(url_for('index'))
    
    return render_template('novo_pedido.html')

@app.route('/novo_grupo', methods=['GET', 'POST'])
def novo_grupo():
    """Criar novo grupo"""
    if request.method == 'POST':
        nome = request.form['nome']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO grupos (nome) VALUES (?)', (nome,))
        conn.commit()
        conn.close()
        
        flash('Grupo criado com sucesso!', 'success')
        return redirect(url_for('index'))
    
    return render_template('novo_grupo.html')

@app.route('/adicionar_pedido_grupo/<int:grupo_id>', methods=['GET', 'POST'])
def adicionar_pedido_grupo(grupo_id):
    """Adicionar pedido a um grupo"""
    conn = get_db_connection()
    grupo = conn.execute('SELECT * FROM grupos WHERE id = ?', (grupo_id,)).fetchone()
    
    if request.method == 'POST':
        pedido_id = request.form['pedido_id']
        
        # Verificar se o grupo tem espaço
        count = conn.execute('SELECT COUNT(*) FROM pedidos WHERE grupo_id = ?', (grupo_id,)).fetchone()[0]
        if count >= 5:
            flash('Grupo já está cheio! Máximo 5 pedidos.', 'error')
        else:
            # Verificar se é pedido padrão
            pedido = conn.execute('SELECT * FROM pedidos WHERE id_pedido = ?', (pedido_id,)).fetchone()
            if pedido and pedido['tipo_frete'] == 'FRETE PADRÃO':
                conn.execute('UPDATE pedidos SET grupo_id = ? WHERE id_pedido = ?', (grupo_id, pedido_id))
                conn.commit()
                flash('Pedido adicionado ao grupo!', 'success')
            else:
                flash('Apenas pedidos com FRETE PADRÃO podem ser adicionados a grupos!', 'error')
        
        conn.close()
        return redirect(url_for('index'))
    
    # Pedidos disponíveis
    pedidos_disponiveis = conn.execute('''
        SELECT * FROM pedidos 
        WHERE grupo_id IS NULL AND tipo_frete = 'FRETE PADRÃO'
        ORDER BY data_criacao
    ''').fetchall()
    
    conn.close()
    
    return render_template('adicionar_pedido_grupo.html', 
                         grupo=grupo, 
                         pedidos_disponiveis=pedidos_disponiveis)

@app.route('/marcar_enviado/<int:grupo_id>', methods=['POST'])
def marcar_enviado(grupo_id):
    """Marcar grupo como enviado"""
    conn = get_db_connection()
    conn.execute('UPDATE grupos SET enviado = 1 WHERE id = ?', (grupo_id,))
    conn.commit()
    conn.close()
    
    flash('Grupo marcado como enviado!', 'success')
    return redirect(url_for('index'))

@app.route('/buscar_pedido', methods=['GET', 'POST'])
def buscar_pedido():
    """Buscar pedido por ID"""
    if request.method == 'POST':
        id_pedido = request.form['id_pedido']
        
        conn = get_db_connection()
        pedido = conn.execute('''
            SELECT p.*, g.nome as nome_grupo, g.enviado as grupo_enviado
            FROM pedidos p
            LEFT JOIN grupos g ON p.grupo_id = g.id
            WHERE p.id_pedido = ?
        ''', (id_pedido,)).fetchone()
        conn.close()
        
        if pedido:
            return render_template('buscar_pedido.html', pedido=pedido, encontrado=True)
        else:
            flash('Pedido não encontrado!', 'error')
    
    return render_template('buscar_pedido.html', encontrado=False)

@app.route('/editar_pedido/<id_pedido>', methods=['GET', 'POST'])
def editar_pedido(id_pedido):
    """Editar pedido"""
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
        ''', (nome_cliente, produto, tamanho, tipo_frete, id_pedido))
        conn.commit()
        
        flash('Pedido atualizado com sucesso!', 'success')
        conn.close()
        return redirect(url_for('index'))
    
    pedido = conn.execute('SELECT * FROM pedidos WHERE id_pedido = ?', (id_pedido,)).fetchone()
    conn.close()
    
    if not pedido:
        flash('Pedido não encontrado!', 'error')
        return redirect(url_for('index'))
    
    return render_template('editar_pedido.html', pedido=pedido)

@app.route('/excluir_pedido/<id_pedido>', methods=['POST'])
def excluir_pedido(id_pedido):
    """Excluir pedido"""
    conn = get_db_connection()
    conn.execute('DELETE FROM pedidos WHERE id_pedido = ?', (id_pedido,))
    conn.commit()
    conn.close()
    
    flash('Pedido excluído com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/exportar_csv')
def exportar_csv():
    """Exportar todos os pedidos para CSV"""
    conn = get_db_connection()
    pedidos = conn.execute('''
        SELECT p.*, g.nome as nome_grupo, g.enviado as grupo_enviado
        FROM pedidos p
        LEFT JOIN grupos g ON p.grupo_id = g.id
        ORDER BY p.data_criacao
    ''').fetchall()
    conn.close()
    
    # Criar CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID Pedido', 'Cliente', 'Produto', 'Tamanho', 'Tipo Frete', 'Grupo', 'Enviado', 'Data Criação'])
    
    for pedido in pedidos:
        writer.writerow([
            pedido['id_pedido'],
            pedido['nome_cliente'],
            pedido['produto'],
            pedido['tamanho'],
            pedido['tipo_frete'],
            pedido['nome_grupo'] or 'Sem grupo',
            'Sim' if pedido['grupo_enviado'] else 'Não',
            pedido['data_criacao']
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'pedidos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/health')
def health_check():
    """Verificação de saúde da aplicação"""
    return "OK", 200

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
