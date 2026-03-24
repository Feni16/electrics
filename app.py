from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta 
from sqlalchemy import text
from collections import defaultdict
from werkzeug.utils import secure_filename
from sqlalchemy import func
from json import JSONEncoder
import os 
from dotenv import load_dotenv
import google.generativeai as genai
import random
from jinja2 import Undefined 
import json  
import secrets  
# ================= APP CONFIG =================
app = Flask(__name__)
app.secret_key = "electrics_secret_key"

# Upload folders
UPLOAD_FOLDER = "static/uploads"
PROBLEM_FOLDER = "static/uploads/problems"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["PROBLEM_FOLDER"] = PROBLEM_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# Create upload folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROBLEM_FOLDER, exist_ok=True)

# ================= LOAD ENVIRONMENT VARIABLES =================
load_dotenv()

# ================= GEMINI AI CONFIG =================
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
print(f"🔑 API Key loaded: {'✅ Yes' if GEMINI_API_KEY else '❌ No'}")

# Configure Gemini (ફક્ત આ રીતે)
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ Gemini AI configured successfully")
else:
    print("❌ No API key found!")

# ================= CUSTOM JSON ENCODER =================
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        try:
            return super().default(obj)
        except:
            return str(obj)

app.json_encoder = CustomJSONEncoder

# ================= DATABASE CONFIG =================
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/electrics'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================= HELPER FUNCTIONS =================
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_technician():
    
    
    return User.query.filter_by(role="technician").order_by(func.rand()).first()
def safe_str(value):
    """Convert any value to string safely"""
    if value is None:
        return ''
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return value
    try:
        return str(value)
    except:
        return ''
    
@app.route('/quick_add_bookings')
def quick_add_bookings():
    """Quick add bookings for testing"""
    if 'user_id' not in session or session.get('role') != 'technician':
        return "Please login as technician first"
    
    tech_id = session.get('user_id')
    
    # Customers IDs (tamara database mathi)
    customer_ids = [1, 6, 9, 13, 18, 22, 26]
    
    count = 0
    for i, cust_id in enumerate(customer_ids[:5]):
        status = ['pending', 'in_progress', 'completed'][i % 3]
        urgency = ['Normal', 'Urgent', 'Emergency'][i % 3]
        
        booking = ServiceRequest(
            customer_id=cust_id,
            technician_id=tech_id,
            service_id=(i % 5) + 1,
            title=f"Service Request #{i+1}",
            description=f"Customer needs service",
            address="Test Address",
            room=['Living', 'Kitchen', 'Bedroom'][i % 3],
            urgency=urgency,
            status=status,
            payment_amount=299 + (i*100),
            created_at=datetime.now()
        )
        db.session.add(booking)
        count += 1
    
    db.session.commit()
    return f"✅ Added {count} bookings!"
# ================= GLOBAL CONTEXT PROCESSORS =================
# ================= GLOBAL CONTEXT PROCESSORS =================
@app.context_processor
def inject_notifications():
    if 'user_id' in session:
        try:
            # Get unread count
            unread = Notification.query.filter_by(
                user_id=session['user_id'],
                is_read=False
            ).count()
            
            # Get all notifications for the user
            notifications = Notification.query.filter_by(
                user_id=session['user_id']
            ).order_by(Notification.created_at.desc()).limit(50).all()
            
            return dict(
                unread_notifications=unread,
                notifications=notifications
            )
        except:
            # If any error occurs, return empty notifications
            return dict(
                unread_notifications=0,
                notifications=[]
            )
    return dict(
        unread_notifications=0,
        notifications=[]
    )

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}
# ================= MODELS =================
# ================= MODELS =================
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default="Active")
    role = db.Column(db.String(50))
    password = db.Column(db.String(200))
    specialization = db.Column(db.String(100))
    salary = db.Column(db.Float)
    rating = db.Column(db.Float)
    address = db.Column(db.String(200)) 
    profile_image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "phone": self.phone,
            "location": self.location,
            "role": self.role,
            "status": self.status,
            "profile_image": self.profile_image,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
    
class Service(db.Model):
    __tablename__ = "service"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, default=0)

class ServiceRequest(db.Model):
    __tablename__ = "service_requests"

    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    technician_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"))

    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    address = db.Column(db.String(255))
    room = db.Column(db.String(50))
    urgency = db.Column(db.String(50))

    created_at = db.Column(db.DateTime)
    request_date = db.Column(db.Date)
    status = db.Column(db.String(50))
    payment_amount = db.Column(db.Float)

    image_filename = db.Column(db.String(255))

    service = db.relationship("Service", backref="requests")

    # ✅ ADD THESE
    customer = db.relationship("User", foreign_keys=[customer_id])
    technician = db.relationship("User", foreign_keys=[technician_id])
        
        
class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="notifications")



class ChatMessage(db.Model):
    __tablename__ = "chat_messages"
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("service_requests.id"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    booking = db.relationship("ServiceRequest", backref="chat_messages")
    sender = db.relationship("User", foreign_keys=[sender_id])
    receiver = db.relationship("User", foreign_keys=[receiver_id])
class AIChat(db.Model):
    __tablename__ = "ai_chat"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    ai_reply = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="chats")

class Feedback(db.Model):
    __tablename__ = "feedbacks"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment = db.Column(db.Text)
    rating = db.Column(db.Integer)
    likes = db.Column(db.Integer, default=0)
    ai_reply = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="feedbacks")

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("service_requests.id"), nullable=False)
    amount = db.Column(db.Float)
    technician_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    method = db.Column(db.String(50))
    status = db.Column(db.String(50), default="Paid")
    paid_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    request = db.relationship("ServiceRequest", backref="payments")
    technician = db.relationship("User", foreign_keys=[technician_id])
    
    # ================= CONTACT MESSAGE MODEL =================
class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'subject': self.subject,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
# ================= CREATE TABLES =================
with app.app_context():
    db.create_all()
    if Service.query.count() == 0:
        services = [
            Service(name="Fan Repair", price=299),
            Service(name="Switch Board Repair", price=399),
            Service(name="AC Installation", price=1499),
            Service(name="Wiring Work", price=999),
            Service(name="MCB Replacement", price=499),
        ]
        for s in services:
            db.session.add(s)
        db.session.commit()
        print("Default services added!")


# ================= ROUTES =================
@app.route("/")
def landing():
    return render_template("home.html")

# ================= login  =================

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user:
            print("DB password:", user.password)
            print("Entered password:", password)

        # ✅ Safe check
        if user and check_password_hash(user.password, password):

            session["user_id"] = user.id
            session["role"] = user.role

            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))
            elif user.role == "technician":
                return redirect(url_for("technician_dashboard"))
            else:
                return redirect(url_for("customer_dashboard"))

        else:
            flash("Invalid Email or Password", "error")  # ✅ category add kari

    return render_template("login.html")

# ==================== FORGOT PASSWORD ROUTES ====================

# Dictionary to store reset tokens (in production, use database)
reset_tokens = {}


