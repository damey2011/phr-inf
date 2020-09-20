import numpy as np
from flask import Flask, render_template, jsonify, request

from api_exceptions import Error400

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route('/')
def home():
    return render_template('index.html')


@app.errorhandler(Error400)
def error_400(e):
    return jsonify(e()), 400


@app.route('/api/sentence-gen/', methods=['POST'])
def sentence_gen():
    word = request.get_json(force=True).get('word', None)
    if not word or not isinstance(word, str):
        raise Error400('Please provide a valid word.')
    word = str(word).lower()
    is_palindrome = word == word[::-1]
    rand_no = np.random.randint(1, 11)
    diff_text = "" if is_palindrome else "not "
    message = f'I would like {rand_no} {word} please. {word.capitalize()} is {diff_text}a palindrome'
    return jsonify({'message': message}), 200


if __name__ == '__main__':
    app.run(debug=True)
