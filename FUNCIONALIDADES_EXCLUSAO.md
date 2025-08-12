# 🗑️ Funcionalidades de Exclusão - Gerenciador de Pedidos

## 📋 Opções de Exclusão Disponíveis

### 1. **Excluir Pedido Individual**

- **Localização**: Dashboard principal (pedidos expresso), página "Todos os Pedidos" ou "Pedidos Disponíveis"
- **Ação**: Remove um pedido específico
- **Confirmação**: Sim, com diálogo de confirmação
- **Efeito**: Pedido é removido tanto da tabela simplificada quanto da completa

### 2. **Excluir Pedido de Grupo**

- **Localização**: Dentro de cada grupo no dashboard ou página "Adicionar Pedido ao Grupo"
- **Ação**: Remove pedido do grupo (não exclui o pedido)
- **Confirmação**: Sim, com diálogo de confirmação
- **Efeito**: Pedido volta para a lista de pedidos disponíveis

### 3. **Excluir Grupo Inteiro**

- **Localização**: Dentro de cada grupo no dashboard
- **Ação**: Remove o grupo e desassocia todos os pedidos
- **Confirmação**: Sim, com diálogo de confirmação
- **Efeito**: Grupo é excluído, pedidos são mantidos (voltam para disponíveis)

### 4. **Excluir Pedido Importado**

- **Localização**: Página "Pedidos Importados"
- **Ação**: Remove pedido das tabelas completa e simplificada
- **Confirmação**: Sim, com diálogo de confirmação
- **Efeito**: Pedido é completamente removido do sistema

### 5. **Limpar Todos os Dados**

- **Localização**: Dashboard principal (botão "Limpar Tudo")
- **Ação**: Remove TODOS os pedidos e grupos
- **Confirmação**: Sim, com aviso de atenção
- **Efeito**: Banco de dados é completamente limpo

### 6. **Ações em Lote (NOVO!)**

- **Localização**: Página "Todos os Pedidos" (seção "Ações em Lote")
- **Ações Disponíveis**:
  - 🗑️ **Excluir Pedidos**: Remove múltiplos pedidos de uma vez
  - ❌ **Remover de Grupos**: Remove pedidos de seus grupos (mantém os pedidos)
  - 📦 **Mover para Grupo**: Move pedidos para um grupo específico
- **Confirmação**: Sim, com diálogo de confirmação
- **Efeito**: Ação aplicada a todos os pedidos selecionados

## 🎯 Como Usar

### **Excluir Pedido Individual:**

1. Vá para o Dashboard, "Todos os Pedidos" ou "Pedidos Disponíveis"
2. Na seção "Pedidos Expresso" ou lista de pedidos
3. Clique no ícone 🗑️ (lixeira) ao lado do pedido
4. Confirme a exclusão

### **Excluir Pedido de Grupo:**

1. Vá para o Dashboard ou página "Adicionar Pedido ao Grupo"
2. No grupo desejado ou lista de pedidos disponíveis
3. Clique no ícone ❌ (X) ou 🗑️ (lixeira) ao lado do pedido
4. Confirme a remoção/exclusão

### **Excluir Grupo:**

1. Vá para o Dashboard
2. No grupo desejado
3. Clique no botão "Excluir" (vermelho)
4. Confirme a exclusão

### **Excluir Pedido Importado:**

1. Vá para "Pedidos Importados"
2. Clique no ícone 🗑️ (lixeira) na linha do pedido
3. Confirme a exclusão

### **Limpar Todos os Dados:**

1. Vá para o Dashboard
2. Clique no botão "Limpar Tudo" (vermelho)
3. Confirme com atenção (ação irreversível)

### **Ações em Lote (NOVO!):**

1. Vá para "Todos os Pedidos"
2. Selecione os pedidos desejados usando os checkboxes
3. Escolha a ação desejada no dropdown "Ação"
4. Se escolher "Mover para Grupo", selecione o grupo de destino
5. Clique em "Executar Ação"
6. Confirme a ação

**Dicas para Seleção:**

- Use o checkbox no cabeçalho para selecionar todos os pedidos visíveis
- Use o botão "Selecionar Todos" para alternar seleção
- Os filtros funcionam com a seleção (apenas pedidos visíveis são afetados)

## ⚠️ Importante

- **Todas as exclusões** têm confirmação para evitar acidentes
- **Pedidos removidos de grupos** voltam para a lista de disponíveis
- **Limpar Todos os Dados** é irreversível
- **Faça backup** antes de usar "Limpar Tudo"

## 🔄 Recuperação de Dados

- **Pedidos removidos de grupos**: Podem ser readicionados
- **Pedidos excluídos**: Não podem ser recuperados
- **Grupos excluídos**: Não podem ser recuperados
- **Limpeza total**: Não pode ser desfeita

## 💡 Dicas

- Use "Remover do Grupo" em vez de "Excluir" se quiser manter o pedido
- Use "Limpar Tudo" apenas quando realmente necessário
- Faça exportação CSV antes de limpezas grandes
- Teste as funcionalidades com dados de exemplo primeiro
- **Ações em Lote**: Ideal para gerenciar muitos pedidos de uma vez
- **Seleção Inteligente**: Os filtros funcionam com a seleção múltipla
- **Confirmação**: Sempre confirme antes de executar ações em lote
