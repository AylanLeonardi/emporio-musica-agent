# 🎸 Empório da Música - Assistente Virtual (CLI)

Agente de atendimento em Python para a **Empório da Música** (loja fictícia de instrumentos musicais em Campo Grande/MS), construído com a API do Google Gemini e **function calling**. Responde dúvidas sobre produtos, preços, promoções, pedidos e políticas da loja, mantendo a persona informal e acolhedora da marca.

---

## 🚀 Como executar

Pré-requisitos: Python 3.10+ e uma chave de API do Google Gemini (https://aistudio.google.com/apikey).

```bash
git clone https://github.com/AylanLeonardi/emporio-musica-agent
cd emporio-musica-agent

python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz do projeto:

```
GEMINI_API_KEY=sua_chave_aqui
# opcional: troca o modelo (padrão: gemini-3.5-flash)
# GEMINI_MODEL=gemini-2.5-flash
```

Execute:

```bash
python src/main.py
```

Digite `sair` para encerrar.

---

## 📁 Estrutura do projeto

```
emporio_musica_agent/
├── data/                  # CSVs da operação e PDF do manual de políticas
├── exemplos/              # Conversas de exemplo com o agente
│   └── interacoes.md
├── src/
│   ├── agent.py           # Persona, system prompt, chat com function calling
│   ├── tools.py           # Ferramentas (catálogo, promoções, pedidos, data/hora) e leitura do PDF
│   └── main.py            # Interface CLI
├── requirements.txt
└── README.md
```

---

## 🧠 Decisões técnicas e justificativas

### Abordagem: function calling (+ políticas no prompt)
O modelo decide sozinho **quando** consultar dados, chamando ferramentas Python. Escolhi function calling em vez de RAG ou agente de SQL porque:

- **Dados estruturados e pequenos** (65 produtos, 50 clientes, 20 pedidos): filtros em pandas são mais precisos que busca vetorial, e dão resultado exato para perguntas como "violões até R$ 1000".
- **Controle sobre o que o modelo vê:** cada ferramenta devolve só os campos necessários, com preços finais já calculados em código (promoção, PIX, parcelamento), em vez de deixar o LLM fazer contas.
- **Mais simples e auditável que SQL gerado por LLM**, que traria risco de consultas erradas ou acesso indevido a dados de outros clientes.

| Ferramenta | Uso |
|---|---|
| `buscar_produtos` | Catálogo com filtros por termo, categoria e faixa de preço; devolve estoque, promoção ativa, preço final, preço no PIX e parcelamento máximo |
| `listar_promocoes` | Promoções ativas no momento |
| `consultar_pedidos` | Status, itens e rastreio de pedidos, identificando o cliente pelo e-mail |
| `data_hora_atual` | Data/hora em Campo Grande e se a loja está aberta; usada para horário e prazos de troca/devolução |

### Políticas inteiras no system prompt
O manual tem cerca de 13 mil caracteres, o que cabe com folga no contexto. Colocá-lo completo no prompt elimina o risco de uma etapa de busca trazer o trecho errado (ou truncar seções, como acontecia na primeira versão) e deixa as respostas consistentes. O texto é lido do PDF uma vez e guardado em cache.

### Modelo e provedor
**Gemini (`gemini-3.5-flash`) via API do Google**, pelo SDK oficial `google-genai`. Motivos: suporte nativo a function calling, camada gratuita para prototipagem e bom desempenho em português. O modelo é configurável por `GEMINI_MODEL`. A temperatura é 0.3 para respostas mais estáveis.

### Estratégia de prompt
- **Persona** definida a partir das diretrizes do próprio manual (informal, mas profissional, sem tom robótico, respostas curtas estilo WhatsApp).
- **Regras de ouro:** só informar preço, estoque e status vindos das ferramentas; regras só do manual; se não souber, dizer que não sabe e indicar o contato da loja.
- **Escopo:** recusa educada de acessórios e de assuntos fora do contexto da loja, e proteção contra pedidos para revelar as instruções.
- **Limites de ação:** o agente não pode abrir devoluções, trocas ou reclamações; ele explica a regra e encaminha o cliente à equipe pelo WhatsApp, em vez de prometer algo que não consegue fazer.
- **Data atual no prompt:** a data/hora é injetada no system prompt no início da sessão e também está disponível pela ferramenta `data_hora_atual`, para que o modelo não chute a data ao calcular prazos.

### Privacidade
Pedidos só são consultados com o **e-mail cadastrado**, validado **dentro da ferramenta** (e não só no prompt). Nunca por nome. A mensagem de "não encontrado" não revela se um cliente existe. A chave de API fica no `.env`, fora do versionamento.

### Tratamento de dados
- Busca sem acentos e sem diferenciar maiúsculas ("violao" encontra "Violão").
- Cruzamento de produtos com categorias e promoções ativas (se houver mais de uma promoção para o mesmo produto, vale a de maior desconto).
- Regras do manual aplicadas em código: PIX (5%) não acumula com preço promocional; parcela mínima por faixa de parcelamento.
- Status do banco (`shipped`, `pending`...) traduzidos para português antes de chegar ao modelo.

### Persistência do histórico
O histórico vive na sessão (objeto de chat do SDK), o suficiente para conversas multi-turno no CLI (por exemplo, o cliente informa o e-mail e depois pergunta pelo pedido). Não há persistência entre execuções.

---

## 📌 Suposições assumidas

- **Contatos divergentes no manual:** a capa e a seção 1.2 trazem (67) 3341-4444; a seção 7 traz (67) 3321-4500 para o WhatsApp. O e-mail aparece com e sem acento. Usei (67) 3341-4444 e `contato@emporiodamusica.com.br`.
- **Identificação do cliente:** os dados não têm CPF; usei o e-mail como identificador.
- **Promoções:** só existe o campo `is_active`, sem datas, então considero ativa toda promoção com `is_active = 1`.
- **E-mail repetido:** `bruno.martins@jmail.com` aparece para dois clientes; a consulta mostra os pedidos dos dois cadastros.
- **Fuso horário:** Campo Grande fixo em UTC-4.

---

## ⚠️ Limitações conhecidas

- **Data fixa na sessão:** a data injetada no prompt é a do início da conversa; em sessões muito longas (que cruzem a meia-noite) ela pode ficar desatualizada, embora a ferramenta `data_hora_atual` continue correta.
- **Data de recebimento:** a base só traz a *previsão* de entrega, não a data real de recebimento, então os prazos de arrependimento usam a previsão como referência.
- **Cálculo de prazos feito pelo modelo:** a comparação de datas (ex.: "ainda estou dentro dos 7 dias?") depende do LLM. Seria mais confiável uma ferramenta que calcule em código.
- **Feriados** não são considerados no horário de funcionamento.
- **Sem persistência** de conversas entre execuções e sem autenticação real além do e-mail.
- **Promoções sem data de validade** nos dados.
- **Políticas no prompt** não escalam se o manual crescer muito; nesse caso seria necessário RAG com busca por trechos.
- **Sem testes automatizados** das respostas do LLM; a validação foi manual com as conversas em `exemplos/`.

### Com mais tempo
- Ferramenta `verificar_prazo_devolucao` (cálculo determinístico de prazos).
- Testes automatizados para as ferramentas e avaliação das respostas do agente (golden set).
- Persistência do histórico por cliente e interface web/WhatsApp.
- Verificação de identidade mais forte (ex.: código enviado por e-mail).
- Registro de reclamações e transferência para atendente humano.

---

## 🤖 Uso de assistentes de código

Usei dois assistentes de IA, em momentos diferentes do projeto:

- **Gemini (Google):** na primeira versão, para construir a **base estrutural** do projeto (organização em `agent.py`, `tools.py` e `main.py`, leitura dos CSVs e do PDF) e para **estudar os componentes** envolvidos (API do Gemini, pandas, PyPDF), além de pesquisar e formatar o código. Essa versão escolhia o contexto por palavras-chave na mensagem do cliente.
- **Claude (Anthropic):** depois, em conversas de chat, para revisar o projeto. A primeira versão dava respostas inconsistentes. Com o Claude diagnostiquei as causas (palavras-chave frágeis, política truncada em 2500 caracteres, `import` faltando, SDK `google-generativeai` descontinuado, falta de regra clara de identificação do cliente) e migrei para function calling com o SDK `google-genai`, mantendo o manual de políticas completo no prompt.

**Meu fluxo:** colava o código e a saída do terminal, recebia uma proposta, lia e adaptava o código (removi trechos sem uso, como uma função auxiliar e um import), e testava manualmente cada mudança no CLI com dados reais. Os testes revelaram problemas que levaram a novos ajustes no prompt, como o agente oferecer ações que não pode executar e supor uma data errada no cálculo do prazo de devolução. Também usei os assistentes para estudar a lógica aplicada (function calling, histórico do chat, diferença para RAG), de modo a conseguir explicar e evoluir o código sozinho.

---

## 💬 Exemplos de interação

A pasta [`exemplos/`](exemplos/) traz 5 conversas reais do agente: filtro de catálogo por faixa de preço, preço e promoções (com regra do PIX), consulta de pedido com identificação por e-mail, pedido fora de escopo com informações da loja, e devolução por arrependimento com cálculo de prazo.
