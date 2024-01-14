# from sqlalchemy import inspect
# from flask import Blueprint, jsonify
# # from models.counter import Counter
# from models.database import db

# counter_bp = Blueprint("counter", __name__)

# def create_counter_table():
#     # Check if the 'counter' table exists
#     inspector = inspect(db.engine)
#     table_exists = 'counter' in inspector.get_table_names()

#     if not table_exists:
#         # If the table doesn't exist, create it
#         db.create_all()

# @counter_bp.route('/counter')
# def get_counter():
#     # Create the 'counter' table if it doesn't exist
#     create_counter_table()

#     counter = Counter.query.first()
#     current_count = counter.count if counter else 0

#     return jsonify({"path": "/counter", "count": current_count})

# @counter_bp.route('/increment')
# def increment():
#     # Create the 'counter' table if it doesn't exist
#     create_counter_table()

#     counter = Counter.query.first()

#     if counter is None:
#         # If the counter doesn't exist, create it
#         counter = Counter()
#         db.session.add(counter)

#     counter.count = (counter.count or 0) + 1
#     db.session.commit()

#     return jsonify({"path": "/increment", "count": counter.count})
