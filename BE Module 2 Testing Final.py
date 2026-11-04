from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint

# Inside create_app, after registering blueprints:
@app.route("/api/spec")
def spec():
	swag = swagger(app)
	swag["info"] = {
		"title": "Your Service Shop API",
		"version": "1.0",
		"description": "API for mechanics, customers, and service tickets"
	}
	swag["securityDefinitions"] = {
		"Bearer": {
			"type": "apiKey",
			"name": "Authorization",
			"in": "header",
			"description": 'JWT Bearer token. Example: "Bearer <token>"'
		}
	}
	# Optionally add shared definitions here if not fully covered in docstrings
	# swag["definitions"] = { ... }
	return jsonify(swag)

SWAGGER_URL = "/api/docs"
API_URL = "/api/spec"
swaggerui_blueprint = get_swaggerui_blueprint(
	SWAGGER_URL,
	API_URL,
	config={"app_name": "Your Service Shop API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
@bp.route("/mechanics", methods=["POST"])
def create_mechanic():
    """
    Create a new mechanic
    ---
    tags:
      - Mechanics
    summary: Create a new mechanic
    description: Adds a mechanic with the provided name, specialty, and other details.
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: "#/definitions/MechanicPayload"
    responses:
      201:
        description: Mechanic created successfully
        schema:
          $ref: "#/definitions/MechanicResponse"
        examples:
          application/json:
            id: 1
            name: "John Doe"
            specialty: "Engine"
            # ... match your actual response fields
      400:
        description: Invalid or missing fields
      401:
        description: Missing or invalid token
    definitions:
      MechanicPayload:
        type: object
        required:
          - name
          - specialty
        properties:
          name:
            type: string
            example: "John Doe"
          specialty:
            type: string
            example: "Engine"
          # ... other real fields
      MechanicResponse:
        type: object
        properties:
          id:
            type: integer
            example: 1
          name:
            type: string
          specialty:
            type: string
          # ... match actual returned shape
    """
    # Your existing route logic here
    ...

	import unittest
from app import create_app, db
from app.models import Mechanic  # adjust import

class MechanicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")  # use a dedicated test config/DB
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        # Optional: create a test token / user for protected routes
        # self.headers = {"Authorization": f"Bearer {self.get_test_token()}"}

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_mechanics_success(self):
        # Create a record first if needed
        response = self.client.get("/mechanics")  # adjust path
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)  # or whatever shape you return

    def test_get_mechanic_by_id_not_found(self):
        response = self.client.get("/mechanics/99999")
        self.assertEqual(response.status_code, 404)
        # assert error message if your API returns one

    def test_create_mechanic_success(self):
        payload = {"name": "Test Mech", "specialty": "Brakes"}  # real required fields
        response = self.client.post("/mechanics", json=payload)  # add headers if protected
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("id", data)
        # Verify it was actually written to the DB
        with self.app.app_context():
            mech = Mechanic.query.get(data["id"])
            self.assertIsNotNone(mech)
            self.assertEqual(mech.name, "Test Mech")

    def test_create_mechanic_missing_fields(self):
        response = self.client.post("/mechanics", json={})  # missing required
        self.assertEqual(response.status_code, 400)

    def test_create_mechanic_unauthorized(self):
        # Only if the route is protected
        response = self.client.post("/mechanics", json={"name": "X", "specialty": "Y"})
        self.assertIn(response.status_code, (401, 403))

    # Repeat pattern for PUT (update + nonexistent ID + invalid payload)
    # and DELETE (success + nonexistent + unauthorized)