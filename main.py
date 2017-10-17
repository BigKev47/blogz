
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

    def __init__(self, name, body, owner):
        self.slug = name
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
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/new_post', methods=['POST', 'GET'])
def new_post(owner): 
    return render_template('newpost.html', owner = owner, title="New Blog Post")
    
@app.route('/redirect', methods=['GET','POST'])
def new_post_redirect(owner):
    if request.method == 'POST':
        blog_slug = request.form['slug']
        blog_body = request.form['body']
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
def index():
    if request.args.get('id') != None:
        id = request.args.get('id')
        entry = Blog.query.filter(Blog.id==id).one()
        return render_template('blog-post.html', entry = entry)
    else:
        blogs = Blog.query.all()
        return render_template('blog.html',title="My Blog", 
            blogs = blogs)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['owner'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            return "<h1>That username is already taken.</h1>"

    return render_template('signup.html')

@app.route('/', methods=['GET'])
def get_start():
    return redirect('/blog')

if __name__ == '__main__':
    app.run()
