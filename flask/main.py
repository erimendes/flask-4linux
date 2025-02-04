from bson import ObjectId
import flask
import montydb
from flask import request, jsonify
from blueprint.users import blueprint as users

app = flask.Flask(__name__)

app.register_blueprint(users)

# Função para serializar o MongoDB ObjectId
def serialize(document):
    if isinstance(document, ObjectId):
        return str(document)  # Converte ObjectId para string
    if isinstance(document, dict):
        return {key: serialize(value) for key, value in document.items()}
    if isinstance(document, list):
        return [serialize(item) for item in document]
    return document

# Função para obter a conexão com o banco de dados
def get_conn(database):
    client = montydb.MontyClient()
    return client.get_database(database)

@app.route("/users/delete/<username>", methods= ['DELETE'])
def delete_by_username(username):
    db = get_conn('pessoa')

    user = db.users.find({'username': username})

    if db.users.count_documents({'username': username}) != 1:
        return flask.jsonify({'NOK': 'Usuário não encontrado ou múltiplas encontradas'}), 400
    
    db.users.delete_one({'username': username})
    return flask.jsonify({'ACK': 'Usuário removido com sucesso'})

@app.route("/users/update", methods= ['PUT'])
def update_user():
    db = get_conn('pessoa')

    user = dict(flask.request.json)

    user_to_update = db.users.find({'username': user.get('username')})

    if db.users.count_documents({'username': user.get('username')}) != 1:
        return flask.jsonify({'NOK': 'Usuário não encontrado ou múltiplas encontradas'}), 400
    
    db.users.update_one({'username': user.get('username')}, {"$set": user})
    return flask.jsonify({'ACK': 'Usuário atualizado com sucesso', 'data': user}), 200

@app.route("/users/insert", methods= ['POST'])
def add_user():
    db = get_conn('pessoa')

    user = dict(flask.request.json)

    # Verificar se o usuário já existe
    user_exists = db.users.find_one({"username": user.get('username')})
    if user_exists:
        return flask.jsonify({'NOK': 'Usuário já existe'}), 400

    db.users.insert_one(user)
    user = serialize(user)  # Convertendo ObjectId para string
    return flask.jsonify({'ACK': 'Usuário inserido com sucesso', 'usuário': user}), 200

@app.route("/users/<username>")
def get_user_by_username(username):
    db = get_conn('pessoa')

    users = [
        {
            'username': user.get('username'),
            'senha': user.get('senha'),
            'nome': user.get('nome'),
        } for user in db.users.find({"username": username })
    ]
    
    if not users:
        return flask.jsonify({'NOK': 'Usuário não encontrado'}), 404
    
    # Convertendo ObjectId para string antes de retornar
    users = serialize(users)
    return flask.jsonify({'ACK': 'Usuário encontrado', 'data': users}), 200

@app.route("/", methods=['GET'])
def home():
    return "Bem-vindo à API!"

# Rodar a aplicação
if __name__ == '__main__':
    app.run(debug=True)