@app.route('/forgot_password', methods=['GET','POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            flash("Passwords do not match", "error")
            return redirect(url_for('forgot_password'))

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Email not found", "error")
            return redirect(url_for('forgot_password'))

        # 🔥 IMPORTANT FIX
        user.password = generate_password_hash(password)

        db.session.commit()

        flash("Password updated successfully!", "success")
        return redirect(url_for('login'))

    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_token(token):  
    # Check if token exists and not expired
    if token not in reset_tokens:
        flash('❌ Invalid or expired reset link!', 'error')
        return redirect(url_for('forgot_password'))
    
    token_data = reset_tokens[token]
    
    if token_data['expiry'] < datetime.now():
        del reset_tokens[token]
        flash('❌ Reset link has expired!', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        
        if password != confirm:
            flash('❌ Passwords do not match!', 'error')
            return render_template('reset_password.html', token=token)
        
        if len(password) < 6:
            flash('❌ Password must be at least 6 characters!', 'error')
            return render_template('reset_password.html', token=token)
        
        # Update password
        user = User.query.get(token_data['user_id'])
        if user:
            user.password = generate_password_hash(password)
            db.session.commit()
            
            # Delete used token
            del reset_tokens[token]
            
            flash('✅ Password reset successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('❌ User not found!', 'error')
            return redirect(url_for('forgot_password'))
    
    return render_template('reset_password.html', token=token)
@app.route('/contact', methods=['GET', 'POST'])
def contact():

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        new_msg = ContactMessage(
            name=name,
            email=email,
            message=message
        )

        db.session.add(new_msg)
        db.session.commit()

        flash("Message sent successfully!", "success")
        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/reset_password_direct', methods=['POST'])
def reset_password_direct():
    password = request.form.get('password')
    confirm = request.form.get('confirm_password')
    
    if password != confirm:
        flash('❌ Passwords do not match!', 'error')
        return redirect(url_for('forgot_password'))
    
    if len(password) < 6:
        flash('❌ Password must be at least 6 characters!', 'error')
        return redirect(url_for('forgot_password'))
    
    # Yahan tum direct kisi ko reset kar sakte ho
    # Jaise pehle user ko find karo
    
    flash('✅ Password reset successful! Please login.', 'success')
    return redirect(url_for('login'))


@app.route('/api/user/<int:user_id>')
def api_get_user(user_id):
    """Get user details by ID for technician view"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if session.get('role') != 'technician' and session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'phone': user.phone,
        'location': user.location,
        'address': user.address,
        'status': user.status,
        'role': user.role,
        'profile_image': user.profile_image,
        'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None
    })
# ================= AUTH ROUTES =================
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        phone = request.form["phone"]
        role = request.form["role"]
        password = request.form["password"]
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists! Please choose another username.", "error")
            return redirect(url_for("register"))
        
        # Check if email already exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash("Email already registered! Please use another email or login.", "error")
            return redirect(url_for("register"))
        
        hashed_password = generate_password_hash(password)
        
        user = User(
            username=username,
            email=email,
            phone=phone,
            role=role,
            password=hashed_password
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # ===== AUTO LOGIN AFTER REGISTRATION =====
            session["user_id"] = user.id
            session["role"] = user.role
            
            flash(f"Welcome {username}! Registration successful!", "success")
            
            # Redirect based on role
            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))
            elif user.role == "technician":
                return redirect(url_for("technician_dashboard"))
            else:  # customer
                return redirect(url_for("customer_dashboard"))
                
        except Exception as e:
            db.session.rollback()
            flash(f"Registration failed: {str(e)}", "error")
            return redirect(url_for("register"))
    
    return render_template("register.html")

@app.route('/delete_duplicate_user/<username>')
def delete_duplicate_user(username):
    """Delete user by username (admin only)"""
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=username).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return f"User {username} deleted successfully!"
    return f"User {username} not found!"
# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))
# ================= CUSTOMER ROUTES =================
@app.route("/customer/dashboard")
def customer_dashboard():
    if "user_id" not in session or session.get("role") != "customer":
        return redirect(url_for("login"))
    
    user = db.session.get(User, session["user_id"])
    if not user:
        return redirect(url_for("login"))
    
    services = Service.query.all()
    bookings = ServiceRequest.query.filter_by(customer_id=user.id).all()
    total_spent = db.session.query(
    db.func.sum(Payment.amount)
    ).join(ServiceRequest, Payment.request_id == ServiceRequest.id).filter(
    ServiceRequest.customer_id == session["user_id"]
    ).scalar() or 0
    
    return render_template(
    "customer_dashboard.html",
    user=user,
    services=services,
    bookings=bookings,
    total_bookings=len(bookings),
    pending_count=sum(1 for b in bookings if b.status == "pending"),
    completed_count=sum(1 for b in bookings if b.status == "completed"),
    total_spent=total_spent
)

# ==================== AI CHAT ROUTES ====================

@app.route('/chat', methods=['POST'])
def chat():
    """Handle AI chat messages"""
    if 'user_id' not in session:
        return jsonify({'reply': 'Please login first!'})
    
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'reply': 'Please enter a message'})
        
        # Simple AI response logic (you can enhance this)
        ai_reply = generate_ai_response(user_message)
        
        # Save to database
        chat = AIChat(
            user_id=session['user_id'],
            user_message=user_message,
            ai_reply=ai_reply,
            created_at=datetime.now()
        )
        db.session.add(chat)
        db.session.commit()
        
        return jsonify({'reply': ai_reply})
        
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({'reply': 'Sorry, something went wrong!'})

@app.route('/chat-history')
def chat_history():
    """Get user's chat history"""
    if 'user_id' not in session:
        return jsonify({'history': []})
    
    try:
        limit = request.args.get('limit', 50, type=int)
        
        chats = AIChat.query.filter_by(
            user_id=session['user_id']
        ).order_by(
            AIChat.created_at.desc()
        ).limit(limit).all()
        
        history = []
        for chat in chats:
            history.append({
                'id': chat.id,
                'user_message': chat.user_message,
                'ai_reply': chat.ai_reply,
                'created_at': chat.created_at.isoformat() if chat.created_at else None
            })
        
        return jsonify({'history': history})
        
    except Exception as e:
        print(f"Chat history error: {str(e)}")
        return jsonify({'history': []})

def generate_ai_response(message):
    """Smart AI Response without API Key - Full Version"""
    try:
        msg_lower = message.lower()
        
        # ==================== FAN PROBLEMS ====================
        if "fan" in msg_lower or "પંખો" in msg_lower:
            if "not working" in msg_lower or "band" in msg_lower or "બંધ" in msg_lower or "nthi" in msg_lower or "નથી" in msg_lower:
                return """🔧 Fan Problem Solution:

📌 Step-by-Step Check:
1️⃣ Check if switch is ON
2️⃣ Check regulator position (turn to maximum)
3️⃣ Listen for any humming sound
4️⃣ If humming but not rotating → Capacitor issue
5️⃣ If no sound → Motor or wiring issue

💰 Estimated Cost: ₹299 - ₹599

🔧 Need a technician? 
Click "My Bookings" → "Book New Service" → Select "Fan Repair"

📞 Emergency: +91 98765 43210"""
            
            elif "slow" in msg_lower or "ધીમો" in msg_lower:
                return """🐢 Fan Running Slow?

Possible Causes:
• Regulator faulty
• Capacitor weak
• Low voltage
• Motor winding issue

Solution: First try with a different regulator. If still slow, capacitor needs replacement.

💰Capacitor Replacement: ₹299 only

🔧 Book a technician from "My Bookings" section!"""
            
            else:
                return """🔧Fan Issues?

I can help with:
• Fan not working
• Fan running slow
• Fan making noise
Tell me exactly what problem you're facing!

Example: "fan not working" or "fan slow" """

        # ==================== SWITCH PROBLEMS ====================
        elif "switch" in msg_lower or "સ્વીચ" in msg_lower:
            if "spark" in msg_lower or "સ્પાર્ક" in msg_lower:
                return """⚠️ ⚠️ DANGER - SPARKING ISSUE! ⚠️

🚨 IMMEDIATE ACTION:
1. TURN OFF MAIN POWER SWITCH NOW!
2. DO NOT touch the sparking switch
3. DO NOT use that socket again
4. Call technician immediately

📞 Emergency Helpline:+91 98765 43210

🔧 Book Emergency Service: Click "Book Service" → Select "Switch Board Repair"

Safety First! Don't try to fix it yourself!"""
            
            elif "not working" in msg_lower or "band" in msg_lower or "બંધ" in msg_lower or "nthi" in msg_lower:
                return """🔌 Switch Not Working?

Possible Causes:
• Loose connection
• Fuse blown
• Switch mechanism damaged
• MCB tripped

Check:First check if MCB is ON. If still not working, switch needs replacement.

💰 Switch Replacement: ₹399 (including labor)

🔧 Book Switch Board Repair from your dashboard!"""
            
            else:
                return """🔌 Switch / Socket Issues?

I can help with:
• Switch not working
• Sparking from switch
• Loose socket
• Damaged switch

Tell me exactly what problem you're facing!

Example: "Switch is sparking" or "Switch not working" """

        # ==================== AC PROBLEMS ====================
        elif "ac" in msg_lower or "એસી" in msg_lower:
            if "not cooling" in msg_lower or "gas" in msg_lower or "ઠંડી" in msg_lower or "ગેસ" in msg_lower:
                return """❄️ AC Not Cooling / Gas Issue:

Check These First:
✅ AC mode set to COOL (not fan/auto)
✅ Temperature set to 16-24°C
✅ Air filters cleaned
✅ Outdoor unit not blocked

If still not cooling:
• Gas might be low (need refilling)
• Compressor issue
• Condenser dirty

💰Gas Refilling Cost: ₹1499 - ₹2499

🔧 Book AC Service from "My Bookings" section!"""
            
            elif "water" in msg_lower or "leak" in msg_lower or "પાણી" in msg_lower:
                return """💧 AC Water Leaking?

Reasons:
• Drain pipe blocked
• Installation angle wrong
• Air filter dirty
• Gas low

Quick Fix: Clean the drain pipe. If still leaking, technician needed.

📞 Call technician immediately!"""
            
            else:
                return """❄️ AC Issues?

I can help with:
• AC not cooling
• Gas refilling
• Water leakage
• Strange noise

Tell me your problem!Example: "AC not cooling" """

        # ==================== WIRING PROBLEMS ====================
        elif "wiring" in msg_lower or "વાયરિંગ" in msg_lower or "wire" in msg_lower:
            return """🔌Wiring Services Available:

✅ Complete House Wiring
✅ Short Circuit Repair
✅ New Connection Installation
✅ Wire Replacement

💰Prices: Starting ₹999
⏱️Timeline: Same day service

📅 Book a technician from "My Bookings" section!"""

        # ==================== BOOKING HELP ====================
        elif "book" in msg_lower or "booking" in msg_lower or "બુક" in msg_lower:
            return """📅 How to Book a Service:

Step-by-Step:
1️⃣ Login to your account
2️⃣ Go to Dashboard
3️⃣ Click "My Bookings"
4️⃣ Click "Book New Service"
5️⃣ Choose service:
   • Fan Repair (₹299)
   • Switch Board (₹399)
   • AC Installation (₹1499)
   • Wiring Work (₹999)
   • MCB Replacement (₹499)
6️⃣ Fill address and schedule time

✅ Technician will contact you within 2 hours!"""

        # ==================== PAYMENT HELP ====================
        elif "payment" in msg_lower or "pay" in msg_lower or "upi" in msg_lower:
            return """💳 Payment Options:

✅Available Payment Methods:
• QR Code Scan (UPI)
• Google Pay / PhonePe
• Cash on Service

📱How to Pay:
1. After service completion
2. Scan QR code shown
3. Enter amount
4. Complete payment

✅ Payment receipt will be sent to your email"""

        # ==================== GREETINGS ====================
        elif any(word in msg_lower for word in ["hi", "hello", "hey", "હાય", "હેલો", "namaste"]):
            return """🙏 Namaste! Welcome to TechnoFix 👋

I'm your AI Assistant. How can I help you today?

🔧 I can help with:
• Fan not working
• Switch board issues
• AC not cooling
• Wiring problems
• Book technician
• Payment help

Just type your problem! 
Example: "My fan is not working" or "Switch sparking"

I'll help you step by step! 💪"""

        # ==================== THANKS / BYE ====================
        elif any(word in msg_lower for word in ["thanks", "thank you", "આભાર", "bye"]):
            return """🙏 You're welcome!😊

📞 Need more help? Call: +91 98765 43210
📱 Book a service: Click "My Bookings"

Have a great day! 🌟"""

        # ==================== DEFAULT ====================
        else:
            return """🙏 I'm TechnoFix AI Assistant!

I can help with:
🔧 Fan not working
⚡ Switch sparking / not working
❄️ AC not cooling / gas issue
🔌 Wiring issues
📅 Book technician
💳 Payment help

Type your problem!

Example:
• "fan not working"
• "switch sparking"
• "ac not cooling"
• "how to book service"

I'll give you step-by-step solution! 💪"""
            
    except Exception as e:
        print(f"AI Error: {str(e)}")
        return """🙏 TechnoFix AI Assistant

I'm here to help! Please tell me your problem:

• Fan not working
• Switch not working
• AC not cooling
• Book a technician

Type your question and I'll assist you! 😊"""
        # Generate response
        response = model.generate_content(
            f"{system_prompt}\n\nUser: {message}\n\nAssistant:"
        )
        
        if response and response.text:
            return response.text
        else:
            return "I'm here to help! Could you please provide more details about your problem?"
            
    except Exception as e:
        print(f"❌ Gemini API Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"I'm having trouble connecting. Please try again in a moment."
    
# ================= AI CHAT PAGE =================
@app.route('/ai-chat')
def ai_chat_page():
    """Show AI chat page"""
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))
    
    return render_template('ai_chat.html')
# ==================== CUSTOMER AI CHAT HISTORY VIEW ====================

@app.route('/customer/chat-history')
def customer_chat_history():
    """View full chat history page for customer"""
    if session.get('role') != 'customer':
        return redirect(url_for('login'))
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        chats = AIChat.query.filter_by(
            user_id=session['user_id']
        ).order_by(
            AIChat.created_at.desc()
        ).paginate(page=page, per_page=per_page)
        
        return render_template(
            'customer_chat_history.html',
            chats=chats.items,
            total_pages=chats.pages,
            current_page=page
        )
        
    except Exception as e:
        print(f"Error: {str(e)}")
        flash('Error loading chat history', 'danger')
        return redirect(url_for('customer_dashboard'))

# ==================== CHAT ROUTES ====================
@app.route('/get_chat_messages/<int:booking_id>')
def get_chat_messages(booking_id):
    """Get all chat messages for a booking"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    
    # Verify booking belongs to user
    booking = ServiceRequest.query.get_or_404(booking_id)
    if booking.customer_id != user_id and booking.technician_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get messages ordered by time
    messages = ChatMessage.query.filter_by(booking_id=booking_id).order_by(ChatMessage.created_at).all()
    
    message_list = []
    for msg in messages:
        sender = User.query.get(msg.sender_id)
        receiver = User.query.get(msg.receiver_id)
        
        # Fix NULL receiver_id if needed
        if not msg.receiver_id:
            if msg.sender_id == booking.customer_id and booking.technician_id:
                msg.receiver_id = booking.technician_id
            elif msg.sender_id == booking.technician_id and booking.customer_id:
                msg.receiver_id = booking.customer_id
            db.session.commit()
        
        message_list.append({
            'id': msg.id,
            'message': msg.message,
            'sender_id': msg.sender_id,
            'receiver_id': msg.receiver_id,
            'sender_name': sender.username if sender else 'Unknown',
            'receiver_name': receiver.username if receiver else 'Unknown',
            'is_read': msg.is_read,
            'created_at': msg.created_at.strftime('%I:%M %p, %d %b') if msg.created_at else ''
        })
    
    # Mark messages as read for current user
    unread = ChatMessage.query.filter_by(
        booking_id=booking_id,
        receiver_id=user_id,
        is_read=False
    ).all()
    
    for msg in unread:
        msg.is_read = True
    
    if unread:
        db.session.commit()
    
    return jsonify({'messages': message_list})


@app.route('/send_chat_message', methods=['POST'])
def send_chat_message():
    """Send a chat message - FIXED VERSION"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    try:
        data = request.get_json()
        booking_id = data.get('booking_id')
        message = data.get('message')
        
        if not booking_id or not message:
            return jsonify({'success': False, 'error': 'Missing data'}), 400
        
        # Get booking
        booking = ServiceRequest.query.get(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        current_user_id = session['user_id']
        current_user = User.query.get(current_user_id)
        
        # Determine receiver ID
        if current_user_id == booking.customer_id:
            # Customer is sending to technician
            receiver_id = booking.technician_id
            sender_role = 'customer'
        elif current_user_id == booking.technician_id:
            # Technician is sending to customer
            receiver_id = booking.customer_id
            sender_role = 'technician'
        else:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Check if receiver exists
        if not receiver_id:
            # Try to assign technician if not assigned
            if sender_role == 'customer' and not booking.technician_id:
                technician = User.query.filter_by(role='technician').first()
                if technician:
                    booking.technician_id = technician.id
                    receiver_id = technician.id
                    db.session.commit()
                else:
                    return jsonify({'success': False, 'error': 'No technician assigned'}), 400
            else:
                return jsonify({'success': False, 'error': 'Receiver not found'}), 400
        
        # Save message
        chat_msg = ChatMessage(
            booking_id=booking_id,
            sender_id=current_user_id,
            receiver_id=receiver_id,
            message=message,
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.session.add(chat_msg)
        
        # Create notification for receiver
        notification = Notification(
            user_id=receiver_id,
            message=f"💬 New message from {current_user.username} about booking #{booking_id}: {message[:50]}",
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Message sent',
            'data': {
                'id': chat_msg.id,
                'message': chat_msg.message,
                'created_at': chat_msg.created_at.strftime('%I:%M %p, %d %b')
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in send_chat_message: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/mark_messages_read/<int:booking_id>', methods=['POST'])
def mark_messages_read(booking_id):
    """Mark all messages in a booking as read"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    ChatMessage.query.filter_by(
        booking_id=booking_id,
        receiver_id=session['user_id'],
        is_read=False
    ).update({'is_read': True})
    
    db.session.commit()
    return jsonify({'success': True})



# ==================== CREATE CHAT TABLE ====================
@app.route('/create_chat_table')
def create_chat_table():
    """Create chat messages table"""
    try:
        # Check if table exists
        inspector = db.inspect(db.engine)
        if 'chat_messages' not in inspector.get_table_names():
            ChatMessage.__table__.create(db.engine)
            return "✅ Chat messages table created successfully!"
        else:
            return "ℹ️ Chat messages table already exists."
    except Exception as e:
        return f"❌ Error: {str(e)}"
    
# ==================== ADMIN CHAT DETAILS VIEW ====================

@app.route('/admin/chat/<int:chat_id>')
def admin_chat_details(chat_id):
    """View single chat details for admin"""
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    chat = AIChat.query.get_or_404(chat_id)
    user = User.query.get(chat.user_id)
    
    return render_template(
        'admin_chat_details.html',
        chat=chat,
        user=user
    )

# ==================== DELETE CHAT ====================

@app.route('/admin/chat/<int:chat_id>/delete', methods=['POST'])
def admin_delete_chat(chat_id):
    """Delete a chat (admin only)"""
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    try:
        chat = AIChat.query.get_or_404(chat_id)
        db.session.delete(chat)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== CLEAR ALL CHATS ====================

@app.route('/admin/clear-chats', methods=['POST'])
def admin_clear_chats():
    """Clear all AI chats (admin only)"""
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    try:
        AIChat.query.delete()
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
#================= BOOK SERVICE ROUTE =================
# ================= BOOK SERVICE ROUTE =================
@app.route('/book_service', methods=['POST'])
def book_service():
    if not session.get("user_id"):
        flash("Please login first!", "danger")
        return redirect(url_for("login"))

    try:
        service_id = request.form.get("service_id")
        title = request.form.get("title")
        description = request.form.get("description")
        address = request.form.get("address")
        room = request.form.get("room")
        urgency = request.form.get("urgency")
        
        if not all([service_id, title, address, room, urgency]):
            flash("Please fill all required fields!", "danger")
            return redirect(url_for("customer_my_booking"))

        service = Service.query.get(service_id)
        if not service:
            flash("Service not found!", "danger")
            return redirect(url_for("customer_my_booking"))

        # Get available technician
        technician = get_technician()
        if not technician:
            flash("No technicians available!", "warning")
            return redirect(url_for("customer_my_booking"))

        customer = User.query.get(session["user_id"])
        if not customer:
            flash("Customer not found!", "danger")
            return redirect(url_for("logout"))

        # Create booking
        new_request = ServiceRequest(
            customer_id=customer.id,
            technician_id=technician.id,
            service_id=service.id,
            title=title,
            description=description,
            address=address,
            room=room,
            urgency=urgency,
            status="pending",
            payment_amount=service.price,
            created_at=datetime.now() 
        )
        db.session.add(new_request)
        db.session.flush()
        
        print(f"✅ Booking created with ID: {new_request.id}")

        # ===== IMPORTANT: Create notification for technician =====
        tech_notification = Notification(
    user_id=technician.id,  # ← AA SAHI HOVU JOIYE (technician nu ID)
    message=f"🔔 New booking #{new_request.id} from {customer.username} for {service.name}",
    is_read=False,
    created_at=datetime.utcnow()
         )
        db.session.add(tech_notification)

        # ===== Create notification for customer =====
        cust_notification = Notification(
    user_id=customer.id,  # ← AA SAHI HOVU JOIYE (customer nu ID)
    message=f"✅ Your booking #{new_request.id} for {service.name} has been created",
    is_read=False,
    created_at=datetime.utcnow()
        )
        db.session.add(cust_notification)

        db.session.commit()
        
        print(f"✅ Notification created for technician {technician.id}")
        flash("✅ Booking created successfully!", "success")

    except Exception as e:
        db.session.rollback()
        print(f"❌ ERROR: {str(e)}")
        flash(f"Error creating booking: {str(e)}", "danger")

    return redirect(url_for("customer_my_booking"))

@app.route('/get_all_notifications')
def get_all_notifications():
    """Get ALL notifications for technician dashboard"""
    if 'user_id' not in session:
        return jsonify({'notifications': []})
    
    try:
        # Simple query - badhi notifications lao
        from sqlalchemy import text
        
        sql = text("""
            SELECT n.*, u.username 
            FROM notifications n
            LEFT JOIN users u ON n.user_id = u.id
            ORDER BY n.id DESC 
            LIMIT 100
        """)
        
        result = db.session.execute(sql)
        
        notif_list = []
        for row in result:
            row_dict = dict(row._mapping)
            
            created_at_str = ''
            if row_dict.get('created_at'):
                try:
                    dt = row_dict['created_at']
                    created_at_str = dt.strftime('%I:%M %p, %d %b %Y')
                except:
                    created_at_str = str(row_dict['created_at'])
            
            notif_list.append({
                'id': row_dict['id'],
                'message': row_dict['message'],
                'created_at': created_at_str,
                'user_id': row_dict['user_id'],
                'username': row_dict.get('username', 'System'),
                'is_read': bool(row_dict['is_read'])
            })
        
        return jsonify({'notifications': notif_list})
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'notifications': []})
    
    
@app.route('/debug_technician_customers')
def debug_technician_customers():
    """Debug technician customers route"""
    if 'user_id' not in session or session.get('role') != 'technician':
        return "Please login as technician first"
    
    technician_id = session.get('user_id')
    
    output = "<h2>🔍 Technician Customers Debug</h2>"
    
    # 1. Technician info
    technician = User.query.get(technician_id)
    output += f"<p><b>Technician:</b> {technician.username} (ID: {technician_id})</p>"
    
    # 2. All customers
    customers = User.query.filter_by(role='customer').all()
    output += f"<h3>Total Customers in DB: {len(customers)}</h3>"
    output += "<table border='1' cellpadding='5'><tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th></tr>"
    for c in customers:
        output += f"<tr><td>{c.id}</td><td>{c.username}</td><td>{c.email}</td><td>{c.phone}</td></tr>"
    output += "</table>"
    
    # 3. Technician's bookings
    bookings = ServiceRequest.query.filter_by(technician_id=technician_id).all()
    output += f"<h3>Technician's Bookings: {len(bookings)}</h3>"
    output += "<table border='1' cellpadding='5'><tr><th>Booking ID</th><th>Customer ID</th><th>Status</th></tr>"
    for b in bookings:
        output += f"<tr><td>{b.id}</td><td>{b.customer_id}</td><td>{b.status}</td></tr>"
    output += "</table>"
    
    return output

# ================= TECHNICIAN UPDATE PROFILE =================
@app.route('/technician/update_profile', methods=['POST'])
def technician_update_profile():
    """Update technician profile"""
    if "user_id" not in session or session.get('role') != 'technician':
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    if not user:
        return redirect(url_for("login"))

    try:
        # Current values fetch karo
        current_user = User.query.get(session["user_id"])
        
        # Form values lo
        username = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        location = request.form.get("location")
        address = request.form.get("address")
        specialization = request.form.get("specialization")
        
        # Update with existing values if empty
        user.username = username if username and username.strip() else current_user.username
        user.email = email if email and email.strip() else current_user.email
        user.phone = phone if phone and phone.strip() else current_user.phone
        user.location = location if location and location.strip() else current_user.location
        user.address = address if address and address.strip() else current_user.address
        
        if specialization and specialization.strip():
            user.specialization = specialization

        # Profile image upload
        if "photo" in request.files:
            file = request.files["photo"]
            if file and file.filename and file.filename.strip() != "":
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    import time
                    unique_filename = f"{int(time.time())}_{filename}"
                    file.save(os.path.join(app.config["UPLOAD_FOLDER"], unique_filename))
                    user.profile_image = unique_filename

        db.session.commit()
        flash("✅ Profile updated successfully!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error updating profile: {str(e)}", "danger")

    return redirect(url_for('technician_profile'))
#========check =========#
@app.route('/check_notifications')
def check_notifications():
    """Check unread notification count"""
    if 'user_id' not in session:
        return jsonify({'unread': 0})
    
    try:
        # Direct SQL for debugging
        from sqlalchemy import text
        sql = text("SELECT COUNT(*) FROM notifications WHERE user_id = :user_id AND is_read = 0")
        result = db.session.execute(sql, {'user_id': session['user_id']})
        count = result.scalar() or 0
        
        print(f"🔔 Unread count for user {session['user_id']}: {count}")
        
        return jsonify({'unread': count})
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'unread': 0})

@app.route('/mark_notifications_read', methods=['POST'])
def mark_notifications_read():
    """Mark all notifications as read"""
    if 'user_id' not in session:
        return jsonify({'success': False})
    
    try:
        from sqlalchemy import text
        sql = text("UPDATE notifications SET is_read = 1 WHERE user_id = :user_id")
        db.session.execute(sql, {'user_id': session['user_id']})
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False})

@app.route('/mark_notification_read/<int:notification_id>', methods=['POST'])
def mark_notification_read(notification_id):
    """Mark single notification as read"""
    if 'user_id' not in session:
        return jsonify({'success': False})
    
    try:
        from sqlalchemy import text
        sql = text("UPDATE notifications SET is_read = 1 WHERE id = :id AND user_id = :user_id")
        db.session.execute(sql, {'id': notification_id, 'user_id': session['user_id']})
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False})

@app.route('/create_test_notification')
def create_test_notification():
    """Create test notification for current technician"""
    if 'user_id' not in session:
        return "Please login first"
    
    try:
        from sqlalchemy import text
        sql = text("""
            INSERT INTO notifications (user_id, message, is_read, created_at) 
            VALUES (:user_id, :message, 0, NOW())
        """)
        db.session.execute(sql, {
            'user_id': session['user_id'],
            'message': f'🔔 Test notification at {datetime.now().strftime("%H:%M:%S")}'
        })
        db.session.commit()
        return "✅ Test notification created!"
    except Exception as e:
        return f"❌ Error: {str(e)}"

#================= BOOKING HISTORY =================
@app.route("/booking-history")
@app.route("/customer/booking-history")
def booking_history():
    """View single booking details"""
    if session.get("role") != "customer":
        return redirect(url_for("login"))
    
    booking_id = request.args.get('id')
    if not booking_id:
        flash("No booking ID provided", "danger")
        return redirect(url_for("customer_my_booking"))
    
    booking = ServiceRequest.query.get_or_404(booking_id)
    
    # Verify this booking belongs to logged-in customer
    if booking.customer_id != session["user_id"]:
        flash("Unauthorized access", "danger")
        return redirect(url_for("customer_my_booking"))
    
    return render_template("booking_details.html", booking=booking)

#================= FIX TECHNICIAN ID FOR EXISTING BOOKINGS =================
@app.route('/fix_technician_id_for_bookings')
def fix_technician_id_for_bookings():
    """Booking ma technician ID set karo"""
    
    # Pehlo technician shodho
    technician = User.query.filter_by(role='technician').first()
    
    if not technician:
        return "❌ Pehla technician create karo!"
    
    # Badha booking ma technician_id update karo jyare NULL hoy
    bookings = ServiceRequest.query.filter(
        ServiceRequest.technician_id.is_(None)
    ).all()
    
    count = 0
    for booking in bookings:
        booking.technician_id = technician.id
        count += 1
    
    db.session.commit()
    
    return f"✅ {count} bookings ma technician_id = {technician.id} set karyo!"


# ==================== FIX CHAT FOR BOOKING #32 ====================
@app.route('/fix_chat_for_booking_32', methods=['POST'])
def fix_chat_for_booking_32():
    """Fix chat messages for booking #32"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    booking = ServiceRequest.query.filter_by(id=32).first()
    if not booking:
        return "Booking #32 not found!"
    
    # Get technician
    if booking.technician_id:
        technician = User.query.get(booking.technician_id)
    else:
        # Assign first technician
        technician = User.query.filter_by(role='technician').first()
        if technician:
            booking.technician_id = technician.id
            db.session.commit()
    
    if not technician:
        return "No technician found!"
    
    # Fix all messages for this booking
    messages = ChatMessage.query.filter_by(booking_id=32).all()
    fixed_count = 0
    
    for msg in messages:
        # Fix receiver_id
        if msg.sender_id == booking.customer_id:
            # Customer sent message - receiver should be technician
            if msg.receiver_id != technician.id:
                msg.receiver_id = technician.id
                fixed_count += 1
        elif msg.sender_id == technician.id:
            # Technician sent message - receiver should be customer
            if msg.receiver_id != booking.customer_id:
                msg.receiver_id = booking.customer_id
                fixed_count += 1
    
    db.session.commit()
    
    return f"✅ Fixed {fixed_count} messages for booking #32! <br><br><a href='/debug_chat_issue'>← Back</a>"

@app.route('/fix_chat_table', methods=['POST'])
def fix_chat_table():
    """Fix chat_messages table structure"""
    try:
        # Check if receiver_id column exists and is NOT NULL
        from sqlalchemy import inspect, text
        
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('chat_messages')]
        
        output = "<h2>🔧 Chat Table Fix</h2>"
        
        if 'receiver_id' not in columns:
            # Add receiver_id column if missing
            db.session.execute(text("""
                ALTER TABLE chat_messages 
                ADD COLUMN receiver_id INT NULL AFTER sender_id
            """))
            output += "<p style='color:#22c55e;'>✅ Added receiver_id column</p>"
        
        # Make sure columns are properly set
        db.session.execute(text("""
            ALTER TABLE chat_messages 
            MODIFY receiver_id INT NOT NULL DEFAULT 0
        """))
        output += "<p style='color:#22c55e;'>✅ Modified receiver_id to NOT NULL</p>"
        
        # Fix any NULL receiver_ids
        db.session.execute(text("""
            UPDATE chat_messages cm
            JOIN service_requests sr ON cm.booking_id = sr.id
            SET cm.receiver_id = CASE 
                WHEN cm.sender_id = sr.customer_id THEN sr.technician_id
                WHEN cm.sender_id = sr.technician_id THEN sr.customer_id
                ELSE 0
            END
            WHERE cm.receiver_id IS NULL OR cm.receiver_id = 0
        """))
        output += "<p style='color:#22c55e;'>✅ Fixed NULL receiver_ids</p>"
        
        db.session.commit()
        
        output += "<p style='color:#22c55e;'>✅ All fixes applied!</p>"
        output += "<br><a href='/debug_chat_issue'>← Back to Debug</a>"
        
        return output
        
    except Exception as e:
        db.session.rollback()
        return f"<p style='color:#ef4444;'>❌ Error: {str(e)}</p>"


@app.route('/fix_all_technician_ids')
def fix_all_technician_ids():
    """Fix technician_id for all bookings"""
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    # Get all technicians
    technicians = User.query.filter_by(role='technician').all()
    if not technicians:
        return "❌ No technicians found!"
    
    import random
    fixed_count = 0
    
    # Find bookings with NULL technician_id
    bookings = ServiceRequest.query.filter(
        ServiceRequest.technician_id.is_(None)
    ).all()
    
    for booking in bookings:
        # Assign random technician
        tech = random.choice(technicians)
        booking.technician_id = tech.id
        fixed_count += 1
        
        # Also fix any chat messages
        messages = ChatMessage.query.filter_by(booking_id=booking.id).all()
        for msg in messages:
            if msg.sender_id == booking.customer_id:
                msg.receiver_id = tech.id
            elif msg.sender_id == tech.id:
                msg.receiver_id = booking.customer_id
    
    db.session.commit()
    
    return f"✅ Fixed {fixed_count} bookings with technician IDs!"
# ==================== BOOKING DETAILS ROUTE ====================
# Keep this one (around line 834)
@app.route('/booking-details/<int:booking_id>')
def booking_details(booking_id):
    """View single booking details"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    booking = ServiceRequest.query.get_or_404(booking_id)
    
    # Verify this booking belongs to logged-in customer
    if booking.customer_id != session['user_id']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('customer_dashboard'))
    
    return render_template('booking_detail.html', booking=booking)

# Remove the duplicate at line 1223
# OR rename it if you need different functionality
# ================= GET CUSTOMER BOOKINGS API =================
@app.route('/api/customer/<int:customer_id>/bookings')
def get_customer_bookings(customer_id):
    if session.get("role") != "admin":
        return jsonify({'error': 'Unauthorized'}), 401
    
    bookings = ServiceRequest.query.filter_by(customer_id=customer_id).order_by(ServiceRequest.created_at.desc()).all()
    booking_list = []
    
    for b in bookings:
        service = Service.query.get(b.service_id)
        booking_list.append({
            'id': b.id,
            'title': b.title,
            'status': b.status,
            'payment_amount': float(b.payment_amount) if b.payment_amount else 0,
            'created_at': b.created_at.strftime('%Y-%m-%d %H:%M:%S') if b.created_at else None,
            'service_name': service.name if service else 'Unknown'
        })
    
    return jsonify(booking_list)
#================= AJAX ROUTE FOR BOOKING =================
@app.route('/book_service_ajax', methods=['POST'])
def book_service_ajax():
    """AJAX request માટે booking create કરો"""
    if not session.get("user_id"):
        return jsonify({'success': False, 'message': 'Please login first!'})

    try:
        # Form data લો
        service_id = request.form.get("service_id")
        title = request.form.get("title")
        description = request.form.get("description")
        address = request.form.get("address")
        room = request.form.get("room")
        urgency = request.form.get("urgency")
        
        # Validation
        if not all([service_id, title, address, room, urgency]):
            return jsonify({'success': False, 'message': 'Please fill all required fields!'})

        service = Service.query.get(service_id)
        if not service:
            return jsonify({'success': False, 'message': 'Service not found!'})

        # ===== FIXED: RANDOM TECHNICIAN SELECT =====
        technicians = User.query.filter_by(role="technician").all()
        if not technicians:
            return jsonify({'success': False, 'message': 'No technicians available!'})
        
        # Select random technician
        import random
        technician = random.choice(technicians)
        print(f"✅ Selected technician: {technician.username} (ID: {technician.id})")

        customer = User.query.get(session["user_id"])
        if not customer:
            return jsonify({'success': False, 'message': 'Customer not found!'})

        # ===== IMAGE UPLOAD HANDLING =====
        image_filename = None
        if 'problem_image' in request.files:
            file = request.files['problem_image']
            if file and file.filename and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    import time
                    unique_filename = f"{int(time.time())}_{filename}"
                    file_path = os.path.join(app.config['PROBLEM_FOLDER'], unique_filename)
                    file.save(file_path)
                    image_filename = unique_filename
                    print(f"✅ Image uploaded: {unique_filename}")

        # Booking create કરો
        new_request = ServiceRequest(
            customer_id=customer.id,
            technician_id=technician.id,  # ← FIXED: technician.id
            service_id=service.id,
            title=title,
            description=description,
            address=address,
            room=room,
            urgency=urgency,
            status="pending",
            payment_amount=service.price,
            image_filename=image_filename,
            created_at=datetime.now()
        )
        db.session.add(new_request)
        db.session.flush()

        # ===== FIXED: NOTIFICATION FOR TECHNICIAN =====
        tech_notification = Notification(
            user_id=technician.id,  # ← FIXED: technician.id
            message=f"🔔 New booking #{new_request.id} from {customer.username} for {service.name}",
            is_read=False,
            created_at=datetime.now()
        )
        db.session.add(tech_notification)
        
        # Notification for customer
        cust_notification = Notification(
            user_id=customer.id,
            message=f"✅ Your booking #{new_request.id} for {service.name} has been created",
            is_read=False,
            created_at=datetime.now()
        )
        db.session.add(cust_notification)

        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Booking created successfully!',
            'booking_id': new_request.id,
            'technician_id': technician.id,
            'technician_name': technician.username,
            'image_uploaded': image_filename is not None
        })

    except Exception as e:
        db.session.rollback()
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)})

#================= TEST ROUTE FOR NOTIFICATION =================
@app.route('/test_create_notification')
def test_create_notification():
    """Direct notification create karva mate test route"""
    if 'user_id' not in session or session.get('role') != 'technician':
        return "Please login as technician first"
    
    try:
        technician_id = session.get('user_id')
        technician = User.query.get(technician_id)
        
        # Test notification create karo
        test_notification = Notification(
            user_id=technician_id,
            message="🔔 Test notification - " + datetime.now().strftime('%H:%M:%S'),
            is_read=False,
            created_at=datetime.utcnow()
        )
        
        db.session.add(test_notification)
        db.session.commit()
        
        return f"✅ Test notification created for {technician.username}!"
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

#================= FORCE NOTIFICATION CREATE ROUTE =================
@app.route('/force_notification')
def force_notification():
    if 'user_id' not in session:
        return "Please login first"
    
    # DELETE all old notifications for this user
    Notification.query.filter_by(user_id=session['user_id']).delete()
    
    # Create FRESH notification with is_read = FALSE
    new_notif = Notification(
        user_id=session['user_id'],
        message="🔴🔴 TEST NOTIFICATION - " + datetime.now().strftime('%H:%M:%S'),
        is_read=False,  # ← THIS IS KEY
        created_at=datetime.utcnow()
    )
    db.session.add(new_notif)
    db.session.commit()
    
    return "✅ FRESH notification created! Go to dashboard now."
#================= CREATE UNREAD NOTIFICATION ROUTE (FOR TESTING) =================
@app.route('/create_unread_notification')
def create_unread_notification():
    if 'user_id' not in session:
        return "Please login first"
    
    try:
        notif = Notification(
            user_id=session['user_id'],
            message="🔔 UNREAD notification - " + datetime.now().strftime('%H:%M:%S'),
            is_read=0,  # ← AA FORCE KARO
            created_at=datetime.utcnow()
        )
        db.session.add(notif)
        db.session.commit()
        return "✅ Unread notification created!"
    except Exception as e:
        return f"❌ Error: {str(e)}"
#================= CREATE NOTIFICATION ROUTE (FOR TESTING) =================
@app.route('/create_notification')
def create_notification():
    if 'user_id' not in session:
        return "Please login first"
    
    try:
        notif = Notification(
            user_id=session['user_id'],
            message="🔔 New notification at " + datetime.now().strftime('%H:%M:%S'),
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.session.add(notif)
        db.session.commit()
        return "✅ Notification created!"
    except Exception as e:
        return f"❌ Error: {str(e)}"
#================= AJAX ROUTE FOR GETTING BOOKING DETAILS =================
# ================= AJAX ROUTE FOR GETTING BOOKING DETAILS =================
# AA BADHU DELETE KARO (Lines 1472-1486)
@app.route('/get_booking_details/<int:booking_id>')
def get_booking_details(booking_id):
    """AJAX request માટે booking details JSON માં મોકલો"""
    if session.get("role") != "customer":
        return jsonify({'error': 'Unauthorized'}), 401
    
    booking = ServiceRequest.query.get_or_404(booking_id)
    
    # Verify this booking belongs to logged-in customer
    if booking.customer_id != session["user_id"]:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # બધા ફિલ્ડ્સને સ્ટ્રિંગમાં કન્વર્ટ કરો
    data = {
        'id': booking.id,
        'service_name': str(booking.service.name) if booking.service else 'N/A',
        'title': str(booking.title) if booking.title else '',
        'description': str(booking.description) if booking.description else '',
        'address': str(booking.address) if booking.address else '',
        'room': str(booking.room) if booking.room else '',
        'urgency': str(booking.urgency) if booking.urgency else 'Normal',
        'status': str(booking.status) if booking.status else 'pending',
        'payment_amount': float(booking.payment_amount) if booking.payment_amount else 0,
        'image_filename': str(booking.image_filename) if booking.image_filename else None,
        'image_url': f"/static/uploads/problems/{booking.image_filename}" if booking.image_filename else None,  # Add this line
        'created_at': booking.created_at.strftime('%d-%m-%Y %H:%M') if booking.created_at else 'N/A'
    }
    
    return jsonify(data)
#================= BOOKING HISTORY WITH DETAILS =================
@app.route("/customer/my-bookings")
def customer_my_booking():
    if session.get("role") != "customer":
        return redirect(url_for("login"))
    
    services = Service.query.all()
    
    # Get all bookings with technician relationship loaded
    all_bookings = ServiceRequest.query.filter_by(
        customer_id=session["user_id"]
    ).options(
        db.joinedload(ServiceRequest.technician)  # Load technician data
    ).order_by(ServiceRequest.created_at.desc()).all()
    
    current_bookings = [b for b in all_bookings if b.status in ['pending', 'in_progress']]
    
    total_bookings = len(all_bookings)
    completed_count = len([b for b in all_bookings if b.status == 'completed'])
    pending_count = len([b for b in all_bookings if b.status == 'pending'])
    total_spent = sum(b.payment_amount or 0 for b in all_bookings if b.status == 'completed')
    
    # Debug print
    print(f"\n=== MY BOOKINGS DEBUG ===")
    print(f"Total bookings: {total_bookings}")
    for b in all_bookings:
        tech_name = b.technician.username if b.technician else 'No technician'
        tech_phone = b.technician.phone if b.technician else 'No phone'
        print(f"Booking #{b.id}: Technician = {tech_name}, Phone = {tech_phone}")
    print(f"=== END DEBUG ===\n")
    
    return render_template(
        "my_booking.html",
        services=services,
        current_bookings=current_bookings,
        all_bookings=all_bookings,
        total_bookings=total_bookings,
        completed_count=completed_count,
        pending_count=pending_count,
        total_spent=total_spent
    )
    
@app.route('/customer/payments')
def my_payments():
    """View all payments for logged in customer"""
    if session.get("role") != "customer":
        return redirect(url_for("login"))
    
    user_id = session['user_id']
    booking_id = request.args.get('booking_id')  # Get booking_id from URL
    
    # Get all payments for this customer's bookings
    query = db.session.query(Payment).join(
        ServiceRequest, Payment.request_id == ServiceRequest.id
    ).filter(
        ServiceRequest.customer_id == user_id
    )
    
    # If specific booking ID is provided, filter by that booking
    if booking_id:
        query = query.filter(Payment.request_id == booking_id)
    
    payments = query.order_by(Payment.paid_at.desc(), Payment.id.desc()).all()
    
    # Prepare payment data with additional info
    payment_list = []
    total_amount = 0
    successful_payments = 0
    pending_payments = 0
    
    for payment in payments:
        booking = ServiceRequest.query.get(payment.request_id)
        technician = User.query.get(payment.technician_id) if payment.technician_id else None
        service = Service.query.get(booking.service_id) if booking else None
        
        payment_data = {
            'id': payment.id,
            'request_id': payment.request_id,
            'amount': payment.amount,
            'method': payment.method or 'Online',
            'status': payment.status or 'Paid',
            'paid_at': payment.paid_at,
            'created_at': payment.paid_at,
            'service_name': service.name if service else 'Unknown',
            'technician_name': technician.username if technician else None,
            'technician_image': technician.profile_image if technician else None
        }
        payment_list.append(payment_data)
        
        total_amount += payment.amount or 0
        if payment.status and payment.status.lower() == 'paid':
            successful_payments += 1
        elif payment.status and payment.status.lower() == 'pending':
            pending_payments += 1
    
    # If booking_id provided but no payments found, show message
    if booking_id and not payment_list:
        flash(f'No payment records found for booking #{booking_id}', 'info')
    
    return render_template(
        'payment.html',
        payments=payment_list,
        total_payments=len(payment_list),
        successful_payments=successful_payments,
        pending_payments=pending_payments,
        total_amount=total_amount,
        booking_id=booking_id  # Pass to template
    )
    
# ==================== QR SCANNER ROUTE ====================
@app.route('/scan-payment/<int:booking_id>')
def scan_payment(booking_id):
    """Open QR scanner for payment"""
    if session.get("role") != "customer":
        return redirect(url_for("login"))
    
    booking = ServiceRequest.query.get_or_404(booking_id)
    
    # Verify this booking belongs to logged-in customer
    if booking.customer_id != session['user_id']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('customer_my_booking'))
    
    service = Service.query.get(booking.service_id)
    
    return render_template(
        'scanner.html',
        booking_id=booking.id,
        amount=booking.payment_amount,
        service_name=service.name if service else 'Service'
    )

# ==================== PROCESS PAYMENT AFTER SCAN ====================
@app.route('/process-payment/<int:booking_id>', methods=['POST'])
def process_payment(booking_id):
    """Process payment after successful QR scan"""
    if session.get("role") != "customer":
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    booking = ServiceRequest.query.get_or_404(booking_id)
    
    # Verify this booking belongs to logged-in customer
    if booking.customer_id != session['user_id']:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    try:
        # Check if payment already exists
        existing_payment = Payment.query.filter_by(request_id=booking_id).first()
        
        if existing_payment:
            return jsonify({
                'success': True, 
                'message': 'Payment already processed',
                'payment_id': existing_payment.id,
                'amount': existing_payment.amount,
                'booking_id': booking.id
            })
        
        # Create new payment - YOUR TABLE STRUCTURE ACCORDING TO YOUR DB
        payment = Payment(
            request_id=booking.id,
            amount=booking.payment_amount,
            method='QR Scan',
            status='Paid',
            paid_at=datetime.now(),
            technician_id=booking.technician_id  # ← AA ADD KARO
        )
        
        db.session.add(payment)
        
        # Update booking status if needed
        if booking.status != 'completed':
            booking.status = 'completed'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Payment processed successfully',
            'payment_id': payment.id,
            'booking_id': booking.id,
            'amount': payment.amount
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error processing payment: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== TEMP SCANNER FOR NEW BOOKINGS ====================
@app.route('/scan-payment-temp')
def scan_payment_temp():
    """Open QR scanner for temporary/new booking"""
    if session.get("role") != "customer":
        return redirect(url_for("login"))
    
    service_id = request.args.get('service_id')
    amount = request.args.get('amount')
    service_name = request.args.get('service')
    
    if not service_id or not amount:
        flash('Please select a service first', 'danger')
        return redirect(url_for('customer_my_booking'))
    
    # Generate a temporary ID for display
    temp_id = f"TEMP-{random.randint(1000, 9999)}"
    
    return render_template(
        'scanner.html',
        booking_id=temp_id,
        amount=amount,
        service_name=service_name or 'Service',
        is_temp=True,
        service_id=service_id
    )
# ================= TECHNICIAN ROUTES =================
@app.route('/technician/dashboard')
def technician_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    technician_id = session.get('user_id')
    technician = User.query.get(technician_id)
    
    # ===== GET ALL BOOKINGS FOR THIS TECHNICIAN =====
    technician_bookings = ServiceRequest.query.filter_by(
        technician_id=technician_id
    ).order_by(ServiceRequest.created_at.desc()).all()
    
    # Convert bookings to list of dicts for template
    bookings_list = []
    for booking in technician_bookings:
        customer = User.query.get(booking.customer_id)
        bookings_list.append({
            'id': booking.id,
            'customer_id': booking.customer_id,
            'title': booking.title,
            'status': booking.status,
            'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M:%S') if booking.created_at else None,
            'address': booking.address,
            'customer_name': customer.username if customer else 'Unknown',
            'customer_phone': customer.phone if customer else '',
            'customer_email': customer.email if customer else '',
            'description': booking.description,
            'room': booking.room,
            'urgency': booking.urgency
        })
    
    # ===== COUNT BY STATUS (SAME AS technician_customers) =====
    pending_count = sum(1 for b in technician_bookings if b.status == 'pending')
    in_progress_count = sum(1 for b in technician_bookings if b.status == 'in_progress')
    completed_count = sum(1 for b in technician_bookings if b.status == 'completed')
    total_jobs = len(technician_bookings)
    
    # ===== GET ALL CUSTOMERS WITH THEIR BOOKING COUNTS =====
    all_customers = User.query.filter_by(role='customer').all()
    customers_list = []
    for customer in all_customers:
        customer_bookings = ServiceRequest.query.filter_by(customer_id=customer.id).all()
        pending = sum(1 for b in customer_bookings if b.status == 'pending')
        in_progress = sum(1 for b in customer_bookings if b.status == 'in_progress')
        completed = sum(1 for b in customer_bookings if b.status == 'completed')
        
        customers_list.append({
            'id': customer.id,
            'username': customer.username,
            'email': customer.email,
            'phone': customer.phone,
            'location': customer.location,
            'pending_count': pending,
            'in_progress_count': in_progress,
            'completed_count': completed
        })
    
    # ===== GET NOTIFICATIONS =====
    notifications = Notification.query.filter_by(
        user_id=technician_id
    ).order_by(Notification.id.desc()).limit(20).all()
    
    notifications_list = []
    for n in notifications:
        notifications_list.append({
            'id': n.id,
            'message': n.message,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%I:%M %p, %d %b %Y') if n.created_at else ''
        })
    
    unread_count = Notification.query.filter_by(
        user_id=technician_id, 
        is_read=False
    ).count()
    
    # ===== GET NEXT APPOINTMENT =====
    next_appointment = None
    upcoming_bookings = [b for b in technician_bookings if b.status in ['pending', 'in_progress']]
    if upcoming_bookings:
        first_booking = upcoming_bookings[0]
        customer = User.query.get(first_booking.customer_id)
        next_appointment = {
            'id': first_booking.id,
            'customer_name': customer.username if customer else 'Unknown',
            'address': first_booking.address,
            'created_at': first_booking.created_at,
            'status': first_booking.status
        }
    
    # ===== PRINT DEBUG INFO =====
    print(f"\n=== TECHNICIAN DASHBOARD DEBUG ===")
    print(f"Technician ID: {technician_id}")
    print(f"Total Bookings: {total_jobs}")
    print(f"Pending: {pending_count}, In Progress: {in_progress_count}, Completed: {completed_count}")
    print(f"Total Customers: {len(customers_list)}")
    print(f"=== END DEBUG ===\n")
    
    return render_template(
        'tech_dashboard.html',
        technician=technician,
        bookings=bookings_list,
        customers=customers_list,  # ← આ ઉમેરો
        total_jobs=total_jobs,
        pending_count=pending_count,
        in_progress_count=in_progress_count,
        completed_count=completed_count,
        total_customers=len(customers_list),
        today_tasks=total_jobs + len(notifications_list),  # Tasks = Bookings + Notifications
        notifications=notifications_list,
        unread_notifications=unread_count,
        next_appointment=next_appointment,
        now=datetime.now()
    )
    
@app.route('/get_unread_chats_count')
def get_unread_chats_count():
    """Get unread chat count for technician"""
    if 'user_id' not in session or session.get('role') != 'technician':
        return jsonify({'count': 0})
    
    try:
        # Count unread messages where technician is receiver
        count = ChatMessage.query.filter_by(
            receiver_id=session['user_id'],
            is_read=False
        ).count()
        
        return jsonify({'count': count})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'count': 0})

@app.route('/get_recent_chats')
def get_recent_chats():
    """Get recent chats for technician"""
    if 'user_id' not in session or session.get('role') != 'technician':
        return jsonify({'chats': []})
    
    try:
        from sqlalchemy import text
        
        sql = text("""
            SELECT DISTINCT 
                cm.booking_id,
                cm.sender_id as customer_id,
                u.username as customer_name,
                s.name as service_name,
                (SELECT message FROM chat_messages cm2 
                 WHERE cm2.booking_id = cm.booking_id 
                 ORDER BY cm2.created_at DESC LIMIT 1) as last_message,
                (SELECT created_at FROM chat_messages cm2 
                 WHERE cm2.booking_id = cm.booking_id 
                 ORDER BY cm2.created_at DESC LIMIT 1) as last_time,
                EXISTS(SELECT 1 FROM chat_messages cm2 
                       WHERE cm2.booking_id = cm.booking_id 
                       AND cm2.receiver_id = :tech_id 
                       AND cm2.is_read = 0) as has_unread
            FROM chat_messages cm
            JOIN users u ON cm.sender_id = u.id
            JOIN service_requests sr ON cm.booking_id = sr.id
            JOIN service s ON sr.service_id = s.id
            WHERE cm.receiver_id = :tech_id OR cm.sender_id = :tech_id
            ORDER BY last_time DESC
            LIMIT 20
        """)
        
        result = db.session.execute(sql, {'tech_id': session['user_id']})
        
        chats = []
        for row in result:
            row_dict = dict(row._mapping)
            last_time = row_dict.get('last_time')
            chats.append({
                'booking_id': row_dict['booking_id'],
                'customer_id': row_dict['customer_id'],
                'customer_name': row_dict['customer_name'],
                'service_name': row_dict['service_name'],
                'last_message': row_dict['last_message'][:50] if row_dict['last_message'] else '',
                'last_time': last_time.strftime('%I:%M %p') if last_time else '',
                'has_unread': bool(row_dict['has_unread'])
            })
        
        return jsonify({'chats': chats})
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'chats': []})
#================= DEBUG ROUTE TO CHECK ACTUAL DATABASE DATA =================
@app.route('/debug_actual_data')
def debug_actual_data():
    """Database ma su che e batao"""
    
    output = "<h2>🔍 DATABASE REAL DATA DEBUG</h2>"
    
    # 1. BADHA USERS
    users = User.query.all()
    output += f"<h3>1. Total Users: {len(users)}</h3>"
    output += "<table border='1' cellpadding='5'>"
    output += "<tr><th>ID</th><th>Username</th><th>Email</th><th>Role</th><th>Status</th></tr>"
    for u in users:
        output += f"<tr>"
        output += f"<td>{u.id}</td>"
        output += f"<td>{u.username}</td>"
        output += f"<td>{u.email}</td>"
        output += f"<td><b>{u.role}</b></td>"
        output += f"<td>{u.status}</td>"
        output += f"</tr>"
    output += "</table>"
    
    # 2. TECHNICIANS (role technician vada)
    techs = User.query.filter_by(role='technician').all()
    output += f"<h3>2. Technicians Found: {len(techs)}</h3>"
    if techs:
        for t in techs:
            output += f"<p>✅ Technician: {t.username} (ID: {t.id})</p>"
    else:
        output += "<p style='color:red;'>❌ Koi technician nathi! role='technician' set karo</p>"
    
    # 3. SERVICE REQUESTS
    bookings = ServiceRequest.query.all()
    output += f"<h3>3. Total Bookings: {len(bookings)}</h3>"
    output += "<table border='1' cellpadding='5'>"
    output += "<tr><th>Booking ID</th><th>Customer ID</th><th>Technician ID</th><th>Status</th><th>Payment</th></tr>"
    for b in bookings:
        output += f"<tr>"
        output += f"<td>{b.id}</td>"
        output += f"<td>{b.customer_id}</td>"
        output += f"<td><b>{b.technician_id}</b></td>"
        output += f"<td>{b.status}</td>"
        output += f"<td>{b.payment_amount}</td>"
        output += f"</tr>"
    output += "</table>"
    
    return output

@app.route('/technician/customers')
def technician_customers():
    if 'user_id' not in session or session.get('role') != 'technician':
        return redirect(url_for('login'))
    
    technician_id = session.get('user_id')
    technician = User.query.get(technician_id)
    
    if not technician:
        return redirect(url_for('login'))
    
    # ===== DEBUG PRINT =====
    print(f"\n=== TECHNICIAN CUSTOMERS ROUTE ===")
    print(f"Technician ID: {technician_id}")
    
    # ===== GET ALL CUSTOMERS (FIXED) =====
    customers = User.query.filter_by(role="customer").all()
    print(f"✅ Total customers found: {len(customers)}")
    
    # ===== GET ALL BOOKINGS FOR THIS TECHNICIAN =====
    bookings_query = ServiceRequest.query.filter_by(technician_id=technician_id).all()
    print(f"✅ Total bookings for technician: {len(bookings_query)}")
    
    bookings = []
    pending_count = 0
    in_progress_count = 0
    completed_count = 0
    
    # Process bookings
    for booking in bookings_query:
        customer = User.query.get(booking.customer_id)
        service = Service.query.get(booking.service_id)
        
        # Count by status
        if booking.status == 'pending':
            pending_count += 1
        elif booking.status == 'in_progress':
            in_progress_count += 1
        elif booking.status == 'completed':
            completed_count += 1
        
        bookings.append({
            'id': booking.id,
            'customer_id': booking.customer_id,
            'title': booking.title,
            'description': booking.description,
            'status': booking.status,
            'payment_amount': float(booking.payment_amount) if booking.payment_amount else 0,
            'created_at': booking.created_at,
            'urgency': booking.urgency,
            'room': booking.room,
            'address': booking.address,
            'image_filename': booking.image_filename,
            'customer_name': customer.username if customer else 'Unknown',
            'service_name': service.name if service else 'Unknown',
        })
    
    # Get all payments for technician's bookings
    booking_ids = [b['id'] for b in bookings]
    payments = Payment.query.filter(Payment.request_id.in_(booking_ids)).all() if booking_ids else []
    
    print(f"📊 Stats - Pending: {pending_count}, In Progress: {in_progress_count}, Completed: {completed_count}")
    print(f"💰 Found {len(payments)} payments for technician's bookings")
    print(f"=== END DEBUG ===\n")
    
    return render_template(
        'technician_customers.html',
        technician=technician,
        customers=customers,
        bookings=bookings,
        payments=payments,
        pending_count=pending_count,
        in_progress_count=in_progress_count,
        completed_count=completed_count,
        total_bookings=len(bookings),
        customers_without_bookings=len(customers) - len(set([b['customer_id'] for b in bookings]))
    )
        
@app.route('/test_customers')
def test_customers():
    """Test route to check customers"""
    customers = User.query.filter_by(role="customer").all()
    
    output = "<h2>📋 All Customers in Database</h2>"
    output += "<table border='1' cellpadding='5'>"
    output += "<tr><th>ID</th><th>Username</th><th>Email</th><th>Phone</th></tr>"
    
    for c in customers:
        output += f"<tr>"
        output += f"<td>{c.id}</td>"
        output += f"<td>{c.username}</td>"
        output += f"<td>{c.email}</td>"
        output += f"<td>{c.phone or 'N/A'}</td>"
        output += f"</tr>"
    
    output += "</table>"
    output += f"<p><b>Total:</b> {len(customers)} customers</p>"
    
    return output
# ================= TECHNICIAN PROFILE =================
@app.route('/technician/profile')
def technician_profile():
    if 'user_id' not in session or session.get('role') != 'technician':
        return redirect(url_for('login'))
    
    technician_id = session.get('user_id')
    technician = User.query.get(technician_id)
    
    if not technician:
        return redirect(url_for('login'))
    
    # Get technician's statistics
    total_bookings = ServiceRequest.query.filter_by(technician_id=technician_id).count()
    completed_bookings = ServiceRequest.query.filter_by(technician_id=technician_id, status='completed').count()
    pending_bookings = ServiceRequest.query.filter_by(technician_id=technician_id, status='pending').count()
    
    # Get recent bookings
    recent_bookings = ServiceRequest.query.filter_by(technician_id=technician_id).order_by(ServiceRequest.created_at.desc()).limit(5).all()
    
    bookings_list = []
    for booking in recent_bookings:
        customer = User.query.get(booking.customer_id)
        bookings_list.append({
            'id': booking.id,
            'title': booking.title,
            'status': booking.status,
            'created_at': booking.created_at,
            'customer_name': customer.username if customer else 'Unknown'
        })
    
    return render_template(
        'technician_profile.html',
        technician=technician,
        total_bookings=total_bookings,
        completed_bookings=completed_bookings,
        pending_bookings=pending_bookings,
        recent_bookings=bookings_list,
        now=datetime.now()
    )

# ==================== GET PAYMENT DETAILS FOR TECHNICIAN ====================
@app.route('/get_payment_details_tech/<int:payment_id>')
def get_payment_details_tech(payment_id):
    """Get payment details for technician view"""
    if session.get("role") != "technician" and session.get("role") != "admin":
        return jsonify({'error': 'Unauthorized'}), 401
    
    payment = Payment.query.get_or_404(payment_id)
    booking = ServiceRequest.query.get(payment.request_id)
    customer = User.query.get(booking.customer_id) if booking else None
    service = Service.query.get(booking.service_id) if booking else None
    
    return jsonify({
        'id': payment.id,
        'request_id': payment.request_id,
        'amount': payment.amount,
        'method': payment.method or 'Online',
        'status': payment.status or 'Paid',
        'paid_at': payment.paid_at.strftime('%d-%m-%Y %H:%M') if payment.paid_at else 'N/A',
        'service_name': service.name if service else 'Unknown',
        'booking_title': booking.title if booking else 'N/A',
        'customer_name': customer.username if customer else 'Unknown'
    })
# ================= UPDATE PROFILE (FIXED) =================
@app.route("/update_profile", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    if not user:
        return redirect(url_for("login"))

    try:
        # 👇 IMPORTANT: Pehla current values fetch karo
        current_user = User.query.get(session["user_id"])
        
        # 👇 Form values check karo - NULL/empty na aave
        username = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        location = request.form.get("location")
        address = request.form.get("address")
        
        # 👇 Agar form field empty hoy to existing value j rakh
        user.username = username if username and username.strip() else current_user.username
        user.email = email if email and email.strip() else current_user.email
        user.phone = phone if phone and phone.strip() else current_user.phone
        user.location = location if location and location.strip() else current_user.location
        user.address = address if address and address.strip() else current_user.address
        
        if request.form.get("specialization") and request.form.get("specialization").strip():
            user.specialization = request.form.get("specialization")

        # ===== PROFILE IMAGE UPLOAD =====
        if "photo" in request.files:
            file = request.files["photo"]
            if file and file.filename and file.filename.strip() != "":
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    import time
                    unique_filename = f"{int(time.time())}_{filename}"
                    file.save(os.path.join(app.config["UPLOAD_FOLDER"], unique_filename))
                    user.profile_image = unique_filename

        db.session.commit()
        flash("✅ Profile updated successfully!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error updating profile: {str(e)}", "danger")

    # Redirect back to profile page
    if user.role == 'technician':
        return redirect(url_for('technician_profile'))
    else:
        return redirect(url_for('profile_page'))
    

# ================= TECHNICIAN HELP & SUPPORT =================
@app.route('/technician/help')
def technician_help():
    if 'user_id' not in session or session.get('role') != 'technician':
        return redirect(url_for('login'))
    
    technician_id = session.get('user_id')
    technician = User.query.get(technician_id)
    
    if not technician:
        return redirect(url_for('login'))
    
    # Get notifications
    notifications = Notification.query.filter_by(
        user_id=technician_id
    ).order_by(Notification.id.desc()).limit(20).all()
    
    notifications_list = []
    for n in notifications:
        notifications_list.append({
            'id': n.id,
            'message': n.message,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%I:%M %p, %d %b %Y') if n.created_at else ''
        })
    
    unread_count = Notification.query.filter_by(
        user_id=technician_id, 
        is_read=False
    ).count()
    
    # Sample FAQs and Guides (you can move to database later)
    faqs = [
        {'question': 'How to accept booking?', 'answer': 'Go to Dashboard...'},
        {'question': 'How to get paid?', 'answer': 'Payments weekly...'}
    ]
    
    guides = [
        {'title': 'Using the App', 'description': 'Complete guide'},
        {'title': 'Service Guidelines', 'description': 'Best practices'}
    ]
    
    return render_template(
        'technician_help.html',
        technician=technician,
        notifications=notifications_list,
        unread_notifications=unread_count,
        faqs=faqs,
        guides=guides,
        now=datetime.now()
    )
# ================= CHANGE PASSWORD =================
@app.route("/change_password", methods=["POST"])
def change_password():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    if not user:
        return redirect(url_for("login"))

    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    # Verify current password
    if not check_password_hash(user.password, current_password):
        flash("❌ Current password is incorrect!", "danger")
        return redirect(url_for('technician_profile') if user.role == 'technician' else url_for('profile_page'))

    # Check if new password matches confirm
    if new_password != confirm_password:
        flash("❌ New passwords do not match!", "danger")
        return redirect(url_for('technician_profile') if user.role == 'technician' else url_for('profile_page'))

    # Update password
    user.password = generate_password_hash(new_password)
    db.session.commit()

    flash("✅ Password changed successfully!", "success")
    return redirect(url_for('technician_profile') if user.role == 'technician' else url_for('profile_page'))

# ================= TECHNICIAN UPDATE PROFILE =================
@app.route("/update_profile_tech", methods=["POST"])
def update_profile_tech():
    if "user_id" not in session or session.get('role') != 'technician':
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    if not user:
        return redirect(url_for("login"))

    try:
        user.username = request.form.get("name")
        user.email = request.form.get("email")
        user.phone = request.form.get("phone")
        user.location = request.form.get("location")
        user.address = request.form.get("address")
        
        if request.form.get("specialization"):
            user.specialization = request.form.get("specialization")

        # ===== PROFILE IMAGE UPLOAD =====
        if "photo" in request.files:
            file = request.files["photo"]

            if file and file.filename != "":
                filename = secure_filename(file.filename)
                import time
                unique_filename = f"{int(time.time())}_{filename}"
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], unique_filename))
                user.profile_image = unique_filename

        db.session.commit()
        flash("✅ Profile updated successfully!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error updating profile: {str(e)}", "danger")

    return redirect(url_for('technician_profile'))

#========
@app.route('/fix_notifications')
def fix_notifications():
    """Fix notifications with invalid user_id"""
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    output = "<h2>🔧 Notification Fix Tool</h2>"
    
    # Step 1: Show all notifications with user info
    sql = text("""
        SELECT n.*, u.username, u.role 
        FROM notifications n
        LEFT JOIN users u ON n.user_id = u.id
        ORDER BY n.id DESC
    """)
    result = db.session.execute(sql)
    
    output += "<h3>Current Notifications:</h3>"
    output += "<table border='1' cellpadding='5' style='border-collapse: collapse;'>"
    output += "<tr><th>ID</th><th>User ID</th><th>Username</th><th>Role</th><th>Message</th><th>Read</th><th>Created</th></tr>"
    
    invalid_count = 0
    for row in result:
        row_dict = dict(row._mapping)
        is_valid = row_dict.get('username') is not None
        if not is_valid:
            invalid_count += 1
        
        output += f"<tr style='background: {'#ffcccc' if not is_valid else '#ccffcc'}'>"
        output += f"<td>{row_dict['id']}</td>"
        output += f"<td>{row_dict['user_id']}</td>"
        output += f"<td>{row_dict.get('username', '❌ MISSING')}</td>"
        output += f"<td>{row_dict.get('role', 'N/A')}</td>"
        output += f"<td>{row_dict['message']}</td>"
        output += f"<td>{'Read' if row_dict['is_read'] else 'Unread'}</td>"
        output += f"<td>{row_dict['created_at']}</td>"
        output += f"</tr>"
    
    output += "</table>"
    output += f"<p><strong>Invalid notifications found: {invalid_count}</strong></p>"
    
    # Step 2: Fix buttons
    output += """
    <div style="margin-top: 20px;">
        <form method="post" action="/execute_fix" style="display: inline;">
            <button type="submit" name="action" value="delete_invalid" style="background: #ef4444; color: white; padding: 10px 20px; border: none; border-radius: 5px; margin-right: 10px; cursor: pointer;">
                🗑️ Delete All Invalid Notifications (user_id=0 or missing users)
            </button>
        </form>
        <form method="post" action="/execute_fix" style="display: inline;">
            <button type="submit" name="action" value="assign_to_technician" style="background: #38bdf8; color: black; padding: 10px 20px; border: none; border-radius: 5px; margin-right: 10px; cursor: pointer;">
                🔧 Assign user_id=0 to First Technician
            </button>
        </form>
    </div>
    """
    
    return output

#======
@app.route('/execute_fix', methods=['POST'])
def execute_fix():
    """Execute notification fix"""
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    action = request.form.get('action')
    
    if action == 'delete_invalid':
        # Delete notifications where user_id=0
        deleted = Notification.query.filter_by(user_id=0).delete()
        
        # Delete notifications where user doesn't exist
        sql = text("""
            DELETE n FROM notifications n
            LEFT JOIN users u ON n.user_id = u.id
            WHERE u.id IS NULL
        """)
        db.session.execute(sql)
        db.session.commit()
        
        flash(f"✅ Deleted {deleted} invalid notifications", "success")
        
    elif action == 'assign_to_technician':
        # Get first technician
        technician = User.query.filter_by(role='technician').first()
        if technician:
            # Update user_id=0 notifications to technician id
            count = Notification.query.filter_by(user_id=0).update({'user_id': technician.id})
            db.session.commit()
            flash(f"✅ Assigned {count} notifications to technician {technician.username}", "success")
        else:
            flash("❌ No technician found!", "danger")
    
    return redirect(url_for('fix_notifications'))
#================= AJAX ROUTE FOR TECHNICIAN TO UPDATE BOOKING STATUS =================
@app.route('/technician/update_status_ajax', methods=['POST'])
def technician_update_status_ajax():
    if 'user_id' not in session or session.get('role') != 'technician':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    booking_id = data.get('booking_id')
    new_status = data.get('status')
    
    if not booking_id or not new_status:
        return jsonify({'success': False, 'error': 'Missing data'}), 400
    
    valid_statuses = ['pending', 'in_progress', 'completed', 'rejected']
    if new_status not in valid_statuses:
        return jsonify({'success': False, 'error': 'Invalid status'}), 400
    
    try:
        booking = ServiceRequest.query.get(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        booking.status = new_status
        db.session.commit()
        
        # Notification for customer
        if booking.customer_id:
            notif = Notification(
                user_id=booking.customer_id,
                message=f"Your booking #{booking_id} status updated to {new_status.replace('_', ' ')}",
                is_read=False,
                created_at=datetime.utcnow()
            )
            db.session.add(notif)
            db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
#================= API ROUTE TO GET LOGGED IN USER INFO =================
@app.route("/api/user")
def get_user():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"})

    user = User.query.get(session["user_id"])

    return jsonify(user.to_dict())

# ================= NOTIFICATION ROUTES =================


# AJAX ROUTE TO MARK NOTIFICATIONS AS READ
@app.route('/admin/mark_notifications_read', methods=['POST'])
def admin_mark_notifications_read():
    if 'user_id' not in session:
        return jsonify({'success': False})
    
    try:
        Notification.query.filter_by(
            user_id=session['user_id'],
            is_read=False
        ).update({'is_read': True})
        
        db.session.commit()
        print(f"Marked all notifications read for user {session['user_id']}")
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False})

#================= DEBUG ROUTE FOR NOTIFICATIONS =================
@app.route('/debug_notifications')
def debug_notifications():
    if session.get('role') != 'technician':
        return "Please login as technician first"
    
    technician_id = session.get('user_id')
    technician = User.query.get(technician_id)
    
    html = f"""
    <html>
    <head><title>Notification Debug</title>
    <style>
        body {{ font-family: Arial; padding: 20px; background: #0f172a; color: white; }}
        .success {{ color: #22c55e; }}
        .error {{ color: #ef4444; }}
        pre {{ background: #1e293b; padding: 10px; border-radius: 5px; }}
    </style>
    </head>
    <body>
    <h1>Notification Debug for {technician.username}</h1>
    """
    
    notifications = Notification.query.filter_by(user_id=technician_id).all()
    html += f"<h2>Notifications in Database: {len(notifications)}</h2>"
    
    if notifications:
        html += "<ul>"
        for n in notifications:
            status = "✅ Read" if n.is_read else "🆕 Unread"
            html += f"<li>{status} - {n.message} - {n.created_at}</li>"
        html += "</ul>"
    else:
        html += "<p class='error'>❌ No notifications found!</p>"
    
    html += f"<h2>Unread Count: {Notification.query.filter_by(user_id=technician_id, is_read=False).count()}</h2>"
    html += f"<h2>Session User ID: {session.get('user_id')}</h2>"
    html += f"<h2>Session Role: {session.get('role')}</h2>"
    html += '<br><a href="/technician/dashboard" style="color: #38bdf8;">Back to Dashboard</a>'
    html += '</body></html>'
    
    return html
#================= DEBUG ROUTE FOR TECHNICIANS =================
@app.route('/debug_technicians')
def debug_technicians():
    """Check technicians in database"""
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    technicians = User.query.filter_by(role="technician").all()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Technicians Debug</title>
        <style>
            body { background: #0f172a; color: #fff; font-family: Arial; padding: 20px; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            th { background: #38bdf8; color: #000; padding: 10px; }
            td { padding: 10px; border-bottom: 1px solid #334155; }
            .success { color: #22c55e; }
            .error { color: #ef4444; }
        </style>
    </head>
    <body>
        <h1>Technicians in Database</h1>
    """
    
    html += f"<p>Total technicians found: <strong>{len(technicians)}</strong></p>"
    
    if technicians:
        html += """
        <table>
            <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Location</th>
                <th>Status</th>
                <th>Created At</th>
            </tr>
        """
        
        for t in technicians:
            html += f"""
            <tr>
                <td>{t.id}</td>
                <td>{t.username}</td>
                <td>{t.email}</td>
                <td>{t.phone or 'N/A'}</td>
                <td>{t.location or 'N/A'}</td>
                <td>{t.status or 'Active'}</td>
                <td>{t.created_at}</td>
            </tr>
            """
        
        html += "</table>"
    else:
        html += """
        <div style="text-align: center; padding: 50px; background: #1e293b; border-radius: 10px; margin-top: 30px;">
            <i class="fas fa-exclamation-triangle" style="font-size: 48px; color: #fbbf24; margin-bottom: 20px;"></i>
            <p class="error">No technicians found in database!</p>
            <p>Please add technicians manually or through registration.</p>
        </div>
        """
    
    html += '<br><a href="/admin/dashboard" style="color: #38bdf8;">← Back to Dashboard</a>'
    html += '</body></html>'
    
    return html

#================= SERVICE PAGE =================
@app.route("/services")
def service():
    services = Service.query.all()
    return render_template("service.html", services=services)

#================= FEEDBACK PAGE =================
@app.route("/feedback")
def feedback_page():

    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()

    return render_template("feedback.html", feedbacks=feedbacks)

# ================= PROFILE PAGE =================
@app.route("/profile")
def profile_page():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    return render_template("profile.html", user=user)

#================= LIKE FEEDBACK =================
@app.route("/like_feedback/<int:id>")
def like_feedback(id):

    feedback = Feedback.query.get_or_404(id)
    feedback.likes += 1

    db.session.commit()

    return redirect(url_for("feedback_page"))
#================= DELETE FEEDBACK =================
@app.route("/delete_feedback/<int:id>", methods=["POST"])
def delete_feedback(id):

    feedback = Feedback.query.get_or_404(id)

    db.session.delete(feedback)
    db.session.commit()

    flash("Feedback deleted")

    return redirect(url_for("feedback_page"))
#================= SUBMIT FEEDBACK =================
@app.route("/submit_feedback", methods=["POST"])
def submit_feedback():

    if "user_id" not in session:
        return redirect(url_for("login"))

    comment = request.form.get("feedback")
    rating = request.form.get("rating")

    feedback = Feedback(
        customer_id=session["user_id"],
        comment=comment,
        rating=rating,
        ai_reply="Thanks for your feedback. We appreciate it!"
    )

    db.session.add(feedback)
    db.session.commit()

    flash("Feedback submitted successfully!")
    return redirect(url_for("feedback_page"))

# ================= ADMIN DASHBOARD =================
@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    try:
        # Total Counts
        total_customers = User.query.filter_by(role="customer").count()
        total_technicians = User.query.filter_by(role="technician").count()
        total_bookings = ServiceRequest.query.count()
        total_ai_chats = AIChat.query.count()
        
        # Feedback data
        total_feedback = Feedback.query.count()
        avg_rating = db.session.query(db.func.avg(Feedback.rating)).scalar() or 0
        
        # Get recent feedback (last 5)
        recent_feedback = Feedback.query.order_by(Feedback.created_at.desc()).limit(5).all()
        recent_feedback_list = []
        for fb in recent_feedback:
            customer = User.query.get(fb.customer_id)
            recent_feedback_list.append({
                'id': fb.id,
                'customer_name': customer.username if customer else 'Unknown',
                'comment': fb.comment or '',
                'rating': fb.rating or 0,
                'created_at': fb.created_at,
                'service_name': 'General Feedback'
            })
        
        # ========== FIX: Get HUMAN CHATS ==========
        from sqlalchemy import text
        
        # Get unique chat conversations
        sql = text("""
            SELECT 
                cm.booking_id,
                sr.customer_id,
                sr.technician_id,
                c.username as customer_name,
                t.username as technician_name,
                s.name as service_name,
                sr.status as booking_status,
                COUNT(cm.id) as message_count,
                MAX(cm.created_at) as last_message_time,
                (SELECT message FROM chat_messages cm2 
                 WHERE cm2.booking_id = cm.booking_id 
                 ORDER BY cm2.created_at DESC LIMIT 1) as last_message
            FROM chat_messages cm
            JOIN service_requests sr ON cm.booking_id = sr.id
            JOIN users c ON sr.customer_id = c.id
            LEFT JOIN users t ON sr.technician_id = t.id
            JOIN service s ON sr.service_id = s.id
            GROUP BY cm.booking_id, sr.customer_id, sr.technician_id, c.username, t.username, s.name, sr.status
            ORDER BY last_message_time DESC
            LIMIT 10
        """)
        
        result = db.session.execute(sql)
        
        recent_human_chats = []
        for row in result:
            row_dict = dict(row._mapping)
            last_time = row_dict.get('last_message_time')
            
            recent_human_chats.append({
                'id': row_dict['booking_id'],
                'booking_id': row_dict['booking_id'],
                'customer_name': row_dict['customer_name'],
                'technician_name': row_dict['technician_name'] or 'Unassigned',
                'service_name': row_dict['service_name'],
                'booking_status': row_dict['booking_status'],
                'message_count': row_dict['message_count'],
                'last_message': row_dict['last_message'] or 'No messages yet',
                'last_message_time': last_time.strftime('%d-%m-%Y %H:%M') if last_time else 'N/A'
            })
        
        total_human_chats = len(recent_human_chats)
        
        # If no chats found, try to get all bookings (for debugging)
        if total_human_chats == 0:
            print("⚠️ No human chats found! Checking if there are any messages...")
            msg_count = ChatMessage.query.count()
            print(f"Total messages in chat_messages: {msg_count}")
        
        # Recent Bookings
        recent_bookings = ServiceRequest.query.order_by(ServiceRequest.created_at.desc()).limit(5).all()
        bookings_list = []
        for b in recent_bookings:
            customer = User.query.get(b.customer_id)
            technician = User.query.get(b.technician_id) if b.technician_id else None
            service = Service.query.get(b.service_id)
            
            bookings_list.append({
                "id": b.id,
                "title": b.title,
                "status": b.status,
                "payment_amount": float(b.payment_amount) if b.payment_amount else 0,
                "created_at": b.created_at,
                "customer_name": customer.username if customer else "Unknown",
                "technician_name": technician.username if technician else "Unassigned",
                "service_name": service.name if service else "Unknown"
            })
        
        # Recent Customers
        recent_customers = User.query.filter_by(role="customer").order_by(User.created_at.desc()).limit(5).all()
        customers_list = []
        for c in recent_customers:
            customers_list.append({
                "id": c.id,
                "username": c.username,
                "email": c.email,
                "phone": c.phone,
                "location": c.location,
                "created_at": c.created_at
            })
        
        print(f"✅ Admin Dashboard Data:")
        print(f"   - Human Chats: {total_human_chats}")
        print(f"   - Feedback: {total_feedback}")
        print(f"   - Bookings: {total_bookings}")
        
        return render_template(
            "admin_dashboard.html",
            total_customers=total_customers,
            total_technicians=total_technicians,
            total_bookings=total_bookings,
            total_ai_chats=total_ai_chats,
            total_human_chats=total_human_chats,
            total_feedback=total_feedback,
            avg_rating=round(avg_rating, 1),
            recent_feedback=recent_feedback_list,
            recent_human_chats=recent_human_chats,
            recent_bookings=bookings_list,
            recent_customers=customers_list,
            now=datetime.now()
        )
        
    except Exception as e:
        print(f"❌ Error in admin_dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f"Error loading dashboard: {str(e)}", "danger")
        return render_template(
            "admin_dashboard.html",
            total_customers=0,
            total_technicians=0,
            total_bookings=0,
            total_ai_chats=0,
            total_human_chats=0,
            total_feedback=0,
            avg_rating=0,
            recent_feedback=[],
            recent_human_chats=[],
            recent_bookings=[],
            recent_customers=[],
            now=datetime.now()
        )


@app.route('/create_test_chats')
def create_test_chats():
    """Create test chat messages for debugging"""
    if session.get("role") != "admin":
        return "Admin access required"
    
    try:
        # Get a booking that has a technician assigned
        booking = ServiceRequest.query.filter(
            ServiceRequest.technician_id.isnot(None)
        ).first()
        
        if not booking:
            return "❌ No booking with technician assigned found!"
        
        # Get customer and technician
        customer = User.query.get(booking.customer_id)
        technician = User.query.get(booking.technician_id)
        
        if not customer or not technician:
            return f"❌ Missing users: Customer={customer}, Technician={technician}"
        
        # Create test messages
        messages = [
            {"sender": customer, "receiver": technician, "msg": f"Hello, I need help with my {booking.service.name}"},
            {"sender": technician, "receiver": customer, "msg": "Hi! I'll be there soon. Can you share more details?"},
            {"sender": customer, "receiver": technician, "msg": "The problem is exactly as described. Please come asap!"},
            {"sender": technician, "receiver": customer, "msg": "On my way! Estimated arrival in 30 minutes."},
        ]
        
        created = 0
        for msg_data in messages:
            chat = ChatMessage(
                booking_id=booking.id,
                sender_id=msg_data["sender"].id,
                receiver_id=msg_data["receiver"].id,
                message=msg_data["msg"],
                is_read=False,
                created_at=datetime.utcnow()
            )
            db.session.add(chat)
            created += 1
        
        db.session.commit()
        
        return f"""
        <h2>✅ Test Chat Messages Created!</h2>
        <p>Booking ID: #{booking.id}</p>
        <p>Customer: {customer.username}</p>
        <p>Technician: {technician.username}</p>
        <p>Messages created: {created}</p>
        <br>
        <a href="/admin/dashboard">← Back to Dashboard</a>
        """
        
    except Exception as e:
        db.session.rollback()
        return f"❌ Error: {str(e)}"
# ================= ADMIN HUMAN CHATS ROUTE =================
@app.route("/admin/human-chats")
def admin_human_chats():
    """View all human chats between customers and technicians"""
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    
    try:
        from sqlalchemy import text
        
        print("=" * 50)
        print("🔍 Fetching Human Chats...")
        
        # Get all unique chat conversations grouped by booking
        sql = text("""
            SELECT 
                cm.booking_id,
                sr.customer_id,
                sr.technician_id,
                c.username as customer_name,
                t.username as technician_name,
                s.name as service_name,
                sr.status as booking_status,
                sr.urgency,
                sr.address,
                COUNT(cm.id) as message_count,
                MAX(cm.created_at) as last_message_time,
                (SELECT message FROM chat_messages cm2 
                 WHERE cm2.booking_id = cm.booking_id 
                 ORDER BY cm2.created_at DESC LIMIT 1) as last_message
            FROM chat_messages cm
            JOIN service_requests sr ON cm.booking_id = sr.id
            JOIN users c ON sr.customer_id = c.id
            LEFT JOIN users t ON sr.technician_id = t.id
            JOIN service s ON sr.service_id = s.id
            GROUP BY cm.booking_id, sr.customer_id, sr.technician_id, c.username, t.username, s.name, sr.status, sr.urgency, sr.address
            ORDER BY last_message_time DESC
        """)
        
        result = db.session.execute(sql)
        
        human_chats = []
        for row in result:
            row_dict = dict(row._mapping)
            last_time = row_dict.get('last_message_time')
            
            human_chats.append({
                'booking_id': row_dict['booking_id'],
                'customer_name': row_dict['customer_name'],
                'technician_name': row_dict['technician_name'] or 'Unassigned',
                'service_name': row_dict['service_name'],
                'booking_status': row_dict['booking_status'],
                'urgency': row_dict['urgency'] or 'Normal',
                'address': row_dict['address'] or 'N/A',
                'message_count': row_dict['message_count'],
                'last_message': row_dict['last_message'][:200] if row_dict['last_message'] else 'No messages yet',
                'last_message_time': last_time.strftime('%d-%m-%Y %H:%M') if last_time else 'N/A'
            })
        
        total_human_chats = len(human_chats)
        print(f"✅ Found {total_human_chats} human chat groups")
        
        # Active human chats (last 7 days)
        from datetime import timedelta
        active_human_chats = 0
        for chat in human_chats:
            if chat['last_message_time'] != 'N/A':
                try:
                    msg_date = datetime.strptime(chat['last_message_time'], '%d-%m-%Y %H:%M')
                    if msg_date > (datetime.now() - timedelta(days=7)):
                        active_human_chats += 1
                except:
                    pass
        
        # Today's messages
        today = datetime.now().date()
        today_messages = ChatMessage.query.filter(
            func.date(ChatMessage.created_at) == today
        ).count()
        
        print(f"📊 Stats: Total={total_human_chats}, Active={active_human_chats}, Today={today_messages}")
        print("=" * 50)
        
        return render_template(
            "admin_human_chats.html",
            human_chats=human_chats,
            total_human_chats=total_human_chats,
            active_human_chats=active_human_chats,
            today_messages=today_messages
        )
        
    except Exception as e:
        print(f"❌ Error in admin_human_chats: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return render_template(
            "admin_human_chats.html",
            human_chats=[],
            total_human_chats=0,
            active_human_chats=0,
            today_messages=0
        )
    
# ================= ADMIN FEEDBACK ROUTE =================
@app.route("/admin/feedback")
def admin_feedback():
    """View all customer feedback for admin"""
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    
    try:
        # Get all feedback with customer info
        feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
        
        feedback_list = []
        total_rating = 0
        
        for fb in feedbacks:
            customer = User.query.get(fb.customer_id)
            total_rating += fb.rating or 0
            
            feedback_list.append({
                'id': fb.id,
                'customer_name': customer.username if customer else 'Unknown',
                'customer_email': customer.email if customer else 'N/A',
                'comment': fb.comment,
                'rating': fb.rating,
                'likes': fb.likes,
                'ai_reply': fb.ai_reply,
                'created_at': fb.created_at
            })
        
        total_feedback = len(feedback_list)
        avg_rating = round(total_rating / total_feedback, 1) if total_feedback > 0 else 0
        
        return render_template(
            "admin_feedback.html",
            feedbacks=feedback_list,
            total_feedback=total_feedback,
            avg_rating=avg_rating
        )
        
    except Exception as e:
        print(f"Error in admin_feedback: {str(e)}")
        flash(f"Error loading feedback: {str(e)}", "danger")
        return redirect(url_for("admin_dashboard"))

# ================= DELETE FEEDBACK FOR ADMIN =================
@app.route("/admin/feedback/<int:feedback_id>/delete", methods=['POST'])
def admin_delete_feedback(feedback_id):
    """Delete feedback as admin"""
    if session.get("role") != "admin":
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    try:
        feedback = Feedback.query.get_or_404(feedback_id)
        db.session.delete(feedback)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
# ================= ADMIN CUSTOMERS =================
@app.route("/admin/customers")
def admin_customers():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    
    customers = User.query.filter_by(role="customer").all()
    customer_list = []
    active_count = 0
    inactive_count = 0
    pending_count = 0
    completed_count = 0
    in_progress_count = 0
    total_bookings_all = 0
    
    for c in customers:
        bookings = ServiceRequest.query.filter_by(customer_id=c.id).all()
        booking_count = len(bookings)
        total_bookings_all += booking_count
        total_spent = sum(b.payment_amount or 0 for b in bookings if b.status == 'completed')
        
        feedbacks = Feedback.query.filter_by(customer_id=c.id).all()
        avg_rating = sum(f.rating for f in feedbacks) / len(feedbacks) if feedbacks else None
        
        status = c.status if c.status else 'Active'
        
        # Count by status
        if status == 'Active':
            active_count += 1
        elif status == 'Inactive':
            inactive_count += 1
        elif status == 'Pending':
            pending_count += 1
        elif status == 'Completed':
            completed_count += 1
        elif status == 'In Progress':
            in_progress_count += 1
            
        customer_list.append({
            'id': c.id,
            'username': c.username,
            'email': c.email,
            'phone': c.phone,
            'location': c.location,
            'status': status,
            'created_at': c.created_at,
            'booking_count': booking_count,
            'total_spent': total_spent,
            'avg_rating': round(avg_rating, 1) if avg_rating else None
        })
    
    return render_template(
        "admin_customers.html",
        customers=customer_list,
        total_customers=len(customer_list),
        active_customers=active_count,
        inactive_customers=inactive_count,
        pending_customers=pending_count,
        completed_customers=completed_count,
        in_progress_customers=in_progress_count,
        total_customer_bookings=total_bookings_all,
        avg_customer_rating=4.5
    )
# ================= UPDATE CUSTOMER STATUS =================
@app.route('/admin/customer/<int:customer_id>/update-status', methods=['POST'])
def update_customer_status(customer_id):
    if session.get("role") != "admin":
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    data = request.get_json()
    new_status = data.get('status')
    
    customer = User.query.get(customer_id)
    if not customer or customer.role != 'customer':
        return jsonify({'success': False, 'error': 'Customer not found'})
    
    try:
        # Convert status to proper format
        if new_status == 'active':
            customer.status = 'Active'
        elif new_status == 'pending':
            customer.status = 'Pending'
        elif new_status == 'completed':
            customer.status = 'Completed'
        elif new_status == 'in_progress':
            customer.status = 'In Progress'
        elif new_status == 'inactive':
            customer.status = 'Inactive'
        else:
            customer.status = new_status.capitalize()
        
        db.session.commit()
        
        # Create notification for customer
        notif = Notification(
            user_id=customer_id,
            message=f"Your account status has been updated to {customer.status}",
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.session.add(notif)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})


# ================= ADMIN BOOKINGS =================
@app.route("/admin/bookings")
def admin_bookings():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    
    # Get page number from request
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Show 10 bookings per page
    
    # Get status filter from request
    status_filter = request.args.get('status', 'all')
    
    # Base query
    query = ServiceRequest.query
    
    # Apply status filter if not 'all'
    if status_filter != 'all':
        # Convert URL status to database status format
        if status_filter == 'in_progress':
            query = query.filter_by(status='in_progress')
        else:
            query = query.filter_by(status=status_filter)
    
    # Order by created_at and paginate
    paginated_bookings = query.order_by(ServiceRequest.created_at.desc()).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    # Prepare booking list for template
    bookings_list = []
    status_counts = {'pending': 0, 'in_progress': 0, 'completed': 0, 'rejected': 0}
    
    # Get all bookings for status counts (without pagination)
    all_bookings = ServiceRequest.query.all()
    for b in all_bookings:
        status_key = b.status.lower().replace(' ', '_') if b.status else 'pending'
        if status_key in status_counts:
            status_counts[status_key] += 1
    
    # Process paginated bookings
    for b in paginated_bookings.items:
        customer = User.query.get(b.customer_id)
        technician = User.query.get(b.technician_id) if b.technician_id else None
        service = Service.query.get(b.service_id)
        
        bookings_list.append({
            "id": b.id,
            "title": b.title,
            "status": b.status,
            "payment_amount": float(b.payment_amount) if b.payment_amount else 0,
            "created_at": b.created_at,
            "urgency": b.urgency,
            "room": b.room,
            "address": b.address,
            "image_filename": b.image_filename,
            "customer_name": customer.username if customer else "Unknown",
            "customer_email": customer.email if customer else "N/A",
            "customer_phone": customer.phone if customer else "N/A",
            "service_name": service.name if service else "Unknown",
            "technician_name": technician.username if technician else "Unassigned"
        })
    
    return render_template(
        "admin_bookings.html",
        bookings=paginated_bookings,  # Pass the paginated object, not the list
        bookings_list=bookings_list,   # Also pass the processed list if needed
        total_bookings=len(all_bookings),
        pending_count=status_counts['pending'],
        in_progress_count=status_counts['in_progress'],
        completed_count=status_counts['completed'],
        rejected_count=status_counts['rejected'],
        status=status_filter  # Pass current status filter
    )
# ================= GET BOOKINGS DETAILS=================
@app.route("/admin/get_booking_details/<int:booking_id>", endpoint="admin_get_booking_details")
def get_booking_details(booking_id):
    """Get booking details for admin view"""
    if session.get("role") != "admin":
        return jsonify({'error': 'Unauthorized'}), 401
    
    booking = ServiceRequest.query.get_or_404(booking_id)
    
    customer = User.query.get(booking.customer_id)
    technician = User.query.get(booking.technician_id) if booking.technician_id else None
    service = Service.query.get(booking.service_id)
    
    data = {
        "id": booking.id,
        "title": booking.title,
        "description": booking.description,
        "status": booking.status,
        "urgency": booking.urgency,
        "room": booking.room,
        "address": booking.address,
        "payment_amount": float(booking.payment_amount) if booking.payment_amount else 0,
        "created_at": booking.created_at.strftime("%d-%m-%Y %H:%M") if booking.created_at else None,
        "image_filename": booking.image_filename,
        
        "customer_name": customer.username if customer else "Unknown",
        "customer_phone": customer.phone if customer else "N/A",
        "customer_email": customer.email if customer else "N/A",
        
        "service_name": service.name if service else "Unknown",
        
        "technician_name": technician.username if technician else "Unassigned",
        "technician_phone": technician.phone if technician else "N/A"
    }
    
    return jsonify(data)

# ================= DELETE BOOKING ROUTE ================
# ================= DELETE BOOKING ROUTE ================
@app.route("/delete_booking/<int:booking_id>")
def delete_booking(booking_id):
    if session.get("role") != "admin":
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    booking = ServiceRequest.query.get_or_404(booking_id)
    
    try:
        # Delete related payments first
        Payment.query.filter_by(request_id=booking_id).delete()
        
        # Delete the booking
        db.session.delete(booking)
        db.session.commit()
        
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})

# ================= ADMIN AI CHATS =================
@app.route("/admin/ai-chats")
def admin_ai_chats():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    
    try:
        # Get ALL AI chats
        all_chats = AIChat.query.order_by(AIChat.created_at.desc()).all()
        
        print("=" * 50)
        print(f"🔍 DEBUG: Total AI chats found = {len(all_chats)}")
        
        chat_list = []
        for chat in all_chats:
            # Safely get user - handle if user doesn't exist
            user = User.query.get(chat.user_id)
            
            # Debug print
            print(f"   Chat #{chat.id}: User ID={chat.user_id}, User exists={user is not None}")
            
            # Create user dict safely
            user_dict = None
            if user:
                user_dict = {
                    'id': user.id,
                    'username': user.username or 'Unknown',
                    'email': user.email or 'N/A',
                    'phone': user.phone or 'N/A'
                }
            else:
                # User doesn't exist - use placeholder
                user_dict = {
                    'id': chat.user_id,
                    'username': f'Deleted User (ID: {chat.user_id})',
                    'email': 'N/A',
                    'phone': 'N/A'
                }
            
            chat_list.append({
                'id': chat.id,
                'user_message': chat.user_message or '',
                'ai_reply': chat.ai_reply or '',
                'created_at': chat.created_at,
                'user': user_dict
            })
        
        print(f"✅ Chat list prepared: {len(chat_list)} items")
        print("=" * 50)
        
        # Stats
        total_ai_chats = len(chat_list)
        
        # Active users (last 30 days) - only count existing users
        thirty_days_ago = datetime.now() - timedelta(days=30)
        active_users = set()
        for chat in all_chats:
            if chat.created_at and chat.created_at >= thirty_days_ago:
                # Only add if user exists in database
                user = User.query.get(chat.user_id)
                if user:
                    active_users.add(chat.user_id)
        active_ai_users = len(active_users)
        
        # Today's chats
        today = datetime.now().date()
        today_chats = 0
        for chat in all_chats:
            if chat.created_at and chat.created_at.date() == today:
                today_chats += 1
        
        return render_template(
            "admin_ai_chats.html",
            ai_chats=chat_list,
            total_ai_chats=total_ai_chats,
            active_ai_users=active_ai_users,
            today_chats=today_chats,
            current_page=1,
            total_pages=1
        )
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}"
        
        
@app.route('/test_ai_chats_json')
def test_ai_chats_json():
    if session.get("role") != "admin":
        return "Admin only"
    
    chats = AIChat.query.order_by(AIChat.created_at.desc()).limit(5).all()
    result = []
    for chat in chats:
        user = User.query.get(chat.user_id)
        result.append({
            'id': chat.id,
            'user': user.username if user else 'Unknown',
            'message': chat.user_message[:50],
            'ai_reply': chat.ai_reply[:50]
        })
    return jsonify(result)
        
@app.route('/debug_ai_chats')
def debug_ai_chats():
    """Debug route to check AI chat data"""
    if session.get("role") != "admin":
        return "Admin access required"
    
    from sqlalchemy import text
    
    output = "<h2>🤖 AI Chat Debug</h2>"
    output += "<style>body{background:#0f172a;color:#fff;font-family:Arial;padding:20px;}</style>"
    
    # 1. Check ai_chat table
    sql = text("SELECT COUNT(*) as total FROM ai_chat")
    result = db.session.execute(sql)
    total_ai_chats = result.scalar()
    output += f"<p>📨 Total AI Chat messages: <strong>{total_ai_chats}</strong></p>"
    
    # 2. Show all AI chats
    if total_ai_chats > 0:
        sql = text("""
            SELECT ac.*, u.username, u.email, u.phone
            FROM ai_chat ac
            LEFT JOIN users u ON ac.user_id = u.id
            ORDER BY ac.created_at DESC
        """)
        chats = db.session.execute(sql)
        
        output += "<h3>📋 All AI Chats:</h3>"
        output += "<table border='1' cellpadding='8' style='border-collapse: collapse; background:#1e293b;'>"
        output += "<tr style='background:#38bdf8; color:#000;'>"
        output += "<th>ID</th><th>User</th><th>User Message</th><th>AI Reply</th><th>Time</th>"
        output += "</tr>"
        
        for chat in chats:
            row = dict(chat._mapping)
            output += f"""
            <tr>
                <td>{row['id']}</td>
                <td><b>{row['username']}</b><br><small>{row['email']}</small></td>
                <td style='max-width:300px;'>{row['user_message'][:100]}</td>
                <td style='max-width:300px;'>{row['ai_reply'][:100]}</td>
                <td>{row['created_at']}</td>
            </tr>
            """
        output += "</table>"
    else:
        output += "<p style='color:#ef4444;'>❌ No AI chats found in database!</p>"
        output += "<p>💡 Tip: Login as a customer and chat with AI assistant to create AI chats.</p>"
    
    # 3. Show users who have AI chats
    sql = text("""
        SELECT u.id, u.username, u.email, COUNT(ac.id) as chat_count
        FROM users u
        LEFT JOIN ai_chat ac ON u.id = ac.user_id
        WHERE u.role = 'customer'
        GROUP BY u.id, u.username, u.email
        ORDER BY chat_count DESC
    """)
    users = db.session.execute(sql)
    
    output += "<h3>👥 Customers with AI Chats:</h3>"
    output += "<table border='1' cellpadding='8' style='border-collapse: collapse; background:#1e293b; margin-top:20px;'>"
    output += "<tr style='background:#38bdf8; color:#000;'>"
    output += "<th>User ID</th><th>Username</th><th>Email</th><th>AI Chat Count</th>"
    output += "</tr>"
    
    for user in users:
        row = dict(user._mapping)
        output += f"""
        <tr>
            <td>{row['id']}</td>
            <td>{row['username']}</td>
            <td>{row['email']}</td>
            <td style='text-align:center;'><b>{row['chat_count']}</b></td>
        </tr>
        """
    output += "</table>"
    
    output += "<br><br><a href='/admin/ai-chats' style='background:#38bdf8; color:#000; padding:10px 20px; text-decoration:none; border-radius:8px;'>← Go to AI Chats Page</a>"
    
    return output

@app.route('/create_test_ai_chats')
def create_test_ai_chats():
    """Create test AI chats for testing"""
    if session.get("role") != "admin":
        return "Admin login required"
    
    # Get any customer
    customer = User.query.filter_by(role='customer').first()
    if not customer:
        return "❌ No customer found! First create a customer account."
    
    # Create test chats
    test_chats = [
        ("My fan is not working", "🔧 Fan Problem Solution:\n\n1. Check switch\n2. Check regulator\n3. Call technician if needed"),
        ("Switch is sparking", "⚠️ DANGER! Turn off main power immediately and call technician!"),
        ("AC not cooling", "❄️ Check AC mode, clean filters, may need gas refilling"),
        ("Hello", "🙏 Namaste! Welcome to TechnoFix AI Assistant!")
    ]
    
    created = 0
    for user_msg, ai_msg in test_chats:
        chat = AIChat(
            user_id=customer.id,
            user_message=user_msg,
            ai_reply=ai_msg,
            created_at=datetime.now()
        )
        db.session.add(chat)
        created += 1
    
    db.session.commit()
    
    return f"""
    <h2>✅ Created {created} test AI chats for customer: {customer.username}</h2>
    <br>
    <a href="/admin/ai-chats">Go to AI Chats Page</a>
    <br><br>
    <a href="/check_ai_chats">Check AI Chats</a>
    """    

@app.route('/check_ai_chats')
def check_ai_chats():
    """Simple check to see if AI chats exist"""
    if session.get("role") != "admin":
        return "Admin login required"
    
    count = AIChat.query.count()
    output = f"""
    <h2>🤖 AI Chats in Database</h2>
    <p><strong>Total AI Chats: {count}</strong></p>
    """
    
    if count > 0:
        chats = AIChat.query.order_by(AIChat.created_at.desc()).limit(10).all()
        output += "<h3>Last 10 AI Chats:</h3>"
        output += "<table border='1' cellpadding='8' style='border-collapse: collapse; background:#1e293b;'>"
        output += "<tr style='background:#38bdf8; color:#000;'><th>ID</th><th>User</th><th>User Message</th><th>AI Reply</th><th>Time</th></tr>"
        
        for chat in chats:
            user = User.query.get(chat.user_id)
            username = user.username if user else "Unknown"
            output += f"""
            <tr>
                <td>{chat.id}</td>
                <td><b>{username}</b></td>
                <td style='max-width:300px;'>{chat.user_message[:80]}</td>
                <td style='max-width:300px;'>{chat.ai_reply[:80]}</td>
                <td>{chat.created_at}</td>
            </tr>
            """
        output += "</table>"
    else:
        output += "<p style='color:red;'>❌ No AI chats found! Click below to create test chats.</p>"
        output += "<a href='/create_test_ai_chats' style='background:#38bdf8; color:#000; padding:10px 20px; text-decoration:none; border-radius:8px;'>Create Test AI Chats</a>"
    
    output += "<br><br><a href='/admin/ai-chats' style='background:#38bdf8; color:#000; padding:10px 20px; text-decoration:none; border-radius:8px;'>← Go to AI Chats Page</a>"
    
    return output
@app.route('/debug_ai_chats_count')
def debug_ai_chats_count():
    """Simple debug to check AI chats"""
    count = AIChat.query.count()
    output = f"""
    <h2>AI Chats Debug</h2>
    <p>Total AI Chats in Database: <strong>{count}</strong></p>
    """
    
    if count > 0:
        chats = AIChat.query.order_by(AIChat.created_at.desc()).limit(5).all()
        output += "<h3>Last 5 AI Chats:</h3>"
        output += "<table border='1' cellpadding='8' style='border-collapse: collapse;'>"
        output += "<tr><th>ID</th><th>User ID</th><th>Message</th><th>AI Reply</th><th>Time</th></tr>"
        for chat in chats:
            output += f"""
            <tr>
                <td>{chat.id}</td>
                <td>{chat.user_id}</td>
                <td>{chat.user_message[:50]}</td>
                <td>{chat.ai_reply[:50]}</td>
                <td>{chat.created_at}</td>
            </tr>
            """
        output += "</table>"
    else:
        output += "<p style='color:red;'>❌ No AI chats found! First chat with AI as customer.</p>"
    
    output += "<br><a href='/admin/ai-chats'>Go to AI Chats Page</a>"
    return output
# ================= LIVE CHAT DATA API =================
@app.route('/api/live_chat_data')
def api_live_chat_data():
    """API endpoint for real-time chat data (poll every 10 seconds)"""
    if session.get("role") != "admin":
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from sqlalchemy import text
        
        total_ai_chats = AIChat.query.count()
        
        # Active AI users (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        active_ai_users = db.session.query(AIChat.user_id).filter(
            AIChat.created_at >= thirty_days_ago
        ).distinct().count()
        
        # Total human chats
        sql = text("SELECT COUNT(DISTINCT booking_id) FROM chat_messages")
        result = db.session.execute(sql)
        total_human_chats = result.scalar() or 0
        
        # Active human chats (last 7 days)
        seven_days_ago = datetime.now() - timedelta(days=7)
        active_sql = text("""
            SELECT COUNT(DISTINCT booking_id) 
            FROM chat_messages 
            WHERE created_at >= :seven_days_ago
        """)
        active_result = db.session.execute(active_sql, {'seven_days_ago': seven_days_ago})
        active_human_chats = active_result.scalar() or 0
        
        # Today's messages
        today = datetime.now().date()
        today_ai = AIChat.query.filter(func.date(AIChat.created_at) == today).count()
        today_human = ChatMessage.query.filter(func.date(ChatMessage.created_at) == today).count()
        today_messages = today_ai + today_human
        
        return jsonify({
            'success': True,
            'total_ai_chats': total_ai_chats,
            'total_human_chats': total_human_chats,
            'active_ai_users': active_ai_users,
            'active_human_chats': active_human_chats,
            'today_messages': today_messages
        })
        
    except Exception as e:
        print(f"Error in live_chat_data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ================= GET HUMAN CHAT MESSAGES FOR ADMIN =================
@app.route('/admin/get_human_chat_messages/<int:booking_id>')
def admin_get_human_chat_messages(booking_id):
    """Get all messages for a specific human chat (admin view)"""
    if session.get("role") != "admin":
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    try:
        messages = ChatMessage.query.filter_by(booking_id=booking_id).order_by(ChatMessage.created_at).all()
        
        message_list = []
        for msg in messages:
            sender = User.query.get(msg.sender_id)
            booking = ServiceRequest.query.get(booking_id)
            sender_role = 'customer' if booking and sender.id == booking.customer_id else 'technician'
            
            message_list.append({
                'id': msg.id,
                'message': msg.message,
                'sender_id': msg.sender_id,
                'sender_name': sender.username if sender else 'Unknown',
                'sender_role': sender_role,
                'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M:%S') if msg.created_at else ''
            })
        
        return jsonify({
            'success': True,
            'messages': message_list
        })
        
    except Exception as e:
        print(f"Error loading human chat messages: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ================= ADMIN TECHNICIANS =================
@app.route("/admin/technicians")
def admin_technicians():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    
    technicians = User.query.filter_by(role="technician").all()
    tech_list = []
    total_earnings = 0
    active_count = 0
    busy_count = 0
    
    for t in technicians:
        bookings = ServiceRequest.query.filter_by(technician_id=t.id).all()
        completed = sum(1 for b in bookings if b.status == 'completed')
        pending = sum(1 for b in bookings if b.status == 'pending')
        
        earnings = t.salary or 0
        total_earnings += earnings
        
        status = t.status if t.status else 'Active'
        if status == 'Active':
            active_count += 1
        elif status == 'Busy':
            busy_count += 1
        
        tech_list.append({
            'id': t.id,
            'username': t.username,
            'email': t.email,
            'phone': t.phone,
            'location': t.location,
            'specialization': t.specialization,
            'salary': t.salary,
            'rating': t.rating or 0,
            'status': status,
            'total_bookings': len(bookings),
            'completed_bookings': completed,
            'pending_bookings': pending
        })
    
    return render_template(
        "admin_technicians.html",  # ← સાચું નામ (ફક્ત આ લાઇન ચેક કરો)
        technicians=tech_list,
        total_technicians=len(tech_list),
        active_technicians=active_count,
        busy_technicians=busy_count,
        total_earnings=total_earnings
    )
# ================= EDIT TECHNICIAN =================
@app.route('/admin/technician/<int:technician_id>/edit', methods=['GET', 'POST'])
def edit_technician(technician_id):
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    
    technician = User.query.get_or_404(technician_id)
    
    if request.method == 'POST':
        try:
            technician.username = request.form.get('username')
            technician.email = request.form.get('email')
            technician.phone = request.form.get('phone')
            technician.location = request.form.get('location')
            technician.specialization = request.form.get('specialization')
            technician.salary = float(request.form.get('salary', 0)) if request.form.get('salary') else None
            technician.rating = float(request.form.get('rating', 0)) if request.form.get('rating') else None
            technician.status = request.form.get('status')
            
            db.session.commit()
            flash("Technician updated successfully!", "success")
            return redirect(url_for("admin_technicians"))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating technician: {str(e)}", "danger")
    
    return render_template("edit_technician.html", technician=technician)

# ================= VIEW TECHNICIAN =================
@app.route('/admin/technician/<int:technician_id>')
def view_technician(technician_id):
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    
    technician = User.query.get_or_404(technician_id)
    bookings = ServiceRequest.query.filter_by(technician_id=technician_id).order_by(ServiceRequest.created_at.desc()).all()
    
    return render_template("view_technician.html", technician=technician, bookings=bookings)

# ================= DELETE TECHNICIAN =================
@app.route('/admin/technician/<int:technician_id>/delete', methods=['POST'])
def delete_technician(technician_id):
    if session.get("role") != "admin":
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    technician = User.query.get(technician_id)
    if not technician or technician.role != 'technician':
        return jsonify({'success': False, 'error': 'Technician not found'})
    
    try:
        # Update bookings
        ServiceRequest.query.filter_by(technician_id=technician_id).update({'technician_id': None})
        Notification.query.filter_by(user_id=technician_id).delete()
        
        db.session.delete(technician)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

# ================= DELETE CUSTOMER =================
@app.route('/admin/customer/<int:customer_id>/delete', methods=['POST'])
def delete_customer(customer_id):
    if session.get("role") != "admin":
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    customer = User.query.get(customer_id)
    if not customer or customer.role != 'customer':
        return jsonify({'success': False, 'error': 'Customer not found'})
    
    try:
        # Delete related records
        ServiceRequest.query.filter_by(customer_id=customer_id).delete()
        Feedback.query.filter_by(customer_id=customer_id).delete()
        AIChat.query.filter_by(user_id=customer_id).delete()
        Notification.query.filter_by(user_id=customer_id).delete()
        
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

# ================= UPDATE BOOKING STATUS =================
@app.route('/admin/update_booking_status', methods=['POST'])
def admin_update_booking_status():
    if session.get("role") != "admin":
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    data = request.get_json()
    booking_id = data.get('booking_id')
    new_status = data.get('status')
    
    booking = ServiceRequest.query.get(booking_id)
    if not booking:
        return jsonify({'success': False, 'error': 'Booking not found'})
    
    try:
        booking.status = new_status
        db.session.commit()
        
        # Create notifications
        if booking.customer_id:
            notif = Notification(
                user_id=booking.customer_id,
                message=f"Your booking #{booking_id} status updated to {new_status}",
                is_read=False
            )
            db.session.add(notif)
        
        if booking.technician_id:
            notif = Notification(
                user_id=booking.technician_id,
                message=f"Booking #{booking_id} status updated to {new_status}",
                is_read=False
            )
            db.session.add(notif)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})
    
    

# ==================== INIT DATABASE ====================
@app.route('/init_db')
def init_db():
    db.create_all()
    
    # Create admin user if not exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            password=generate_password_hash('admin123'),
            role='admin',
            status='Active'
        )
        db.session.add(admin)
    
    # Create sample customers
    if User.query.filter_by(role='customer').count() == 0:
        customer1 = User(
            username='john_doe',
            email='john@example.com',
            password=generate_password_hash('password123'),
            role='customer',
            phone='1234567890',
            address='New York',
            status='Active'
        )
        customer2 = User(
            username='jane_smith',
            email='jane@example.com',
            password=generate_password_hash('password123'),
            role='customer',
            phone='0987654321',
            address='Los Angeles',
            status='Active'
        )
        db.session.add_all([customer1, customer2])
    
    # Create sample technicians
    if User.query.filter_by(role='technician').count() == 0:
        tech1 = User(
            username='mike_wilson',
            email='mike@example.com',
            password=generate_password_hash('password123'),
            role='technician',
            phone='1112223333',
            location='New York',
            specialization='Plumbing',
            salary=3000,
            status='Active',
            rating=4.8
        )
        tech2 = User(
            username='sarah_johnson',
            email='sarah@example.com',
            password=generate_password_hash('password123'),
            role='technician',
            phone='4445556666',
            location='Los Angeles',
            specialization='Electrical',
            salary=3200,
            status='Active',
            rating=4.9
        )
        db.session.add_all([tech1, tech2])
    
    db.session.commit()
    
    return 'Database initialized!'

@app.route('/debug_human_chats')
def debug_human_chats():
    """Debug human chats"""
    if session.get("role") != "admin":
        return "Admin only"
    
    from sqlalchemy import text
    
    output = "<h2>🔍 Human Chats Debug</h2>"
    
    # Check chat_messages table
    sql = text("SELECT COUNT(*) FROM chat_messages")
    result = db.session.execute(sql)
    total_msgs = result.scalar()
    output += f"<p>Total messages in chat_messages: <strong>{total_msgs}</strong></p>"
    
    if total_msgs > 0:
        # Show all chats grouped by booking
        sql = text("""
            SELECT 
                cm.booking_id,
                COUNT(cm.id) as msg_count,
                MIN(cm.created_at) as first_msg,
                MAX(cm.created_at) as last_msg,
                (SELECT message FROM chat_messages cm2 
                 WHERE cm2.booking_id = cm.booking_id 
                 ORDER BY cm2.created_at DESC LIMIT 1) as last_message
            FROM chat_messages cm
            GROUP BY cm.booking_id
            ORDER BY last_msg DESC
        """)
        result = db.session.execute(sql)
        
        output += "<h3>📋 Chat Groups (by Booking ID):</h3>"
        output += "<table border='1' cellpadding='8' style='border-collapse: collapse; background:#1e293b;'>"
        output += "<tr style='background:#38bdf8; color:#000;'><th>Booking ID</th><th>Messages</th><th>Last Message</th><th>Last Time</th></tr>"
        
        for row in result:
            row_dict = dict(row._mapping)
            output += f"""
            <tr>
                <td><b>#{row_dict['booking_id']}</b></td>
                <td>{row_dict['msg_count']}</td>
                <td>{row_dict['last_message'][:50] if row_dict['last_message'] else ''}</td>
                <td>{row_dict['last_msg']}</td>
            </tr>
            """
        output += "</table>"
    else:
        output += "<p style='color:red;'>❌ No messages in chat_messages table!</p>"
        output += "<p>Create test chats: <a href='/create_test_human_chats'>Click here</a></p>"
    
    return output

@app.route('/create_test_human_chats')
def create_test_human_chats():
    """Create test human chats"""
    if session.get("role") != "admin":
        return "Admin only"
    
    # Get a booking with technician assigned
    booking = ServiceRequest.query.filter(
        ServiceRequest.technician_id.isnot(None)
    ).first()
    
    if not booking:
        return "❌ No booking with technician assigned found! First create a booking with technician."
    
    # Get customer and technician
    customer = User.query.get(booking.customer_id)
    technician = User.query.get(booking.technician_id)
    
    if not customer or not technician:
        return f"❌ Missing users: Customer={customer}, Technician={technician}"
    
    # Create test messages
    test_messages = [
        {"sender": customer, "receiver": technician, "msg": f"Hello, I need help with my {booking.service.name} service."},
        {"sender": technician, "receiver": customer, "msg": "Hi! I'll be there soon. Can you share more details about the problem?"},
        {"sender": customer, "receiver": technician, "msg": "The problem is exactly as described in the booking. Please come asap!"},
        {"sender": technician, "receiver": customer, "msg": "On my way! Estimated arrival in 30 minutes."},
    ]
    
    created = 0
    for msg_data in test_messages:
        chat = ChatMessage(
            booking_id=booking.id,
            sender_id=msg_data["sender"].id,
            receiver_id=msg_data["receiver"].id,
            message=msg_data["msg"],
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.session.add(chat)
        created += 1
    
    db.session.commit()
    
    return f"""
    <h2>✅ Test Human Chats Created!</h2>
    <p>Booking ID: #{booking.id}</p>
    <p>Customer: {customer.username}</p>
    <p>Technician: {technician.username}</p>
    <p>Messages created: {created}</p>
    <br>
    <a href="/admin/human-chats">Go to Human Chats Page</a>
    <br><br>
    <a href="/debug_human_chats">Check Debug</a>
    """
# ==================== FIX CHAT FOR BOOKING #32 - NEW NAME ====================
@app.route('/fix_booking_32_chat')
def fix_booking_32_chat():
    """Fix chat for booking #32 - NEW NAME"""
    output = "<h2>🔧 Chat Fix for Booking #32</h2>"
    output += "<style>body{background:#0f172a;color:#fff;font-family:Arial;padding:20px;}</style>"
    
    # 1. Check booking
    booking = ServiceRequest.query.get(32)
    if not booking:
        return output + "<p style='color:#ef4444;'>❌ Booking #32 not found!</p>"
    
    output += f"<p>✅ Booking #32 found</p>"
    output += f"<p>Customer ID: {booking.customer_id}</p>"
    output += f"<p>Technician ID: <b>{booking.technician_id}</b></p>"
    
    # 2. Check technician
    if booking.technician_id:
        tech = User.query.get(booking.technician_id)
        if tech:
            output += f"<p style='color:#22c55e;'>✅ Technician: {tech.username} (ID: {tech.id})</p>"
        else:
            output += f"<p style='color:#ef4444;'>❌ Technician not found in users table!</p>"
            # Assign first technician
            first_tech = User.query.filter_by(role='technician').first()
            if first_tech:
                booking.technician_id = first_tech.id
                db.session.commit()
                output += f"<p style='color:#22c55e;'>✅ Assigned technician: {first_tech.username}</p>"
    else:
        # Assign first technician
        first_tech = User.query.filter_by(role='technician').first()
        if first_tech:
            booking.technician_id = first_tech.id
            db.session.commit()
            output += f"<p style='color:#22c55e;'>✅ Assigned technician: {first_tech.username}</p>"
        else:
            output += f"<p style='color:#ef4444;'>❌ No technicians in database!</p>"
    
    # 3. Fix chat messages
    from sqlalchemy import text
    
    # Update all messages with NULL receiver_id
    sql1 = text("""
        UPDATE chat_messages cm
        JOIN service_requests sr ON cm.booking_id = sr.id
        SET cm.receiver_id = CASE 
            WHEN cm.sender_id = sr.customer_id THEN sr.technician_id
            WHEN cm.sender_id = sr.technician_id THEN sr.customer_id
            ELSE 0
        END
        WHERE cm.booking_id = 32 
        AND (cm.receiver_id IS NULL OR cm.receiver_id = 0)
    """)
    
    result1 = db.session.execute(sql1)
    output += f"<p>✅ Fixed {result1.rowcount} messages with NULL receiver_id</p>"
    
    # Ensure all messages have correct receiver_id
    sql2 = text("""
        UPDATE chat_messages cm
        JOIN service_requests sr ON cm.booking_id = sr.id
        SET cm.receiver_id = CASE 
            WHEN cm.sender_id = sr.customer_id THEN sr.technician_id
            WHEN cm.sender_id = sr.technician_id THEN sr.customer_id
        END
        WHERE cm.booking_id = 32
        AND (
            (cm.sender_id = sr.customer_id AND cm.receiver_id != sr.technician_id)
            OR 
            (cm.sender_id = sr.technician_id AND cm.receiver_id != sr.customer_id)
        )
    """)
    
    result2 = db.session.execute(sql2)
    output += f"<p>✅ Corrected {result2.rowcount} messages with wrong receiver_id</p>"
    
    db.session.commit()
    
    # 4. Show all messages now
    messages = ChatMessage.query.filter_by(booking_id=32).order_by(ChatMessage.created_at).all()
    output += f"<h3>📨 Total Messages: {len(messages)}</h3>"
    
    for msg in messages:
        sender = User.query.get(msg.sender_id)
        receiver = User.query.get(msg.receiver_id)
        output += f"""
        <div style="background:#1e293b; padding:10px; margin:5px; border-radius:5px;">
            <b>From:</b> {sender.username if sender else 'Unknown'} (ID:{msg.sender_id})<br>
            <b>To:</b> {receiver.username if receiver else 'Unknown'} (ID:{msg.receiver_id})<br>
            <b>Msg:</b> {msg.message}<br>
            <b>Time:</b> {msg.created_at}
        </div>
        """
    
    output += "<br><a href='/customer/my-bookings' style='color:#38bdf8;'>← Back to Bookings</a>"
    
    return output

    
# ==================== DEBUG CHAT ISSUE ====================
@app.route('/debug_chat_issue')
def debug_chat_issue():
    """Debug chat issue for booking #32"""
    if 'user_id' not in session:
        return "Please login first"
    
    output = "<h2>🔍 Chat Issue Debug</h2>"
    output += "<style>body{background:#0f172a;color:#fff;font-family:Arial;padding:20px;} table{border-collapse:collapse;width:100%;} th{background:#38bdf8;color:#000;padding:10px;} td{padding:10px;border-bottom:1px solid#334155;}</style>"
    
    # 1. Check booking #32
    booking = ServiceRequest.query.filter_by(id=32).first()
    if booking:
        output += f"<h3>📋 Booking #32</h3>"
        output += f"<p>Booking ID: {booking.id}</p>"
        output += f"<p>Customer ID: {booking.customer_id}</p>"
        output += f"<p><b>Technician ID: {booking.technician_id}</b></p>"
        output += f"<p>Status: {booking.status}</p>"
        
        # Check technician
        if booking.technician_id:
            tech = User.query.get(booking.technician_id)
            if tech:
                output += f"<p style='color:#22c55e;'>✅ Technician: {tech.username} (ID: {tech.id})</p>"
            else:
                output += f"<p style='color:#ef4444;'>❌ Technician not found in users table!</p>"
        else:
            output += f"<p style='color:#ef4444;'>❌ technician_id is NULL!</p>"
    else:
        output += f"<p style='color:#ef4444;'>❌ Booking #32 not found!</p>"
    
    # 2. Check all chat messages for booking #32
    messages = ChatMessage.query.filter_by(booking_id=32).all()
    output += f"<h3>💬 Chat Messages (Total: {len(messages)})</h3>"
    
    if messages:
        output += "<table>"
        output += "<tr><th>ID</th><th>Sender</th><th>Receiver</th><th>Message</th><th>Created</th></tr>"
        for msg in messages:
            sender = User.query.get(msg.sender_id)
            receiver = User.query.get(msg.receiver_id)
            output += f"<tr>"
            output += f"<td>{msg.id}</td>"
            output += f"<td>{sender.username if sender else 'Unknown'} (ID:{msg.sender_id})</td>"
            output += f"<td><b>{receiver.username if receiver else 'NULL'}</b> (ID:{msg.receiver_id})</td>"
            output += f"<td>{msg.message[:30]}</td>"
            output += f"<td>{msg.created_at}</td>"
            output += f"</tr>"
        output += "</table>"
    else:
        output += "<p>No messages found</p>"
    
    # 3. Fix button
    output += """
    <div style='margin-top:30px;'>
        <form action='/fix_chat_for_booking_32' method='post' style='display:inline;'>
            <button type='submit' style='background:#38bdf8; color:black; padding:10px 20px; border:none; border-radius:5px; margin:5px; cursor:pointer; font-size:16px;'>
                🔧 FIX CHAT FOR BOOKING #32
            </button>
        </form>
        <form action='/fix_chat_table' method='post' style='display:inline;'>
            <button type='submit' style='background:#22c55e; color:black; padding:10px 20px; border:none; border-radius:5px; margin:5px; cursor:pointer; font-size:16px;'>
                🛠️ FIX CHAT TABLE STRUCTURE
            </button>
        </form>
    </div>
    """
    
    return output


@app.route('/debug_database')
def debug_database():
    """Check database users and roles"""
    output = "<h2>Database Users Debug</h2>"
    
    # Saare users check karo
    all_users = User.query.all()
    output += f"<h3>Total Users: {len(all_users)}</h3>"
    
    output += "<table border='1' cellpadding='5' style='border-collapse: collapse;'>"
    output += "<tr><th>ID</th><th>Username</th><th>Email</th><th>Role</th><th>Status</th></tr>"
    
    for user in all_users:
        output += f"<tr>"
        output += f"<td>{user.id}</td>"
        output += f"<td>{user.username}</td>"
        output += f"<td>{user.email}</td>"
        output += f"<td>{user.role if user.role else 'NOT SET'}</td>"
        output += f"<td>{user.status if user.status else 'NOT SET'}</td>"
        output += f"</tr>"
    
    output += "</table>"
    
    # Technicians count
    technicians = User.query.filter_by(role='technician').all()
    output += f"<h3>Technicians Found: {len(technicians)}</h3>"
    
    if technicians:
        output += "<ul>"
        for t in technicians:
            output += f"<li>ID: {t.id}, Name: {t.username}</li>"
        output += "</ul>"
    else:
        output += "<p style='color:red;'>❌ No technicians found with role='technician'</p>"
    
    # Service requests check
    requests = ServiceRequest.query.all()
    output += f"<h3>Service Requests: {len(requests)}</h3>"
    
    return output
@app.route('/debug_bookings')
def debug_bookings():
    if 'user_id' not in session or session.get('role') != 'technician':
        return 'Please login as technician first'
    
    tech_id = session.get('user_id')
    bookings = ServiceRequest.query.filter_by(technician_id=tech_id).all()
    
    html = f"<h2>Bookings for Technician ID: {tech_id}</h2>"
    html += f"<p>Total Bookings: {len(bookings)}</p>"
    
    if bookings:
        html += "<ul>"
        for b in bookings:
            html += f"<li>Booking ID: {b.id}, Customer ID: {b.customer_id}, Status: {b.status}</li>"
        html += "</ul>"
    else:
        html += "<p style='color:red;'>No bookings found!</p>"
    
    html += '<br><a href="/technician/dashboard">Back to Dashboard</a>'
    return html

@app.route('/debug_customers')
def debug_customers():
    customers = User.query.filter_by(role='customer').all()
    
    html = f"<h2>All Customers: {len(customers)}</h2>"
    html += "<ul>"
    for c in customers:
        html += f"<li>ID: {c.id}, Name: {c.username}, Email: {c.email}</li>"
    html += "</ul>"
    
    return html
@app.route('/debug_technician_notifications')
def debug_technician_notifications():
    """Check all notifications in database"""
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    notifications = Notification.query.order_by(Notification.id.desc()).limit(50).all()
    
    html = "<h2>🔔 All Notifications in Database</h2>"
    html += "<table border='1' cellpadding='8' style='border-collapse: collapse;'>"
    html += "<tr><th>ID</th><th>User ID</th><th>Username</th><th>Message</th><th>Read</th><th>Created At</th></tr>"
    
    for n in notifications:
        user = User.query.get(n.user_id)
        html += f"<tr>"
        html += f"<td>{n.id}</td>"
        html += f"<td>{n.user_id}</td>"
        html += f"<td>{user.username if user else 'Unknown'}</td>"
        html += f"<td>{n.message}</td>"
        html += f"<td>{'✅' if n.is_read else '❌'}</td>"
        html += f"<td>{n.created_at}</td>"
        html += f"</tr>"
    
    html += "</table>"
    
    # Show technicians
    technicians = User.query.filter_by(role='technician').all()
    html += "<h2>👨‍🔧 Technicians</h2>"
    html += "<ul>"
    for t in technicians:
        html += f"<li>ID: {t.id}, Name: {t.username}, Email: {t.email}</li>"
    html += "</ul>"
    
    return html


@app.route('/debug_my_notifications')
def debug_my_notifications():
    """Check notifications for current logged in user"""
    if 'user_id' not in session:
        return "Please login first"
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Get notifications from database
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.id.desc()).all()
    
    html = f"""
    <html>
    <head>
        <title>My Notifications Debug</title>
        <style>
            body {{ background: #0f172a; color: white; font-family: Arial; padding: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th {{ background: #38bdf8; color: black; padding: 10px; }}
            td {{ padding: 10px; border-bottom: 1px solid #334155; }}
            .unread {{ background: rgba(56, 189, 248, 0.2); }}
        </style>
    </head>
    <body>
        <h1>🔍 My Notifications Debug</h1>
        <p>User ID: <strong>{user_id}</strong></p>
        <p>Username: <strong>{user.username}</strong></p>
        <p>Role: <strong>{user.role}</strong></p>
        
        <h2>Total Notifications: {len(notifications)}</h2>
        
        <table>
            <tr>
                <th>ID</th>
                <th>Message</th>
                <th>Read Status</th>
                <th>Created At</th>
            </tr>
    """
    
    for n in notifications:
        row_class = "unread" if not n.is_read else ""
        html += f"""
            <tr class="{row_class}">
                <td>{n.id}</td>
                <td>{n.message}</td>
                <td>{'❌ Unread' if not n.is_read else '✅ Read'}</td>
                <td>{n.created_at}</td>
            </tr>
        """
    
    html += """
        </table>
        
        <h2>Test Actions:</h2>
        <button onclick="createTest()" style="background:#38bdf8; color:black; padding:10px 20px; border:none; border-radius:5px; margin:5px; cursor:pointer;">
            Create Test Notification
        </button>
        
        <button onclick="checkAPI()" style="background:#22c55e; color:black; padding:10px 20px; border:none; border-radius:5px; margin:5px; cursor:pointer;">
            Check API Response
        </button>
        
        <div id="result" style="margin-top:20px; padding:10px; background:#1e293b; border-radius:5px;"></div>
        
        <script>
            function createTest() {
                fetch('/create_test_notification')
                    .then(r => r.text())
                    .then(data => {
                        document.getElementById('result').innerHTML = data;
                        setTimeout(() => location.reload(), 2000);
                    });
            }
            
            function checkAPI() {
                fetch('/get_technician_notifications')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('result').innerHTML = 
                            '<pre style="color:#38bdf8;">' + JSON.stringify(data, null, 2) + '</pre>';
                    });
            }
        </script>
    </body>
    </html>
    """
    

    return html
@app.route('/debug_chats_data')
def debug_chats_data():
    """Debug route to check chat data"""
    if session.get("role") != "admin":
        return "Admin access required"
    
    from sqlalchemy import text
    
    output = "<h2>🔍 Database Chat Debug</h2>"
    
    # 1. Check chat_messages table
    sql = text("SELECT COUNT(*) as total FROM chat_messages")
    result = db.session.execute(sql)
    total_msgs = result.scalar()
    output += f"<p>📨 Total chat messages: <strong>{total_msgs}</strong></p>"
    
    # 2. Show sample messages
    if total_msgs > 0:
        sql = text("""
            SELECT cm.*, 
                   s.username as sender_name,
                   r.username as receiver_name,
                   sr.id as booking_id,
                   c.username as customer_name,
                   t.username as technician_name
            FROM chat_messages cm
            LEFT JOIN users s ON cm.sender_id = s.id
            LEFT JOIN users r ON cm.receiver_id = r.id
            LEFT JOIN service_requests sr ON cm.booking_id = sr.id
            LEFT JOIN users c ON sr.customer_id = c.id
            LEFT JOIN users t ON sr.technician_id = t.id
            ORDER BY cm.created_at DESC
            LIMIT 10
        """)
        messages = db.session.execute(sql)
        
        output += "<h3>📋 Recent Messages (Last 10):</h3>"
        output += "<table border='1' cellpadding='8' style='border-collapse: collapse;'>"
        output += "<tr><th>ID</th><th>Booking</th><th>From</th><th>To</th><th>Message</th><th>Time</th></tr>"
        
        for msg in messages:
            row = dict(msg._mapping)
            output += f"""
            <tr>
                <td>{row['id']}</td>
                <td>#{row['booking_id']}</td>
                <td>{row['sender_name']}</td>
                <td>{row['receiver_name']}</td>
                <td>{row['message'][:50]}</td>
                <td>{row['created_at']}</td>
            </tr>
            """
        output += "</table>"
    else:
        output += "<p style='color:red;'>❌ No chat messages found in database!</p>"
        output += "<p>💡 Tip: Create a test chat message to see if it appears.</p>"
    
    # 3. Check service_requests table
    bookings = ServiceRequest.query.all()
    output += f"<h3>📚 Total Bookings: {len(bookings)}</h3>"
    
    return output
@app.route('/test_chat_route', methods=['POST'])
def test_chat_route():
    return jsonify({'success': True, 'message': 'Route working!'})

@app.route('/debug_missing_users')
def debug_missing_users():
    """Find chats with missing users"""
    if session.get("role") != "admin":
        return "Admin only"
    
    chats = AIChat.query.all()
    missing_users = []
    
    for chat in chats:
        user = User.query.get(chat.user_id)
        if not user:
            missing_users.append({
                'chat_id': chat.id,
                'user_id': chat.user_id,
                'message': chat.user_message[:50]
            })
    
    if missing_users:
        output = "<h2>⚠️ Chats with Missing Users</h2>"
        output += "<table border='1' cellpadding='8'>"
        output += "汽<th>Chat ID</th><th>User ID (Missing)</th><th>Message</th> </tr>"
        for m in missing_users:
            output += f"<tr><td>{m['chat_id']}</td><td>{m['user_id']}</td><td>{m['message']}</td></tr>"
        output += "</table>"
        output += "<p>Total missing users: {len(missing_users)}</p>"
    else:
        output = "<h2>✅ All chats have valid users!</h2>"
    
    return output

@app.route('/debug-ai')
def debug_ai():
    """Check AI configuration"""
    if GEMINI_API_KEY:
        return f"""
        <html>
        <head><title>AI Debug</title>
        <style>
            body {{ background: #0f172a; color: white; font-family: Arial; padding: 20px; }}
            .success {{ color: #22c55e; }}
            .error {{ color: #ef4444; }}
            pre {{ background: #1e293b; padding: 10px; border-radius: 5px; }}
        </style>
        </head>
        <body>
            <h1 class='success'>✅ AI Configuration OK</h1>
            <p>API Key: {GEMINI_API_KEY[:8]}...{GEMINI_API_KEY[-5:]}</p>
            <p>Model: gemini-1.5-flash</p>
            <p>GenAI Configured: Yes</p>
            <h3>Test Response:</h3>
            <pre>Testing... <span id='result'></span></pre>
            <button onclick='testAI()' style='padding:10px 20px; background:#38bdf8; border:none; border-radius:5px; cursor:pointer;'>Test AI</button>
            <script>
                async function testAI() {{
                    let res = await fetch('/chat', {{
                        method:'POST',
                        headers:{{'Content-Type':'application/json'}},
                        body:JSON.stringify({{message:'Hello, test message'}})
                    }});
                    let data = await res.json();
                    document.getElementById('result').innerText = data.reply;
                }}
            </script>
            <br><br>
            <a href='/customer/dashboard' style='color:#38bdf8;'>← Back to Dashboard</a>
        </body>
        </html>
        """
    else:
        return """
        <html>
        <head><title>AI Debug</title>
        <style>
            body { background: #0f172a; color: white; font-family: Arial; padding: 20px; }
            .error { color: #ef4444; }
        </style>
        </head>
        <body>
            <h1 class='error'>❌ API Key Missing</h1>
            <p>Create .env file with: GEMINI_API_KEY=your_key_here</p>
            <p>Current directory: """ + os.getcwd() + """</p>
            <p>Files in directory:</p>
            <pre>""" + str(os.listdir('.')) + """</pre>
        </body>
        </html>
        """
# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
    
