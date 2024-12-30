import pg8000

# Database connection details
host = "dpg-ctoo311opnds73fjflag-a.frankfurt-postgres.render.com"
database = "task_db_m4nd"
user = "task_db_m4nd_user"
password = "40Ma9VCQ6jnyNqyGBXvvY1lMqxVi04k9"

try:
    # Attempt to connect to the PostgreSQL database
    connection = pg8000.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )
    print("Database connection successful!")
    connection.close()
except Exception as e:
    print("Failed to connect to the database:", e)
