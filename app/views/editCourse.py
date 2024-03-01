from flask import Blueprint, render_template,request,jsonify,current_app

# Create a blueprint instance
edit_course_bp = Blueprint('edit_course', __name__)

# Define a route for the root URL '/'
@edit_course_bp.route('/')
def index():
    # Render the index.html template
    return render_template('edit-course.html')

@edit_course_bp.route('/backend_endpoint', methods=['POST'])
def handle_form_data():
    data = request.json
    # Process the received data here
    current_app.logger.info(data)  # You can log the data to check if it's received correctly

    # Here, you can perform further processing with the data, such as saving it to a database
    
    # Send a response back to the client
    return jsonify({"message": "Data received successfully"}), 200
