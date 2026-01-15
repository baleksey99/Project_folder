from db.db_manager import DBManager

def main():
    db = DBManager()
    try:
        db.create_database()
        db.connect_to_database()
        db.create_tables()
        print("Настройка БД завершена успешно.")
    except Exception as e:
        print(f"Ошибка при настройке БД: {e}")
    finally:
        if db.conn:
            db.conn.close()

if __name__ == "__main__":
    main()
