# 🎮 RPG Discord Bot V2

RPG procedural modular para Discord, desenvolvido em Python.

## ⚙️ Setup

```bash
# 1. Clone o repositório
git clone <url-do-repo>
cd discord_bot_v2

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure o .env
cp .env.example .env
# edite o .env com seu token

# 4. Rode o bot
python main.py
```

## 🗂️ Estrutura

```
discord_bot_v2/
├── main.py              ← entrada do bot
├── commands/            ← comandos Discord
├── database/
│   ├── connection.py    ← conexão SQLite
│   ├── schema.py        ← criação das tabelas
│   └── repository.py    ← todas as queries
├── utils/
│   ├── xp.py            ← fórmulas de progressão
│   ├── embeds.py        ← embeds padronizados
│   └── checks.py        ← decorators de verificação
├── views/               ← botões e UI interativa
├── data/                ← banco SQLite (gerado automaticamente)
└── tests/               ← testes automatizados
```

## 🧪 Testes

```bash
pip install pytest
pytest tests/ -v
```

## 📐 Regras de desenvolvimento

- Nunca acessar SQLite fora de `database/repository.py`
- Toda lógica compartilhada vai para `utils/`
- `commands/` apenas orquestra — sem SQL, sem lógica pesada
