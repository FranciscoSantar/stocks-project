from database import create_connection, close_cursor_and_coonection, get_cursor
from fmp import FMP

def update_stocks_name_and_symbol():
    stocks = FMP().get_top_500_US_stocks()
    connection = create_connection()
    cursor = get_cursor(connection=connection)
    cursor.execute("SELECT id FROM assets_type WHERE type = 'stock'")
    asset_type_id = cursor.fetchone()[0]
    if not cursor and not connection:
        print("Hubo un error al momento de conectarse a la base de datos.")
    try:
        added_stocks=0
        for stock in stocks:
            cursor.execute("SELECT id FROM stocks WHERE symbol = %s", (stock['symbol'],))
            existing_stock = cursor.fetchone()
            if not existing_stock:
                added_stocks += 1
                cursor.execute("INSERT INTO assets (type_id) VALUES (%s) RETURNING id", (asset_type_id,))
                asset_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO stocks (asset_id, name, symbol) VALUES (%s, %s, %s)", (asset_id, stock['name'], stock['symbol']))
        connection.commit()
        if added_stocks > 0:
            print(f"Se agregaron {added_stocks} stocks a la base de datos.")
        else:
            print("No se agregaron stocks a la base de datos.")
    except Exception as e:
        close_cursor_and_coonection(connection, cursor)
        print("ERROR: ", e)
    finally:
        close_cursor_and_coonection(connection, cursor)
# load_stocks()
update_stocks_name_and_symbol()