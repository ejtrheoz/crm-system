import sqlite3

def new_record(id, amount, buy_price, sell_price, path=None):
    
    conn = sqlite3.connect('products.db') if path==None else sqlite3.connect(path+'/products.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO Products  VALUES (?, ?, ?, ?)", (id, amount, buy_price, sell_price))

    conn.commit()
    cursor.close()
    conn.close()


def delete_record(id, path=None):
    conn = sqlite3.connect('products.db') if path==None else sqlite3.connect(path+'/products.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Products WHERE id = ?", (id,))

    conn.commit()
    cursor.close()
    conn.close()


def get_info(id, path=None):
    conn = sqlite3.connect('products.db') if path==None else sqlite3.connect(path+'/products.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Products WHERE id = ?", (id,))
    data = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()

    return data


def change_info(id, parameter, new_value, path=None):
    conn = sqlite3.connect('products.db') if path==None else sqlite3.connect(path+'/products.db')
    cursor = conn.cursor()


    cursor.execute(f"""
    UPDATE Products
    SET {parameter} = ?
    WHERE id = ?
    """, (new_value, id))

    conn.commit()
    cursor.close()
    conn.close()

def amount_info(product_id):

    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT amount
    FROM Products
    WHERE id = ?
    """, (product_id,))

    info = cursor.fetchone()
    cursor.close()
    conn.close()

    return info[0]


def reduce_amount(product_id, amount):
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()

    cursor.execute("""
UPDATE Products
SET amount = amount-?
WHERE id = ?
""", (amount, product_id,))
    
    conn.commit()
    cursor.close()
    conn.close()


def add_client(info):
    conn = sqlite3.connect("clients.db")
    cursor = conn.cursor()

    cursor.execute("""
INSERT INTO Clients VALUES (?, ?, ?)
""", (info[0], info[1], info[2]))
    
    conn.commit()
    cursor.close()
    conn.close()

def add_profit(info):
    conn = sqlite3.connect("profit.db")
    cursor = conn.cursor()

    cursor.execute("""
INSERT INTO Profit VALUES (?, ?, ?)
""", (info[0], info[1], info[2]))
    
    conn.commit()
    cursor.close()
    conn.close()
