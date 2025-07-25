from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from werkzeug.utils import secure_filename
import pandas as pd

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"  # Change this in production
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "images").replace("\\", "/")

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def get_id(self):
        return self.username

# Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    interest_score = db.Column(db.Float, nullable=False)
    personality_traits = db.Column(db.String(200), nullable=False)
    image_path = db.Column(db.String(200))

# Order model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(20), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username=user_id).first()

# Global search_products dictionary to avoid undefined variable warnings
search_products = {
    "mobiles": [
        {"name": "Samsung Galaxy", "image": "static/images/samsung.jpg"},
        {"name": "iPhone 15", "image": "static/images/iphone.jpg"},
        {"name": "Google Pixel", "image": "static/images/pixel.jpg"},
        {"name": "OnePlus 12", "image": "static/images/oneplus.jpg"},
        {"name": "Xiaomi 14", "image": "static/images/xiaomi.jpg"},
        {"name": "Oppo Find X", "image": "static/images/oppo.jpg"},
        {"name": "Vivo V30", "image": "static/images/vivo.jpg"}
    ],
    "fashion": [
        {"name": "Levi's Jeans", "image": "static/images/levis.png"},
        {"name": "Zara Dress", "image": "static/images/zara.png"},
        {"name": "H&M Shirt", "image": "static/images/hm.png"},
        {"name": "Adidas Sneakers", "image": "static/images/adidas.png"},
        {"name": "Gucci Bag", "image": "static/images/gucci.png"},
        {"name": "Nike Jacket", "image": "static/images/nike.png"},
        {"name": "Puma T-shirt", "image": "static/images/puma.png"}
    ],
    "electronics": [
        {"name": "Sony TV", "image": "static/images/sony.png"},
        {"name": "LG Monitor", "image": "static/images/lg.png"},
        {"name": "Bose Speaker", "image": "static/images/bose.png"},
        {"name": "JBL Headphones", "image": "static/images/jbl.png"},
        {"name": "Dell Laptop", "image": "static/images/dell.png"},
        {"name": "HP Printer", "image": "static/images/hp.png"},
        {"name": "Canon Camera", "image": "static/images/canon.png"}
    ],
    "books": [
        {"name": "Python Cookbook", "image": "static/images/python.png"},
        {"name": "The Alchemist", "image": "static/images/alchemist.png"},
        {"name": "1984", "image": "static/images/1984.png"},
        {"name": "To Kill a Mockingbird", "image": "static/images/mockingbird.png"},
        {"name": "Sapiens", "image": "static/images/sapiens.png"},
        {"name": "The Hobbit", "image": "static/images/hobbit.png"},
        {"name": "Dune", "image": "static/images/dune.png"}
    ],
    "gadgets": [
        {"name": "Apple Watch", "image": "data:image/jpeg;base64,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"},
        {"name": "Fitbit Charge 5", "image": "https://m.media-amazon.com/images/I/61wn2jfhBkL._AC_UY327_FMwebp_QL65_.jpg"},
        {"name": "GoPro Hero 12", "image": "https://m.media-amazon.com/images/I/613kXwYXRjL._AC_UY327_FMwebp_QL65_.jpg"},
        {"name": "Oculus Quest 2", "image": "https://m.media-amazon.com/images/I/71A+oUI624L._AC_UY327_FMwebp_QL65_.jpg"},
        {"name": "Tile Tracker", "image": "https://m.media-amazon.com/images/I/61fzqBysxaL._AC_UY327_FMwebp_QL65_.jpg"},
        {"name": "Anker Power Bank", "image": "https://m.media-amazon.com/images/I/71Sn62lz-PL._AC_UY327_FMwebp_QL65_.jpg"},
        {"name": "Amazon Echo Dot", "image": "https://m.media-amazon.com/images/I/71IlSs3nCHL._AC_UY327_FMwebp_QL65_.jpg"}
    ],
    "sports": [
        {"name": "Nike Football", "image": "https://m.media-amazon.com/images/I/71De7+aRnuL._AC_UL480_FMwebp_QL65_.jpg"},
        {"name": "Adidas Running Shoes", "image": "https://m.media-amazon.com/images/I/613wTu5YLOL._AC_UL480_FMwebp_QL65_.jpg"},
        {"name": "Wilson Tennis Racket", "image": "https://m.media-amazon.com/images/I/61ATGL+aEyL._AC_UL480_FMwebp_QL65_.jpg"},
        {"name": "Yonex Badminton Set", "image": "https://m.media-amazon.com/images/I/71veBQxpTqL._AC_UL480_FMwebp_QL65_.jpg"},
        {"name": "Spalding Basketball", "image": "https://m.media-amazon.com/images/I/7187crn3osS._AC_UL480_FMwebp_QL65_.jpg"},
        {"name": "Decathlon Skipping Rope", "image": "https://m.media-amazon.com/images/I/71wm42EtoNL._AC_UL480_FMwebp_QL65_.jpg"},
        {"name": "Reebok Gym Gloves", "image": "https://m.media-amazon.com/images/I/71Qa99mgPPL._AC_UL480_FMwebp_QL65_.jpg"}
    ],
    "beauty": [
        {"name": "L'Oréal Paris Foundation", "image": "https://m.media-amazon.com/images/I/615tifniQIL._AC_UL480_FMwebp_QL65_.jpg"},
        {"name": "Maybelline Mascara","image": "https://m.media-amazon.com/images/I/51Qq0Tp6NdL._CR,,,_QL70_SL300_.jpg"},
        {"name": "Nykaa Lipstick", "image":"https://m.media-amazon.com/images/I/614ojM80IgL._AC_UL480_FMwebp_QL65_.jpg"},
        {"name": "Neutrogena Sunscreen", "image": "https://m.media-amazon.com/images/I/81yyTEU3I6L._AC_UL480_FMwebp_QL65_.jpg"},
        {"name": "The Ordinary Serum", "image": "https://m.media-amazon.com/images/I/51w7Xo6Ed7L._AC_UL480_FMwebp_QL65_.jpg"},
        {"name": "Garnier Micellar Water", "image": "https://m.media-amazon.com/images/I/71Pe1fxadeL._AC_UL480_FMwebp_QL65_.jpg"},
        {"name": "Lakme Compact Powder", "image": "https://m.media-amazon.com/images/I/61kzA5lTumL._AC_UL480_FMwebp_QL65_.jpg"}
    ],
    "toys": [
        {"name": "Lego Classic Bricks", "image": "https://m.media-amazon.com/images/I/81hG0AHDATL._AC_UL480_FMwebp_QL65_.jpghttps://m.media-amazon.com/images/I/81hG0AHDATL._AC_UL480_FMwebp_QL65_.jpg"},
        {"name": "Hot Wheels Cars", "image": "https://m.media-amazon.com/images/I/81vzbt7pIcL._AC_UL480_FMwebp_QL65_.jpg"},
        {"name": "Barbie Doll", "image": "https://m.media-amazon.com/images/I/81vzhncrMpL._AC_UL480_FMwebp_QL65_.jpg"},
        {"name": "Nerf Gun", "image": "https://m.media-amazon.com/images/I/813PgKRWmKL._AC_UL480_FMwebp_QL65_.jpg"},
        {"name": "Play-Doh Set", "image":  "https://m.media-amazon.com/images/I/81WAG75PXaL._AC_UL480_FMwebp_QL65_.jpg"},
        {"name": "UNO Cards", "image": "https://m.media-amazon.com/images/I/81EgK3tJ+xL._AC_UL480_FMwebp_QL65_.jpg"},
        {"name": "Remote Control Car", "image": "https://m.media-amazon.com/images/I/81AbyRBeJlL._AC_UL480_FMwebp_QL65_.jpg"}
    ]
}

