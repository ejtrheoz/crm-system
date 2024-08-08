from flask import *
from PIL import Image   
from io import BytesIO
import os
import database
from waitress import serve
import json
from json_orders import *
import requests
import telebot
from telebot.types import InputMediaPhoto
import config

app = Flask(__name__, template_folder="F:\projects\osty-jewelry-bot\web")


@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":

        id = request.form["id"]
        amount = request.form["amount"]
        buy_price = request.form["buy_price"]
        sell_price = request.form["sell_price"]

        database.new_record(id, amount, buy_price, sell_price)

        photo_file = request.files["photo"]

        if photo_file:

            file_contents = photo_file.read()
            image = Image.open(BytesIO(file_contents))
            image = image.convert('RGB')

            image.save(f"static/images/{id}.jpg", format='JPEG')


    return render_template("templates/Add.html")


@app.route("/delete", methods=["GET","POST"], endpoint='func1')
def delete():
    if request.method == "POST":
        product_id = int(request.form.get("id"))

        database.delete_record(int(product_id))
        os.remove(f"static/images/{product_id}.jpg")
    
    products = list(map(lambda x: x[:-4], os.listdir("static/images")))
    return render_template("templates/Delete.html", products=products)

@app.route('/show', methods=["GET","POST"], endpoint="func2")
def show():

    products = list(map(lambda x: x[:-4], os.listdir("static/images")))

    if request.method == "POST":
        product_id = int(request.form.get("id"))
        new_info = database.get_info(int(product_id))

        return render_template("templates/Show.html", products=products, new_info=new_info)
    
    return render_template("templates/Delete.html", products=products)


@app.route('/change', methods=["POST", "GET"])
def change():
    if request.method == "POST":

        product_id = int(request.form['id'])
        parameter = request.form['parameter']
        new_value = int(request.form['value'])

        database.change_info(product_id, parameter, int(new_value))

    products = list(map(lambda x: x[:-4], os.listdir("static/images")))
    return render_template("templates/Change.html", products=products)


@app.route('/form', methods=["POST", "GET"])
def send_form():
    products = list(map(lambda x: x[:-4], os.listdir("static/images")))

    if request.method == "POST":

        id_list = list(filter(lambda x: "id" in x, list(request.form.keys())))
        amount_list = list(filter(lambda x: "amount" in x, list(request.form.keys())))

        for idx, id in enumerate(id_list):
            if database.amount_info(int(request.form[f"{id}"])) - int(request.form[amount_list[idx]]) < 0:
                return render_template("templates/SendForm.html", products=products, alert=True)

        add_json(request.form)

        text = ""
        for i in range(len(id_list)):
            text += f"""
Тип: {request.form[f'type{i+1}']}
ID: {request.form[f'id{i+1}']}
Кількість: {request.form[f'amount{i+1}']}
"""

        text += f"""
Ім'я: {request.form['name']}
Адреса Пошти: {request.form['destination']}
Телефон: {request.form['phone']}
Email: {request.form['mail']}
            """
        
        photos = []
        for idx, i in enumerate(id_list):
            if idx == 0:
                photos.append(InputMediaPhoto(open(f'static/images/{request.form[i]}.jpg', 'rb'), caption=text))
            else:
                photos.append(InputMediaPhoto(open(f'static/images/{request.form[i]}.jpg', 'rb')))

        bot = telebot.TeleBot(config.token)
        bot.send_media_group("-4247054566", photos)
        
        

    return render_template("templates/SendForm.html", products=products)

@app.route('/orders', methods=["POST", "GET"])
def manage_orders():
    orders = load_json()

    length_dict = {}
    for i in orders.keys():
        id_list = list(filter(lambda x: "id" in x, list(orders[i].keys())))
        length_dict[i] = len(id_list)



    return render_template("templates/Orders.html", orders=orders, length=length_dict)


@app.route('/confirm_order', methods=['POST'])
def confirm_order():
    
    data = request.get_json()
    order_id = data.get('order_Id')
    orders = load_json()
    remove_json(order_id)

    products = []
    id_list = list(filter(lambda x: "id" in x, list(orders[order_id].keys())))

    for i in range(1, len(id_list)+1):
        products.append(database.get_info(int(orders[order_id][f"id{i}"])))

    for i in range(1, len(id_list)+1):
        database.reduce_amount(int(orders[order_id][f"id{i}"]), int(orders[order_id][f"amount{i}"]))


    database.add_client([orders[order_id]["name"], orders[order_id]["mail"], orders[order_id]["phone"]])
    
    for idx, product in enumerate(products):
        for _ in range( int(orders[order_id][f"amount{idx+1}"]) ):
            database.add_profit([product[0], product[2], product[3]])
    
    # database.add_profit([product[0], product[2], product[3]])


    return jsonify(message='Order confirmed successfully')

@app.route('/delete_order', methods=['POST'])
def delete_order():
    data = request.get_json()
    order_id = data.get('order_Id')


    remove_json(order_id)
    return jsonify(message='Order was deleted')

@app.route('/edit_order', methods=['POST'])
def edit_order():
    data = request.get_json()
    order_id = data.get('order_id')

    remove_json(order_id)
    return jsonify(message='Order was edited')


if __name__ == "__main__":
    app.run()
    # serve(app, host="0.0.0.0", port=8080)
