# database/connection.py
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

class DatabaseConnection:
    """Gestion de la connexion à la base de données MySQL"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Établir la connexion à MySQL"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                print("✓ Connexion à MySQL réussie")
                return True
        except Error as e:
            print(f"✗ Erreur de connexion : {e}")
            return False
    
    def disconnect(self):
        """Fermer la connexion"""
        if self.connection and self.connection.is_connected():
            if self.cursor:
                self.cursor.close()
            self.connection.close()
            print("✓ Connexion MySQL fermée")
    
    def execute_query(self, query, params=None):
        """Exécuter une requête INSERT, UPDATE, DELETE"""
        try:
            self.cursor.execute(query, params or ())
            self.connection.commit()
            return True
        except Error as e:
            print(f"✗ Erreur d'exécution : {e}")
            self.connection.rollback()
            return False
    
    def fetch_one(self, query, params=None):
        """Récupérer une seule ligne"""
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchone()
        except Error as e:
            print(f"✗ Erreur de lecture : {e}")
            return None
    
    def fetch_all(self, query, params=None):
        """Récupérer toutes les lignes"""
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Error as e:
            print(f"✗ Erreur de lecture : {e}")
            return []
    
    def get_last_insert_id(self):
        """Récupérer le dernier ID inséré"""
        return self.cursor.lastrowid


# Instance globale de connexion
db = DatabaseConnection()


# Fonction utilitaire pour tester la connexion
def test_connection():
    """Tester la connexion à la base de données"""
    if db.connect():
        result = db.fetch_one("SELECT DATABASE() as db_name")
        if result:
            print(f"✓ Base de données active : {result['db_name']}")
        db.disconnect()
        return True
    return False


if __name__ == "__main__":
    # Test de connexion
    test_connection()
