# High Control Point (HCP) 🚀
> *Sistema Inteligente de Gestão de Ponto Eletrônico e Auditoria de Recursos Humanos*

---

## 📌 Sobre o Projeto
O *High Control Point* é uma aplicação desktop de alta performance desenvolvida como projeto interdisciplinar de conclusão de ciclo acadêmico. O sistema visa automatizar, auditar e otimizar o controle de ponto eletrônico, banco de horas e justificativas de ausência para colaboradores e administradores de RH.

A aplicação mitiga falhas humanas de digitação, unifica o ecossistema de banco de dados e gera relatórios gerenciais consolidados em tempo real, respeitando as parametrizações legais de fuso horário brasileiro (America/Sao_Paulo).

---

## 🏗️ Arquitetura e Stack Tecnológica

O projeto adota uma arquitetura descentralizada cliente-servidor dividida em três camadas principais, garantindo isolamento de escopo e facilidade de manutenção:

* *Frontend (Desktop App):* [Electron.js](https://www.electronjs.org/) (Chromium Engine) integrado com HTML5, CSS3 estruturado e JavaScript Assíncrono nativo (Vanilla JS / Fetch API).
* *Backend (API RESTful):* [Flask](https://flask.palletsprojects.com/) (Python) para gerenciamento de regras de negócio, criptografia, manipulação de fuso horário (pytz) e renderização de relatórios.
* *Banco de Dados:* [PostgreSQL](https://www.postgresql.org/), garantindo persistência relacional robusta, integridade referencial e sanitização de dados em nível de query.

---

## ⚡ Principais Funcionalidades

* 🔐 *Autenticação Segura:* Login administrativo e de colaboradores com verificação de hash criptográfico via Bcrypt.
* ⏱️ *Ponto Inteligente:* Registro assíncrono de entradas e saídas integrado ao fuso horário oficial de Brasília.
* 📊 *Dashboard Administrativo:* Painel dinâmico em tempo real com métricas de presenças, alertas de atrasos acumulados e solicitações pendentes.
* 📄 *Geração de Relatórios:* Exportação automatizada de espelhos de ponto e auditorias de horas em formato *PDF* via backend.
* 🔍 *Sanitização Automatizada:* Algoritmo SQL customizado para higienização e validação de documentos (ex: CPF) independente da formatação de entrada do usuário.

---

## ⚙️ Pré-requisitos para Execução

Antes de iniciar, certifique-se de ter instalado em sua máquina:
* [Node.js](https://nodejs.org/) (versão 16 ou superior)
* [Python](https://www.python.org/) (versão 3.10 ou superior)
* [PostgreSQL](https://www.postgresql.org/) ativo e configurado

---

## 🚀 Como Executar o Projeto

Para rodar a aplicação localmente, siga o fluxo de inicialização segregada das camadas:

### 1. Clonar o Repositório
```bash
git clone [https://github.com/Lanaduti/gestao-de-ponto.git](https://github.com/Lanaduti/gestao-de-ponto.git)
cd gestao-de-ponto

2. Configurar e Iniciar o Backend (Flask)
Certifique-se de que o serviço do seu PostgreSQL está ativo no Windows (⁠services.msc⁠) antes de rodar o comando.

# Instalar as dependências do Python
pip install -r requirements.txt

# Iniciar o servidor de API
python server.py

O servidor estará ativo em: ⁠http://127.0.0.1:5000⁠

3. Configurar e Iniciar o Frontend (Electron)
Abra uma nova aba ou janela de terminal para não derrubar o backend:

🛠️ Solução de Problemas Comuns (Troubleshooting)

 Erro de Conexão com o Servidor: Certifique-se de que o comando ⁠python server.py⁠ foi executado em um terminal dedicado e continua rodando em segundo plano.
 Verifique também se o serviço do PostgreSQL está "Executando" no painel de serviços do Windows.

 Bloqueios de CORS/Segurança: O arquivo ⁠main.js⁠ do Electron está parametrizado com ⁠webSecurity: false⁠ para permitir chamadas HTTP na API local.
 Não altere essa flag em ambiente de desenvolvimento.

 Concorrência do Git (index.lock): Caso o Git trave ao commitar localmente, execute o comando de expurgo da trava no PowerShell: ⁠Remove-Item .git\index.lock -Force⁠.

👥 Autores e Desenvolvimento

O desenvolvimento deste projeto foi realizado colaborativamente pela equipe:

 Lanaduti 
 Vitruviano999
 JayaneEllen

 Contexto: Projeto Técnico Acadêmico de Engenharia de Software / Desenvolvimento de Sistemas.
