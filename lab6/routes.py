from flask import request, jsonify
from models.database import db
from models.electro_scooter import ElectroScooter
from __main__ import app
from flasgger import Swagger

swagger = Swagger(app)
@app.route('/api/electro-scooters', methods=['POST'])
def create_electro_scooter():
    """
    Create
    ---
    tags:
      - Electro Scooters
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: ElectroScooter
          required:
            - name
            - battery_level
          properties:
            name:
              type: string
              description: Name of the Electro Scooter
            battery_level:
              type: number
              description: Battery level of the Electro Scooter
    responses:
      201:
        description: Electro Scooter created successfully
      400:
        description: Invalid request data
    """
    try:
        data = request.get_json()

        name = data['name']
        battery_level = data['battery_level']

        electro_scooter = ElectroScooter(name=name, battery_level=battery_level)

        db.session.add(electro_scooter)
        db.session.commit()

        return jsonify({"message": "Electro Scooter created successfully"}), 201 
    except KeyError:
        return jsonify({"error": "Invalid request data"}), 400
    
@app.route('/api/electro-scooters/<int:scooter_id>', methods=['GET']) 
def get_electro_scooter_by_id(scooter_id):
    """
    Get
    ---
    tags:
      - Electro Scooters
    parameters:
      - name: scooter_id
        in: path
        type: integer
        required: true
        description: ID of the Electro Scooter
    responses:
      200:
        description: Electro Scooter found
        schema:
          id: ElectroScooter
          properties:
            id:
              type: integer
            name:
              type: string
            battery_level:
              type: number
      404:
        description: Electro Scooter not found
    """
    scooter = ElectroScooter.query.get(scooter_id)
    if scooter is not None: 
        return jsonify({
            "id": scooter.id,
            "name": scooter.name,
            "battery_level": scooter.battery_level
        }), 200 
    else:
        return jsonify({"error": "Electro Scooter not found"}), 404
    
@app.route('/api/electro-scooters/<int:scooter_id>', methods=['PUT']) 
def update_electro_scooter(scooter_id):
    """
    Update
    ---
    tags:
      - Electro Scooters
    parameters:
      - name: scooter_id
        in: path
        type: integer
        required: true
        description: ID of the Electro Scooter
      - name: body
        in: body
        required: true
        schema:
          id: ElectroScooter
          properties:
            name:
              type: string
              description: New name for the Electro Scooter
            battery_level:
              type: number
              description: New battery level for the Electro Scooter
    responses:
      200:
        description: Electro Scooter updated successfully
      404:
        description: Electro Scooter not found
      500:
        description: Internal server error
    """
    try:
        scooter = ElectroScooter.query.get(scooter_id)
        if scooter is not None:
            data = request.get_json()
            scooter.name = data.get('name', scooter.name)
            scooter.battery_level = data.get('battery_level', scooter.battery_level)
            db.session.commit()
            return jsonify({"message": "Electro Scooter updated successfully"}), 200 
        else:
            return jsonify({"error": "Electro Scooter not found"}), 404 
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/api/electro-scooters/<int:scooter_id>', methods=['DELETE']) 
def delete_electro_scooter(scooter_id):
    """
    Delete
    ---
    tags:
      - Electro Scooters
    parameters:
      - name: scooter_id
        in: path
        type: integer
        required: true
        description: ID
      - name: X-Delete-Password
        in: header
        type: string
        required: true
        description: Password for authentication
    responses:
      200:
        description: Electro Scooter deleted successfully
      401:
        description: Incorrect password
      404:
        description: Electro Scooter not found
      500:
        description: Internal server error
    """
    try:
        scooter = ElectroScooter.query.get(scooter_id)
        if scooter is not None:
            password = request.headers.get('X-Delete-Password')
            if password == 'your_secret_password':
                db.session.delete(scooter)
                db.session.commit()
                return jsonify({"message": "Electro Scooter deleted successfully"}), 200
            else:
                return jsonify({"error": "Incorrect password"}), 401
        else:
            return jsonify({"error": "Electro Scooter not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500