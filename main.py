from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000))
    body = db.Column(db.String(5000))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/')
def index():
    all_blogs = Blog.query.all()
    return render_template('blog.html', title="Build a Blog!", body=all_blogs)

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

    
@app.route('/newpost', methods=['POST', 'GET'])
def add_new_post():
    if request.method == 'GET':
        return render_template('new_post.html', title="New Blog Post")

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        new_blog_post = Blog(blog_title, blog_body)

        title_error = ''
        body_error = ''

        if len(blog_title) == 0:
            title_error = "Please enter a title for your blog post."
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

if __name__ == '__main__':
    app.run()