# API Documentation — My Restaurant Adventure

## Introduction

This document describes the main backend routes available in the **My Restaurant Adventure** Flask application.

The application uses traditional Flask routes for navigation and game actions, and also includes a JSON API route used by the frontend through the Fetch API.

---

# Leaderboard API

## GET /api/leaderboard

### Description

Returns the Top 10 players in the application, ordered by the total amount of money earned since account creation.

This route is used by JavaScript through the Fetch API to update the leaderboard without requiring a full manual page reload.

### Authentication

This route requires the user to be authenticated.

### Method

```http
GET /api/leaderboard
```

### Parameters

This route does not receive any parameters.

### Successful Response

HTTP status code:

```http
200 OK
```

### Response Example

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

### Response Fields

| Field        | Type    | Description                                |
| ------------ | ------- | ------------------------------------------ |
| position     | Integer | Player position in the leaderboard         |
| username     | String  | Player username                            |
| total_earned | Integer | Total amount of money earned by the player |
| rank_name    | String  | Current rank name of the player            |
| rank_icon    | String  | Emoji associated with the player's rank    |

---

# Application Routes

## GET /

### Description

Simple initial route of the application.

---

## GET /login

### Description

Displays the login form.

---

## POST /login

### Description

Authenticates an existing user.

### Form Data

| Field    | Type   | Description   |
| -------- | ------ | ------------- |
| username | String | User username |
| password | String | User password |

---

## GET /register

### Description

Displays the registration form.

---

## POST /register

### Description

Creates a new user account.

### Form Data

| Field    | Type   | Description   |
| -------- | ------ | ------------- |
| username | String | User username |
| email    | String | User email    |
| password | String | User password |

---

## GET /logout

### Description

Logs out the currently authenticated user.

---

## GET /dashboard

### Description

Displays the main game dashboard.

On this page, the player can view current resources, purchased restaurants, locked restaurants, production states, progress bars and available actions.

### Authentication

Requires login.

---

## GET /buy-business/<int:business_type_id>

### Description

Buys a new restaurant if the player has enough money and has not already purchased that restaurant type.

### Authentication

Requires login.

### Parameters

| Name             | Type    | Description                                   |
| ---------------- | ------- | --------------------------------------------- |
| business_type_id | Integer | Identifier of the restaurant type to purchase |

### Result

After the action is completed, the user is redirected to the dashboard.

---

## GET /finish-building/<int:user_business_id>

### Description

Finishes the construction of a restaurant purchased by the player.

This route exists as part of the game logic control, although restaurant states are also updated automatically when the dashboard is loaded.

### Authentication

Requires login.

### Parameters

| Name             | Type    | Description                           |
| ---------------- | ------- | ------------------------------------- |
| user_business_id | Integer | Identifier of the player's restaurant |

---

## GET /start-production/<int:user_business_id>

### Description

Starts production for a restaurant owned by the authenticated user.

Production can only be started when the restaurant is in the `ready` state.

### Authentication

Requires login.

### Parameters

| Name             | Type    | Description                           |
| ---------------- | ------- | ------------------------------------- |
| user_business_id | Integer | Identifier of the player's restaurant |

---

## GET /finish-production/<int:user_business_id>

### Description

Finishes the production process of a restaurant.

This route exists as part of the game logic control, although production completion is also updated automatically when the dashboard is loaded.

### Authentication

Requires login.

### Parameters

| Name             | Type    | Description                           |
| ---------------- | ------- | ------------------------------------- |
| user_business_id | Integer | Identifier of the player's restaurant |

---

## GET /collect-profit/<int:user_business_id>

### Description

Collects the profit produced by a restaurant owned by the authenticated user.

If the restaurant has a hired manager, production automatically restarts after the player collects the profit.

### Authentication

Requires login.

### Parameters

| Name             | Type    | Description                           |
| ---------------- | ------- | ------------------------------------- |
| user_business_id | Integer | Identifier of the player's restaurant |

---

## GET /upgrade-business/<int:user_business_id>

### Description

Starts an upgrade for a restaurant, moving it towards the next level.

An upgrade can only be started if the restaurant belongs to the authenticated user, has not reached the maximum level and the player has enough money.

### Authentication

Requires login.

### Parameters

| Name             | Type    | Description                           |
| ---------------- | ------- | ------------------------------------- |
| user_business_id | Integer | Identifier of the player's restaurant |

---

## GET /managers

### Description

Displays the available managers page.

On this page, the player can view the managers associated with each restaurant, their costs and whether they are locked, available or already hired.

### Authentication

Requires login.

---

## GET /buy-manager/<int:user_business_id>

### Description

Buys a manager for a restaurant owned by the authenticated user.

The manager automatically restarts production after profit collection.

### Authentication

Requires login.

### Parameters

| Name             | Type    | Description                                                  |
| ---------------- | ------- | ------------------------------------------------------------ |
| user_business_id | Integer | Identifier of the restaurant where the manager will be hired |

---

## GET /leaderboard

### Description

Displays the visual leaderboard page.

The data displayed on this page is loaded through the following API route:

```http
GET /api/leaderboard
```

### Authentication

Requires login.

---

## GET /ranks

### Description

Displays all available ranks and highlights the player's current rank.

### Authentication

Requires login.

---

## GET /historico

### Description

Displays the most recent actions performed by the authenticated user.

### Authentication

Requires login.

---

# Technologies Used

* Flask;
* Flask-Login;
* SQLite;
* HTML;
* CSS;
* JavaScript;
* Fetch API.

---

# Technical Notes

* The application uses Flask to define backend routes.
* Authentication is handled with Flask-Login.
* The database used by the project is SQLite.
* The leaderboard uses the Fetch API to request JSON data from the backend.
* The main game actions redirect the user to the corresponding page after execution.
* Routes that receive identifiers use integer route parameters, for example: `<int:user_business_id>`.
* Most game actions are implemented as traditional Flask routes with redirects, while `/api/leaderboard` is implemented as a JSON API route.
