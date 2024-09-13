import sqlite3

def new_record(id, amount, buy_price, sell_price, type, name, ring_size, path=None):
    
    conn = sqlite3.connect('products.db') if path==None else sqlite3.connect(path+'/products.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO Products  VALUES (?, ?, ?, ?, ?, ?, ?)", (id, amount, buy_price, sell_price, type, name, ring_size))

    conn.commit()
    cursor.close()
    conn.close()


def delete_record(id, ring_size=None, path=None):
    conn = sqlite3.connect('products.db') if path==None else sqlite3.connect(path+'/products.db')
    cursor = conn.cursor()

    if ring_size:
        cursor.execute("DELETE FROM Products WHERE id = ? AND ring_size = ?", (id, ring_size))
    else:
        cursor.execute("DELETE FROM Products WHERE id = ?", (id,))

    conn.commit()
    cursor.close()
    conn.close()


def get_info(id, path=None):
    conn = sqlite3.connect('products.db') if path==None else sqlite3.connect(path+'/products.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Products WHERE id = ?", (id,))
    data = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()

    return data


def change_info(id, parameter, new_value, ring_size=None, path=None):
    conn = sqlite3.connect('products.db') if path==None else sqlite3.connect(path+'/products.db')
    cursor = conn.cursor()

    if ring_size:
        cursor.execute(f"""
        UPDATE Products
        SET {parameter} = ?
        WHERE id = ? AND ring_size = ?
        """, (new_value, id, ring_size))
    else:
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
INSERT INTO Profit VALUES (?, ?, ?, ?, ?, ?, ?)
""", (info[0], info[1], info[2], info[3], info[4], info[5], info[6]))
    
    conn.commit()
    cursor.close()
    conn.close()


def get_products():
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, type, ring_size FROM Products")
    data = cursor.fetchall()
    products = {}

    products["necklaces"] = [str(i[0]) for i in data if i[1] == "necklace"]
    products["rings"] = [str(i[0])+" "+str(i[2]) for i in data if i[1] == "ring"]
    products["bracelettes"] = [str(i[0]) for i in data if i[1] == "bracelette"]
    products["earrings"] = [str(i[0]) for i in data if i[1] == "earrings"]

    return products


def get_amount_dict():
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, amount, ring_size FROM Products")
    data = cursor.fetchall()
    amount_list = {}

    print(data)


    for product_info in data:
        if product_info[2] == "":
            amount_list[product_info[0]] = product_info[1]
        else:
            amount_list[str(product_info[0]) + " " + str(product_info[2])] = product_info[1]

    return amount_list
