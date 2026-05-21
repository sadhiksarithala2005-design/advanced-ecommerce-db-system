from flask import Blueprint, request, jsonify
from extensions import mysql

products_bp = Blueprint('products', __name__)

MOCK_PRODUCTS = [
    # Electronics (5 items)
    {"Product_ID": 1, "Product_Name": "Smartphone Pro Max", "Category": "Electronics", "Price": 25000.0, "Quantity": 10, "Image_URL": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&auto=format&fit=crop&q=60"},
    {"Product_ID": 2, "Product_Name": "High-End Gaming Laptop", "Category": "Electronics", "Price": 45000.0, "Quantity": 5, "Image_URL": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=500&auto=format&fit=crop&q=60"},
    {"Product_ID": 3, "Product_Name": "Wireless Noise Cancelling Headphones", "Category": "Electronics", "Price": 3500.0, "Quantity": 15, "Image_URL": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&auto=format&fit=crop&q=60"},
    {"Product_ID": 4, "Product_Name": "Smart Watch Series 5", "Category": "Electronics", "Price": 5000.0, "Quantity": 8, "Image_URL": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&auto=format&fit=crop&q=60"},
    {"Product_ID": 5, "Product_Name": "Portable Bluetooth Speaker", "Category": "Electronics", "Price": 2500.0, "Quantity": 20, "Image_URL": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=500&auto=format&fit=crop&q=60"},

    # Clothing (5 items)
    {"Product_ID": 6, "Product_Name": "Premium Denim Jeans", "Category": "Clothing", "Price": 1999.0, "Quantity": 25, "Image_URL": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=500&auto=format&fit=crop&q=60"},
    {"Product_ID": 7, "Product_Name": "Casual Cotton T-Shirt", "Category": "Clothing", "Price": 599.0, "Quantity": 50, "Image_URL": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500&auto=format&fit=crop&q=60"},
    {"Product_ID": 8, "Product_Name": "Warm Hooded Sweatshirt", "Category": "Clothing", "Price": 1499.0, "Quantity": 12, "Image_URL": "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=500&auto=format&fit=crop&q=60"},
    {"Product_ID": 9, "Product_Name": "Sports Running Shoes", "Category": "Clothing", "Price": 2499.0, "Quantity": 18, "Image_URL": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&auto=format&fit=crop&q=60"},
    {"Product_ID": 10, "Product_Name": "Classic Leather Belt", "Category": "Clothing", "Price": 499.0, "Quantity": 30, "Image_URL": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500&auto=format&fit=crop&q=60"},

    # Books (5 items)
    {"Product_ID": 11, "Product_Name": "Introduction to Algorithms", "Category": "Books", "Price": 999.0, "Quantity": 7, "Image_URL": "https://images.unsplash.com/photo-1532012197267-da84d127e765?w=500&auto=format&fit=crop&q=60"},
    {"Product_ID": 12, "Product_Name": "Clean Code", "Category": "Books", "Price": 1200.0, "Quantity": 10, "Image_URL": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&auto=format&fit=crop&q=60"},
    {"Product_ID": 13, "Product_Name": "Atomic Habits", "Category": "Books", "Price": 399.0, "Quantity": 40, "Image_URL": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500&auto=format&fit=crop&q=60"},
    {"Product_ID": 14, "Product_Name": "The Psychology of Money", "Category": "Books", "Price": 299.0, "Quantity": 35, "Image_URL": "https://images.unsplash.com/photo-1592496431122-2349e0fbc666?w=500&auto=format&fit=crop&q=60"},
    {"Product_ID": 15, "Product_Name": "Zero to One", "Category": "Books", "Price": 450.0, "Quantity": 22, "Image_URL": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=500&auto=format&fit=crop&q=60"}
]

def get_mock_products(category, search, min_price, max_price, sort, page, limit):
    filtered = MOCK_PRODUCTS.copy()

    if category and category != 'All':
        filtered = [p for p in filtered if p['Category'] == category]

    if search:
        search_lower = search.lower()
        filtered = [p for p in filtered if search_lower in p['Product_Name'].lower()]

    if min_price:
        filtered = [p for p in filtered if p['Price'] >= float(min_price)]

    if max_price:
        filtered = [p for p in filtered if p['Price'] <= float(max_price)]

    if sort == 'price_asc':
        filtered.sort(key=lambda x: x['Price'])

    elif sort == 'price_desc':
        filtered.sort(key=lambda x: x['Price'], reverse=True)

    total = len(filtered)
    offset = (page - 1) * limit
    paginated = filtered[offset:offset + limit]

    return paginated, total


@products_bp.route('/', methods=['GET'])
def get_products():

    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    offset = (page - 1) * limit

    category = request.args.get('category')
    search = request.args.get('search')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    sort = request.args.get('sort', 'price_asc')

    try:
        query = "SELECT * FROM Products WHERE 1=1"
        params = []

        if category and category != 'All':
            query += " AND Category = %s"
            params.append(category)

        if search:
            query += " AND Product_Name LIKE %s"
            params.append(f"%{search}%")

        if min_price:
            query += " AND Price >= %s"
            params.append(float(min_price))

        if max_price:
            query += " AND Price <= %s"
            params.append(float(max_price))

        if sort == 'price_asc':
            query += " ORDER BY Price ASC"

        elif sort == 'price_desc':
            query += " ORDER BY Price DESC"

        elif sort == 'newest':
            query += " ORDER BY Created_At DESC"

        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cur = mysql.connection.cursor()
        cur.execute(query, tuple(params))
        products = cur.fetchall()

        cur.execute("SELECT COUNT(*) as total FROM Products")
        total = cur.fetchone()['total']

        cur.close()

        return jsonify({
            "products": products,
            "page": page,
            "limit": limit,
            "total": total
        }), 200

    except Exception as e:

        products, total = get_mock_products(
            category,
            search,
            min_price,
            max_price,
            sort,
            page,
            limit
        )

        return jsonify({
            "products": products,
            "page": page,
            "limit": limit,
            "total": total,
            "note": "Using mock data (MySQL connection failed)"
        }), 200


@products_bp.route('/<int:product_id>', methods=['GET'])
def get_single_product(product_id):

    try:
        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM Products WHERE Product_ID = %s",
            (product_id,)
        )

        product = cur.fetchone()

        cur.close()

        if product:
            return jsonify(product), 200

        return jsonify({"error": "Product not found"}), 404

    except Exception as e:

        product = next(
            (p for p in MOCK_PRODUCTS if p['Product_ID'] == product_id),
            None
        )

        if product:
            return jsonify(product), 200

        return jsonify({"error": "Product not found (mock)"}), 404