# api_documentacao.md — My Restaurant Adventure

## Introdução

Este documento descreve as principais rotas disponibilizadas pelo backend Flask da aplicação **My Restaurant Adventure**.

A aplicação utiliza rotas Flask tradicionais para navegação e ações do jogo, e inclui também uma rota API em JSON utilizada pelo frontend através da Fetch API.

---

# API da Leaderboard

## GET /api/leaderboard

### Descrição

Devolve o Top 10 jogadores da aplicação, ordenados pelo total de dinheiro acumulado desde o início da conta.

Esta rota é utilizada pelo JavaScript através da Fetch API para atualizar a leaderboard sem necessidade de recarregar manualmente a página.

### Autenticação

Esta rota requer que o utilizador esteja autenticado.

### Método

```http
GET /api/leaderboard
```

### Parâmetros

Não recebe parâmetros.

### Resposta de Sucesso

Código HTTP:

```http
200 OK
```

### Exemplo de Resposta

```json
[
  {
    "position": 1,
    "username": "Teste01",
    "total_earned": 6300,
    "rank_name": "Dono da Banca",
    "rank_icon": "🌭"
  },
  {
    "position": 2,
    "username": "Teste02",
    "total_earned": 2200,
    "rank_name": "Empreendedor",
    "rank_icon": "🚀"
  }
]
```

### Campos da Resposta

| Campo        | Tipo    | Descrição                                |
| ------------ | ------- | ---------------------------------------- |
| position     | Integer | Posição do jogador na leaderboard        |
| username     | String  | Nome do jogador                          |
| total_earned | Integer | Total de dinheiro acumulado pelo jogador |
| rank_name    | String  | Nome do rank atual do jogador            |
| rank_icon    | String  | Emoji associado ao rank do jogador       |

---

# Rotas da Aplicação

## GET /

### Descrição

Página inicial simples da aplicação.

---

## GET /login

### Descrição

Apresenta o formulário de login.

---

## POST /login

### Descrição

Autentica um utilizador existente.

### Dados do Formulário

| Campo    | Tipo   | Descrição                   |
| -------- | ------ | --------------------------- |
| username | String | Nome de utilizador          |
| password | String | Palavra-passe do utilizador |

---

## GET /register

### Descrição

Apresenta o formulário de registo.

---

## POST /register

### Descrição

Cria uma nova conta de utilizador.

### Dados do Formulário

| Campo    | Tipo   | Descrição                   |
| -------- | ------ | --------------------------- |
| username | String | Nome de utilizador          |
| email    | String | Email do utilizador         |
| password | String | Palavra-passe do utilizador |

---

## GET /logout

### Descrição

Termina a sessão do utilizador autenticado.

---

## GET /dashboard

### Descrição

Apresenta o dashboard principal do jogo.

Nesta página, o jogador pode consultar os seus recursos, restaurantes comprados, restaurantes bloqueados, estados de produção, barras de progresso e ações disponíveis.

### Autenticação

Requer login.

---

## GET /buy-business/<int:business_type_id>

### Descrição

Compra um novo restaurante, caso o jogador tenha dinheiro suficiente e ainda não tenha comprado esse tipo de restaurante.

### Autenticação

Requer login.

### Parâmetros

| Nome             | Tipo    | Descrição                                      |
| ---------------- | ------- | ---------------------------------------------- |
| business_type_id | Integer | Identificador do tipo de restaurante a comprar |

### Resultado

Depois da ação, o utilizador é redirecionado para o dashboard.

---

## GET /finish-building/<int:user_business_id>

### Descrição

Finaliza a construção de um restaurante comprado pelo jogador.

Esta rota existe para controlo da lógica do jogo, embora os estados também sejam atualizados automaticamente quando o dashboard é carregado.

### Autenticação

Requer login.

### Parâmetros