# Initial data population from CSV and path fix
with app.app_context():
    db.create_all()
    if Product.query.count() == 0:
        df = pd.read_csv("data/products.csv")
        for _, row in df.iterrows():
            product = Product(
                product_name=row["product_name"],
                category=row["category"],
                interest_score=row["interest_score"],
                personality_traits=row["personality_traits"],
                image_path=None
            )
            db.session.add(product)
        db.session.commit()
    # Fix existing image paths to use forward slashes
    for product in Product.query.filter(Product.image_path.isnot(None)).all():
        if product.image_path:
            new_path = product.image_path.replace("\\", "/")
            if product.image_path != new_path:
                product.image_path = new_path
                db.session.commit()
                print(f"Updated image_path for {product.product_name} to: {new_path}")

# Category image data with static paths
image_dir = os.path.join(app.static_folder, "images")
category_icon_sources = {
    "Gadgets": "images/gadgets.png" if os.path.exists(os.path.join(image_dir, 'gadgets.png')) else "images/default.png",
    "Fashion": "images/fashion.png" if os.path.exists(os.path.join(image_dir, 'fashion.png')) else "images/default.png",
    "Electronics": "images/electronics.png" if os.path.exists(os.path.join(image_dir, 'electronics.png')) else "images/default.png",
    "Sports": "images/sports.png" if os.path.exists(os.path.join(image_dir, 'sports.png')) else "images/default.png",
    "Books": "images/books.png" if os.path.exists(os.path.join(image_dir, 'books.png')) else "images/default.png",
    "Beauty": "images/beauty.png" if os.path.exists(os.path.join(image_dir, 'beauty.png')) else "images/default.png",
    "Toys": "images/toys.png" if os.path.exists(os.path.join(image_dir, 'toys.png')) else "images/default.png",
}

