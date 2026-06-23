GUIA_USUARIO.md
Sistema de Barbearia - Guia de Uso

Senha para o cadastro de novos barbeiros: barber@admin123(configuravel no app.py)

Este documento tem como objetivo orientar a execução e utilização do sistema de barbearia, tanto em ambiente local quanto em ambiente de produção (AWS EC2), utilizando Docker e Docker Compose.

1. Pré-requisitos

Antes de iniciar, é necessário ter instalado:

Docker Engine
Docker Compose (v2 ou superior)
Docker Desktop (obrigatório para execução local no Windows/macOS)
Git

Observação: O Docker Desktop já inclui Docker Engine e Docker Compose para ambientes Windows.

2. Clonando o repositório

Execute os comandos abaixo:

git clone https://github.com/Nathan-ADL/atividade4
cd atividade4
3. Configuração do ambiente (.env)

O projeto utiliza variáveis de ambiente para conexão com o banco de dados.

Crie o arquivo .env a partir do exemplo:

cp .env.example .env

Edite o arquivo .env conforme necessário:

DB_HOST=db
DB_USER=root
DB_PASSWORD=123456
DB_NAME=barbearia

Importante:

Em Docker, o host deve ser db
Em execução local sem Docker, pode ser localhost
4. Estrutura do projeto
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
5. Execução com Docker (ambiente local)
5.1 Subir os containers

Dentro da pasta do projeto, execute:

docker compose up --build

Ou em modo detached (recomendado):

docker compose up -d --build
5.2 Verificar containers ativos
docker ps

Você deverá ver:

container do MySQL
container da aplicação Flask
5.3 Acessar aplicação

Após execução, acesse no navegador:

http://localhost:5000
6. Execução na AWS EC2
6.1 Pré-requisitos na instância

Na instância EC2 é necessário:

Docker instalado
Docker Compose instalado
Porta 5000 liberada no Security Group
6.2 Clonar o projeto na EC2
git clone https://github.com/Nathan-ADL/atividade4
cd nome-projeto
6.3 Criar arquivo .env
cp .env.example .env
nano .env

Configuração recomendada:

DB_HOST=db
DB_USER=user
DB_PASSWORD=123456
DB_NAME=barbearia
6.4 Subir aplicação
sudo docker compose up -d --build
6.5 Verificar containers
sudo docker ps
6.6 Acessar aplicação na AWS

Use o IP público da instância:
(100.55.215.67 - ip elástico utilizado na instância)
http://IP_PUBLICO_DA_EC2:5000
7. Publicação no Docker Hub (opcional)
Build da imagem
docker build -t usuario/barbearia-web .
Push para o Docker Hub
docker login
docker push usuario/barbearia-web
8. Possíveis problemas
8.1 Porta 5000 não abre
Verificar Security Group da AWS
Liberar inbound rule TCP 5000
8.2 Banco não conecta
Verificar .env
DB_HOST deve ser db no Docker
8.3 Docker sem permissão
sudo usermod -aG docker $USER
newgrp docker
8.4 Falta de espaço na EC2
sudo docker system prune -a -f
9. Considerações finais

O sistema foi desenvolvido para ser totalmente containerizado, garantindo portabilidade entre ambientes locais e servidores em nuvem.

A utilização do Docker Compose permite inicialização automática do banco de dados e da aplicação Flask com um único comando.