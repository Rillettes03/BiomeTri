import mysql.connector

class DatabaseHandler:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.connect()

    def connect(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def is_connected(self):
        return self.connection.is_connected() if self.connection else False
    
    def get_cursor(self):
        return self.connection.cursor()
    
    def commit(self):
        if self.connection.is_connected():
            self.connection.commit()
        else:
            raise Exception("La connexion à la base de données est fermée.")
    
    # Execution SQL avec gestion des erreurs
    def execute_query(self, query, values=None):
        try:
            cursor = self.connection.cursor()
            if values:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
            self.connection.commit()
            cursor.close()
        except mysql.connector.Error as err:
            print("Erreur lors de l'exécution de la requête :", err)

    # Ajout utilisateur
    def addUser (self, id, nom, prenom, email, FacialData, lastAccess):
        query = "INSERT INTO membres (id, nom, prenom, email, FacialData, lastAccess) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (id, nom, prenom, email, FacialData, lastAccess)
        cursor = self.connection.cursor()
        cursor.execute(query, values)
        self.connection.commit()
        cursor.close()
    
    # def add_user(db_config, id, nom, prenom, email, FacialData, lastAccess):
    #     connection = None 

    #     try:
    #         connection = mysql.connector.connect(**db_config)
    #         cursor = connection.cursor()

    #         cursor.execute("""
    #             INSERT INTO membres (id, nom, prenom, email, FacialData, lastAccess)
    #             VALUES (%s, %s, %s, %s, %s, %s)
    #         """, (id, nom, prenom, email, FacialData, lastAccess))

    #         connection.commit()

    #         print(f"User '{nom}' '{prenom}' added successfully.")

    #     except mysql.connector.Error as err:
    #         print(f"Error: {err}")

    #     finally:
    #         if connection is not None and connection.is_connected():
    #             cursor.close()
    #             connection.close()

    def close(self):
        if self.connection.is_connected():
            self.connection.close()

# # Example usage:
# db_handler = DatabaseHandler("localhost", "user", "password", "mydatabase")
# db_handler.insert_user("john_doe", "john@example.com")
# db_handler.close()
