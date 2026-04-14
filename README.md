Markdown
# 🤖 Robô de Automação: Microsoft Partner Incentives

Este projeto é um script em Python desenvolvido para automatizar a verificação de licenças e incentivos de clientes dentro do portal **Microsoft Partner Center**. 

O robô lê uma base de clientes a partir de uma planilha Excel, navega no portal para verificar a elegibilidade de cada cliente e, por fim, envia automaticamente um e-mail com os resultados para o responsável.

## 🚀 Funcionalidades

- **Leitura de Dados:** Importa a lista de domínios e e-mails de responsáveis a partir de um arquivo Excel (`.xlsx`).
- **Navegação Web Automatizada:** Utiliza o Selenium para aceder ao Microsoft Partner Center, preencher formulários de pesquisa e extrair dados da interface.
- **Validação de Status:** Identifica se o cliente está "Qualificado" ou "Não Qualificado" e lista as licenças disponíveis.
- **Envio de Notificações:** Envia e-mails formatados em HTML, com alertas visuais consoante o status do cliente, utilizando o protocolo SMTP.
- **Geração de Relatório:** Guarda os resultados (Status e Licenças Disponíveis) numa nova planilha Excel.

## 🛠️ Tecnologias Utilizadas

- **Python 3**
- **Selenium** (Automação Web)
- **Pandas** (Manipulação de dados em Excel)
- **WebDriver Manager** (Gestão automática do ChromeDriver)
- **SMTP & Email.mime** (Envio de e-mails)

## 📋 Pré-requisitos e Configuração

1. **Instalar Dependências:**
   Certifique-se de ter o Python instalado. Depois, instale as bibliotecas necessárias executando:
   ```bash
   pip install pandas selenium webdriver-manager openpyxl
Preparar a Planilha de Entrada:
O script espera um arquivo Excel (minha_base_clientes.xlsx) com as seguintes colunas (no mínimo):

Dominio: O domínio do cliente a ser pesquisado.

Email_Responsavel: O e-mail da pessoa que receberá a notificação.

Configuração de Variáveis (Segurança):
No arquivo automacao_partner.py, atualize as variáveis de caminho dos arquivos Excel.

⚠️ MUITO IMPORTANTE: Nunca coloque a sua senha de e-mail real diretamente no código, especialmente se o repositório for público. Recomenda-se o uso de variáveis de ambiente (.env) para gerir credenciais (ex: EMAIL_SENHA).

⚙️ Como Executar
Após configurar a planilha e as credenciais, basta correr o script no terminal:

Bash
python automacao_partner.py
Nota: O robô fará uma pausa no início para que o utilizador possa realizar o login manualmente (devido a autenticações MFA/2FA da Microsoft). Depois de logado na tela inicial, basta premir ENTER no terminal para que a automação prossiga.
