from flask import Blueprint, request, jsonify

blueprint = Blueprint('data', __name__, url_prefix='/data/member')

@blueprint.route('/appointments.json', methods=['GET'])
def appointments_json():
    json = """
    [
        { 
            "start": "2006-01-01T00:00:00",
            "end": "2010-01-01T00:00:00",
            "name": "Utskottet för det ena"
        },
        { 
            "start": "2005-01-01T00:00:00",
            "end": "2010-01-01T00:00:00",
            "name": "Utskottet för det andra"
        },
        { 
            "start": "2008-01-01T00:00:00",
            "end": "2012-01-01T00:00:00",
            "name": "Utskottet för det tredje"
        }
    ]
    """

    return json