from flask import Flask ,render_template,request, url_for, request, redirect ,flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_mail import Mail, Message
import os
from bs4 import BeautifulSoup
import requests
import numpy as np
import pandas as pd
from estimated_date import Get_Delivery_date
from passlib.hash import sha256_crypt 
import razorpay

app = Flask(__name__,template_folder='templates',static_folder = 'static')
app.secret_key = 'fashion'


# - - - - - - - - - - - - - - - - - - - - - - - - - - - -

app.config.update(
    MAIL_DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL = True,
    TESTING = False,
    MAIL_USERNAME = 'akshitspam1@gmail.com',
    MAIL_PASSWORD = 'ywcanawfzlfowwod'
    ) 

mail = Mail(app)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -

global cart_count

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# save the .sqlite3 file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+'database.sqlite'
app.config['SQLALCHMEY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class Add_to_cart(db.Model):

    __tablename__ = 'Add_to_cart'

    id = db.Column(db.Integer, primary_key=True) # for numbers use Integer
    product_image = db.Column(db.String(200))
    product_title = db.Column(db.String(50))          # for text use Text
    product_quantity = db.Column(db.Integer)
    product_price = db.Column(db.Float)

    def __init__(self,product_image, product_title, product_quantity, product_price):
        self.product_image = product_image
        self.product_title = product_title
        self.product_quantity = product_quantity
        self.product_price = product_price

    def __repr__(self):  
        return(f"{self.id} | {self.product_title} | {self.product_quantity} | {self.product_price}")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class User(db.Model):

    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    number = db.Column(db.String(10))
    password = db.Column(db.String(200), nullable=False)

    def __init__(self, name,email,number,password):
        self.name = name
        self.email = email
        self.number = number
        self.password = password

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class UserHistory(db.Model):

    __tablename__ = 'UserHistory'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(200), nullable=False)
    state = db.Column(db.String(200), nullable=False)
    zipcode = db.Column(db.String(6))
    orders = db.Column(db.String(200), nullable=False)

    def __init__(self,name,address,city,state,zipcode,orders):
        self.name = name
        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.orders = orders

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
cos_similarity = pd.read_csv('all_similarites_DeepFashion_data_women.csv', index_col=0)
#cos_similarity.set_index('Unnamed: 0', inplace=True)

def retrieve_similarity(given_img, nb_closest_images=8):
    
    closest_imgs = cos_similarity[given_img].sort_values(ascending=False)[1: nb_closest_images+1].index
    #closest_imgs_scores = cos_similarity[given_img].sort_values(ascending=False)[1: nb_closest_images+1]
    print(closest_imgs)

    return(closest_imgs, given_img)

cos_similarity_men = pd.read_csv('all_similarites_DeepFashion_data_men.csv', index_col=0)
#cos_similarity_men.set_index('Unnamed: 0', inplace=True)

def retrieve_similarity_men(given_img, nb_closest_images=8):
    
    closest_imgs = cos_similarity_men[given_img].sort_values(ascending=False)[1: nb_closest_images+1].index
    #closest_imgs_scores = cos_similarity[given_img].sort_values(ascending=False)[1: nb_closest_images+1]
    
    return(closest_imgs, given_img)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - -

@app.route('/login', methods = ['GET','POST'])
def login():

    session['logged_in'] = False

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()

        if user.email == email and sha256_crypt.verify(password, user.password):
            session['logged_in'] = True
            session["username"] = user.name
            session["email"] = user.email
            session["number"] = user.number

            flash ('Successfully Logged In!' ,'success')
            return(redirect(url_for('my_acc')))

        else :
            flash('Please Enter Correct Password' , 'danger')
        
    return render_template('login.html')

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -

@app.route('/signup',methods = ['GET','POST'])
def signup():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        number = request.form['number']
        password0 = request.form['password0']
        password = request.form['password']
        hash_password = sha256_crypt.encrypt(str(password))

        existing = User.query.filter_by(email=email).first()

        if existing:
            flash ('This email is already registered !','danger')

        else:
            user = User(name=name,email=email,number=number,password=hash_password)

            db.session.add(user)
            db.session.commit()

            if password0 == password:
                flash ('Account succesfully created','success')
                return redirect(url_for('login'))

            else:
                flash ('Check Your password')

    return render_template('signup.html')

@app.route("/logout")
def logout():
    session.clear()
    session['logged_in'] = False
    return redirect(url_for('index'))


@app.route('/')
def index() :
    items = Add_to_cart.query.all()
    cart_count = len(items)

    return render_template('index.html',cart_count = cart_count)

@app.route('/mens_collection' , methods=['GET', 'POST'])
def mens_collection () :
    items = Add_to_cart.query.all()
    cart_count = len(items)

    return render_template('mens-coll.html' ,cart_count = cart_count)

