
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# إعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT, password TEXT, role TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price REAL, image TEXT, description TEXT, category TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS cart (user_id INTEGER, product_id INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (product_id INTEGER, user_id INTEGER, rating INTEGER, comment TEXT)''')
    conn.commit()
    conn.close()

# إنشاء حساب المدير
def create_admin():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    hashed_password = bcrypt.hashpw('Ali12121997@#'.encode('utf-8'), bcrypt.gensalt())
    c.execute("INSERT OR IGNORE INTO users (email, password, role) VALUES (?, ?, ?)", 
              ('alisaedi012@gmail.com', hashed_password, 'admin'))
    conn.commit()
    conn.close()

# إرسال إشعارات عبر البريد الإلكتروني
def send_email(to_email, subject, message):
    from_email = "alisaedi012@gmail.com"
    password = "Ali12121997@#"
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", e)

# صفحة إعدادات الحساب الشخصي
@app.route('/account', methods=['GET', 'POST'])
def account():
    if 'user' in session:
        if request.method == 'POST':
            email = request.form['email']
            password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("UPDATE users SET email = ?, password = ? WHERE email = ?", (email, password, session['user']))
            conn.commit()
            session['user'] = email
            flash('تم تحديث الحساب بنجاح!')
            conn.close()
        return render_template('account.html', user=session['user'])
    return redirect(url_for('login'))

# صفحة تفاصيل المنتج مع دعم الصور المتعددة
@app.route('/product/<int:product_id>')
def product_details(product_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = c.fetchone()
    conn.close()
    return render_template('product.html', product=product)

# صفحة التصنيفات
@app.route('/category/<category>')
def category(category):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE category = ?", (category,))
    products = c.fetchall()
    conn.close()
    return render_template('index.html', products=products)

if __name__ == '__main__':
    init_db()
    create_admin()
    app.run(debug=True)
