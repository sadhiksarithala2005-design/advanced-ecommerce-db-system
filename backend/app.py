from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

from config import Config
from extensions import mysql

jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    # Initialize extensions
    mysql.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # Home Route
    @app.route('/')
    def home():
        return "Backend is running successfully!"

    # Test Route
    @app.route('/api/test-db')
    def test_db():
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT 1")
            cur.close()

            return jsonify({
                "message": "Database connection successful!"
            }), 200

        except Exception as e:
            return jsonify({
                "error": str(e)
            }), 500

    # Import Blueprints
    from routes.auth import auth_bp
    from routes.products import products_bp
    from routes.orders import orders_bp
    from routes.admin import admin_bp

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)