category_images = {
    "Gadgets": ["static/images/gadget1.jpg", "images/gadget2.jpg", "images/gadget3.jpg"],
    "Fashion": ["images/fashion1.jpg", "images/fashion2.jpg", "images/fashion3.jpg"],
    "Electronics": ["images/electronics1.jpg", "images/electronics2.jpg", "images/electronics3.jpg"],
    "Jewelry": ["images/jewelry1.jpg", "images/jewelry2.jpg", "images/jewelry3.jpg"],
    "Sports": ["images/sports1.jpg", "images/sports2.jpg", "images/sports3.jpg"],
    "Books": ["images/book1.jpg", "images/book2.jpg", "images/book3.jpg"],
    "Beauty": ["images/beauty1.jpg", "images/beauty2.jpg", "images/beauty3.jpg"],
    "Toys": ["images/toy1.jpg", "images/toy2.jpg", "images/toy3.jpg"],
    "Grocery": ["images/grocery1.jpg", "images/grocery2.jpg", "images/grocery3.jpg"]
}

@app.route("/")
@login_required
def home():
    session.pop('last_category', None)
    session.pop('last_search', None)
    session.pop('last_traits', None)
    return render_template("index.html", recommendations=[], username=current_user.username, category_images=category_images, category_icon_sources=category_icon_sources)

@app.route("/category/<category>")
@login_required
def category_page(category):
    if category in category_images:
        session['last_category'] = category
        return render_template("index.html", recommendations=[], username=current_user.username, selected_category=category, category_images=category_images, category_icon_sources=category_icon_sources)
    return redirect(url_for("home"))

@app.route("/product")
@login_required
def product():
    products_per_page = 10
    page = request.args.get("page", 1, type=int)
    start_idx = (page - 1) * products_per_page
    end_idx = start_idx + products_per_page
    paginated_products = Product.query.all()[start_idx:end_idx]
    total_pages = (Product.query.count() + products_per_page - 1) // products_per_page
    return render_template("index.html", products=paginated_products, page=page, total_pages=total_pages, username=current_user.username, category_icon_sources=category_icon_sources)

@app.route("/recommended")
@login_required
def recommended():
    last_category = session.get('last_category')
    last_search = session.get('last_search')
    last_traits = session.get('last_traits')
    recommendations = []
    if last_search:
        recommendations = Product.query.filter(Product.product_name.ilike(f'%{last_search}%')).order_by(Product.interest_score.desc()).limit(5).all()
    elif last_category:
        recommendations = Product.query.filter_by(category=last_category).order_by(Product.interest_score.desc()).limit(5).all()
    elif last_traits:
        trait_map = {
            "openness": ["home decor", "art supplies"],
            "extraversion": ["bluetooth speaker", "party items"]
        }
        traits = trait_map.get(last_traits.lower(), [])
        recommendations = Product.query.filter(Product.product_name.ilike(f'%{"%|%".join(traits)}%')).order_by(Product.interest_score.desc()).limit(5).all()
    if not recommendations:
        recommendations = Product.query.order_by(Product.interest_score.desc()).limit(5).all()
    return render_template("index.html", recommendations=recommendations, username=current_user.username, category_icon_sources=category_icon_sources)

@app.route("/update_category", methods=["POST"])
@login_required
def update_category():
    category = request.form.get("category")
    if category in category_images:
        session['last_category'] = category
    return redirect(url_for("category_page", category=category))

