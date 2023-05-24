from flask import Flask, jsonify, request
from src.product_updater.product_updater import MyDb

DB_HOST = 'db'
DB_USER = 'root'
DB_PASS = '1111'
DB_NAME = 'svyaznoy_iphone_data'
DB_PORT = '3306'


app = Flask(__name__)


@app.route('/products', methods=['GET'])
def get_all_products():
    db = MyDb(DB_HOST, DB_USER, DB_PASS, DB_NAME, DB_PORT)
    attr = ['name', 'memory', 'color', 'price']
    products = [dict(zip(attr, product)) for product in db.get_products()]
    return jsonify(products=products)


@app.route('/products', methods=['POST'])
def get_products_by():
    name, memory, color, min_price, max_price = extract_from_json()
    db = MyDb(DB_HOST, DB_USER, DB_PASS, DB_NAME, DB_PORT)
    attr = ['name', 'memory', 'color', 'price']
    products = [dict(zip(attr, product)) for product in db.get_products(
        (name, memory, color, min_price, max_price))]
    return jsonify(products=products)


def extract_from_json():
    json_data = request.get_json()
    return json_data['name'], json_data['memory'], \
           json_data['color'], json_data['min_price'], json_data['max_price']


if __name__ == '__main__':
    app.run(debug=True, port=8765)
