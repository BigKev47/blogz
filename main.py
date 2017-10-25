from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'savdaser5yLLCoolJ'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, slug, body, owner):
        self.slug = slug
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60))
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username 
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup','blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    del session['username']
    return redirect('/')

@app.route('/new_post', methods=['POST', 'GET'])
def new_post():
    owner = User.query.filter_by(username=session['username']).first()
    return render_template('newpost.html', title="New Blog Post")
    
@app.route('/redirect', methods=['GET','POST'])
def new_post_redirect():
    if request.method == 'POST':
        blog_slug = request.form['slug']
        blog_body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        if blog_slug == "":
            return render_template('newpost.html', title='New Blog Post', error1 = "Give your post a title!")
        if blog_body == "":
            return render_template('newpost.html', title='New Blog Post', error2 = "This isn't twitter, write something!")
        new_blog = Blog(blog_slug, blog_body, owner)
        db.session.add(new_blog)
        db.session.commit()
    id = Blog.query.order_by(Blog.id.desc()).first().id
    
    return redirect("/blog?id="+str(id))

@app.route('/blog', methods = ['POST','GET'])
def blog():
    if request.args.get('id') != None:
        id = request.args.get('id')
        entry = Blog.query.filter(Blog.id==id).one()
        return render_template('blog-post.html', entry = entry)
    elif request.args.get('user') != None:
        user = request.args.get('user')
        blogs = Blog.query.filter(Blog.owner_id==user).all()
        return render_template('blog.html', blogs=blogs)
    else:
        blogs = Blog.query.all()
        return render_template('blog.html',title="My Blog", 
            blogs = blogs)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        error = ""
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username 
            return redirect('/')
        elif user:
            return render_template('login.html',error2 = "Incorrect password")
        else:
            return render_template('login.html',error1 = 'User does not exist')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first() 
        if not existing_user:
            if [is_valid(username),is_valid(password),password_match(password,verify)] == ["","",""]:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return render_template('newpost.html')
        else:
            if existing_user:
                return render_template('signup.html', error1 = "User already registered.")
        return render_template('signup.html', error1 = is_valid(username), error2 = is_valid(password), error3 = password_match(password,verify))

    return render_template('signup.html')

def is_valid(response):
    if response != "":
        if " " not in response:
            if 2<len(response):
                return ""
            return "Field must be at least 3 characters."
        return "Field cannot contain spaces."
    else:
        return "No input"

def password_match(first_PW,conf):
    if first_PW == conf:
        return ""
    else:
        return "Passwords do not match."

@app.route('/', methods=['GET', 'POST'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run()
