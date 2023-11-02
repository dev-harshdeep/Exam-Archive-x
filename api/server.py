from flask import Flask, render_template, jsonify
import json
from collections import OrderedDict

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
    return render_template('index.html')


@app.route("/archive")
def archive():
    return render_template('courseSelector.html')


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

    ordered_keys = list(OrderedDict.fromkeys(
        key for d in data[int(cid)]['data'] for key in d))

    return jsonify(ordered_keys)
    # return jsonify(data[int(cid)])


@app.route('/SemSelect/<cid>')
def selectSem(cid):
    return render_template('semselect.html')


@app.route('/subSelect/<cid>/<sem>')
def selectSub(cid, sem):
    print(cid, sem)
    return render_template('subselect.html')


@app.route('/getSub/<cid>/<sem>')
def getSub(cid, sem):
    print("Recievedd")
    # print(data[int(cid)]['data'])
    print(data[int(cid)]['data'])
    sanitized_sem = sem.replace("%20", " ")  # Convert "%20" to spaces
    print(sanitized_sem)
    for sem in data[int(cid)]['data']:
        if sanitized_sem in sem:
            print(sem[sanitized_sem])
            return sem[sanitized_sem]

    return jsonify(data[int(cid)])


if __name__ == "__main__":
    app.run(debug=True)
