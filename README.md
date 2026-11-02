# 🎸 Empório da Música - Assistente Virtual CLI (IA)



Assistente virtual inteligente desenvolvido em Python utilizando a API do Google Gemini (`google-generativeai`), projetado para operar como um atendente virtual especializado da **Empório da Música** (Campo Grande/MS, fundada em 2008).



---



## 🚀 Tecnologias Utilizadas

* **Python 3.10+**

* **Google GenAI SDK** (`google-generativeai`) para processamento de linguagem natural e chat contextual.

* **Pandas** para manipulação e consulta estruturada de bases de dados (CSV).

* **PyPDF** para extração de texto do manual de políticas da loja.

* **Dotenv** para gerenciamento seguro de variáveis de ambiente.



---



## 📁 Estrutura do Projeto



emporio_musica_agent/

│

├── data/                         # Bases de dados (CSV e PDF de políticas)

│   ├── products.csv

│   ├── promotions.csv

│   ├── customers.csv

│   ├── orders.csv

│   ├── order_items.csv

│   └── políticas_da_loja.pdf

│

├── examples/                     # Cenários de testes e interações simuladas

│   └── interacoes.md

│

├── src/                          # Código fonte principal

│   ├── agent.py                  # Lógica do LLM, System Instruction e injeção de contexto

│   ├── tools.py                  # Funções de leitura de CSV/PDF e cruzamento de dados

│   └── main.py                   # Interface de linha de comando (CLI) interativa

│

├── .env                          # Chave de API (excluída do versionamento)

├── .gitignore                    # Arquivos ignorados pelo Git

├── requirements.txt              # Dependências do projeto

└── README.md                     # Documentação oficial do projeto



---



## 🛠️ Como Executar o Projeto Localmente



1. Clone o repositório e acesse a pasta:

   git clone https://github.com/AylanLeonardi/emporio-musica-agent

   cd emporio-musica-agent



2. Crie e ative um ambiente virtual (venv):

   python -m venv venv

   # No Windows:

   venv\Scripts\activate

   # No Linux/macOS:

   source venv/bin/activate



3. Instale as dependências:

   pip install -r requirements.txt



4. Configure sua Chave da API:

   Crie um arquivo chamado .env na raiz do projeto e adicione sua chave do Google Gemini:

   GEMINI_API_KEY=sua_chave_aqui



5. Execute a Assistente no Terminal:

   python src/main.py



---



## 💡 Decisões Arquiteturais e Segurança

* Escopo Restrito: A diretriz de sistema (`System Instruction`) restringe estritamente o agente à comercialização de instrumentos musicais, bloqueando acessórios e redirecionando o cliente educadamente.

* Injeção Dinâmica de Contexto: O agente analisa as palavras-chave da mensagem do usuário e busca nas bases locais (CSV/PDF) apenas o contexto relevante (produtos, promoções ativas, políticas de troca ou dados de pedidos), otimizando o uso de tokens e preservando a precisão das respostas.

* Privacidade e Segurança: Dados confidenciais como chaves de API são isolados via `.env` (ignorados pelo `.gitignore`), e consultas a pedidos exigem validação por e-mail ou nome do cliente.