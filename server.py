from flask import Flask
from flask_login import LoginManager
import os
import views
from models.database import Database
from models.user import User


def create_app():
    app = Flask(__name__)
    app.config.from_object("settings")

    # Sets the secret key used by Flask sessions
    app.secret_key = app.config["SECRET_KEY"]

    models_dir = os.path.dirname(os.path.abspath(__file__))
    db = Database(os.path.join(models_dir, "game.db"))
    app.config["db"] = db

    # Makes visual helper functions available inside Jinja templates
    app.jinja_env.globals["format_value"] = views.format_value
    app.jinja_env.globals["business_icon"] = views.business_icon
    app.jinja_env.globals["manager_icon"] = views.manager_icon
    
    # Makes rank icon helper available inside Jinja templates
    app.jinja_env.globals["rank_icon"] = views.rank_icon
    
    # Makes upgrade time helper available inside Jinja templates
    app.jinja_env.globals["upgrade_time"] = views.upgrade_time

    # Configures Flask-Login to manage user sessions
    login_manager = LoginManager()
    login_manager.login_view = "login_page"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # Loads the logged user from the database using the session id
        user = db.get_user_by_id(user_id)

        if user is None:
            return None

        return User(user[0], user[1], user[2])

    app.add_url_rule("/", view_func=views.home_page)
    app.add_url_rule("/dashboard", view_func=views.dashboard_page)

    app.add_url_rule(
        "/buy-business/<int:business_type_id>", view_func=views.buy_business_page
    )
    app.add_url_rule(
        "/finish-building/<int:user_business_id>", view_func=views.finish_building_page
    )
    app.add_url_rule(
        "/start-production/<int:user_business_id>",
        view_func=views.start_production_page,
    )
    app.add_url_rule(
        "/finish-production/<int:user_business_id>",
        view_func=views.finish_production_page,
    )
    app.add_url_rule(
        "/collect-profit/<int:user_business_id>", view_func=views.collect_profit_page
    )
    app.add_url_rule(
        "/upgrade-business/<int:user_business_id>",
        view_func=views.upgrade_business_page,
    )
    app.add_url_rule(
        "/buy-manager/<int:user_business_id>", view_func=views.buy_manager_page
    )
    app.add_url_rule("/managers", view_func=views.managers_page)
    app.add_url_rule(
        "/register", view_func=views.register_page, methods=["GET", "POST"]
    )
    app.add_url_rule("/login", view_func=views.login_page, methods=["GET", "POST"])
    app.add_url_rule("/logout", view_func=views.logout_page)
    app.add_url_rule("/historico", view_func=views.history_page)
    app.add_url_rule("/leaderboard", view_func=views.leaderboard_page)
    app.add_url_rule("/api/leaderboard", view_func=views.leaderboard_api)
    app.add_url_rule("/ranks", view_func=views.ranks_page)
    
    return app


if __name__ == "__main__":
    app = create_app()
    port = app.config.get("PORT", 5000)
    app.run(host="0.0.0.0", port=port)
