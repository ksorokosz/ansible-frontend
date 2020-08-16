from flask import Flask, render_template, request
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

    # Get query string - application name
    application = "all"
    if "app" in request.args:
        application = request.args.get("app")

    # Return variables
    variables = parser.parse(path, application)
    return render_template('index.html', variables = variables, application = application)

if __name__ == '__main__':
    app.run(debug=True)