@app.route("/search", methods=["POST"])
@login_required
def search():
    query = request.form.get("category").strip()
    session['last_search'] = query
    products = []
    for cat, items in search_products.items():
        if query.lower() in cat:
            for item in items[:7]:
                addons = get_addons(item["name"])
                products.append({"name": item["name"], "image": item["image"], "addons": addons})
    return render_template("index.html", search_results=products, username=current_user.username, query=query, category_icon_sources=category_icon_sources, category_images=category_images)

@app.route("/traits", methods=["POST"])
@login_required
def traits():
    trait = request.form.get("trait")
    if trait in ["openness", "extraversion"]:
        session['last_traits'] = trait
    return redirect(url_for("home"))

@app.route("/traits_search", methods=["GET", "POST"])
@login_required
def traits_search():
    traits_data = {}
    recommended_product = None
    if request.method == "POST":
        # Get trait values
        traits_data = {
            "openness": float(request.form.get("openness", 0)),
            "extraversion": float(request.form.get("extraversion", 0)),
            "conscientiousness": float(request.form.get("conscientiousness", 0)),
            "agreeableness": float(request.form.get("agreeableness", 0)),
            "neuroticism": float(request.form.get("neuroticism", 0))
        }
        
        # Simple logic to recommend a product based on dominant trait
        dominant_trait = max(traits_data, key=traits_data.get)
        trait_map = {
            "openness": {"name": "Python Cookbook", "image": "static/images/python.png", "category": "Books"},
            "extraversion": {"name": "Bose Speaker", "image": "static/images/bose.png", "category": "Electronics"},
            "conscientiousness": {"name": "Dell Laptop", "image": "static/images/dell.png", "category": "Electronics"},
            "agreeableness": {"name": "Lego Classic Bricks", "image": "https://m.media-amazon.com/images/I/81Ndb0y0OPL._SL1500_.jpg", "category": "Toys"},
            "neuroticism": {"name": "Neutrogena Sunscreen", "image": "https://m.media-amazon.com/images/I/61j4KjZUt1L._SL1500_.jpg", "category": "Beauty"}
        }
        recommended_product = trait_map.get(dominant_trait, {"name": "Python Cookbook", "image": "static/images/python.png", "category": "Books"})

    return render_template(
        "traits_search.html",
        traits_data=traits_data,
        recommended_product=recommended_product,
        username=current_user.username,
        category_icon_sources=category_icon_sources,
        category_images=category_images,
        search_products=search_products
    )

@app.route("/search_product", methods=["POST"])
@login_required
def search_product():
    product_name = request.form.get("product_name")
    searched_product = None
    
    # Search for the product in search_products
    for category, products in search_products.items():
        for product in products:
            if product["name"] == product_name:
                searched_product = {
                    "name": product["name"],
                    "image": product["image"],
                    "category": category.capitalize(),
                    "addons": get_addons(product["name"])
                }
                break
        if searched_product:
            break
    
    return render_template(
        "traits_search.html",
        searched_product=searched_product,
        username=current_user.username,
        category_icon_sources=category_icon_sources,
        category_images=category_images,
        search_products=search_products
    )

