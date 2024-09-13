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
import datetime

app = Flask(__name__, template_folder="F:\projects\osty-jewelry-shop\web")
# app = Flask(__name__, template_folder="/home/ubuntu/jura/web")


@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":


        id = request.form["id"]
        amount = request.form["amount"]
        buy_price = request.form["buy_price"]
        sell_price = request.form["sell_price"]
        type = request.form["type"]
        name = request.form["name"]
        ring_size = request.form["ring_size"]

        if database.get_info(id) != []:
            if type == "ring":
                for ring in database.get_info(id):
                    if ring[6] == ring_size:
                        return render_template("templates/Add.html", alert_ring=True)
            else:
                return render_template("templates/Add.html", alert=True)

        database.new_record(id, amount, buy_price, sell_price, type, name, ring_size)

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

        if request.form["type"] == "ring":
            product_id = int(request.form.get("id").split(' ')[0])
            ring_size = int(request.form.get("id").split(' ')[1])
            database.delete_record(int(product_id), ring_size=ring_size)
        else:
            product_id = int(request.form.get("id"))
            database.delete_record(int(product_id))

        if database.get_info(product_id) == []:
            os.remove(f"static/images/{product_id}.jpg")
    
    products = list(map(lambda x: x[:-4], os.listdir("static/images")))
    return render_template("templates/Delete.html", products=database.get_products())

@app.route('/show', methods=["GET","POST"], endpoint="func2")
def show():

    if request.method == "POST":
    
        if request.form["type"] == "ring":
            product_id = int(request.form.get("id").split(' ')[0])
            ring_size = int(request.form.get("id").split(' ')[1])

            for ring in database.get_info(int(product_id)):
                if ring[6] == ring_size:
                    new_info = ring
        else:
            product_id = int(request.form.get("id").split)
            new_info = database.get_info(int(product_id))


        return render_template("templates/Show.html", products=database.get_products(), new_info=new_info)
    
    return render_template("templates/Delete.html", products=database.get_products())


@app.route('/change', methods=["POST", "GET"])
def change():
    if request.method == "POST":

        if request.form["type"] == "ring":
            product_id = int(request.form.get("id").split(' ')[0])
            ring_size = int(request.form.get("id").split(' ')[1])
            parameter = request.form['parameter']
            if parameter == "name":
                new_value = request.form['value']
            else:
                new_value = int(request.form['value'])

            database.change_info(product_id, parameter, new_value, ring_size=ring_size)
        else:
            product_id = int(request.form['id'])
            parameter = request.form['parameter']
            if parameter == "name":
                new_value = request.form['value']
            else:
                new_value = int(request.form['value'])


            database.change_info(product_id, parameter, new_value)

    products = list(map(lambda x: x[:-4], os.listdir("static/images")))
    return render_template("templates/Change.html", products=database.get_products())


@app.route('/form', methods=["POST", "GET"])
def send_form():

    if request.method == "POST":

        id_list = list(filter(lambda x: "id" in x, list(request.form.keys())))
        amount_list = list(filter(lambda x: "amount" in x, list(request.form.keys())))

        for idx, id in enumerate(id_list):
            if database.amount_info(int(request.form[f"{id}"])) - int(request.form[amount_list[idx]]) < 0:
                return render_template("templates/SendForm.html", products=database.get_products(), alert=True, product_id=request.form[f"{id}"])


        add_json(request.form)


        text = ""
        for i in range(len(id_list)):

            product_type = ""
            if request.form[f'type{i+1}'] == "ring":
                product_type = "Кільце"
            
            if request.form[f'type{i+1}'] == "necklace":
                product_type = "Намисто"

            if request.form[f'type{i+1}'] == "earrings":
                product_type = "Cережки"
            
            if request.form[f'type{i+1}'] == "bracelette":
                product_type = "Браслет"

            if request.form[f'type{i+1}'] == "ring":

                for j in database.get_info(request.form[f'id{i+1}']):
                    if j[6] == int(request.form[f"ringsize{i+1}"]):
                        text += f"""
Тип: {product_type}
ID: {request.form[f'id{i+1}']}
Ім'я: {j[5]}
Кількість: {request.form[f'amount{i+1}']}
Розмір кільця: {request.form[f'ringsize{i+1}']}
"""
   
            else:
                text += f"""
Тип: {product_type}
ID: {request.form[f'id{i+1}']}
Ім'я: {database.get_info(request.form[f'id{i+1}'])[0][5]}
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
        
        

    return render_template("templates/SendForm.html", products=database.get_products(), amount=database.get_amount_dict())

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
        if orders[order_id][f"type{i}"] == "ring":
            for ring in database.get_info(int(orders[order_id][f"id{i}"])):
                if str(ring[6]) == orders[order_id][f"ringsize{i}"]:
                    products.append(ring)
        else:
            products.append(database.get_info(int(orders[order_id][f"id{i}"]))[0])

    for i in range(1, len(id_list)+1):
        database.reduce_amount(int(orders[order_id][f"id{i}"]), int(orders[order_id][f"amount{i}"]))


    database.add_client([orders[order_id]["name"], orders[order_id]["mail"], orders[order_id]["phone"]])
    
    for i in products:
        print(i)

    for idx, product in enumerate(products):
        database.add_profit([product[0], product[2], product[3], int(orders[order_id][f"amount{idx+1}"]), str(datetime.date.today()), product[4], product[6]])
    
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
