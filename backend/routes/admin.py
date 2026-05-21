from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from extensions import mysql

admin_bp = Blueprint('admin', __name__)


def admin_required():
    def wrapper(fn):

        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):

            current_user_id = get_jwt_identity()

            if current_user_id != 1:
                return jsonify({
                    "error": "Admin privileges required"
                }), 403

            return fn(*args, **kwargs)

        return decorator

    return wrapper


@admin_bp.route('/dashboard', methods=['GET'])
@admin_required()
def dashboard_stats():

    cur = mysql.connection.cursor()

    # Today's orders
    cur.execute(
        "SELECT COUNT(*) as count FROM Orders WHERE DATE(Order_Date) = CURDATE()"
    )

    today_orders = cur.fetchone()['count']

    # Revenue
    cur.execute(
        "SELECT SUM(Total_Amount) as sum FROM Orders WHERE Status != 'Cancelled'"
    )

    total_revenue = cur.fetchone()['sum'] or 0

    # Low stock
    cur.execute(
        "SELECT COUNT(*) as count FROM Products WHERE Quantity <= 5"
    )

    low_stock = cur.fetchone()['count']

    # Recent orders
    cur.execute("""
        SELECT
            o.Order_ID,
            c.Name,
            o.Total_Amount,
            o.Status
        FROM Orders o
        JOIN Customers c
        ON o.Customer_ID = c.Customer_ID
        ORDER BY o.Order_Date DESC
        LIMIT 5
    """)

    recent_orders = cur.fetchall()

    cur.close()

    return jsonify({
        "today_orders": today_orders,
        "total_revenue": float(total_revenue),
        "low_stock_alerts": low_stock,
        "recent_orders": recent_orders
    }), 200