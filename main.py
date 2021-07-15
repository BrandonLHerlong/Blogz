from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = ''



class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000))
    body = db.Column(db.String(5000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup' ]
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users = users)
# def index():
#     all_blogs = Blog.query.all()
#     return render_template('blog.html', title="Build a Blog!", body=all_blogs)

@app.route('/blog', methods=['POST', 'GET'])
def view_blog():
    
    blog_id = request.args.get('id')
    if (blog_id):
        individual_post = Blog.query.get(blog_id)
        return render_template('individual_post.html', 
        individual_post=individual_post)

    else:
        all_blogs = Blog.query.all()
        return render_template('blog.html', body=all_blogs)

def home():
    blogs = Blog.query.all()
    welcome = "Not logged in"
    if 'user' in session:
        welcome = "Logged in as: " + session['user']

    return render_template('home.html', title= "A Dumb Blog by Jim Vargas", 
        blogs= blogs, welcome= welcome)


    
@app.route('/newpost', methods=['POST', 'GET'])
def add_new_post():

    title_error = ''
    body_error = ''

    if request.method == 'GET':
        return render_template('new_post.html', title="New Blog Post")

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        new_blog_post = Blog(blog_title, blog_body, owner)

        
        if len(blog_title) <= 4:
            title_error = "Blog title must be 5 or more characters."
        if len(blog_body) <= 10:
            body_error = "Your blog needs content!"

        if not title_error and not body_error:
            db.session.add(new_blog_post)
            db.session.commit()
            return redirect('/blog?id={}'.format(new_blog_post.id))
        
        else:
            all_blogs = Blog.query.all()
            return render_template('new_post.html', title="Build a Blog!", body=all_blogs,
                blog_title=blog_title, title_error=title_error, 
                blog_body=blog_body, body_error=body_error)


@app.route('/login', methods=['POST', 'GET'])
def login():
    username = ""
    username_error = ""
    password_error = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username = username).first()

        if not user:
            username_error = "User does not exist."
            if username == "":
                username_error = "Please enter your username."

        if password == "":
            password_error = "Please enter your password."

        if user and user.password != password:
            password_error = "That is the wrong password."

        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')

    return render_template('login.html', username = username, username_error = username_error, password_error = password_error)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username = ""
    username_error = ""
    password_error = ""
    verify_error = ""

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username = username).first()

        if len(username) < 3:
            username_error = "Usernames must be longer than 3 characters."
            

        if password != verify:
            password_error = "Passwords must match."
            verify_error = "Passwords must match."
            
        if len(password) < 3:
            password_error = "Password must be longer than 3 characters."
            


        if not username_error and not password_error and not verify_error:
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                username_error = "Username already registered."

    return render_template('signup.html', username = username, username_error = username_error, password_error = password_error, verify_error = verify_error)


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')    


if __name__ == '__main__':
    app.run()
