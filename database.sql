CREATE DATABASE IF NOT EXISTS barbearia;
USE barbearia;

CREATE TABLE cliente (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(45) NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL DEFAULT ''
);

CREATE TABLE barbeiro (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(45) NOT NULL,
    especialidade VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    senha VARCHAR(255) NOT NULL DEFAULT ''
);




CREATE TABLE disponibilidade (
    id INT PRIMARY KEY AUTO_INCREMENT,
    barbeiro_id INT,
    dia_semana INT,
    hora_inicio TIME,
    hora_fim TIME,
    FOREIGN KEY (barbeiro_id) REFERENCES barbeiro(id) ON DELETE CASCADE
);

CREATE TABLE servicos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(45) NOT NULL,
    preco DECIMAL(5,2) NOT NULL,
    descricao VARCHAR(100),
    duracao_min INT NOT NULL DEFAULT 30
);

CREATE TABLE agendamento (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cliente_id INT,
    barbeiro_id INT,
    servico_id INT,
    data DATE NOT NULL,
    horario VARCHAR(10) NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES cliente(id),
    FOREIGN KEY (barbeiro_id) REFERENCES barbeiro(id),
    FOREIGN KEY (servico_id) REFERENCES servicos(id)
);

CREATE TABLE agendamento_servicos (
    agendamento_id INT,
    servico_id INT,
    FOREIGN KEY (agendamento_id) REFERENCES agendamento(id) ON DELETE CASCADE,
    FOREIGN KEY (servico_id) REFERENCES servicos(id)
);

CREATE TABLE IF NOT EXISTS disponibilidade_excecao (
    id           INT PRIMARY KEY AUTO_INCREMENT,
    barbeiro_id  INT NOT NULL,
    data         DATE NOT NULL,
    hora_inicio  TIME DEFAULT NULL,
    hora_fim     TIME DEFAULT NULL,
    -- hora_inicio e hora_fim NULL = folga (dia bloqueado)
    UNIQUE KEY uq_barbeiro_data (barbeiro_id, data),
    FOREIGN KEY (barbeiro_id) REFERENCES barbeiro(id) ON DELETE CASCADE
);

ALTER TABLE agendamento DROP FOREIGN KEY agendamento_ibfk_3;
ALTER TABLE agendamento DROP COLUMN servico_id;