# DentalClin: landing page (projeto de estudo)

Landing page de implantes dentários. FastAPI + Docker endurecido + Tailscale. Todos os CTAs abrem o WhatsApp.

## Comandos
```powershell
copy .env.example .env        # preencha WHATSAPP_NUMBER (somente dígitos, com 55)
docker compose up -d --build  # sobe em 127.0.0.1:8087
docker compose ps             # STATUS deve ficar "healthy"
docker compose logs -f dentalclin
docker compose down           # para
python tests/check_site.py http://127.0.0.1:8087
```

## Tailscale (a porta 443 é do Facesort; esta página usa a 8443)
```powershell
tailscale serve --bg --https=8443 http://127.0.0.1:8087    # só tailnet
tailscale funnel --bg --https=8443 http://127.0.0.1:8087   # público: https://breno-pc.tailf5368d.ts.net:8443/
tailscale funnel --https=8443 off                          # tira do ar
tailscale serve status
```

## Estrutura
- `app/main.py`: FastAPI; renderiza o HTML uma vez, injeta `wa.me` com mensagens por botão, CSP estrita, sem cookies.
- `app/templates/index.html`, `app/static/style.css` (mobile-first), `app/static/app.js` (melhorias opcionais).
- `.env` (não vai ao git): `WHATSAPP_NUMBER`, `ALLOW_INDEXING` (0 = `noindex` durante o estudo).

## Antes de ir ao ar de verdade
- A clínica deve revisar os textos marcados como [EXEMPLO] em `CONTENT.md` (FAQ, "por que implante", etapas).
- Trocar as fotos de Vitória (placeholders, com crédito no rodapé) por fotos da clínica.
- Rodar `pip-audit -r requirements.txt` (ver nota no PLAN: falhou por certificado TLS nesta máquina).
- Mudar `ALLOW_INDEXING=1` quando for para ser encontrado no Google.