@app.route('/womens_collection' , methods=['GET', 'POST'])
def womens_collection () :
    items = Add_to_cart.query.all()
    cart_count = len(items)

    return render_template('womens-coll.html'  ,cart_count = cart_count)

@app.route('/3d_dresses' , methods=['GET', 'POST'])
def three_d_dresses() :
    return render_template('3d_dresses.html')

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# create all routes for all men dresses
@app.route('/mens_collection/men_dress_1' , methods=['GET', 'POST'])
def men_dress_1() :

    ip_img = "Tees_Tanks/id_00000390/09_1_front.jpg"
    similar_items_img_list, given_img = retrieve_similarity_men(ip_img)

    return render_template('men_dress_1.html', similar_items_img_list=similar_items_img_list, given_img=given_img, os=os)

@app.route('/mens_collection/men_dress_2' , methods=['GET', 'POST'])
def men_dress_2() :

    ip_img = "Shirts_Polos/id_00000846/03_1_front.jpg"
    similar_items_img_list, given_img = retrieve_similarity_men(ip_img)

    return render_template('men_dress_2.html', similar_items_img_list=similar_items_img_list, given_img=given_img, os=os)

@app.route('/mens_collection/men_dress_3' , methods=['GET', 'POST'])
def men_dress_3() :

    ip_img = "Shirts_Polos/id_00000193/06_7_additional.jpg"
    similar_items_img_list, given_img = retrieve_similarity_men(ip_img)

    return render_template('men_dress_3.html', similar_items_img_list=similar_items_img_list, given_img=given_img, os=os)

@app.route('/mens_collection/men_dress_4' , methods=['GET', 'POST'])
def men_dress_4() :

    ip_img = "Tees_Tanks/id_00000185/01_4_full.jpg"
    similar_items_img_list, given_img = retrieve_similarity_men(ip_img)

    return render_template('men_dress_4.html', similar_items_img_list=similar_items_img_list, given_img=given_img, os=os)

@app.route('/mens_collection/men_dress_5' , methods=['GET', 'POST'])
def men_dress_5() :

    ip_img = "Tees_Tanks/id_00000390/14_7_additional.jpg"
    similar_items_img_list, given_img = retrieve_similarity_men(ip_img)

    return render_template('men_dress_5.html', similar_items_img_list=similar_items_img_list, given_img=given_img, os=os)

@app.route('/mens_collection/men_dress_6' , methods=['GET', 'POST'])
def men_dress_6() :

    ip_img = "Tees_Tanks/id_00000705/01_1_front.jpg"
    similar_items_img_list, given_img = retrieve_similarity_men(ip_img)

    return render_template('men_dress_6.html', similar_items_img_list=similar_items_img_list, given_img=given_img, os=os)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# create all routes for all women dresses
@app.route('/womens_collection/women_dress_1' , methods=['GET', 'POST'])
def women_dress_1() :

    ip_img = "Dresses/id_00000169/04_1_front.jpg"
    similar_items_img_list, given_img = retrieve_similarity(ip_img)

    #print(similar_items_img_list)

    return render_template('women_dress_1.html', similar_items_img_list=similar_items_img_list, given_img=given_img, os=os)

@app.route('/womens_collection/women_dress_2' , methods=['GET', 'POST'])
def women_dress_2() :

    ip_img = "Dresses/id_00000348/07_4_full.jpg"
    similar_items_img_list, given_img = retrieve_similarity(ip_img)

    #print(similar_items_img_list)

    return render_template('women_dress_2.html', similar_items_img_list=similar_items_img_list, given_img=given_img, os=os)

@app.route('/womens_collection/women_dress_3' , methods=['GET', 'POST'])
def women_dress_3() :

    ip_img = "Dresses/id_00000134/02_4_full.jpg"
    similar_items_img_list, given_img = retrieve_similarity(ip_img)

    #print(similar_items_img_list)

    return render_template('women_dress_3.html', similar_items_img_list=similar_items_img_list, given_img=given_img, os=os)

@app.route('/womens_collection/women_dress_4' , methods=['GET', 'POST'])
def women_dress_4() :

    ip_img = "Dresses/id_00000229/02_1_front.jpg"
    similar_items_img_list, given_img = retrieve_similarity(ip_img)

    #print(similar_items_img_list)

    return render_template('women_dress_4.html', similar_items_img_list=similar_items_img_list, given_img=given_img, os=os)

@app.route('/womens_collection/women_dress_5' , methods=['GET', 'POST'])
def women_dress_5() :

    ip_img = "Dresses/id_00000021/05_1_front.jpg"
    similar_items_img_list, given_img = retrieve_similarity(ip_img)

    #print(similar_items_img_list)

    return render_template('women_dress_5.html', similar_items_img_list=similar_items_img_list, given_img=given_img, os=os)