def get_addons(product_name):
    # Dictionary of add-ons for each product
    addons = {
        "Samsung Galaxy": ["Earphones", "Charger", "Case"],
        "iPhone 15": ["AirPods", "Charger", "Case"],
        "Google Pixel": ["Earphones", "Charger", "Case"],
        "OnePlus 12": ["Earphones", "Charger", "Case"],
        "Xiaomi 14": ["Earphones", "Charger", "Case"],
        "Oppo Find X": ["Earphones", "Charger", "Case"],
        "Vivo V30": ["Earphones", "Charger", "Case"],
        "Levi's Jeans": ["Belt", "Shirt", "Hat"],
        "Zara Dress": ["Scarf", "Bag", "Shoes"],
        "H&M Shirt": ["Tie", "Pants", "Jacket"],
        "Adidas Sneakers": ["Socks", "Cap", "Backpack"],
        "Gucci Bag": ["Wallet", "Sunglasses", "Scarf"],
        "Nike Jacket": ["Hat", "Gloves", "Pants"],
        "Puma T-shirt": ["Cap", "Shorts", "Socks"],
        "Sony TV": ["Remote", "Mount", "Cables"],
        "LG Monitor": ["Stand", "Cables", "Keyboard"],
        "Bose Speaker": ["Adapter", "Cover", "Cables"],
        "JBL Headphones": ["Case", "Adapter", "Cable"],
        "Dell Laptop": ["Mouse", "Bag", "Charger"],
        "HP Printer": ["Ink", "Paper", "Cable"],
        "Canon Camera": ["Lens", "Tripod", "Bag"],
        "Python Cookbook": ["Notebook", "Pen", "Bookmark"],
        "The Alchemist": ["Notebook", "Pen", "Bookmark"],
        "1984": ["Notebook", "Pen", "Bookmark"],
        "To Kill a Mockingbird": ["Notebook", "Pen", "Bookmark"],
        "Sapiens": ["Notebook", "Pen", "Bookmark"],
        "The Hobbit": ["Notebook", "Pen", "Bookmark"],
        "Dune": ["Notebook", "Pen", "Bookmark"],
        
        "Lego Classic Bricks": ["Storage Box", "Building Guide", "Extra Bricks"],
    "Hot Wheels Cars": ["Track Set", "Car Wash Kit", "Storage Case"],
    "Barbie Doll": ["Clothing Set", "Furniture", "Accessories Kit"],
    "Nerf Gun": ["Extra Darts", "Target Board", "Vest"],
    "Play-Doh Set": ["Molds", "Cutter Set", "Storage Bag"],
    "UNO Cards": ["Card Holder", "Score Pad", "Card Sleeve"],
    "Remote Control Car": ["Battery Pack", "Remote", "Track"],
    "Nike Football": ["Pump", "Shin Guards", "Bag"],
    "Adidas Running Shoes": ["Laces", "Insoles", "Shoe Cleaner"],
    "Wilson Tennis Racket": ["Grip Tape", "Tennis Balls", "Bag"],
    "Yonex Badminton Set": ["Shuttlecocks", "Gloves", "Net"],
    "Spalding Basketball": ["Pump", "Gloves", "Bag"],
    "Decathlon Skipping Rope": ["Grip Tape", "Counter", "Bag"],
    "Reebok Gym Gloves": ["Hat", "Jacket", "Bag"],
    "L'Oréal Paris Foundation": ["Brush", "Sponge", "Primer"],
    "Maybelline Mascara": ["Remover", "Eyelash Curler", "Primer"],
    "Nykaa Lipstick": ["Lip Liner", "Gloss", "Remover"],
    "Neutrogena Sunscreen": ["Applicator", "Cleanser", "Moisturizer"],
    "The Ordinary Serum": ["Dropper", "Cleanser", "Moisturizer"],
    "Garnier Micellar Water": ["Cotton Pads", "Cleanser", "Moisturizer"],
    "Lakme Compact Powder": ["Puff", "Mirror", "Brush"],
    "Apple Watch": ["Strap", "Charger", "Screen Protector"],
    "Fitbit Charge 5": ["Strap", "Charger", "Screen Protector"],
    "GoPro Hero 12": ["Mount", "Case", "Battery"],
    "Oculus Quest 2": ["Head Strap", "Controller Grip", "Case"],
    "Tile Tracker": ["Keychain", "Adhesive", "Battery"],
    "Anker Power Bank": ["Cable", "Pouch", "Adapter"],
    "Amazon Echo Dot": ["Stand", "Cable", "Smart Plug"]
}
    

    # Dictionary mapping add-on names to verified image URLs
    addon_image_urls = {
        "Earphones": "https://www.boat-lifestyle.com/cdn/shop/products/1orange_ee72a502-2184-42c7-ab95-50f3beaaab8b.png?v=1592544752",
        "Charger": "https://m.media-amazon.com/images/I/51biarCGp4L._AC_UF1000,1000_QL80_.jpg",
        "Case": "https://popitout.in/cdn/shop/files/17_0c4c2e14-3776-457e-9ee2-502ab2fbb514.jpg?v=1714467222",
        "AirPods": "https://iplanet.one/cdn/shop/files/AirPods_Pro_2_PDP_Image_Position_1__en-IN.jpg?v=1727267590",
        "Belt": "https://m.media-amazon.com/images/I/71pTWgK873L._AC_UY1100_.jpg",
        "Shirt": "https://imagescdn.louisphilippe.com/img/app/product/3/39676856-13741100.jpg",
        "Hat": "https://m.media-amazon.com/images/I/71XH3dt7LJL._AC_UY1100_.jpg",
        "Scarf": "https://m.media-amazon.com/images/I/61fjbLrfqTL._AC_UY1100_.jpg",
        "Bag": "https://safaribags.com/cdn/shop/files/2_3d6acc65-50a9-4d45-b83c-31bb315d7b05.jpg",
        "Shoes": "https://rukminim2.flixcart.com/image/850/1250/xif0q/shoe/7/2/m/6-tm-12-6-trm-white-original-imagjqyzz8z9jrgf.jpeg",
        "Tie": "https://www.collinsdictionary.com/images/full/tie_171498722_1000.jpg",
        "Pants": "https://freakins.com/cdn/shop/files/09june2024_6816-Edit.jpg",
        "Jacket": "https://m.media-amazon.com/images/I/71E7c09iTdL._AC_UY1100_.jpg",
        "Socks": "https://www.momshome.in/cdn/shop/products/FP5TO8P3STRIPE1.jpg",
        "Cap": "https://images-cdn.ubuy.co.in/654796080c41125dc934a424-top-level-baseball-cap-men-women.jpg",
        "Backpack": "https://m.media-amazon.com/images/I/71aSI364SxL._AC_UY1100_.jpg",
        "Wallet": "https://m.media-amazon.com/images/I/51bj9L43I1S._SX300_SY300_.jpg",
        "Sunglasses": "https://images.unsplash.com/photo-1572635196237-14b3f281503f",
        "Gloves": "https://m.media-amazon.com/images/I/41rY8qVSTBL._SX300_SY300_QL70_FMwebp_.jpg",
        "Shorts": "https://m.media-amazon.com/images/I/61wGhG-B-pL._AC_SY741_.jpg",
        "Remote": "https://sm.pcmag.com/pcmag_me/review/a/amazon-ale/amazon-alexa-voice-remote-pro_9kbw.jpg",
        "Mount": "https://m.media-amazon.com/images/I/61bGjKfwDvL.jpg",
        "Cables": "https://m.media-amazon.com/images/I/71WXc4iKKXL._AC_UY327_FMwebp_QL65_.jpg",
        "Stand": "https://images.meesho.com/images/products/295450427/b6206_512.webp",
        "Keyboard": "https://m.media-amazon.com/images/I/711hcPp2r8L._AC_SL1500_.jpg",
        "Adapter": "https://m.media-amazon.com/images/I/51sPyZDiRwL._AC_UF1000,1000_QL80_.jpg",
        "Cover": "https://casekaro.com/cdn/shop/files/ZCK-0007-SOFTSILI-OPND25G_7b19d5fc-1ce1-4297-97d3-accd7e85b5df.jpg",
        "Mouse": "https://m.media-amazon.com/images/I/614q24eTLBL.jpg",
        "Ink": "https://m.media-amazon.com/images/I/61SddsasYwL.jpg",
        "Paper": "https://m.media-amazon.com/images/I/61BkQBxaRwL._AC_UF1000,1000_QL80_.jpg",
        "Lens": "https://www.zeiss.co.in/content/dam/vis-b2c/reference-master/images/find-lenses/findlens_smartlife-pal.jpg/_jcr_content/renditions/original./findlens_smartlife-pal.jpg",
        "Tripod": "https://images-cdn.ubuy.co.in/64ca77dbce264705b57d57f1-camera-tripod-72-tripod-for-camera.jpg",
        "Notebook": "https://m.media-amazon.com/images/I/71E181iSlLL.jpg",
        "Pen": "https://m.media-amazon.com/images/I/61oQrwDChAL._AC_UF1000,1000_QL80_.jpg",
        "Bookmark": "https://images.meesho.com/images/products/170261284/hfbtt_400.webp",
        
        
        
        
    "Storage Box": "https://m.media-amazon.com/images/I/71OCVJ0MrAL._AC_UL480_FMwebp_QL65_.jpg",
    "Building Guide": "https://m.media-amazon.com/images/I/71weASvIeCL._AC_UL480_FMwebp_QL65_.jpg",
    "Extra Bricks": "https://m.media-amazon.com/images/I/91UjWKcxb9L._AC_UL480_FMwebp_QL65_.jpg",
    "Track Set": "https://m.media-amazon.com/images/I/718RCZd31UL._AC_UL480_FMwebp_QL65_.jpg",
    "Car Wash Kit": "https://m.media-amazon.com/images/I/71KrSqNT1OL._AC_UL480_FMwebp_QL65_.jpg",
    "Storage Case": "https://m.media-amazon.com/images/I/71loy0S3FQL._AC_UL480_FMwebp_QL65_.jpg",
    "Clothing Set": "https://m.media-amazon.com/images/I/7137+AAWWOL._AC_UL480_FMwebp_QL65_.jpg",
    "Furniture": "https://m.media-amazon.com/images/I/61K+Kw7-LTL._AC_UL480_FMwebp_QL65_.jpg",
    "Accessories Kit": "https://m.media-amazon.com/images/I/615anMYuQmL._AC_UL480_FMwebp_QL65_.jpg",
    "Extra Darts": "https://m.media-amazon.com/images/I/81C+iqqojvL._AC_UL480_FMwebp_QL65_.jpg",
    "Target Board": "https://m.media-amazon.com/images/I/81I7EZAdnZL._AC_UL480_FMwebp_QL65_.jpg",
    "Vest": "https://m.media-amazon.com/images/I/71ohcFlrEHL._AC_UL480_FMwebp_QL65_.jpg",
    "Molds": "https://m.media-amazon.com/images/I/717aNXUrs5L._AC_UL480_FMwebp_QL65_.jpg",
    "Cutter Set": "https://m.media-amazon.com/images/I/71WRS8+G3IL._AC_UL480_FMwebp_QL65_.jpg",
    "Storage Bag": "https://m.media-amazon.com/images/I/71nimMH7uXL._AC_UL480_FMwebp_QL65_.jpg",
    "Card Holder": "https://m.media-amazon.com/images/I/81MXkgtn-AL._AC_UL480_FMwebp_QL65_.jpg",
    "Score Pad": "https://m.media-amazon.com/images/I/71JXJ0I9e-L._AC_UL480_FMwebp_QL65_.jpg",
    "Card Sleeve": "https://m.media-amazon.com/images/I/81pkiwOjW6L._AC_UL480_FMwebp_QL65_.jpg",
    "Battery Pack": "https://m.media-amazon.com/images/I/81+l8eyss7L._AC_UL480_FMwebp_QL65_.jpg",
    "Track": "https://m.media-amazon.com/images/I/71R3bNLu1xL._AC_UL480_FMwebp_QL65_.jpg",
    "Pump": "https://m.media-amazon.com/images/I/71FS4QSI0DL._AC_UL480_FMwebp_QL65_.jpg",
    "Shin Guards": "https://m.media-amazon.com/images/I/71H4YZu0XdL._AC_UL480_FMwebp_QL65_.jpg",
    "Laces": "https://m.media-amazon.com/images/I/71e3Vp-lN1L._AC_UL480_FMwebp_QL65_.jpg",
    "Insoles": "https://m.media-amazon.com/images/I/81mLoXcJ4dL._AC_UL480_FMwebp_QL65_.jpg",
    "Shoe Cleaner": "https://m.media-amazon.com/images/I/71uLthIHviL._AC_UL480_FMwebp_QL65_.jpg",
    "Grip Tape": "https://m.media-amazon.com/images/I/71GDdJlef+L._AC_UY327_FMwebp_QL65_.jpg",
    "Tennis Balls": "https://m.media-amazon.com/images/I/81S5dFqbqNL._AC_UL480_FMwebp_QL65_.jpg",
    "Shuttlecocks": "https://m.media-amazon.com/images/I/816r96pRI-L._AC_UL480_FMwebp_QL65_.jpg",
    "Net": "https://m.media-amazon.com/images/I/81f6xacX-vL._AC_UL480_FMwebp_QL65_.jpg",
    "Hoop": "https://m.media-amazon.com/images/I/81z9z9z9z9L._AC_UL480_FMwebp_QL65_.jpg",
    "Counter": "https://m.media-amazon.com/images/I/61m8KN1TtfL._AC_UL480_FMwebp_QL65_.jpg",
    "Wrist Wrap": "https://m.media-amazon.com/images/I/81z9z9z9z9L._AC_UL480_FMwebp_QL65_.jpg",
    "Towel": "https://m.media-amazon.com/images/I/81z9z9z9z9L._AC_UL480_FMwebp_QL65_.jpg",
    "Brush": "https://m.media-amazon.com/images/I/71AEbODrs9L._AC_UL480_FMwebp_QL65_.jpg",
    "Sponge": "https://m.media-amazon.com/images/I/81FGBRh3elL._AC_UL480_FMwebp_QL65_.jpg",
    "Primer": "https://m.media-amazon.com/images/I/71Qn75c2LiL._AC_UL480_FMwebp_QL65_.jpg",
    "Remover": "https://m.media-amazon.com/images/I/718tZy6VWQL._AC_UL480_FMwebp_QL65_.jpg",
    "Eyelash Curler": "https://m.media-amazon.com/images/I/81sqQ27vaFL._AC_UL480_FMwebp_QL65_.jpg",
    "Lip Liner": "https://m.media-amazon.com/images/I/71QYvufGd6L._AC_UL480_FMwebp_QL65_.jpg",
    "Gloss": "https://m.media-amazon.com/images/I/61F8cLxjlML._AC_UL480_FMwebp_QL65_.jpg",
    "Applicator": "https://m.media-amazon.com/images/I/51HhBKDFBeL._AC_UL480_FMwebp_QL65_.jpg",
    "Cleanser": "https://m.media-amazon.com/images/I/61AOpW073sL._AC_UL480_FMwebp_QL65_.jpg",
    "Moisturizer": "https://m.media-amazon.com/images/I/71G1bwds-SL._AC_UL480_FMwebp_QL65_.jpg",
    "Puff": "https://m.media-amazon.com/images/I/71ZqhkV3VML._AC_UL480_FMwebp_QL65_.jpg",
    "Mirror": "https://m.media-amazon.com/images/I/41G5hbKA0TL._AC_UL480_FMwebp_QL65_.jpg",
    "Strap": "https://m.media-amazon.com/images/I/71xI3pjOVdL._AC_UL480_FMwebp_QL65_.jpg",
    "Screen Protector": "https://m.media-amazon.com/images/I/8137X-qOV2L._AC_UY327_FMwebp_QL65_.jpg",
    "Clip": "https://m.media-amazon.com/images/I/81z9z9z9z9L._AC_UL480_FMwebp_QL65_.jpg",
    "Head Strap": "https://m.media-amazon.com/images/I/71vCzSwtizS._AC_UL480_FMwebp_QL65_.jpg",
    "Controller Grip": "https://m.media-amazon.com/images/I/81yAIGEYq+L._AC_UY327_FMwebp_QL65_.jpg",
    "Keychain": "https://m.media-amazon.com/images/I/619bHP0tkBL._AC_UL480_FMwebp_QL65_.jpg",
    "Adhesive": "https://m.media-amazon.com/images/I/61AfuQo6ibL._AC_UL480_FMwebp_QL65_.jpg",
    "Pouch": "https://m.media-amazon.com/images/I/81nP8PTk0YL._AC_UL480_FMwebp_QL65_.jpg",
    "Smart Plug": "https://m.media-amazon.com/images/I/515sebA4zGL._AC_UL480_FMwebp_QL65_.jpg"

    }
    # Return a list of dictionaries with add-on names and their online image URLs
    return [{
        "name": addon,
        "image": addon_image_urls.get(addon, "https://images.unsplash.com/photo-1493612276216-ee3925520721")
    } for addon in addons.get(product_name, [])]

