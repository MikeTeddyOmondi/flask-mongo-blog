from flask import Flask, render_template, request, redirect
from flask_mongoengine import MongoEngine
from flask_security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required
from flask_security.utils import hash_password

# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'SECRET_KEY_HERE'
app.config['SECURITY_PASSWORD_SALT'] = 'SECRET_SALT_KEY'

# MongoDB Config
app.config['MONGODB_DB'] = 'basic_blog'
app.config['MONGODB_HOST'] = 'localhost'
app.config['MONGODB_PORT'] = 27017

# Create database connection object
db = MongoEngine(app)

# Database Models
class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)

class User(db.Document, UserMixin):
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField(Role), default=[])

class Post(db.Document):
    title = db.StringField(max_length=255)
    author = db.StringField(max_length=30)
    content = db.StringField()

class Archive(db.Document):
    title = db.StringField(max_length=255)
    author = db.StringField(max_length=30)
    content = db.StringField()

# Setup Flask-Security
user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Routes
@app.route("/signin", methods=['GET', 'POST'])
def login():
    return render_template("security/login.html")

@app.route("/signup", methods=['GET', 'POST'])
def register():
    #user_datastore.create_user(email='matt@nobien.net', password='password')

    if request.method == 'POST':
        email = request.form['email']
        password = hash_password(request.form['password'])
        user_datastore.create_user(email=email, password=password)
        return redirect('/login')
    else:
        return render_template("security/register.html")

@app.route("/password-reset", methods=['GET', 'POST'])
def reset():
    return render_template("register.html")

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/posts", methods=['GET'])
@login_required
def all():
    all_posts = Post.objects.all()
    return render_template("posts.html", posts=all_posts)

@app.route("/posts/<string:id>", methods=['GET'])
@login_required
def single(id):
    post = Post.objects.get(id=id)

    if request.method == 'PUT':
        post.title = request.form['title']
        post.content = request.form['content']
        return redirect("/posts")
    else:        
        return render_template("single-post.html", post=post)

@app.route("/add-post", methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']

        new_post = Post.objects.create(title=post_title, content=post_content)
        return redirect("/posts")
    else: 
        return render_template("create-post.html")  

@app.route("/edit/<string:id>", methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.objects.get(id=id)

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        Post.save(post)
        return redirect("/posts")
    else:        
        return render_template("edit-post.html", post=post)

@app.route("/delete/<string:id>")
@login_required
def delete(id):
    post = Post.objects.get(id=id)
    archive = Archive.objects.create(title=post.title, content=post.content)
    post.delete()
    return redirect("/posts")      

@app.route("/about")
@login_required
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="8888")
