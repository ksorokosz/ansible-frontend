from flask import Flask, render_template
from inventory_parser import InventoryParser
import os, json

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventory')
def inventory():
    
    parser = InventoryParser.InventoryParser()
    path = os.path.join("inv_example", "inventory.ini")
    variables = parser.parse(path, "master1")
    return json.dumps(variables)

if __name__ == '__main__':
    app.run(debug=True)
