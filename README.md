# LEFI EDGE — Telegram Publisher

Tento repozitář slouží jako tracker tipů a bezpečná publikační fronta pro Telegram kanál LEFI EDGE.

## Jak funguje publikování

1. Tip se nejdříve analyzuje a připraví v ChatGPT.
2. Zveřejnění proběhne až po výslovném potvrzení uživatele **SCHVALUJI TIP**.
3. Schválený tip se zapíše do `index.html` jako `pending`.
4. Současně se přidá nový JSON soubor do `telegram-queue/`.
5. GitHub Actions odešle obsah JSON souboru přes Telegram bota.

## Povinné GitHub Secrets

V repozitáři otevřete:

`Settings → Secrets and variables → Actions → New repository secret`

Vložte:

- `TELEGRAM_BOT_TOKEN` — token získaný od BotFather.
- `TELEGRAM_CHAT_ID` — například `@lefiedge`, pokud bot publikuje do veřejného kanálu.

Bot musí být v kanálu administrátor a mít právo zveřejňovat příspěvky.

Token nikdy nevkládejte do HTML, JSON fronty ani do chatu.
