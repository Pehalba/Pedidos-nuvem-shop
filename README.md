# 🏈 Gerenciador de Pedidos de Camisas de Futebol

Sistema simples e eficiente para gerenciar pedidos de camisas de futebol, com foco na separação de lotes e organização interna.

## 🎯 Objetivo

Organizar pedidos de dois tipos de frete:

- **FRETE PADRÃO** → Camisas chegam primeiro para você, depois envia ao cliente
- **EXPRESSO** → Envio direto para o cliente (não entra na separação por grupos)

## ✨ Funcionalidades

### 📝 Cadastro de Pedidos

- ID único do pedido
- Nome do cliente
- Produto (ex.: Brasil 2024, Real Madrid)
- Tamanho (PP, P, M, G, GG, XG, XXG)
- Tipo de frete (FRETE PADRÃO ou EXPRESSO)

### 📦 Gestão de Grupos

- Criação de grupos numerados (Grupo 1, Grupo 2, etc.)
- Máximo de 5 pedidos por grupo
- Grupos podem ter pedidos diferentes (ex.: Brasil M + Real Madrid G)
- Marcação de grupos como "enviado"

### 🔍 Visualização Organizada

- Dashboard com estatísticas em tempo real
- Lista de grupos com pedidos detalhados
- Lista separada de pedidos EXPRESSO
- Busca rápida por ID do pedido
- Status visual (pendente/enviado)

### 📊 Importação e Exportação

- **Importação de CSV** com todos os dados completos dos pedidos
- **Exportação para CSV** com todos os dados
- **Backup completo** dos pedidos e grupos
- **Visualização detalhada** de pedidos importados

### ✏️ Edição e Remoção

- Editar dados de pedidos existentes
- Remover pedidos de grupos
- Excluir pedidos expresso

## 🚀 Instalação e Uso

### Pré-requisitos

- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)

### Passos para Instalação

1. **Clone ou baixe o projeto**

   ```bash
   # Se estiver usando git
   git clone [URL_DO_REPOSITORIO]
   cd gerenciador-pedidos-camisas
   ```

2. **Instale as dependências**

   ```bash
   pip install -r requirements.txt
   ```

3. **Execute a aplicação**

   ```bash
   python app.py
   ```

4. **Acesse no navegador**
   ```
   http://localhost:5000
   ```

## 📱 Como Usar

### 1. Primeiro Acesso

- A aplicação criará automaticamente o banco de dados SQLite
- Comece cadastrando seus primeiros pedidos

### 2. Fluxo de Trabalho

1. **Cadastre pedidos** → Use "Novo Pedido" para adicionar pedidos
2. **Crie grupos** → Use "Novo Grupo" para organizar pedidos padrão
3. **Adicione pedidos aos grupos** → Clique em "Adicionar Pedido" nos grupos
4. **Monitore o progresso** → Dashboard mostra estatísticas em tempo real
5. **Marque como enviado** → Quando enviar um grupo, marque como "Enviado"

### 3. Pedidos Expresso

- Pedidos com frete EXPRESSO aparecem separadamente
- Não entram em grupos (envio direto)
- Podem ser editados ou excluídos

### 4. Importação de CSV

- Use "Importar CSV" para carregar pedidos em massa
- O sistema lê todos os dados completos dos pedidos
- Pedidos são automaticamente organizados por tipo de frete
- Visualize detalhes completos de cada pedido importado

### 5. Busca e Exportação

- Use "Buscar" para encontrar pedidos por ID
- Use "Exportar CSV" para backup ou impressão

## 🗄️ Estrutura do Banco de Dados

### Tabela: `pedidos`

- `id` - ID interno (auto-incremento)
- `id_pedido` - ID único do pedido (ex: PED001)
- `nome_cliente` - Nome do cliente
- `produto` - Produto (ex: Brasil 2024)
- `tamanho` - Tamanho da camisa
- `tipo_frete` - FRETE PADRÃO ou EXPRESSO
- `grupo_id` - Referência ao grupo (NULL para expresso)
- `data_criacao` - Data/hora de criação

### Tabela: `grupos`

- `id` - ID interno (auto-incremento)
- `nome` - Nome do grupo (ex: Grupo 1)
- `enviado` - Status de envio (0/1)
- `data_criacao` - Data/hora de criação

## 🎨 Interface

- **Design responsivo** - Funciona em desktop, tablet e mobile
- **Interface intuitiva** - Navegação clara e botões bem posicionados
- **Cores diferenciadas** - Pedidos expresso em amarelo, grupos em azul
- **Ícones informativos** - Facilita a identificação rápida

## 🔧 Tecnologias Utilizadas

- **Backend**: Python + Flask
- **Banco de Dados**: SQLite
- **Frontend**: HTML5 + CSS3 + Bootstrap 5
- **Ícones**: Font Awesome
- **Processamento de Dados**: Pandas
- **Importação/Exportação**: CSV nativo

## 📁 Estrutura do Projeto

```
gerenciador-pedidos-camisas/
├── app.py                 # Aplicação principal Flask
├── requirements.txt       # Dependências Python
├── README.md             # Este arquivo
├── exemplo_pedidos.csv   # Arquivo CSV de exemplo
├── templates/            # Templates HTML
│   ├── base.html         # Template base
│   ├── index.html        # Dashboard principal
│   ├── novo_pedido.html  # Formulário novo pedido
│   ├── novo_grupo.html   # Formulário novo grupo
│   ├── editar_pedido.html # Formulário editar pedido
│   ├── buscar_pedido.html # Página de busca
│   ├── adicionar_pedido_grupo.html # Adicionar pedido ao grupo
│   ├── importar_csv.html # Importação de CSV
│   ├── pedidos_importados.html # Lista de pedidos importados
│   └── detalhes_pedido.html # Detalhes de pedido importado
└── pedidos.db           # Banco de dados SQLite (criado automaticamente)
```

## 🆘 Suporte

### Problemas Comuns

1. **Erro de porta em uso**

   - A aplicação usa a porta 5000 por padrão
   - Se estiver ocupada, altere a linha `app.run(port=5000)` em `app.py`

2. **Erro de dependências**

   - Execute: `pip install -r requirements.txt`
   - Verifique se o Python está instalado corretamente

3. **Banco de dados corrompido**
   - Delete o arquivo `pedidos.db`
   - Reinicie a aplicação (será recriado automaticamente)

### Backup

- O arquivo `pedidos.db` contém todos os dados
- Faça backup regular deste arquivo
- Use a função "Exportar CSV" para backup em formato texto

## 📈 Próximas Funcionalidades

- [ ] Histórico de alterações
- [ ] Relatórios detalhados
- [ ] Notificações de pedidos pendentes
- [ ] Integração com APIs de frete
- [ ] Sistema de usuários e permissões

---

**Desenvolvido com ❤️ para facilitar a gestão de pedidos de camisas de futebol**
