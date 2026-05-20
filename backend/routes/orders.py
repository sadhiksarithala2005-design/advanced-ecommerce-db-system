from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mysql

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/place', methods=['POST'])
@jwt_required()
def place_order():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    cart_items = data.get('items') # Example: [{"product_id": 1, "quantity": 2}]
    payment_method = data.get('payment_method')
    
    if not cart_items or not payment_method:
        return jsonify({"error": "Cart items and payment method are required"}), 400
        
    cur = mysql.connection.cursor()
    placed_orders = []
    
    try:
        # Loop through cart and call the Stored Procedure for each item
        for item in cart_items:
            cur.execute("CALL PlaceOrder(%s, %s, %s, %s)", 
                       (current_user_id, item['product_id'], item['quantity'], payment_method))
            result = cur.fetchone()
            placed_orders.append(result)
            
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "Order(s) placed successfully", "details": placed_orders}), 200
        
    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({"error": "Failed to place order: " + str(e)}), 500

@orders_bp.route('/my-orders', methods=['GET'])
@jwt_required()
def my_orders():
    current_user_id = get_jwt_identity()
    status_filter = request.args.get('status')
    
    query = "SELECT * FROM Orders WHERE Customer_ID = %s"
    params = [current_user_id]
    
    if status_filter:
        query += " AND Status = %s"
        params.append(status_filter)
        
    query += " ORDER BY Order_Date DESC"
    
    cur = mysql.connection.cursor()
    cur.execute(query, tuple(params))
    orders = cur.fetchall()
    cur.close()
    
    return jsonify(orders), 200
