# README.md — My Restaurant Adventure

## Descrição

**My Restaurant Adventure** é um jogo web de gestão de recursos desenvolvido no âmbito da unidade curricular de Desenvolvimento de Aplicações Web (DAW).

O jogador começa com recursos iniciais e deve construir um império de restauração através da compra de restaurantes, produção de dinheiro, recolha de lucros, evolução dos negócios e contratação de gestores. Ao longo do jogo, o utilizador ganha reputação, sobe de rank e compete com outros jogadores numa leaderboard global.

O projeto foi desenvolvido com Flask, SQLite, HTML, CSS e JavaScript, seguindo uma estrutura simples inspirada no padrão MVC.

---

## Objetivo do Jogo

O objetivo principal é expandir a rede de restaurantes do jogador, gerindo bem os recursos disponíveis e maximizando o dinheiro acumulado.

Durante o jogo, o utilizador pode:

* Criar uma conta;
* Iniciar e terminar sessão;
* Comprar restaurantes;
* Aguardar pela construção dos restaurantes;
* Iniciar produções;
* Acompanhar barras de progresso;
* Recolher lucros;
* Evoluir restaurantes;
* Contratar gestores;
* Ganhar reputação;
* Subir de rank;
* Consultar a leaderboard;
* Consultar o histórico de ações.

---

## Tecnologias Utilizadas

### Backend

* Python
* Flask
* Flask-Login
* SQLite

### Frontend

* HTML5
* CSS3
* JavaScript
* Fetch API

### Ferramentas

* Git
* GitHub
* Visual Studio Code

---

## Funcionalidades Implementadas

### Sistema de Utilizadores

* Registo de novos utilizadores;
* Login de utilizadores existentes;
* Logout;
* Gestão de sessões com Flask-Login;
* Proteção de páginas através de autenticação.

### Gestão de Restaurantes

* Compra de restaurantes;
* Restaurantes fixos como slots de construção;
* Construção temporizada;
* Produção temporizada;
* Recolha manual de lucro;
* Evolução temporizada dos restaurantes;
* Cálculo de custos, lucros e recompensas por nível.

### Restaurantes Disponíveis

O jogo utiliza restaurantes fixos, funcionando como slots de progressão. Cada restaurante tem custos, tempos, lucros e recompensas diferentes.

Restaurantes existentes:

* Banca de Cachorros;
* Café;
* Croissanteria;
* Hamburgueria.

Cada restaurante pode estar em diferentes estados:

* Bloqueado;
* Em construção;
* Pronto;
* A produzir;
* Completo;
* A evoluir.

### Sistema de Gestores

* Cada restaurante tem um gestor associado;
* O gestor pode ser contratado quando o restaurante já está desbloqueado;
* A contratação exige dinheiro e reputação;
* O gestor automatiza o reinício da produção após o jogador recolher o lucro;
* A recolha do lucro continua a ser feita manualmente pelo jogador.

### Sistema de Progressão

* Sistema de reputação;
* Reputação total acumulada;
* Sistema de ranks;
* Notificação quando o jogador sobe de rank;
* Página com todos os ranks disponíveis;
* Rank atual apresentado na sidebar e na leaderboard.

### Leaderboard

* Leaderboard global dos jogadores;
* Ordenação por dinheiro total acumulado;
* Apresentação do Top 10 jogadores;
* Destaque visual para os três primeiros lugares;
* Atualização através de Fetch API;
* Apresentação do rank e respetivo emoji de cada jogador.

### Histórico de Ações

* Registo das principais ações do jogador;
* Histórico limitado às ações mais recentes;
* Mensagens com data e hora;
* Registo de compras, recolhas de lucro, evoluções e contratação de gestores.

### Interface

* Dashboard principal;
* Página de gestores;
* Página de leaderboard;
* Página de ranks;
* Página de histórico;
* Mensagens temporárias de sucesso e erro;
* Confirmações antes de ações importantes;
* Barras de progresso para construção, produção e evolução;
* Preservação da posição da página após ações na dashboard;
* Layout responsivo para diferentes tamanhos de ecrã.

---

## Estrutura do Projeto

```text
daw-projeto/
├── models/
│   ├── database.py
│   └── user.py
├── static/
│   ├── scripts/
│   │   └── main.js
│   └── styles/
│       └── style.css
├── templates/
│   ├── dashboard.html
│   ├── history.html
│   ├── leaderboard.html
│   ├── login.html
│   ├── managers.html
│   ├── ranks.html
│   └── register.html
├── server.py
├── views.py
├── settings.py
├── README.md
├── api_documentacao.md
├── base_dados.sql
└── game.db
```

---

## Instalação

### 1. Criar ambiente virtual

```bash
python -m venv .venv
```

### 2. Ativar ambiente virtual

No Windows PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependências

```bash
pip install flask flask-login
```

---

## Execução

Para iniciar o servidor Flask:

```bash
python server.py
```

Depois, abrir o navegador em:

```text
http://127.0.0.1:8080
```

---

## Base de Dados

A aplicação utiliza SQLite.

A base de dados é criada automaticamente quando o projeto é executado, através da classe `Database`, presente no ficheiro:

```text
models/database.py
```

As principais tabelas são:

* `USER`;
* `BUSINESS_TYPE`;
* `USER_BUSINESS`;
* `ACTION_HISTORY`.

A tabela `BUSINESS_TYPE` guarda os restaurantes fixos do jogo, enquanto a tabela `USER_BUSINESS` guarda os restaurantes comprados por cada jogador.

---

## API

O projeto inclui uma rota API para a leaderboard:

```http
GET /api/leaderboard
```

Esta rota devolve os 10 melhores jogadores em formato JSON e é utilizada pelo frontend através da Fetch API.

---

## Validações e Segurança

O projeto inclui várias validações para impedir ações inválidas, tais como:

* Aceder a páginas protegidas sem login;
* Comprar restaurantes inexistentes;
* Produzir restaurantes que não pertencem ao utilizador;
* Recolher lucro de restaurantes de outro utilizador;
* Evoluir restaurantes de outro utilizador;
* Comprar gestores para restaurantes de outro utilizador;
* Submeter login ou registo com campos vazios.

As passwords são guardadas através de hash, utilizando as funções de segurança do Werkzeug.

---

## Authors

Academic project submitted by:

- Guilherme Monteiro
- António Henriques
- Gonçalo Gouveia

Main implementation and technical integration led by Guilherme Monteiro.

## AI Assistance

AI tools were used as support during the development process, mainly for debugging, code review, documentation improvement and learning assistance. The project was tested, adapted and integrated by the author to ensure understanding and functionality.

