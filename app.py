
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import requests
from newsapi import NewsApiClient
from key import my_api_key
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from newspaper import Article
from urllib.parse import unquote
my_api_key =
newsapi = NewsApiClient(api_key=my_api_key )


app = Flask(__name__)
app.config['SECRET_KEY'] = 'freshNewsPass202394!!!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fresh_NEWS.db'
db = SQLAlchemy(app)

class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), primary_key=False)
    text = db.Column(db.Text, nullable=False)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route("/index")
@app.route("/")
def index():
    data = newsapi.get_everything(q='Новости', language='ru', page_size=20)
    articles = data['articles']
    posts = Post.query.all()
    return render_template("index.html", articles=articles, posts=posts)

@app.route("/create", methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        title =request.form['title']
        text = request.form['text']
        post = Post(title=title, text=text)

        try:
            db.session.add(post)
            db.session.commit()
            return redirect("/")
        except:
            return "При добавлении статьи произошла ошибка"

    else:
        return render_template("create.html")

@app.context_processor
def base():
    form = SearchForm()
    return dict(form = form)

@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    articles = []
    posts = []
    searched = ""
    if form.validate_on_submit():
        searched = form.searched.data

        posts = Post.query.filter(Post.title.contains(searched)).all()
        data = newsapi.get_everything(q=searched, language='ru', page_size=10)
        articles = data['articles']


    return render_template("search.html", form=form, searched=searched, articles=articles, posts=posts)

@app.route("/post_page/<int:id>")
def post_page(id):
    post = Post.query.get_or_404(id)
    return render_template("post_page.html", post=post)


@app.route("/article_page")
def article_page():
    raw_url = request.args.get("url")
    if not raw_url:
        return "Ошибка URL", 400

    decoded_url = unquote(raw_url)

    try:
        article = Article(decoded_url, language='ru')
        article.download()
        article.parse()
    except Exception as e:
        return f"Не удалось получить статью: {e}"

    published_date = (
        article.publish_date.strftime('%Y-%m-%d')
        if article.publish_date else "Дата неизвестна"
    )

    return render_template("article_page.html", article=article, published_date=published_date)

def extract_full_text(url):
    try:
        article = Article(url, language='ru')
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        return f"Не удалось получить статью: {e}"

if __name__ == '__main__':
    app.run(debug=True)