| Nome             | Tipo    | Descrição                                  |
| ---------------- | ------- | ------------------------------------------ |
| user_business_id | Integer | Identificador do restaurante do utilizador |

---

## GET /start-production/<int:user_business_id>

### Descrição

Inicia a produção de um restaurante pertencente ao utilizador autenticado.

A produção só pode ser iniciada quando o restaurante está no estado `ready`.

### Autenticação

Requer login.

### Parâmetros

| Nome             | Tipo    | Descrição                                  |
| ---------------- | ------- | ------------------------------------------ |
| user_business_id | Integer | Identificador do restaurante do utilizador |

---

## GET /finish-production/<int:user_business_id>

### Descrição

Finaliza a produção de um restaurante.

Esta rota existe para controlo da lógica do jogo, embora a conclusão da produção também seja atualizada automaticamente quando o dashboard é carregado.

### Autenticação

Requer login.

### Parâmetros

| Nome             | Tipo    | Descrição                                  |
| ---------------- | ------- | ------------------------------------------ |
| user_business_id | Integer | Identificador do restaurante do utilizador |

---

## GET /collect-profit/<int:user_business_id>

### Descrição

Recolhe o lucro produzido por um restaurante pertencente ao utilizador autenticado.

Se o restaurante tiver gestor contratado, a produção volta a iniciar automaticamente depois da recolha do lucro.

### Autenticação

Requer login.

### Parâmetros

| Nome             | Tipo    | Descrição                                  |
| ---------------- | ------- | ------------------------------------------ |
| user_business_id | Integer | Identificador do restaurante do utilizador |

---

## GET /upgrade-business/<int:user_business_id>

### Descrição

Inicia a evolução de um restaurante para o nível seguinte.

A evolução só pode ser iniciada se o restaurante pertencer ao utilizador, se ainda não estiver no nível máximo e se o jogador tiver dinheiro suficiente.

### Autenticação

Requer login.

### Parâmetros

| Nome             | Tipo    | Descrição                                  |
| ---------------- | ------- | ------------------------------------------ |
| user_business_id | Integer | Identificador do restaurante do utilizador |

---

## GET /managers

### Descrição

Apresenta a página dos gestores disponíveis.

Nesta página, o jogador pode ver os gestores associados a cada restaurante, os respetivos custos e se estão bloqueados, disponíveis ou já adquiridos.

### Autenticação

Requer login.

---

## GET /buy-manager/<int:user_business_id>

### Descrição

Compra um gestor para um restaurante pertencente ao utilizador autenticado.

O gestor automatiza o reinício da produção após a recolha do lucro.

### Autenticação

Requer login.

### Parâmetros

| Nome             | Tipo    | Descrição                                                  |
| ---------------- | ------- | ---------------------------------------------------------- |
| user_business_id | Integer | Identificador do restaurante onde o gestor será contratado |

---

## GET /leaderboard

### Descrição

Apresenta a página visual da leaderboard.

Os dados são carregados através da rota:

```http
GET /api/leaderboard
```

### Autenticação

Requer login.

---

## GET /ranks

### Descrição

Apresenta a página com todos os ranks disponíveis e destaca o rank atual do jogador.

### Autenticação

Requer login.

---

## GET /historico

### Descrição

Apresenta o histórico das ações mais recentes do utilizador.

### Autenticação

Requer login.

---

# Tecnologias Utilizadas

* Flask;
* Flask-Login;
* SQLite;
* HTML;
* CSS;
* JavaScript;
* Fetch API.

---

# Notas Técnicas

* A aplicação utiliza Flask para definir as rotas do backend.
* A autenticação é feita com Flask-Login.
* A base de dados utilizada é SQLite.
* A leaderboard utiliza Fetch API para obter dados em JSON.
* As ações principais do jogo redirecionam o utilizador para a página correspondente depois de executadas.
* As rotas que recebem identificadores utilizam parâmetros inteiros, por exemplo: `<int:user_business_id>`.

