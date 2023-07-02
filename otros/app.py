from flask import Flask, jsonify
from otros.colores import arrayColores

app = Flask(__name__)

@app.route("/")
def hello_world():
    print(arrayColores)
    return jsonify(message='Colores', content = arrayColores)