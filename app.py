from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import qrcode
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'qrcodes'
db = SQLAlchemy(app)

# Database Model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120))
    event_name = db.Column(db.String(100))
    qr_code = db.Column(db.String(200))

# Initialize DB
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        event_name = request.form['event']

        booking = Booking(name=name, email=email, event_name=event_name)
        db.session.add(booking)
        db.session.commit()

        # Generate QR Code
        qr_data = f"Name: {name}\nEvent: {event_name}\nBooking ID: {booking.id}"
        qr_img = qrcode.make(qr_data)
        qr_path = os.path.join(app.config['UPLOAD_FOLDER'], f"ticket_{booking.id}.png")
        qr_img.save(qr_path)

        booking.qr_code = qr_path
        db.session.commit()

        return redirect(url_for('success', booking_id=booking.id))
    return render_template('book.html')

@app.route('/success/<int:booking_id>')
def success(booking_id):
    booking = Booking.query.get(booking_id)
    return render_template('success.html', booking=booking)

@app.route('/qrcodes/<filename>')
def qrcodes(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/admin')
def admin():
    all_bookings = Booking.query.all()
    return render_template('admin.html', bookings=all_bookings)

if __name__ == '__main__':
    if not os.path.exists('qrcodes'):
        os.makedirs('qrcodes')
    app.run(debug=True)