@app.route('/womens_collection/women_dress_6' , methods=['GET', 'POST'])
def women_dress_6() :

    ip_img = "Dresses/id_00000472/02_1_front.jpg"
    similar_items_img_list, given_img = retrieve_similarity(ip_img)

    #print(similar_items_img_list)

    return render_template('women_dress_6.html', similar_items_img_list=similar_items_img_list, given_img=given_img, os=os)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# dynamic routing
@app.route('/<collections>/<product_name>,<img_url1>,<img_url2>,<img_url3>', methods=['GET', 'POST'])
def dynamic_route(collections, product_name, img_url1, img_url2, img_url3):
    
    img_url = f"{img_url3}/{img_url2}/{img_url1}"

    ip_img = img_url

    if collections == 'womens_collection':
        similar_items_img_list, given_img = retrieve_similarity(ip_img)
    
    elif collections == 'mens_collection':
        similar_items_img_list, given_img = retrieve_similarity_men(ip_img)
    
    return(render_template('dynamic_route.html', name=product_name, img_url=img_url, similar_items_img_list=similar_items_img_list, given_img=given_img, os=os, collections=collections))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@app.route('/contact')
def contact():
    return(render_template('contact-us.html'))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.route('/last_viewed')
def return_last():
    print(request.referrer)

    return(redirect(url_for('view_cart')))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.route('/added_to_cart', methods=['GET', 'POST'])
def add_to_cart():
    
    if request.method == 'POST':
        #print(request.referrer)
        reqs = requests.get(request.referrer)
        soup = BeautifulSoup(reqs.text, 'lxml')

        product_image = soup.find("img", {"id": "ProductImg"})['src']
        product_name = soup.find("h1", {"class": "product-title"}).text
        product_prize = soup.find("span", class_ = "current-price").text[1:]
      
        #print(product_image)

        item = Add_to_cart(product_image, product_name, 1, float(product_prize))
        db.session.add(item)
        db.session.commit()
        
        #print(os.path.split(request.referrer)[0])

        return(redirect(os.path.split(request.referrer)[0]))
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@app.route('/removed_from_cart/<name>', methods=['GET'])
def remove_item(name):

    item = Add_to_cart.query.filter_by(product_title=name).first()
    db.session.delete(item)
    db.session.commit()

    return(redirect(url_for('view_cart')))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.route('/view_cart_items')
def view_cart():
    
    items = Add_to_cart.query.all()
    cart_count = len(items)
    
    subtotal = 0

    for item in items:
        subtotal += item.product_price
    
    return(render_template('shopping_cart.html', items=items, subtotal=subtotal,cart_count = cart_count ,total=(subtotal+9)))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.route('/checkout',  methods=['GET', 'POST'])
def checkout() :
    
    try:
        if session['logged_in']:
                
            user_cred = UserHistory.query.filter_by(name = session['username']).first()
            user_address = user_cred.address
            user_city = user_cred.city
            user_state = user_cred.state
            user_zipcode = user_cred.zipcode

            items = Add_to_cart.query.all()

            if len(items) == 0:
                flash('Add items in the cart' ,'danger')
                return(render_template('shopping_cart.html', cart_count = len(items)))

            else:
                subtotal = 0

                for item in items:
                    subtotal += item.product_price

                name = session["username"].split(' ') 
                email = session["email"] 
                number = session["number"]

                # print(name, email, number)

                total_INR = (subtotal+9)*100*72.59
                print(total_INR)

                return render_template('checkout_page.html', items=items, subtotal = subtotal,total=(subtotal+9), total_INR=total_INR, shipping_total = (subtotal+9+5), name=name, email=email, number=number, user_address = user_address, user_city = user_city,user_state = user_state, user_zipcode = user_zipcode)

    except:
        flash('Please login into your account for further shopping!' ,'danger')
        return redirect(url_for('login'))
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -

key_id = 'rzp_test_UXcC4YP3qme4qP'
secret_key = 'Y8x8Ku7y2sCO33TFiirK1AxI'

razorpay_client = razorpay.Client(auth=(key_id,secret_key))

