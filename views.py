import sqlite3

from flask import (
    render_template,
    current_app,
    redirect,
    url_for,
    request,
    session,
    jsonify,
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User


def set_game_message(message, message_type):
    # Saves a temporary message and its visual type after a game action
    session["game_message"] = message
    session["game_message_type"] = message_type


def get_game_message():
    # Gets and removes the temporary message data from the session
    message = session.pop("game_message", None)
    message_type = session.pop("game_message_type", None)

    return message, message_type


def get_player_rank(db, user_id):
    # Gets the current player rank using total reputation
    user = db.get_user_by_id(user_id)

    return db.get_rank_name(user[5])


def get_new_rank_if_needed(db, user_id, old_rank):
    # Returns the new rank name when the player reaches a higher rank
    new_rank = get_player_rank(db, user_id)

    if new_rank != old_rank:
        return new_rank

    return None

def upgrade_time(business_name, current_level):
    # Calculates the upgrade time shown in the dashboard progress bar
    next_level = current_level + 1

    if business_name == "Banca de Cachorros":
        return 5 * (next_level - 1)

    if business_name == "Café":
        return 10 * (next_level - 1)

    if business_name == "Croissanteria":
        return 15 * (next_level - 1)

    if business_name == "Hamburgueria":
        return 20 * (next_level - 1)

    return 10 * (next_level - 1)

def format_value(value):
    # Formats large numbers to keep the interface cleaner
    value = int(value)

    if value >= 1000000:
        formatted_value = value / 1000000
        return str(round(formatted_value, 2)).rstrip("0").rstrip(".") + "M"

    if value >= 1000:
        formatted_value = value / 1000
        return f"{formatted_value:.1f}k"

    return str(value)


def business_icon(business_name):
    # Returns an emoji icon for each business type
    if business_name == "Banca de Cachorros":
        return "🌭"

    if business_name == "Café":
        return "☕"

    if business_name == "Croissanteria":
        return "🥐"

    if business_name == "Hamburgueria":
        return "🍔"

    return "🍽️"


def manager_icon(manager_name):
    # Returns an emoji icon for each manager
    if manager_name == "Jeff Peso":
        return "💼"

    if manager_name == "Mark Lattenberg":
        return "👔"

    if manager_name == "Elon Saint":
        return "🚀"

    if manager_name == "Warren Burget":
        return "🏦"

    return "🧑‍💼"


def rank_icon(rank_name):
    # Returns an emoji icon for each player rank
    if rank_name == "Lenda Gastronómica":
        return "👑"

    if rank_name == "Mestre da Restauração":
        return "🏆"

    if rank_name == "Magnata da Restauração":
        return "💎"

    if rank_name == "Gestor de Restaurantes":
        return "🍽️"

    if rank_name == "Mestre da Tasca":
        return "🍻"

    if rank_name == "Dono da Banca":
        return "🌭"

    return "🚀"


def home_page():
    return "My Restaurant Adventure"


@login_required
def dashboard_page():
    db = current_app.config["db"]

    user_id = current_user.id

    # Updates finished buildings and productions before showing the dashboard
    db.update_business_states(user_id)

    user = db.get_user_by_id(user_id)
    # Gets the current player rank based on total reputation
    rank_name = db.get_rank_name(user[5])
    businesses = db.get_user_businesses(user_id)
    all_business_types = db.get_business_types()

    owned_business_type_ids = []

    for business in businesses:
        owned_business_type_ids.append(business[2])

    business_types = []

    for business_type in all_business_types:
        if business_type[0] not in owned_business_type_ids:
            business_types.append(business_type)

    # Gets the temporary message and type to show on the dashboard
    game_message, game_message_type = get_game_message()

    return render_template(
        "dashboard.html",
        user=user,
        businesses=businesses,
        business_types=business_types,
        game_message=game_message,
        game_message_type=game_message_type,
        rank_name=rank_name,
    )


@login_required
def buy_business_page(business_type_id):
    db = current_app.config["db"]
    user_id = current_user.id

    # Saves the old rank before adding reputation
    old_rank = get_player_rank(db, user_id)

    # Tries to buy a new business for the logged user
    success = db.buy_business(user_id, business_type_id)

    if success:
        # Checks if the player reached a new rank after buying the business
        new_rank = get_new_rank_if_needed(db, user_id, old_rank)

        if new_rank is not None:
            set_game_message(
                "Negócio comprado com sucesso. Novo rank desbloqueado: "
                + new_rank
                + "!",
                "success",
            )
        else:
            set_game_message("Negócio comprado com sucesso.", "success")
    else:
        set_game_message("Dinheiro insuficiente para comprar este negócio.", "error")

    return redirect(url_for("dashboard_page"))


@login_required
def finish_building_page(user_business_id):
    db = current_app.config["db"]

    if not protect_business_action(user_business_id):
        # Sends the user to login if the action is not allowed
        return redirect(url_for("login_page"))

    # Tries to finish the selected business construction
    success = db.finish_building(user_business_id)

    if success:
        set_game_message("Construção terminada.")
    else:
        set_game_message("Não foi possível terminar esta construção.")

    return redirect(url_for("dashboard_page"))


@login_required
def start_production_page(user_business_id):
    db = current_app.config["db"]

    if not protect_business_action(user_business_id):
        # Sends the user to dashboard if the action is not allowed
        return redirect(url_for("dashboard_page"))

    # Starts production without showing a message to avoid visual spam
    db.start_production(user_business_id)

    return redirect(url_for("dashboard_page"))


@login_required
def finish_production_page(user_business_id):
    db = current_app.config["db"]

    if not protect_business_action(user_business_id):
        # Sends the user to login if the action is not allowed
        return redirect(url_for("login_page"))

    # Tries to finish the selected business production
    success = db.finish_production(user_business_id)

    if success:
        set_game_message("Produção terminada.")
    else:
        set_game_message("Não foi possível terminar esta produção.")

    return redirect(url_for("dashboard_page"))


@login_required
def collect_profit_page(user_business_id):
    db = current_app.config["db"]

    if not protect_business_action(user_business_id):
        # Sends the user to dashboard if the action is not allowed
        return redirect(url_for("dashboard_page"))

    # Collects profit without showing a message to avoid visual spam
    db.collect_profit(user_business_id)

    return redirect(url_for("dashboard_page"))


@login_required
def upgrade_business_page(user_business_id):
    db = current_app.config["db"]

    if not protect_business_action(user_business_id):
        # Sends the user to dashboard if the action is not allowed
        return redirect(url_for("dashboard_page"))

    user_id = current_user.id

    # Saves the old rank before adding reputation
    old_rank = get_player_rank(db, user_id)

    # Tries to upgrade the selected business
    success = db.upgrade_business(user_business_id)

    if success:
        # Checks if the player reached a new rank after upgrading the business
        new_rank = get_new_rank_if_needed(db, user_id, old_rank)

        if new_rank is not None:
            set_game_message(
                "Negócio evoluído com sucesso. Novo rank desbloqueado: "
                + new_rank
                + "!",
                "success",
            )
        else:
            set_game_message("Negócio evoluído com sucesso.", "success")
    else:
        set_game_message("Dinheiro insuficiente ou nível máximo atingido.", "error")

    return redirect(url_for("dashboard_page"))


@login_required
def buy_manager_page(user_business_id):
    db = current_app.config["db"]

    if not protect_business_action(user_business_id):
        # Sends the user to managers if the action is not allowed
        return redirect(url_for("managers_page"))

    # Tries to buy a manager for the selected business
    success = db.buy_manager(user_business_id)

    if success:
        set_game_message("Gestor contratado com sucesso.", "success")
    else:
        set_game_message(
            "Dinheiro ou reputação insuficiente para contratar este gestor.", "error"
        )

    return redirect(url_for("managers_page"))


# Managers Page
@login_required
def managers_page():
    db = current_app.config["db"]

    user_id = current_user.id

    # Updates the game state before showing the managers page
    db.update_business_states(user_id)

    user = db.get_user_by_id(user_id)
    # Gets the current player rank based on total reputation
    rank_name = db.get_rank_name(user[5])
    user_businesses = db.get_user_businesses(user_id)
    business_types = db.get_business_types()

    managers = []

    for business_type in business_types:
        user_business = None

        for business in user_businesses:
            if business[2] == business_type[0]:
                user_business = business

        money_cost = business_type[9]
        reputation_cost = business_type[10]

        manager = {
            "business_name": business_type[1],
            "manager_name": business_type[8],
            "manager_money_cost": money_cost,
            "manager_rep_cost": reputation_cost,
            "is_business_unlocked": user_business is not None,
            "user_business_id": None,
            "has_manager": False,
            "can_buy": False,
            "missing_message": "",
        }

        if user_business is not None:
            manager["user_business_id"] = user_business[0]
            manager["has_manager"] = user_business[5] == 1

            has_enough_money = user[3] >= money_cost
            has_enough_reputation = user[4] >= reputation_cost

            if has_enough_money and has_enough_reputation:
                manager["can_buy"] = True

            elif not has_enough_money and not has_enough_reputation:
                manager["missing_message"] = "Dinheiro e reputação insuficientes"

            elif not has_enough_money:
                manager["missing_message"] = "Dinheiro insuficiente"

            elif not has_enough_reputation:
                manager["missing_message"] = "Reputação insuficiente"

        managers.append(manager)

    # Gets the temporary message and type to show on the managers page
    game_message, game_message_type = get_game_message()

    return render_template(
        "managers.html",
        user=user,
        managers=managers,
        game_message=game_message,
        game_message_type=game_message_type,
        rank_name=rank_name,
    )


def register_page():
    db = current_app.config["db"]

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Creates a secure hash so the plain password is not stored in the database
        password_hash = generate_password_hash(password)

        try:
            # Creates a new player account in the database
            db.create_user(username, email, password_hash)

            return redirect(url_for("login_page"))

        except sqlite3.IntegrityError:
            # Shows an error when the username or email already exists
            return render_template(
                "register.html", error="Esse username ou email já está registado."
            )

    return render_template("register.html", error=None)


def login_page():
    db = current_app.config["db"]

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Gets the user from the database using the username written in the form
        user = db.get_user_by_username(username)

        if user is not None:
            password_hash = user[3]

            # Checks if the written password matches the stored password hash
            if check_password_hash(password_hash, password):
                logged_user = User(user[0], user[1], user[2])

                # Logs the player in using Flask-Login
                login_user(logged_user)

                return redirect(url_for("dashboard_page"))

        return render_template("login.html", error="Login inválido.")

    return render_template("login.html", error=None)


def logout_page():
    # Logs out the current player using Flask-Login
    logout_user()

    return redirect(url_for("login_page"))


def protect_business_action(user_business_id):
    db = current_app.config["db"]

    if not current_user.is_authenticated:
        # Blocks the action when there is no logged user
        return False

    user_id = current_user.id

    # Checks if the selected business belongs to the logged user
    if not db.user_owns_business(user_id, user_business_id):
        return False

    return True


@login_required
def history_page():
    db = current_app.config["db"]

    user_id = current_user.id

    # Gets the logged user and the most recent game actions
    user = db.get_user_by_id(user_id)
    # Gets the current player rank based on total reputation
    rank_name = db.get_rank_name(user[5])
    history = db.get_user_history(user_id)

    return render_template(
        "history.html",
        user=user,
        history=history,
        rank_name=rank_name,
    )


# Leaderboard Update
@login_required
def leaderboard_page():
    db = current_app.config["db"]
    user_id = current_user.id

    # Gets the logged user to show player information in the sidebar
    user = db.get_user_by_id(user_id)
    # Gets the current player rank based on total reputation
    rank_name = db.get_rank_name(user[5])

    return render_template(
        "leaderboard.html",
        user=user,
        rank_name=rank_name,
    )


@login_required
def leaderboard_api():
    db = current_app.config["db"]

    # Gets ranking data that will be requested by JavaScript Fetch API
    leaderboard = db.get_leaderboard()

    data = []
    position = 1

    for player in leaderboard:
        rank_name = db.get_rank_name(player[2])

        data.append(
            {
                "position": position,
                "username": player[0],
                "total_earned": player[1],
                "rank_name": rank_name,
                "rank_icon": rank_icon(rank_name),
            }
        )

        position = position + 1

    return jsonify(data)


# Ranks Update
@login_required
def ranks_page():
    db = current_app.config["db"]
    user_id = current_user.id

    # Gets the logged user and all available ranks
    user = db.get_user_by_id(user_id)
    rank_name = db.get_rank_name(user[5])
    ranks = db.get_ranks()

    return render_template("ranks.html", user=user, rank_name=rank_name, ranks=ranks)
