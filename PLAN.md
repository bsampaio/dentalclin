# Plano: Landing page DentalClin (implantes dentários)

Projeto de estudo. Stack: Python + FastAPI, Docker endurecido, exposto com Tailscale Funnel.

## 1. O que já sabemos

| Fonte | Resultado |
|---|---|
| Instagram @dentalclinvitoria | "DentalClin \| Implantes em Vitória", "Reabilitando Sorrisos", EPAO 2902/ES, Enseada do Suá, Vitória-ES, ~1,8 mil seguidores. WhatsApp de agendamento: `https://wa.me/message/EC3BMQHSIGB3A1` |
| meudoutor.com | **Não extraído.** A página carrega por JavaScript e o fetch voltou vazio ("Clínica / Loading"). Precisamos do texto por outro caminho (ver perguntas). |
| /images | 21 arquivos, todos **marca/logo**: fundo petróleo escuro com logo prata 3D (perfil), logo prata sobre branco, variações. **Nenhuma foto** de clínica, equipe ou paciente. |

Identidade: monograma "DC", logotipo serifado fino, "Reabilitação oral & estética", prata metalizado sobre azul-petróleo escuro.

## 2. Decisões de design

- **Direção:** premium escuro e sóbrio. Fundo azul-petróleo (da placa do logo), tinta clara, prata como detalhe, um único acento para os botões de WhatsApp. O logo metálico é um asset da marca, então o degradê dele fica (exceção declarada).
- **Apple-like:** muito espaço, tipografia grande e leve, uma ideia por tela, movimento suave e interrompível, `prefers-reduced-motion` respeitado.
- **Mobile-first:** CSS escrito para 390px e ampliado com `min-width`. Alvos de toque de 44px ou mais, `100svh`, safe-area, sem hover como requisito.
- **Ideia central (a confirmar após `draw.mjs`):** o logo é feito de dois traços que se encaixam, e um implante é uma peça que se encaixa. O encaixe vira o motivo visual e o movimento de rolagem.
- **Elemento interativo:** um simulador curto "Quero saber sobre implantes". Escolhe a situação (um dente, vários, protocolo) e o botão abre o WhatsApp com a mensagem já escrita. Funciona sem JS (link simples).
- **CTAs:** todos para WhatsApp via `wa.me`, texto pré-preenchido por contexto. **Nenhum e-mail ou mailto.** Botão fixo na parte de baixo no mobile.
- **Imagens:** sem fotos reais, a página será de tipografia, cor e ilustração desenhada em código (implante, arcada, encaixe), mais os logos. Foto de banco não será apresentada como da clínica. Se você tiver fotos (consultório, equipe, casos), o resultado melhora muito.

## 3. Estrutura da página (argumento, uma seção por afirmação)

1. **Hero:** "Implantes dentários em Vitória" + frase de apoio + botão "Agendar avaliação" (WhatsApp).
2. **Por que implante:** o que resolve (mastigar, falar, sorrir sem prótese solta).
3. **Como funciona:** etapas reais do tratamento (avaliação, planejamento, cirurgia, prótese). Conteúdo conferido com a clínica.
4. **Tratamentos:** implante unitário, múltiplos, protocolo, estética (lentes, clareamento). Só o que a clínica oferece.
5. **A clínica e os profissionais:** nome, registro (EPAO 2902/ES), localização.
6. **Simulador / pergunta frequente:** FAQ curto (dói? quanto tempo? tenho osso suficiente?).
7. **Contato:** endereço, horário, mapa (link, sem embed pesado), botão de WhatsApp, link do Instagram.
8. **Rodapé:** logo grande, registro profissional, aviso LGPD simples.

Não vou inventar depoimentos, números, antes/depois ou preços. Conteúdo de exemplo fica marcado para você confirmar.

## 4. Arquitetura técnica

