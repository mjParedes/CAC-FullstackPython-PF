from flask import Flask, jsonify, request
from .resources.cars import Cars

app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'pong!'})

@app.route('/cars', methods=['GET'])
def getCars():
    return jsonify({'cars': Cars, 'message': "Cars List"})

@app.route('/cars/<string:car_name>', methods=['GET'])
def getCar(car_name):
    carsFound = [car for car in Cars if car['car_name'] ==  car_name] 
    return jsonify(carsFound)

@app.route('/cars', methods=['PUT'])
def addCar():
    print(request.json)
    return 'recibido'

if __name__ == '__main__':
    app.run(debug=True)