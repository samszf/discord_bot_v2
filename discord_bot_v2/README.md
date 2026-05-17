# 🎮 RPG Discord Bot V2

Bot de RPG procedural e modular para Discord, desenvolvido em Python. Os jogadores podem batalhar contra slimes, coletar itens, evoluir personagens e interagir com uma economia completa — tudo dentro do servidor.

---

## ✨ Funcionalidades

### ⚔️ Combate
- Batalhas por turnos contra **7 tipos de slimes** gerados proceduralmente
- Dificuldade escala com o nível do jogador
- Críticos, esquivas e fuga com chances configuráveis
- Interface com botões interativos no Discord

### 🎒 Itens e Loot
- **21 itens** em 4 categorias: armas, armaduras, acessórios e consumíveis
- **6 raridades**: comum, incomum, raro, épico, lendário e divino
- Drop automático ao vencer batalhas, com chances por raridade

### 📊 Progressão
- Sistema de XP com level up automático
- Bônus de HP, ATK e DEF ao subir de nível
- XP passivo por mensagens de texto e por tempo em canais de voz

### 🏪 Economia
- Loja com compra e venda de itens
- Ouro como moeda do jogo
- Preço de venda = 40% do preço de compra

### 🧙 Personagem
- Perfil completo com stats, equipamentos e histórico de batalhas
- 3 slots de equipamento: arma, armadura e acessório
- Stats finais calculados com bônus dos itens equipados

---

## 🕹️ Comandos

| Comando | Descrição |
|---|---|
| `/registrar` | Cria seu personagem |
| `/perfil [@usuário]` | Exibe stats, equipamentos e histórico |
| `/aventura` | Inicia uma batalha contra um slime |
| `/inventario [categoria]` | Lista seus itens com paginação |
| `/equipar <item_id>` | Equipa um item do inventário |
| `/desequipar <slot>` | Remove um item equipado |
| `/loja [seção]` | Exibe itens disponíveis para compra |
| `/comprar <item_id>` | Compra um item da loja |
| `/vender <item_id> [quantidade]` | Vende um item do inventário |

### Comando de administração
| Comando | Descrição |
|---|---|
| `!sync` | Força a sincronização de slash commands (apenas dono do bot) |

---

## 🗂️ Estrutura do Projeto

```
discord_bot_v2/
├── main.py                  ← entrada do bot
├── .env                     ← variáveis de ambiente (não versionar)
├── .env.example             ← modelo do .env
├── requirements.txt
├── Procfile                 ← configuração de deploy (Railway)
├── runtime.txt              ← versão do Python
│
├── commands/                ← slash commands (sem SQL, sem lógica pesada)
│   ├── registro.py
│   ├── perfil.py
│   ├── aventura.py
│   ├── inventario.py
│   ├── equipar.py
│   ├── loja.py
│   └── xp_eventos.py        ← XP passivo por mensagem e voz
│
├── database/                ← todo acesso ao banco passa por aqui
│   ├── connection.py        ← conexão singleton SQLite
│   ├── schema.py            ← criação das tabelas
│   └── repository.py       ← todas as queries
│
├── utils/                   ← lógica do RPG
│   ├── player.py            ← criação e stats do jogador
│   ├── xp.py                ← fórmulas de progressão
│   ├── xp_passivo.py        ← configurações de XP passivo
│   ├── levelup.py           ← level up e notificações
│   ├── slimes.py            ← geração procedural de inimigos
│   ├── combat.py            ← lógica de turno
│   ├── loot.py              ← sistema de drop
│   ├── items.py             ← catálogo de itens
│   ├── economy.py           ← compra, venda, preços
│   ├── cooldown.py          ← gerenciamento de cooldowns
│   ├── embeds.py            ← embeds padronizados
│   └── checks.py            ← decorators de verificação
│
├── views/                   ← UI interativa
│   └── combat_view.py       ← botões de combate
│
├── assets/                  ← imagens e recursos visuais
│   ├── slimes/
│   ├── raridades/
│   ├── itens/
│   └── ui/
│
├── data/                    ← banco SQLite (gerado automaticamente)
└── tests/                   ← testes automatizados
    ├── test_banco.py
    ├── test_fase2.py
    ├── test_fase3.py
    ├── test_fase4.py
    ├── test_fase5.py
    └── test_xp_passivo.py
```

---

## ⚙️ Setup Local

### Pré-requisitos
- Python 3.11+
- Conta no [Discord Developer Portal](https://discord.com/developers/applications)

### 1. Clone o repositório
```bash
git clone https://github.com/samszf/discord_bot_v2
cd discord_bot_v2
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure o `.env`
```bash
cp .env.example .env
```

Edite o `.env` com suas credenciais:
```env
DISCORD_TOKEN=seu_token_aqui
PREFIX=!
DB_PATH=data/rpg.db
```

### 4. Rode o bot
```bash
python main.py
```

O banco de dados é criado automaticamente na primeira execução.

---

## 🚀 Deploy no Railway

### 1. Faça o push do projeto para o GitHub

### 2. Acesse [railway.app](https://railway.app) e conecte o repositório

### 3. Configure as variáveis de ambiente no painel do Railway

| Variável | Valor |
|---|---|
| `DISCORD_TOKEN` | token do bot |
| `PREFIX` | `!` |
| `DB_PATH` | `/data/rpg.db` |

### 4. Crie um volume persistente
No painel do projeto: **+ New → Volume**, montado em `/data`.
Isso garante que os dados dos jogadores não são perdidos entre deploys.

### 5. Pronto
O Railway faz deploy automático a cada `git push`.

---

## 🧪 Testes

```bash
python tests/test_banco.py
python tests/test_fase2.py
python tests/test_fase3.py
python tests/test_fase4.py
python tests/test_fase5.py
python tests/test_xp_passivo.py
```

---

## 🏗️ Arquitetura

O projeto segue um fluxo estrito de camadas:

```
Usuário
  ↓
commands/       ← recebe o comando, valida, orquestra
  ↓
utils/          ← executa a lógica do RPG
  ↓
repository.py   ← acessa o banco de dados
  ↓
SQLite
```

### Regras invioláveis
- `commands/` nunca acessa o banco diretamente
- Todo SQL fica em `database/repository.py`
- Toda lógica compartilhada fica em `utils/`
- Nunca duplicar lógica entre sistemas

---

## 🔮 Roadmap

- [x] Sistema de registro e perfil
- [x] Combate por turnos com slimes procedurais
- [x] Loot por raridade
- [x] Inventário com paginação
- [x] Equipamentos com bônus de stats
- [x] Loja e economia
- [x] XP passivo por mensagem e canal de voz
- [ ] Classes (Guerreiro, Mago, Arqueiro)
- [ ] Bosses com mecânicas especiais
- [ ] PvP entre jogadores
- [ ] Guildas
- [ ] Crafting
- [ ] Pets
- [ ] Achievements
- [ ] Eventos globais
- [ ] Rank global

---

## 🛠️ Tecnologias

- [discord.py](https://discordpy.readthedocs.io/) — biblioteca principal
- [SQLite](https://www.sqlite.org/) — banco de dados
- [python-dotenv](https://pypi.org/project/python-dotenv/) — variáveis de ambiente

---

## 👥 Equipe

| Papel | Responsabilidade |
|---|---|
| Backend / Arquitetura | Código, banco de dados, sistemas, lógica RPG |
| Design / Arte | Ilustrações, ícones, assets visuais, identidade do bot |

---

## 📄 Licença

Projeto privado. Todos os direitos reservados.
