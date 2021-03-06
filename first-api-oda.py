import os
from flask import Flask, jsonify, request
from itsdangerous import json
from step1.lexer import CompilerLexer
import pathlib

app = Flask(__name__)


@app.route('/')
def dont_panic():
    if request.headers.get('Authorization') == '42':
        return jsonify({"42": "The answer to life the universe and everything"})
    return jsonify({"message": "Don't panic!"})

@app.route("/getLexerFile", methods=['POST'])
def getLexerFile():
    file = request.files['file']
    lexer = CompilerLexer()
    data = lexer.scan(str(file.read()))
    return data

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)