import mysql.connector
from mysql.connector import Error

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="Tanuska@2004",
            database="Accidents_Database"
        )


        if connection.is_connected():
            print("Connected to Accidents_Database successfully!")

            cursor = connection.cursor()
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()

            print("Tables in the database:")
            for table in tables:
                print(table[0])

    except Error as e:
        print("Error while connecting:", e)

    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("Connection closed.")

if __name__ == "__main__":
    connect_to_database()
