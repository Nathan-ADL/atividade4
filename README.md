Sistema de Barbearia
1. Visão geral

Este projeto é um sistema web para gerenciamento de barbearia, desenvolvido com o objetivo de permitir o controle de usuários, agendamentos e serviços de forma simples e organizada.

A aplicação foi construída utilizando Flask, MySQL e Docker, garantindo portabilidade entre ambientes locais e em nuvem (AWS EC2).

2. Funcionalidades
Cadastro de usuários
Login de clientes e barbeiros
Agendamento de serviços
Visualização de agendamentos
Painel administrativo para barbeiros
Integração com banco de dados MySQL
3. Tecnologias utilizadas
Python 3
Flask
MySQL 8.0
Docker
Docker Compose
HTML5
CSS3
4. Arquitetura

O sistema é composto por dois serviços principais:

web (Flask): aplicação principal responsável pelas rotas, lógica e interface
db (MySQL): banco de dados responsável pela persistência das informações

A comunicação entre os serviços é feita via rede interna do Docker Compose.

5. Estrutura do projeto
├── static
│   └── style.css
├── templates
│   ├── cadastro.html
│   ├── index.html
│   ├── login.html
│   ├── meus_agendamentos.html
│   └── painel_barbeiro.html
├── .env.example
├── .gitignore
├── Dockerfile
├── app.py
├── database.py
├── database.sql
├── docker-compose.yml
└── requirements.txt
6. Configuração do ambiente

O projeto utiliza variáveis de ambiente definidas no arquivo .env.

Crie o arquivo .env com base no exemplo:

cp .env.example .env

Exemplo de configuração:

DB_HOST=db
DB_USER=user
DB_PASSWORD=123456
DB_NAME=barbearia
7. Execução local

As instruções completas de execução estão no arquivo:

GUIA_USUARIO.md
8. Execução na AWS EC2

Após o deploy na instância EC2, o sistema pode ser acessado através de:

http://IP_PUBLICO_DA_EC2:5000
IMPORTANTE:

Substitua IP_PUBLICO_DA_EC2 pelo IP real da sua instância.

9. Docker Hub

A imagem do projeto pode ser acessada em:

https://hub.docker.com/r/nathanadl/atividade4-web/tags
IMPORTANTE:

Substitua pelos seus dados reais do Docker Hub.

10. Repositório GitHub
https://github.com/Nathan-ADL/atividade4
IMPORTANTE:

Substitua pelo link real do seu repositório.

11. Observações importantes
O sistema depende do Docker e Docker Compose para execução correta
O banco de dados é inicializado automaticamente pelo docker-compose
O arquivo .env é obrigatório para funcionamento correto da aplicação
A porta padrão da aplicação é 5000
12. Execução geral (resumo)
git clone https://github.com/Nathan-ADL/atividade4
cd atividade4
cp .env.example .env
docker compose up -d --build

Acesso:

http://localhost:5000

ou

http://IP_PUBLICO_DA_EC2:5000