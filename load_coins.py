from database import create_connection, close_cursor_and_coonection, get_cursor
from coingecko import Coingecko

def update_coins_name_and_symbol():
    coins = Coingecko().get_top_100_coins()
    connection = create_connection()
    cursor = get_cursor(connection=connection)
    cursor.execute("SELECT id FROM assets_type WHERE type = 'coin'")
    asset_type_id = cursor.fetchone()[0]
    if not cursor and not connection:
        print("Hubo un error al momento de conectarse a la base de datos.")
    try:
        added_coins =0
        for coin in coins:
            cursor.execute("SELECT id FROM coins WHERE symbol = %s", (coin['symbol'],))
            existing_coin = cursor.fetchone()
            if not existing_coin:
                added_coins += 1
                cursor.execute("INSERT INTO assets (type_id) VALUES (%s) RETURNING id", (asset_type_id,))
                asset_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO coins (asset_id, name, symbol, image) VALUES (%s, %s, %s, %s)", (asset_id, coin['name'], coin['symbol'], coin['image']))
        connection.commit()
        if added_coins > 0:
            print(f"Se agregaron {added_coins} coins a la base de datos.")
        else:
            print("No se agregaron coins a la base de datos.")
    # except Exception as e:
    #     close_cursor_and_coonection(connection, cursor)
    #     print("ERROR: ", e)
    finally:
        close_cursor_and_coonection(connection, cursor)
# load_coins()
update_coins_name_and_symbol()