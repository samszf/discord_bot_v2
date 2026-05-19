SCHEMA = """

CREATE TABLE IF NOT EXISTS players (
    user_id     INTEGER PRIMARY KEY,
    nivel       INTEGER DEFAULT 1,
    xp          INTEGER DEFAULT 0,
    ouro        INTEGER DEFAULT 100,
    hp_base     INTEGER DEFAULT 100,
    atk_base    INTEGER DEFAULT 10,
    defesa_base INTEGER DEFAULT 5,
    classe      TEXT    DEFAULT NULL,
    criado_em   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inventory (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    item_id     TEXT    NOT NULL,
    quantidade  INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES players(user_id)
);

CREATE TABLE IF NOT EXISTS equipment (
    user_id     INTEGER PRIMARY KEY,
    arma        TEXT DEFAULT NULL,
    armadura    TEXT DEFAULT NULL,
    acessorio   TEXT DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES players(user_id)
);

CREATE TABLE IF NOT EXISTS cooldowns (
    user_id     INTEGER NOT NULL,
    comando     TEXT    NOT NULL,
    ultimo_uso  TIMESTAMP NOT NULL,
    PRIMARY KEY (user_id, comando),
    FOREIGN KEY (user_id) REFERENCES players(user_id)
);

CREATE TABLE IF NOT EXISTS battle_stats (
    user_id           INTEGER PRIMARY KEY,
    vitorias          INTEGER DEFAULT 0,
    derrotas          INTEGER DEFAULT 0,
    slimes_derrotados INTEGER DEFAULT 0,
    dano_total        INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES players(user_id)
);

CREATE TABLE IF NOT EXISTS habilidades_cooldown (
    user_id       INTEGER NOT NULL,
    habilidade_id TEXT    NOT NULL,
    ultimo_uso    TIMESTAMP NOT NULL,
    PRIMARY KEY (user_id, habilidade_id),
    FOREIGN KEY (user_id) REFERENCES players(user_id)
);

"""
