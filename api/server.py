from flask import Flask, render_template, jsonify
import json

data = []
with open('output.json', 'r') as file:
    data = json.load(file)

cources = []
for i in range(0, len(data)):
    cources.append(data[i]['Course'])
print(cources)
app = Flask(__name__)


cources = []


@app.route("/")
def home():
    return render_template('example.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.route('/getCourses', methods=['GET'])
def get_data():
    cources = []
    for i in range(0, len(data)):
        cources.append(data[i]['Course'])

    return jsonify(cources)


@app.route('/getSem/<cid>')
def getSem(cid):
    print(cid)

    return jsonify(data[int(cid)])


if __name__ == "__main__":
    app.run(debug=True)