@app.route("/orders", methods=["GET", "POST"])
@login_required
def orders():
    if request.method == "POST" and request.form.get("add_order"):
        product_id = int(request.form["product_id"])
        product = Product.query.get_or_404(product_id)
        order = Order(user_id=current_user.id, product_id=product_id, status="Processing", date="2025-04-15")
        db.session.add(order)
        db.session.commit()
        flash("Order added!", "success")
        return redirect(url_for("orders"))
    user_orders = Order.query.filter_by(user_id=current_user.id).all()
    products = Product.query.all()
    return render_template("index.html", orders=user_orders, products=products, username=current_user.username, category_icon_sources=category_icon_sources, category_images=category_images)

@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    recommendations = []
    if request.method == "POST":
        traits = request.form.get("traits", "").lower().split(",")
        traits = [t.strip() for t in traits if t.strip()]
        if traits:
            products = Product.query.all()
            for product in products:
                match_score = sum(t in product.personality_traits.lower() for t in traits) / len(traits) if traits else 0
                product.match_score = match_score
            recommendations = sorted(products, key=lambda x: (x.interest_score, getattr(x, "match_score", 0)), reverse=True)[:3]
    return render_template("index.html", recommendations=recommendations, username=current_user.username, category_icon_sources=category_icon_sources, category_images=category_images)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("home"))
        flash("Invalid credentials!", "error")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "error")
            return redirect(url_for("signup"))
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Signup successful! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return render_template("logout.html")

if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

if __name__ == "__main__":
    app.run(debug=True)