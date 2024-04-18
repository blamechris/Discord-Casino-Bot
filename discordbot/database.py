import sys
import mysql.connector
from dotenv import load_dotenv
import os
import mysql.connector

class database:
    load_dotenv()  # This loads the environment variables from .env

    def __init__(self) -> None:
        self.db = mysql.connector.connect(
            host       = os.environ.get('DB_HOST', 'default_host'),  # Fallback to 'default_host' if not set
            user       = os.environ.get('DB_USER', 'default_user'),  # Fallback to 'default_user' if not set
            password   = os.environ.get('DB_PASSWORD', 'default_password'),  # Fallback to 'default_password' if not set
            database   = os.environ.get('DB_NAME', 'default_database')  # Fallback to 'default_database' if not set
        )
        self.cursor = self.db.cursor(dictionary=True)
        self.cursor.execute("SELECT VERSION()")
        results = self.cursor.fetchone()
        if(results):
            print("Database connection successfully established")
        else:
            print("ERROR: CONNECTION UNABLE TO BE ESTABLISHED. EXITTING PROGRAM.")
            sys.exit()
        pass

    # Creates an account to the database if not created.
    # int discord_id, str username
    # returns true or false if account is created successfully
    def create_account(self, discord_id, username):
        query = "INSERT INTO `casino`.`users` (discord_id, username) VALUES (%s, %s)"
        self.cursor.execute(query, (discord_id, str(username)))
        self.db.commit()

    def withdraw(self, discord_id, total):
        query = "INSERT INTO `casino`.`transactions` (`transactionType`, `recipientID`, `total`) VALUES (%s, %s, %s);"
        self.cursor.execute(query, ('WITHDRAWAL', discord_id, total))
        self.db.commit()
    def deposit(self, discord_id, total):
        query = "INSERT INTO `casino`.`transactions` (`transactionType`, `recipientID`, `total`) VALUES (%s, %s, %s);"
        self.cursor.execute(query, ('DEPOSIT', discord_id, total))
        self.db.commit()

    def transfer(self, sender_id, recipient_id, total):
        query = "INSERT INTO `casino`.`transactions` (`transactionType`, 'senderID', `recipientID`, `total`) VALUES (%s, %s, %s, %s);"
        self.cursor.execute(query, ('TRANSFER', sender_id, recipient_id, total))
        self.db.commit()

    def blackjack_result(self, result, player_id, payout):
        query = "INSERT INTO `casino`.`blackjack_matches` (`player_id`, `result`, `payout`) VALUES (%s, %s, %s);"
        self.cursor.execute(query, (player_id, result, payout))
        self.db.commit()

    def get_player_stats(self, discord_id):
        query = """
        SELECT a.discord_id, a.username, a.chip_count, wins, losses, last_withdrawal, 
            ROW_NUMBER() OVER (ORDER BY a.discord_id) AS user_rank
        FROM `casino`.`users` a
        WHERE a.discord_id = %s;
        """
        self.cursor.execute(query, (discord_id,))
        user_data = self.cursor.fetchone()
        return user_data
    
    def get_last_withdraw(self, discord_id):
        # Fetch the last withdrawal time and chip count
        query = "SELECT last_withdrawal FROM `casino`.`users` WHERE discord_id = %s"
        self.cursor.execute(query, (discord_id,))
        last_withdrawal = self.cursor.fetchone()['last_withdrawal']
        return last_withdrawal
    
    def update_last_withdraw(self, discord_id, timestamp):
        # Update chip count and last withdrawal timestamp
        update_query = """
        UPDATE `casino`.`users` SET last_withdrawal = %s WHERE discord_id = %s
        """
        self.cursor.execute(update_query, (timestamp, discord_id))
        self.db.commit()

    # todo
    #def get_leaderboard_overall(num_per_page, page):
    #    query = 

    #def get_leaderboard_blackjack():