```
internet ─► Tailscale Funnel ─► tailscaled (TLS) ─► 127.0.0.1:8080 ─► Docker: uvicorn + FastAPI (não-root, read-only)
```

```
Dentalclin/
  app/main.py        FastAPI: GET / (Jinja2), /healthz, headers de segurança + CSP
  app/config.py      números/URLs via variáveis de ambiente
  app/templates/     index.html
  app/static/        css, js (sem inline, CSP estrita), fontes self-host, imagens otimizadas
  tests/             teste de headers, links wa.me, ausência de mailto
  Dockerfile, compose.yaml, .env.example, requirements.txt, README.md, PLAN.md
```

- Sem formulário e sem banco: a página é estática servida pelo FastAPI. Não coletamos dados pessoais, o que simplifica LGPD. Sem analytics de terceiros nesta fase.
- Docker conforme a skill: imagem fixada por digest, usuário não-root, rootfs read-only, `cap_drop: ALL`, porta só em 127.0.0.1, healthcheck.
- Dependências fixadas com `==` e checadas com pip-audit.

## 5. Passos e critérios de pronto

| # | Passo | Pronto quando | Status |
|---|---|---|---|
| 0 | Plano e respostas | aprovado | feito |
| 1 | Conteúdo (CONTENT.md) | copy deck aprovado | feito ("24 horas" mantido; sem CRO de dentistas) |
| 2 | Direção de design | direção e tokens definidos | feito: relojoaria/joalheria fina; hero e tratamentos redesenhados; paleta e tipo da marca (Bodoni Moda + Jost) |
| 3 | Scaffold FastAPI + Docker | /healthz 200, uid 10001 | feito (porta 8087, pois 8080 é do Facesort) |
| 4 | Seções mobile-first | 390px sem overflow, 1 h1 | feito |
| 5 | CTAs WhatsApp + cupom | zero mailto | feito (23/23 checks em tests/check_site.py) |
| 6 | Movimento e polimento | inspect 0 FAIL | feito; `still-page` liberado porque este Windows tem animações desligadas (verificado com no-preference) |
| 7 | Segurança | headers, CSP, audit | parcial: container e headers ok; **pip-audit pendente** (erro de certificado TLS, sem contornar) |
| 8 | Tailscale | Serve, depois Funnel | Serve ok (tailnet, :8443); **Funnel aguardando seu OK** |
| 9 | README | runbook | feito |

Antes de cada execução eu digo o comando, o que ele sobe e como acompanhar (`docker compose logs -f`).

## 6. Riscos

- **Exposição pública:** o Funnel publica a página para qualquer pessoa. Por isso só entra conteúdo próprio para o público. Nada interno, nada de dados de pacientes.
- **O PC precisa ficar ligado** e sem suspensão. Para estudo é aceitável; produção real pediria hospedagem dedicada.
- **Funnel exige** HTTPS e Funnel habilitados no painel Tailscale (posso orientar).
- **Claims de saúde:** nada de promessas de resultado. A comunicação odontológica tem regras do CFO; a revisão final do texto deve ser da clínica ou do responsável técnico.
- **Imagem sem fotos reais** pode deixar a página fria. Mitigação: ilustração própria e tipografia forte.

## 7. Perguntas para você (bloqueiam o passo 1)

1. **Número de WhatsApp:** uso o link do Instagram (`wa.me/message/EC3BMQHSIGB3A1`) ou você prefere informar o número direto?
2. **Texto do site atual:** pode colar o conteúdo (serviços, profissionais, endereço completo, horários) ou prefere que eu abra com um navegador automatizado (Chrome)?
3. **Fotos reais** da clínica, equipe ou casos autorizados? Se não, sigo com ilustração.
4. **Máquina e Tailscale:** este PC fica ligado? Docker Desktop e Tailscale já estão instalados e o Funnel habilitado na sua tailnet?
5. **Git:** quer repositório? Se sim, qual identidade (e-mail pessoal ou do trabalho) para os commits?
