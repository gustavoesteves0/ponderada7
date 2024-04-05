from flask import Flask, request, jsonify, render_template
from serial.tools import list_ports
import pydobot
import inquirer
import tinydb

app = Flask(__name__)
db = tinydb.TinyDB('db.json')

@app.route('/ligar', methods=['GET'])
def ligar():
    # Listas as portas seriais disponíveis
    available_ports = list_ports.comports()
    porta_escolhida = inquirer.prompt([
        inquirer.List("porta", message="Escolha a porta serial", choices=[x.device for x in available_ports])
    ])["porta"]
    # Cria uma instância do robô
    device = pydobot.Dobot(port=porta_escolhida, verbose=False)
    device.speed(100, 100)

@app.route('/', methods=['GET'])
def index():
    logs = db.all()
    return render_template("index.html", logs=logs)

@app.route('/home', methods=['POST'])
def home():
    device.move_to_J(240.53, 0, 150.23, 0, wait=True)
    db.insert({'action': 'home'})
    return jsonify({'message': 'Home realizado com sucesso'})

@app.route('/ligar_ferramenta', methods=['POST'])
def ligar_ferramenta():
    device.suck(True)
    db.insert({'action': 'ligar_ferramenta'})
    return jsonify({'message': 'Ferramenta ligada'})

@app.route('/desligar_ferramenta', methods=['POST'])
def desligar_ferramenta():
    device.suck(False)
    db.insert({'action': 'desligar_ferramenta'})
    return jsonify({'message': 'Ferramenta desligada'})

@app.route('/mover', methods=['POST'])
def mover():
    data = request.json
    nova_posicao_x = device.pose()[0] + float(data['distancia_x'])
    nova_posicao_y = device.pose()[1] + float(data['distancia_y'])
    nova_posicao_z = device.pose()[2] + float(data['distancia_z'])
    device.move_to(nova_posicao_x, nova_posicao_y, nova_posicao_z, 0, wait=True)
    db.insert({'action': 'mover', 'distancia_x': data['distancia_x'], 'distancia_y': data['distancia_y'], 'distancia_z': data['distancia_z']})
    return jsonify({'message': 'Movido com sucesso'})

@app.route('/posicao_atual', methods=['GET'])
def posicao_atual():
    db.insert({'action': 'posicao_atual'})
    return render_template("index.html", posicao_atual=device.pose())

@app.route('/logs', methods=['GET'])
def logs():
    logs = db.all()
    return render_template("logs.html", logs=logs)

@app.route('/delete_logs', methods=['GET'])
def delete_logs():
    db.truncate()
    return jsonify({'success': 'Logs deleted'}), 200

@app.route('/get_logs', methods=['GET'])
def get_logs():
    logs = db.all()
    return jsonify(logs)

if __name__ == '__main__':
    app.run(debug=True)
