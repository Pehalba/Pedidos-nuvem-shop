# 🚀 Instruções Rápidas - Gerenciador de Pedidos

## ⚡ Início Rápido

### 1. Instalar e Executar

```bash
pip install -r requirements.txt
python app.py
```

### 2. Acessar

Abra o navegador e vá para: `http://localhost:5000`

### 3. Criar Dados de Exemplo (Opcional)

```bash
python exemplo_uso.py
```

## 📋 Fluxo de Trabalho

### Passo 1: Cadastrar Pedidos

1. Clique em "Novo Pedido" no menu
2. Preencha todos os campos obrigatórios
3. Escolha o tipo de frete:
   - **FRETE PADRÃO** → Para organizar em grupos
   - **EXPRESSO** → Envio direto (não entra em grupos)

### Passo 2: Criar Grupos (apenas para FRETE PADRÃO)

1. Clique em "Novo Grupo" no menu
2. Digite um nome (ex: "Grupo 1")
3. Clique em "Criar Grupo"

### Passo 3: Organizar Pedidos em Grupos

1. No dashboard, clique em "Adicionar Pedido" no grupo desejado
2. Selecione um pedido da lista (apenas FRETE PADRÃO aparecem)
3. Clique em "Adicionar ao Grupo"

### Passo 4: Gerenciar Envios

1. Quando um grupo for enviado, clique em "Marcar Enviado"
2. Grupos enviados ficam com visual diferente (mais claro)
3. Use "Marcar Pendente" para desfazer se necessário

## 🎯 Funcionalidades Principais

### Dashboard

- **Estatísticas** em tempo real
- **Grupos** organizados por cards
- **Pedidos Expresso** separados
- **Status visual** (pendente/enviado)

### Busca

- Use "Buscar" no menu
- Digite o ID do pedido
- Veja a qual grupo pertence

### Exportação

- Clique em "Exportar CSV" no menu
- Arquivo baixado com todos os dados
- Útil para backup e impressão

## 🔧 Dicas Importantes

### Limites

- Máximo **5 pedidos por grupo**
- Apenas **FRETE PADRÃO** vai para grupos
- **EXPRESSO** fica separado

### Organização

- Use nomes claros para grupos (ex: "Grupo 1", "Grupo 2")
- Mantenha IDs únicos para pedidos
- Marque grupos como enviado quando despachar

### Backup

- O arquivo `pedidos.db` contém todos os dados
- Use "Exportar CSV" regularmente
- Faça backup do arquivo `.db`

## 🆘 Problemas Comuns

### Aplicação não inicia

```bash
# Verificar se Flask está instalado
pip install Flask

# Verificar se a porta 5000 está livre
# Se não estiver, altere a porta em app.py
```

### Erro de banco de dados

```bash
# Deletar e recriar
rm pedidos.db
python app.py
```

### Dados não aparecem

- Verifique se criou pedidos primeiro
- Use o script de exemplo: `python exemplo_uso.py`

## 📱 Interface Mobile

- Sistema **totalmente responsivo**
- Funciona em **celular, tablet e desktop**
- **Navegação otimizada** para touch

## 🎨 Cores e Status

- **Azul**: Grupos e pedidos padrão
- **Amarelo**: Pedidos expresso
- **Verde**: Enviado
- **Laranja**: Pendente

---

**💡 Dica**: Comece criando alguns pedidos de teste para familiarizar-se com o sistema!
