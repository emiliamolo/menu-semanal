PRAGMA foreign_keys = ON;

CREATE TABLE usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    mail TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL,
    reset_token TEXT,
    expires_at DATETIME
);

CREATE TABLE recetas (
    id_receta INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    tiempo INTEGER, -- minutos
    tipo TEXT,
    comida TEXT,
    instrucciones TEXT,
    id_usuario INTEGER,
    publica INTEGER DEFAULT 0, --0: privada, 1: publica
    precio_estimado INTEGER,
    image_ruta TEXT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario) ON DELETE CASCADE
);

CREATE TABLE menus (
    id_menu INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    fecha DATE NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario) ON DELETE CASCADE
);

CREATE TABLE menu_receta (
    id_menu INTEGER NOT NULL,
    id_receta INTEGER NOT NULL,
    nro_dia INTEGER NOT NULL, -- 0 lunes a 6 domingo
    PRIMARY KEY (id_menu, id_receta, nro_dia),
    FOREIGN KEY (id_menu) REFERENCES menus (id_menu) ON DELETE CASCADE,
    FOREIGN KEY (id_receta) REFERENCES recetas (id_receta) ON DELETE CASCADE
);

CREATE TABLE ingredientes (
    id_ingrediente INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE ingrediente_receta (
    id_ingrediente INTEGER,
    id_receta INTEGER,
    PRIMARY KEY (id_ingrediente, id_receta),
    FOREIGN KEY (id_ingrediente) REFERENCES ingredientes (id_ingrediente) ON DELETE CASCADE,
    FOREIGN KEY (id_receta) REFERENCES recetas (id_receta) ON DELETE CASCADE
);

CREATE TABLE preferidas (
    id_receta INTEGER,
    id_usuario INTEGER,
    PRIMARY KEY (id_receta, id_usuario),
    FOREIGN KEY (id_receta) REFERENCES recetas (id_receta) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario) ON DELETE CASCADE
);

-- Índices para mejorar el rendimiento
CREATE INDEX idx_recetas_id_usuario ON recetas(id_usuario);
CREATE INDEX idx_recetas_comida ON recetas(comida);
CREATE INDEX idx_recetas_publica ON recetas(publica);
CREATE INDEX idx_menus_id_usuario ON menus(id_usuario);
CREATE INDEX idx_menu_receta_id_menu ON menu_receta(id_menu);
CREATE INDEX idx_ingrediente_receta_id_receta ON ingrediente_receta(id_receta);
CREATE INDEX idx_preferidas_id_usuario ON preferidas(id_usuario);