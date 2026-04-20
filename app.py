from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
import os
from config import get_config
from database import Database
from ai_processor import AIProcessor

# Initialize Flask app
app = Flask(__name__)

# Load configuration
config = get_config()
app.config.from_object(config)
config.init_app(app)

# Set secret key
app.secret_key = app.config['SECRET_KEY']

# Initialize database and AI processor
db = Database(app.config['MONGODB_URI'], app.config['MONGODB_DB_NAME'])

GROQ_API_KEY = app.config['GROQ_API_KEY']
GROQ_MODEL = app.config['GROQ_MODEL']

if not GROQ_API_KEY:
    print("\n⚠️  WARNING: Groq API key not set!")
    print("Please set GROQ_API_KEY in config.py\n")

ai = AIProcessor(GROQ_API_KEY, GROQ_MODEL)

# Allowed file extensions
ALLOWED_EXTENSIONS = app.config['ALLOWED_EXTENSIONS']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route('/')
def landing():
    """Landing page with chatbot"""
    return render_template('landing.html')

@app.route('/auth')
def auth():
    """Authentication page (login/signup/forgot password)"""
    return render_template('auth.html')

@app.route('/signup', methods=['POST'])
def signup():
    """Handle user signup"""
    try:
        data = request.get_json()
        name = data.get('name')
        mobile = data.get('mobile')
        password = data.get('password')
        
        result = db.create_user(name, mobile, password)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/login', methods=['POST'])
def login():
    """Handle user login"""
    try:
        data = request.get_json()
        mobile = data.get('mobile')
        password = data.get('password')
        
        result = db.verify_user(mobile, password)
        if result['success']:
            session.permanent = True
            session['user_id'] = result['user_id']
            session['name'] = result['name']
            session['mobile'] = result['mobile']
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Handle forgot password"""
    try:
        data = request.get_json()
        mobile = data.get('mobile')
        new_password = data.get('new_password')
        
        result = db.update_password(mobile, new_password)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    return redirect(url_for('landing'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard after login"""
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    return render_template('dashboard.html', user_name=session.get('name'))

@app.route('/task/<task_type>')
def task(task_type):
    """Task page for prescription/lab/drug"""
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    if task_type not in ['prescription', 'lab', 'drug']:
        return redirect(url_for('dashboard'))
    
    return render_template('task.html', task_type=task_type)

@app.route('/process', methods=['POST'])
def process():
    """Process user input with AI"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    try:
        task_type = request.form.get('task_type')
        language = request.form.get('language', 'English')
        
        ai_output = ""
        file_name = ""
        input_data = ""
        
        if task_type in ['prescription', 'lab']:
            # Handle file upload
            if 'file' not in request.files:
                return jsonify({'success': False, 'message': 'No file uploaded'})
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'message': 'No file selected'})
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                file_name = filename
                
                # Process with AI
                if task_type == 'prescription':
                    ai_output = ai.process_prescription(file_path, language)
                else:
                    ai_output = ai.process_lab_report(file_path, language)
                
                input_data = f"File: {filename}"
            else:
                return jsonify({'success': False, 'message': 'Invalid file type'})
        
        elif task_type == 'drug':
            # Handle drug guidance
            medicine_name = request.form.get('medicine_name')
            age = request.form.get('age')
            
            if not medicine_name or not age:
                return jsonify({'success': False, 'message': 'Please provide medicine name and age'})
            
            ai_output = ai.process_drug_guidance(medicine_name, age, language)
            input_data = f"Medicine: {medicine_name}, Age: {age}"
            file_name = "drug_guidance"
        
        # Save to history
        db.save_history(
            session['user_id'],
            task_type,
            file_name,
            input_data,
            ai_output,
            language
        )
        
        # Store in session for result page
        session['last_result'] = {
            'task_type': task_type,
            'output': ai_output,
            'language': language
        }
        
        return jsonify({'success': True, 'message': 'Processing complete'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/result')
def result():
    """Display AI processing result"""
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    if 'last_result' not in session:
        return redirect(url_for('dashboard'))
    
    result_data = session['last_result']
    return render_template('result.html', result=result_data)

@app.route('/history')
def history():
    """Get user's processing history"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    result = db.get_user_history(session['user_id'])
    return jsonify(result)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chatbot messages"""
    try:
        data = request.get_json()
        message = data.get('message')
        language = data.get('language', 'English')
        
        response = ai.chat_response(message, language)
        return jsonify({'success': True, 'response': response})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    # Create uploads folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Run application
    print(f"\n{'='*50}")
    print(f"🏥 {app.config['APP_NAME']} v{app.config['APP_VERSION']}")
    print(f"{'='*50}")
    print(f"Server: http://{app.config['HOST']}:{app.config['PORT']}")
    print(f"Debug Mode: {app.config['DEBUG']}")
    print(f"{'='*50}\n")
    
    app.run(
        debug=app.config['DEBUG'],
        host=app.config['HOST'],
        port=app.config['PORT']
    )