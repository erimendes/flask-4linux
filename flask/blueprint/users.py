from flask import Blueprint, jsonify, render_template
from config.database import get_conn

blueprint = Blueprint('users', __name__)

@blueprint.route('/users', methods= ['GET'])
def get_users():
    db = get_conn('pessoa')

    users = [
        {
            'username': user.get('username'),
            'senha': user.get('senha'),
            'nome': user.get('nome')
        } for user in db.users.find()
    ]

    return render_template("users.html", context=users)
