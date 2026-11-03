# 🎵 Exemplos de interação - Empório da Música

Conversas reais executadas via CLI (`python src/main.py`) com o modelo `gemini-3.5-flash`. As respostas foram coladas do terminal, sem edição, e os valores podem ser conferidos nos CSVs da pasta `data/`. O Cenário 5 foi executado em 02/11/2026, data usada pelo agente no cálculo do prazo.

---

## Cenário 1: Catálogo por faixa de preço

**O que demonstra:** ferramenta `buscar_produtos` com filtro de categoria e preço máximo, retornando só itens ativos e com estoque.

**Cliente:** Quais violões disponíveis até R$ 1000?

**Atendente:** Temos ótimas opções de violões por até R$ 1.000! Aqui estão os primeiros modelos do nosso catálogo:

1. **Tagima Memphis AC-39 Nylon Natural** — R$ 429,90 *(perfeito para iniciantes)*
2. **Rozini RC-104 Nylon Estudante** — R$ 459,90 *(madeiras nacionais)*
3. **Shelby SN-100 Folk Aço Preto** — R$ 549,00 *(folk com visual moderno)*
4. **Giannini GF-1R Aço Folk Sunburst** — R$ 579,90 *(tampo em Spruce)*
5. **Yamaha C40 Nylon Natural** — R$ 599,90 *(excelente projeção sonora)*

Quer ver o restante das opções disponíveis nessa faixa de preço? 🎸

---

## Cenário 2: Preço de um produto e promoções

**O que demonstra:** preço de tabela, desconto do PIX e parcelamento calculados em código; promoções ativas com preço original, percentual e preço final.

**Cliente:** Quanto custa o Takamine GD20?

**Atendente:** O Takamine GD20 Dreadnought Natural custa R$ 2.199,00 à vista ou no cartão, podendo parcelar em até 12x sem juros aqui na loja! No PIX, tem aquele descontinho especial de 5%, saindo por R$ 2.089,05. 🎶

**Cliente:** tem promoção em ukulele?

**Atendente:** Temos sim! Olha só os ukuleles que estão com preço promocional agora:

1. **Ohana CK-20 Concert Natural** — de R$ 549,00 por **R$ 439,20** *(20% de desconto)*
2. **Kalani KAL-700T Tenor Natural** — de R$ 359,00 por **R$ 323,10** *(10% de desconto)*

Quer saber mais detalhes sobre algum deles? 🎵

---

## Cenário 3: Consulta de pedido com identificação por e-mail (caso não trivial)

**O que demonstra:** o agente não consulta pedido só pelo nome (privacidade/LGPD), pede o e-mail cadastrado e, em seguida, busca dados reais do pedido via `consultar_pedidos`, mantendo o contexto entre as mensagens.

**Cliente:** Oi, sou a Ana Carolina, tem pedido no meu nome?

**Atendente:** Oi, Ana Carolina! Por motivos de segurança e privacidade (LGPD), não consigo consultar pedidos apenas pelo nome.

Poderia me informar o seu e-mail cadastrado? Assim eu consigo verificar isso rapidinho para você! 🎸

**Cliente:** anacarol.ferreira@coldmail.com

**Atendente:** Achei seu pedido por aqui, Ana!

O **pedido #8** (que inclui o Ukulele Kala KA-C Concert Mogno) está com o status **Enviado (a caminho)** e a previsão de entrega é para o dia **28/02/2026**.

O código de rastreamento é o `BRJL5544332BR`, e você já deve ter recebido os detalhes por e-mail e WhatsApp também.

Precisa de ajuda com mais alguma coisa? 🎶

---

## Cenário 4: Fora do escopo e informações da loja

**O que demonstra:** recusa educada de acessórios (a loja vende só instrumentos) e resposta com endereço e horários extraídos do manual de políticas.

**Cliente:** Vocês vendem cabos P10?

**Atendente:** Poxa, infelizmente nós trabalhamos exclusivamente com **instrumentos musicais** (como violões, guitarras, teclados, ukuleles, entre outros) e não comercializamos acessórios, cabos, palhetas ou amplificadores.

Se precisar de ajuda para escolher algum instrumento, é só chamar! 🎵

**Cliente:** qual o endereço e o horário?

**Atendente:** Nossa loja física fica na **Rua 14 de Maio, 3200 — Centro, Campo Grande - MS**.

Funcionamos de segunda a sexta-feira, das 09:00 às 18:00, e aos sábados, das 09:00 às 13:00 (aos domingos e feriados a loja fica fechada).

Se precisar falar com a gente por telefone ou WhatsApp, o número é **(67) 3341-4444**! 🏢

---

## Cenário 5: Devolução por arrependimento (aplica regras das políticas + dados do pedido)

**O que demonstra:** o agente explica a regra, pede o e-mail, consulta o pedido (`consultar_pedidos`) e conclui, com base na data de entrega e na data atual, que o prazo de 7 dias corridos já passou.

**Cliente:** Me arrependi da minha compra, posso devolver?

**Atendente:** Com certeza! Para compras online, você tem até 7 dias corridos após o recebimento para solicitar a devolução por arrependimento, sem precisar justificar, tá?

Para eu conferir os prazos certinho para você, me informa o seu e-mail cadastrado na compra, por favor? 🎵

**Cliente:** leticia.rocha@jmail.com

**Atendente:** Olá, Letícia! Vi aqui que o seu pedido (número 7, do ukulele Shelby Soprano) foi entregue.

Como a entrega aconteceu em fevereiro e o prazo para arrependimento em compras online é de até 7 dias corridos após o recebimento, infelizmente o prazo já passou.

Se tiver alguma dúvida ou precisar de ajuda com outra coisa, é só falar! 🎸

> Nota: a base de dados só tem a *previsão* de entrega (`estimated_delivery`, 17/02/2026), não a data real de recebimento; o agente usou essa data como referência.