@app.route('/success',  methods=['GET', 'POST'])
def success():

    user_cred = UserHistory.query.filter_by(name = session['username']).first()
    
    user_order = []

    # getting estimated delivery date
    est_date = Get_Delivery_date().get_Delivery_date()
    
    name = session["username"]

    subtotal = 0
    
    items = Add_to_cart.query.all()

    for item in items:
        user_order.append([f"{item.product_title}, {item.product_price}, {est_date}, {item.product_image}"])
        subtotal += item.product_price

    #print(user_order)
    for i in user_order:
        user_history = UserHistory(session['username'], user_cred.address, user_cred.city, user_cred.state, user_cred.zipcode, i[0])
        db.session.add(user_history)
        db.session.commit()

    amount = (subtotal + 9 ) * 100 * 72.59

    try:
        payment_id = request.form['razorpay_payment_id']
        razorpay_client.payment.capture(payment_id, amount)
        
        msg = Message(f'Order Confirmation for {name}',
        sender='vidhisejpal1@gmail.com',
        recipients=[session["email"] ])
        
        msg.html = render_template('order_details_mailing.html', name = name, items = items, total = (subtotal + 9 ), address = user_cred.address,city = user_cred.city,zip = user_cred.zipcode,state = user_cred.state,est_date = est_date)

        mail.send(msg)
        
        # remove all items for cart once payment is done
        db.session.query(Add_to_cart).delete()
        db.session.commit()
            
        return(render_template('thankyou.html', name=name, email=session['email']))
 
    except:
        return(redirect(url_for('error_page')))
   

@app.route('/Thank-You')
def thankyou():
    return(render_template('thankyou.html'))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.route('/Unexpected')
def error_page():
    return(render_template('error.html'))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.route('/my_orders')
def my_orders():
    items = Add_to_cart.query.all()
    cart_count = len(items)

    order_history = UserHistory.query.filter_by(name=session["username"]).all()
    
    orders = []

    for i in order_history:
        if i.orders.split(', ')[0] == '0':
            continue
        else:
            orders.append(i.orders.split(', '))

    #print(orders)
        
    return render_template('my_orders.html' ,cart_count = cart_count,orders=orders[::-1])

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -


# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.route('/my_acc')
def my_acc():
    items = Add_to_cart.query.all()
    cart_count = len(items)

    current_user = User.query.filter_by(email=session["email"]).first()
    name = current_user.name.split(' ')
    email = current_user.email
    number = current_user.number

    try:
        current_user_contact = UserHistory.query.filter_by(name=session["username"]).first()
        
        address = current_user_contact.address
        city = current_user_contact.city
        state = current_user_contact.state
        zipcode = current_user_contact.zipcode
        print(address,city,state,zipcode)

        return render_template('my_acc.html',cart_count = cart_count,name = name,email = email,number = number,address = address,city = city,state = state,zipcode = zipcode)

    except:
        print('First time user')
        return render_template('my_acc.html',cart_count = cart_count,name = name,email = email,number = number)

        
    #return render_template('my_acc.html',cart_count = cart_count,name = name,email = email,number = number,address = address,city = city,state = state,zipcode = zipcode)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.route('/updated_profile' , methods = ['GET','POST'])
def update_profile():

    current_user = User.query.filter_by(email=session["email"]).first()
    current_user_contact = UserHistory.query.filter_by(name=session["username"]).all()

    if request.method == 'POST':
        new_number = request.form['new_number']
        new_address = request.form['new_address']
        new_city = request.form['new_city']
        new_state = request.form['new_state']
        new_zip = request.form['new_zip']
        
        if new_number == '':
            new_number = current_user.number

        try:
            if len(new_number) > 1:
                current_user.number = new_number
                session['number'] = new_number

            for i in current_user_contact:
                
                if new_address == '':
                    pass
                else:
                    i.address = new_address

                if new_city == '':
                    pass
                else:
                    i.city = new_city

                if new_state == '':
                    pass
                else:
                    i.state = new_state

                if new_zip == '':
                    pass
                else:
                    i.zipcode = new_zip
            
            db.session.add([current_user, current_user_contact])
            db.session.commit()

        except:
            print('ERROR ERROR !!!')
            current_user_contact = UserHistory(session["username"], new_address, new_city, new_state, new_zip, 0)

            db.session.add(current_user_contact)
            db.session.commit()


    flash('Your account has been updated','success')
    return(redirect(url_for('my_acc')))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.route('/3d_dresses/dress_1')
def dress_1_3d():
    return(render_template('3d_dress_1.html'))

@app.route('/3d_dresses/dress_2')
def dress_2_3d():
    return(render_template('3d_dress_2.html'))


@app.route('/3d_dresses/dress_3')
def dress_3_3d():
    return(render_template('3d_dress_3.html'))

@app.route('/3d_dresses/dress_4')
def dress_4_3d():
    return(render_template('3d_dress_4.html'))

@app.route('/3d_dresses/dress_5')
def dress_5_3d():
    return(render_template('3d_dress_5.html'))


if __name__ == "__main__" :

    #create the database file
    #db.create_all()

    app.run(debug = True)