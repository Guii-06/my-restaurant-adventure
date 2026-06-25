import sqlite3 as dbapi2
from datetime import datetime, timedelta


class Database:
    def __init__(self, dbfile):
        self.dbfile = dbfile
        self.create_tables()
        self.create_business_types()

    def create_tables(self):
        # Creates the database tables used by the game
        with dbapi2.connect(self.dbfile, timeout=10) as connection:
            cursor = connection.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS USER (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    USERNAME TEXT UNIQUE NOT NULL,
                    EMAIL TEXT UNIQUE NOT NULL,
                    PASSWORD_HASH TEXT NOT NULL,
                    MONEY INTEGER NOT NULL,
                    REPUTATION INTEGER NOT NULL,
                    TOTAL_EARNED INTEGER NOT NULL DEFAULT 0,
                    TOTAL_REPUTATION INTEGER NOT NULL DEFAULT 0
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS BUSINESS_TYPE (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    NAME TEXT UNIQUE NOT NULL,
                    INITIAL_COST INTEGER NOT NULL,
                    BUILD_TIME INTEGER NOT NULL,
                    PRODUCTION_TIME INTEGER NOT NULL,
                    BASE_PROFIT INTEGER NOT NULL,
                    REPUTATION_BUY INTEGER NOT NULL,
                    REPUTATION_UPGRADE INTEGER NOT NULL,
                    MANAGER_NAME TEXT NOT NULL,
                    MANAGER_MONEY_COST INTEGER NOT NULL,
                    MANAGER_REP_COST INTEGER NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS USER_BUSINESS (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    USER_ID INTEGER NOT NULL,
                    BUSINESS_TYPE_ID INTEGER NOT NULL,
                    LEVEL INTEGER NOT NULL,
                    STATE TEXT NOT NULL,
                    HAS_MANAGER INTEGER NOT NULL,
                    BUILD_FINISH_TIME TEXT,
                    PRODUCTION_FINISH_TIME TEXT,
                    UPGRADE_FINISH_TIME TEXT,
                    FOREIGN KEY (USER_ID) REFERENCES USER(ID),
                    FOREIGN KEY (BUSINESS_TYPE_ID) REFERENCES BUSINESS_TYPE(ID)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ACTION_HISTORY (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    USER_ID INTEGER NOT NULL,
                    MESSAGE TEXT NOT NULL,
                    CREATED_AT TEXT NOT NULL,
                    FOREIGN KEY (USER_ID) REFERENCES USER(ID)
                )
            """)

            try:
                # Adds the total earned column to databases created before the leaderboard update
                cursor.execute("""
                    ALTER TABLE USER
                    ADD COLUMN TOTAL_EARNED INTEGER NOT NULL DEFAULT 0
                """)
            except dbapi2.OperationalError:
                pass

            try:
                # Adds total reputation to databases created before the rank system
                cursor.execute("""
                    ALTER TABLE USER
                    ADD COLUMN TOTAL_REPUTATION INTEGER NOT NULL DEFAULT 0
                """)
            except dbapi2.OperationalError:
                pass

            try:
                # Adds the upgrade finish time column to databases created before the progession bar update
                cursor.execute("""
                    ALTER TABLE USER_BUSINESS
                    ADD COLUMN UPGRADE_FINISH_TIME TEXT
                """)
            except dbapi2.OperationalError:
                pass

            connection.commit()

    def create_business_types(self):
        # Inserts or updates the fixed restaurant types used by the game
        with dbapi2.connect(self.dbfile, timeout=10) as connection:
            cursor = connection.cursor()

            business_types = [
                ("Banca de Cachorros", 250, 10, 1, 25, 1, 1, "Jeff Peso", 2500, 5),
                ("Café", 1000, 30, 3, 150, 2, 2, "Mark Lattenberg", 12000, 12),
                ("Croissanteria", 5000, 60, 5, 800, 4, 4, "Elon Saint", 60000, 25),
                ("Hamburgueria", 20000, 90, 8, 3500, 8, 6, "Warren Burget", 250000, 50),
            ]

            for business in business_types:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO BUSINESS_TYPE
                    (NAME, INITIAL_COST, BUILD_TIME, PRODUCTION_TIME, BASE_PROFIT,
                    REPUTATION_BUY, REPUTATION_UPGRADE, MANAGER_NAME,
                    MANAGER_MONEY_COST, MANAGER_REP_COST)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    business,
                )

                # Updates construction time if the business already exists
                cursor.execute(
                    """
                    UPDATE BUSINESS_TYPE
                    SET BUILD_TIME = ?
                    WHERE NAME = ?
                """,
                    (business[2], business[0]),
                )

            connection.commit()

    def get_business_types(self):
        business_types = []

        with dbapi2.connect(self.dbfile, timeout=10) as connection:
            cursor = connection.cursor()

            query = """
                SELECT ID, NAME, INITIAL_COST, BUILD_TIME, PRODUCTION_TIME,
                       BASE_PROFIT, REPUTATION_BUY, REPUTATION_UPGRADE,
                       MANAGER_NAME, MANAGER_MONEY_COST, MANAGER_REP_COST
                FROM BUSINESS_TYPE
                ORDER BY ID
            """

            cursor.execute(query)

            for row in cursor:
                business_types.append(row)

        return business_types

    def create_user(self, username, email, password_hash):
        # Creates a new player with initial resources and progress counters
        with dbapi2.connect(self.dbfile, timeout=10) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO USER (
                    USERNAME,
                    EMAIL,
                    PASSWORD_HASH,
                    MONEY,
                    REPUTATION,
                    TOTAL_EARNED,
                    TOTAL_REPUTATION
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (username, email, password_hash, 500, 0, 0, 0),
            )

            connection.commit()

            return cursor.lastrowid

    def get_user_by_username(self, username):
        with dbapi2.connect(self.dbfile, timeout=10) as connection:
            cursor = connection.cursor()

            query = """
                SELECT ID, USERNAME, EMAIL, PASSWORD_HASH, MONEY, REPUTATION
                FROM USER
                WHERE USERNAME = ?
            """

            cursor.execute(query, (username,))

            row = cursor.fetchone()

            return row

    def buy_business(self, user_id, business_type_id):
        with dbapi2.connect(self.dbfile, timeout=10) as connection:
            cursor = connection.cursor()

            # Gets the business information needed to buy it
            cursor.execute(
                """
                SELECT NAME, INITIAL_COST, REPUTATION_BUY, BUILD_TIME
                FROM BUSINESS_TYPE
                WHERE ID = ?
            """,
                (business_type_id,),
            )

            business = cursor.fetchone()

            if business is None:
                return False

            # Stores the selected business data in variables
            business_name = business[0]
            initial_cost = business[1]
            reputation_buy = business[2]
            build_time = business[3]

            # Buscar dinheiro do utilizador
            cursor.execute(
                """
                SELECT MONEY, REPUTATION
                FROM USER
                WHERE ID = ?
            """,
                (user_id,),
            )

            user = cursor.fetchone()

            if user is None:
                return False

            money = user[0]
            reputation = user[1]

            # Verificar se tem dinheiro suficiente
            if money < initial_cost:
                return False

            # Removes money and adds reputation when the player buys a business
            cursor.execute(
                """
                UPDATE USER
                SET MONEY = MONEY - ?,
                    REPUTATION = REPUTATION + ?,
                    TOTAL_REPUTATION = TOTAL_REPUTATION + ?
                WHERE ID = ?
            """,
                (initial_cost, reputation_buy, reputation_buy, user_id),
            )

            cursor.execute(
                """
                SELECT ID
                FROM USER_BUSINESS
                WHERE USER_ID = ? AND BUSINESS_TYPE_ID = ?
            """,
                (user_id, business_type_id),
            )

            existing_business = cursor.fetchone()

            if existing_business is not None:
                return False

            # Criar negócio do utilizador
            build_finish_time = datetime.now() + timedelta(seconds=build_time)
            cursor.execute(
                """
                INSERT INTO USER_BUSINESS
                (USER_ID, BUSINESS_TYPE_ID, LEVEL, STATE, HAS_MANAGER,
                 BUILD_FINISH_TIME, PRODUCTION_FINISH_TIME)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    user_id,
                    business_type_id,
                    1,
                    "building",
                    0,
                    build_finish_time.isoformat(),
                    None,
                ),
            )
            # Saves the business purchase in the player history
            cursor.execute(
                """
                INSERT INTO ACTION_HISTORY (USER_ID, MESSAGE, CREATED_AT)
                VALUES (?, ?, ?)
            """,
                (
                    user_id,
                    "Comprou " + business_name,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )

            connection.commit()

            return True

    def get_user_businesses(self, user_id):
        # Gets all businesses owned by a player with their business type data
        user_businesses = []

        with dbapi2.connect(self.dbfile, timeout=10) as connection:
            cursor = connection.cursor()

            query = """
                SELECT 
                    USER_BUSINESS.ID,
                    USER_BUSINESS.USER_ID,
                    USER_BUSINESS.BUSINESS_TYPE_ID,
                    USER_BUSINESS.LEVEL,
                    USER_BUSINESS.STATE,
                    USER_BUSINESS.HAS_MANAGER,
                    USER_BUSINESS.BUILD_FINISH_TIME,
                    USER_BUSINESS.PRODUCTION_FINISH_TIME,
                    USER_BUSINESS.UPGRADE_FINISH_TIME,
                    BUSINESS_TYPE.NAME,
                    BUSINESS_TYPE.INITIAL_COST,
                    BUSINESS_TYPE.BUILD_TIME,
                    BUSINESS_TYPE.PRODUCTION_TIME,
                    BUSINESS_TYPE.BASE_PROFIT,
                    BUSINESS_TYPE.REPUTATION_BUY,
                    BUSINESS_TYPE.REPUTATION_UPGRADE,
                    BUSINESS_TYPE.MANAGER_NAME,
                    BUSINESS_TYPE.MANAGER_MONEY_COST,
                    BUSINESS_TYPE.MANAGER_REP_COST
                FROM USER_BUSINESS
                JOIN BUSINESS_TYPE
                ON USER_BUSINESS.BUSINESS_TYPE_ID = BUSINESS_TYPE.ID
                WHERE USER_BUSINESS.USER_ID = ?
                ORDER BY BUSINESS_TYPE.ID
            """

            cursor.execute(query, (user_id,))

            for row in cursor:
                user_businesses.append(row)

        return user_businesses

    def finish_building(self, user_business_id):
        with dbapi2.connect(self.dbfile, timeout=10) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT STATE
                FROM USER_BUSINESS
                WHERE ID = ?
            """,
                (user_business_id,),
            )

            user_business = cursor.fetchone()

            if user_business is None:
                return False

            state = user_business[0]

            if state != "building":
                return False

            cursor.execute(
                """
                UPDATE USER_BUSINESS
                SET STATE = ?
                WHERE ID = ?
            """,
                ("ready", user_business_id),
            )

            connection.commit()

            return True

    def start_production(self, user_business_id):
        with dbapi2.connect(self.dbfile, timeout=10) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT USER_BUSINESS.STATE, BUSINESS_TYPE.PRODUCTION_TIME
                FROM USER_BUSINESS
                JOIN BUSINESS_TYPE
                ON USER_BUSINESS.BUSINESS_TYPE_ID = BUSINESS_TYPE.ID
                WHERE USER_BUSINESS.ID = ?
            """,
                (user_business_id,),
            )

            result = cursor.fetchone()

            if result is None:
                return False

            state = result[0]
            production_time = result[1]

            if state != "ready":
                return False

            production_finish_time = datetime.now() + timedelta(seconds=production_time)

            cursor.execute(
                """
                UPDATE USER_BUSINESS
                SET STATE = ?, PRODUCTION_FINISH_TIME = ?
                WHERE ID = ?
            """,
                ("producing", production_finish_time.isoformat(), user_business_id),
            )

        connection.commit()

        return True

    def finish_production(self, user_business_id):
        with dbapi2.connect(self.dbfile, timeout=10) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT STATE
                FROM USER_BUSINESS
                WHERE ID = ?
            """,
                (user_business_id,),
            )

            user_business = cursor.fetchone()

            if user_business is None:
                return False

            state = user_business[0]

            if state != "producing":
                return False

            cursor.execute(
                """
                UPDATE USER_BUSINESS
                SET STATE = ?
                WHERE ID = ?
            """,
                ("completed", user_business_id),
            )

            connection.commit()

            return True

    def collect_profit(self, user_business_id):
        with dbapi2.connect(self.dbfile, timeout=10) as connection:
            cursor = connection.cursor()

            # Gets the business data needed to calculate profit and check manager automation
            cursor.execute(
                """
                SELECT USER_BUSINESS.USER_ID,
                    USER_BUSINESS.LEVEL,
                    USER_BUSINESS.STATE,
                    USER_BUSINESS.HAS_MANAGER,
                    BUSINESS_TYPE.BASE_PROFIT,
                    BUSINESS_TYPE.PRODUCTION_TIME
                FROM USER_BUSINESS
                JOIN BUSINESS_TYPE
                ON USER_BUSINESS.BUSINESS_TYPE_ID = BUSINESS_TYPE.ID
                WHERE USER_BUSINESS.ID = ?
            """,
                (user_business_id,),
            ),

            result = cursor.fetchone()

            if result is None:
                return False

            # Stores each selected value in a variable to make the game logic easier to read
            user_id = result[0]
            level = result[1]
            state = result[2]
            has_manager = result[3]
            base_profit = result[4]
            production_time = result[5]

            if state != "completed":
                return False

            profit = base_profit * (2 ** (level - 1))

            # Adds the collected profit to the player's money and lifetime earnings
            cursor.execute(
                """
                UPDATE USER
                SET MONEY = MONEY + ?,
                    TOTAL_EARNED = TOTAL_EARNED + ?
                WHERE ID = ?
            """,
                (profit, profit, user_id),
            )

            # If the business has a manager, production starts again automatically after collecting profit
            if has_manager == 1:
                production_finish_time = datetime.now() + timedelta(
                    seconds=production_time
                )

                cursor.execute(
                    """
                    UPDATE USER_BUSINESS
                    SET STATE = ?, PRODUCTION_FINISH_TIME = ?
                    WHERE ID = ?
                """,
                    ("producing", production_finish_time.isoformat(), user_business_id),
                )

            else:
                cursor.execute(
                    """
                    UPDATE USER_BUSINESS
                    SET STATE = ?, PRODUCTION_FINISH_TIME = ?
                    WHERE ID = ?
                """,
                    ("ready", None, user_business_id),
                )

                # Saves the collected profit with a formatted money value
                cursor.execute(
                    """
                    INSERT INTO ACTION_HISTORY (USER_ID, MESSAGE, CREATED_AT)
                    VALUES (?, ?, ?)
                """,
                    (
                        user_id,
                        "💰 Recolheu " + self.format_history_money(profit),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ),
                )

            connection.commit()

            return True

    def upgrade_business(self, user_business_id):
        # Starts a timed upgrade if the player has enough money and the business can evolve
        with dbapi2.connect(self.dbfile, timeout=10) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT USER_BUSINESS.USER_ID,
                    USER_BUSINESS.LEVEL,
                    USER_BUSINESS.STATE,
                    BUSINESS_TYPE.INITIAL_COST,
                    BUSINESS_TYPE.BUILD_TIME,
                    BUSINESS_TYPE.REPUTATION_UPGRADE,
                    BUSINESS_TYPE.NAME,
                    BUSINESS_TYPE.BASE_PROFIT,
                    USER.MONEY
                FROM USER_BUSINESS
                JOIN BUSINESS_TYPE
                ON USER_BUSINESS.BUSINESS_TYPE_ID = BUSINESS_TYPE.ID
                JOIN USER
                ON USER_BUSINESS.USER_ID = USER.ID
                WHERE USER_BUSINESS.ID = ?
            """,
                (user_business_id,),
            )

            result = cursor.fetchone()

            if result is None:
                return False

            user_id = result[0]
            level = result[1]
            state = result[2]
            initial_cost = result[3]
            base_time = result[4]
            reputation_upgrade = result[5]
            business_name = result[6]
            base_profit = result[7]
            money = result[8]

            if level >= 10:
                return False

            if state != "ready" and state != "completed":
                return False

            upgrade_cost = initial_cost * (2**level)
            # Calculates the upgrade time using the faster game progression
            upgrade_time = self.get_upgrade_time(business_name, level + 1)
            pending_profit = 0

            if state == "completed":
                # Collects the pending profit automatically before starting the upgrade
                pending_profit = base_profit * (2 ** (level - 1))

            available_money = money + pending_profit

            if available_money < upgrade_cost:
                return False

            upgrade_finish_time = datetime.now() + timedelta(seconds=upgrade_time)

            # Updates money, reputation, lifetime earnings and rank progress when an upgrade starts
            cursor.execute(
                """
                UPDATE USER
                SET MONEY = ?,
                    REPUTATION = REPUTATION + ?,
                    TOTAL_EARNED = TOTAL_EARNED + ?,
                    TOTAL_REPUTATION = TOTAL_REPUTATION + ?
                WHERE ID = ?
            """,
                (
                    available_money - upgrade_cost,
                    reputation_upgrade,
                    pending_profit,
                    reputation_upgrade,
                    user_id,
                ),
            )

            # Starts the upgrade timer without increasing the level immediately
            cursor.execute(
                """
                UPDATE USER_BUSINESS
                SET STATE = ?,
                    UPGRADE_FINISH_TIME = ?,
                    PRODUCTION_FINISH_TIME = ?
                WHERE ID = ?
            """,
                ("upgrading", upgrade_finish_time.isoformat(), None, user_business_id),
            )

            if pending_profit > 0:
                # Saves the automatic profit collection in the player history
                cursor.execute(
                    """
                    INSERT INTO ACTION_HISTORY (USER_ID, MESSAGE, CREATED_AT)
                    VALUES (?, ?, ?)
                """,
                    (
                        user_id,
                        "💰 Recolheu "
                        + self.format_history_money(pending_profit)
                        + " antes da evolução",
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ),
                )

            # Saves the upgrade start in the player history
            cursor.execute(
                """
                INSERT INTO ACTION_HISTORY (USER_ID, MESSAGE, CREATED_AT)
                VALUES (?, ?, ?)
            """,
                (
                    user_id,
                    "⬆️ Iniciou evolução de "
                    + business_name
                    + " para nível "
                    + str(level + 1),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )

            connection.commit()

            return True

    def buy_manager(self, user_business_id):
        with dbapi2.connect(self.dbfile, timeout=10) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT USER_BUSINESS.USER_ID,
                        USER_BUSINESS.HAS_MANAGER,
                        BUSINESS_TYPE.MANAGER_MONEY_COST,
                        BUSINESS_TYPE.MANAGER_REP_COST,
                        BUSINESS_TYPE.MANAGER_NAME
                FROM USER_BUSINESS
                JOIN BUSINESS_TYPE
                ON USER_BUSINESS.BUSINESS_TYPE_ID = BUSINESS_TYPE.ID
                WHERE USER_BUSINESS.ID = ?
            """,
                (user_business_id,),
            )

            result = cursor.fetchone()

            if result is None:
                return False

            user_id = result[0]
            has_manager = result[1]
            manager_money_cost = result[2]
            manager_rep_cost = result[3]
            manager_name = result[4]

            if has_manager == 1:
                return False

            cursor.execute(
                """
                SELECT MONEY, REPUTATION
                FROM USER
                WHERE ID = ?
            """,
                (user_id,),
            )

            user = cursor.fetchone()

            if user is None:
                return False

            money = user[0]
            reputation = user[1]

            if money < manager_money_cost:
                return False

            if reputation < manager_rep_cost:
                return False

            cursor.execute(
                """
                UPDATE USER
                SET MONEY = ?, REPUTATION = ?
                WHERE ID = ?
            """,
                (money - manager_money_cost, reputation - manager_rep_cost, user_id),
            )

            cursor.execute(
                """
                UPDATE USER_BUSINESS
                SET HAS_MANAGER = ?
                WHERE ID = ?
            """,
                (1, user_business_id),
            )

            # Saves the manager purchase in the player history
            cursor.execute(
                """
                INSERT INTO ACTION_HISTORY (USER_ID, MESSAGE, CREATED_AT)
                VALUES (?, ?, ?)
            """,
                (
                    user_id,
                    "👔 Contratou gestor " + manager_name,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )

            connection.commit()

            return True

    def get_user_by_id(self, user_id):
        # Gets the user data used in pages, sidebars and rank calculations
        with dbapi2.connect(self.dbfile, timeout=10) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT ID, USERNAME, EMAIL, MONEY, REPUTATION, TOTAL_REPUTATION
                FROM USER
                WHERE ID = ?
            """,
                (user_id,),
            )

            return cursor.fetchone()

    def get_upgrade_time(self, business_name, next_level):
        # Calculates a faster upgrade time based on business type and next level
        if business_name == "Banca de Cachorros":
            return 5 * (next_level - 1)

        if business_name == "Café":
            return 10 * (next_level - 1)

        if business_name == "Croissanteria":
            return 15 * (next_level - 1)

        if business_name == "Hamburgueria":
            return 20 * (next_level - 1)

        return 10 * (next_level - 1)

    
    def update_business_states(self, user_id):
        # Updates finished buildings, productions and upgrades
        now = datetime.now()

        with dbapi2.connect(self.dbfile, timeout=10) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT ID, STATE, BUILD_FINISH_TIME, PRODUCTION_FINISH_TIME, UPGRADE_FINISH_TIME
                FROM USER_BUSINESS
                WHERE USER_ID = ?
            """,
                (user_id,),
            )

            user_businesses = cursor.fetchall()

            for user_business in user_businesses:
                user_business_id = user_business[0]
                state = user_business[1]
                build_finish_time = user_business[2]
                production_finish_time = user_business[3]
                upgrade_finish_time = user_business[4]

                if state == "building" and build_finish_time is not None:
                    finish_time = datetime.fromisoformat(build_finish_time)

                    if now >= finish_time:
                        cursor.execute(
                            """
                            UPDATE USER_BUSINESS
                            SET STATE = ?
                            WHERE ID = ?
                        """,
                            ("ready", user_business_id),
                        )

                if state == "producing" and production_finish_time is not None:
                    finish_time = datetime.fromisoformat(production_finish_time)

                    if now >= finish_time:
                        cursor.execute(
                            """
                            UPDATE USER_BUSINESS
                            SET STATE = ?
                            WHERE ID = ?
                        """,
                            ("completed", user_business_id),
                        )

                if state == "upgrading" and upgrade_finish_time is not None:
                    finish_time = datetime.fromisoformat(upgrade_finish_time)

                    if now >= finish_time:
                        cursor.execute(
                            """
                            UPDATE USER_BUSINESS
                            SET STATE = ?,
                                LEVEL = LEVEL + 1,
                                UPGRADE_FINISH_TIME = ?
                            WHERE ID = ?
                        """,
                            ("ready", None, user_business_id),
                        )

            connection.commit()

    def user_owns_business(self, user_id, user_business_id):
        # Checks if the selected business belongs to the logged user
        with dbapi2.connect(self.dbfile, timeout=10) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT ID
                FROM USER_BUSINESS
                WHERE ID = ? AND USER_ID = ?
            """,
                (user_business_id, user_id),
            )

            result = cursor.fetchone()

            if result is None:
                return False

            return True

    def add_history(self, user_id, message):
        # Saves a game action in the player's history
        with dbapi2.connect(self.dbfile, timeout=10) as connection:
            cursor = connection.cursor()

            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute(
                """
                INSERT INTO ACTION_HISTORY (USER_ID, MESSAGE, CREATED_AT)
                VALUES (?, ?, ?)
            """,
                (user_id, message, created_at),
            )

            connection.commit()

    def get_user_history(self, user_id):
        # Gets the most recent actions from the player's history
        with dbapi2.connect(self.dbfile, timeout=10) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT MESSAGE, CREATED_AT
                FROM ACTION_HISTORY
                WHERE USER_ID = ?
                ORDER BY ID DESC
                LIMIT 20
            """,
                (user_id,),
            )

            return cursor.fetchall()

    def get_leaderboard(self):
        # Gets the top 10 players ordered by total money earned
        leaderboard = []

        with dbapi2.connect(self.dbfile, timeout=10) as connection:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT USERNAME, TOTAL_EARNED, TOTAL_REPUTATION
                FROM USER
                ORDER BY TOTAL_EARNED DESC, MONEY DESC
                LIMIT 10
            """)

            for row in cursor:
                leaderboard.append(row)

        return leaderboard

    def get_rank_name(self, total_reputation):
        # Returns the player rank name based on lifetime reputation
        if total_reputation >= 130:
            return "Lenda Gastronómica"

        if total_reputation >= 100:
            return "Mestre da Restauração"

        if total_reputation >= 65:
            return "Magnata da Restauração"

        if total_reputation >= 35:
            return "Gestor de Restaurantes"

        if total_reputation >= 15:
            return "Mestre da Tasca"

        if total_reputation >= 5:
            return "Dono da Banca"

        return "Empreendedor"

    def get_ranks(self):
        # Gets all available ranks shown in the ranks page
        ranks = [
            (0, "Empreendedor"),
            (5, "Dono da Banca"),
            (15, "Mestre da Tasca"),
            (35, "Gestor de Restaurantes"),
            (65, "Magnata da Restauração"),
            (100, "Mestre da Restauração"),
            (130, "Lenda Gastronómica"),
        ]

        return ranks

    def format_history_money(self, value):
        # Formats money values before saving them in the action history
        value = int(value)

        if value >= 1000000:
            formatted_value = value / 1000000
            return str(round(formatted_value, 2)).rstrip("0").rstrip(".") + "M€"

        if value >= 1000:
            formatted_value = value / 1000
            return f"{formatted_value:.1f}k€"

        return str(value) + "€"
