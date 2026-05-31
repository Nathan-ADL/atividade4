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

INSERT INTO servicos (nome, preco, descricao, duracao_min) VALUES
('Sobrancelha', 20.00, 'Design com fio · 15 min', 15),
('Corte', 45.00, 'Corte tradicional · 30 min', 30),
('Barba', 35.00, 'Navalha e toalha quente · 25 min', 25),
('Corte + Barba', 70.00, 'Combo completo · 55 min', 55),
('Hidratação', 60.00, 'Tratamento capilar · 40 min', 40);

INSERT INTO barbeiro (nome, especialidade) VALUES
('Ricardo C.', 'Clássico & moderno'),
('Felipe M.', 'Especialista em barba'),
('André G.', 'Coloração & estilo'),
('João P.', 'Cortes modernos');

INSERT INTO disponibilidade (barbeiro_id, dia_semana, hora_inicio, hora_fim) VALUES

-- Ricardo C. (id = 1)
(1, 1, '08:00:00', '18:00:00'), -- Segunda
(1, 2, '08:00:00', '18:00:00'), -- Terça
(1, 3, '08:00:00', '18:00:00'), -- Quarta
(1, 4, '08:00:00', '18:00:00'), -- Quinta
(1, 5, '08:00:00', '18:00:00'), -- Sexta
(1, 6, '08:00:00', '14:00:00'), -- Sábado

-- Felipe M. (id = 2)
(2, 1, '09:00:00', '19:00:00'), -- Segunda
(2, 2, '09:00:00', '19:00:00'), -- Terça
(2, 3, '09:00:00', '19:00:00'), -- Quarta
(2, 4, '09:00:00', '19:00:00'), -- Quinta
(2, 5, '09:00:00', '19:00:00'), -- Sexta
(2, 6, '09:00:00', '15:00:00'); -- Sábado