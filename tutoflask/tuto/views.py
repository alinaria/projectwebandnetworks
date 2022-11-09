from .app import app,db
from flask import render_template,url_for, redirect, request
from .models import get_book_detail, get_sample, get_author, Author, User, Book, get_user_detail,getnbpages
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed,FileField
from wtforms import StringField, HiddenField, validators, PasswordField, FloatField,URLField,SelectField
from hashlib import sha256 
from flask_login import login_user, current_user, logout_user, login_required
import os
import uuid

###Definition de la page d'accueil et du book des pages de livres
@app.route("/")
def home():
    """ page d'accueil page 1 des livres"""
    numpagecourante=1
    return render_template( "booksbs.html", title="My books",books=get_sample (numpagecourante),nbpages=getnbpages(),numpagecourante=numpagecourante,chemin='home2')

@app.route("/<numpagecourante>")
def home2(numpagecourante):
    """ page d'accueil page numpagecourante des livres"""     
    numpagecourante=int(numpagecourante)
    return render_template( "booksbs.html", title="My books",books=get_sample (numpagecourante),nbpages=getnbpages(),numpagecourante=numpagecourante,chemin='home2')
    

###Gestion des auteurs
class AuthorForm(FlaskForm):
    """ formulaire pour ajouter un auteur"""
    id = HiddenField('id')
    name = StringField('Nom',
            [validators.InputRequired(),
            validators.length(min=2,max=25,
            message="Le nom doit avoir entre 2 et 25 caractères!"),
            validators.Regexp('^[a-zA-Z \.\-]+$',message = "Le nom doit contenir seuleument des lettres, espaces ou tirets et points"),]) 

@app.route("/author/")
def gestion_author():
    """ Récupère la liste des auteurs dans l'ordre alphabétique"""
    authors=Author.query.order_by(Author.name).all()
    return render_template( "author.html",authors=authors)

@app.route("/author/<int:id>")
def one_author(id):
    """ Récupère la liste des livres d'un auteur"""
    auteur=get_author(id)
    return render_template( "book.html", title="Livre de "+auteur.name,books=auteur.books)

@app.route("/edit/author/")
@app.route("/edit/author/<int:id>")
@login_required
def edit_author(id=None):
    """ Ajoute ou modifie un auteur"""
    if id is not None : #modification auteur existant
        a=get_author(id)
        nom=a.name
    else :#saisie nouvel auteur
        a=None
        nom=None 
    f=AuthorForm(id=id,name=nom)
    return render_template( "edit_author.html",author=a,form=f)

@app.route("/save/author/", methods =("POST" ,))
@login_required
def save_author ():
    """ Enregistre un auteur"""
    f = AuthorForm()
    # Si en update, on a un id
    if f.id.data!="":
        id = int(f.id.data)
        a = get_author(id)
    else : #Création d'un nouvel auteur
        a = Author(name=f.name.data)
        db.session.add(a)
    if f. validate_on_submit ():
        a.name = f.name.data
        db.session.commit()
        return redirect(url_for('one_author', id=a.id))
    a = get_author (int(f.id.data ))
    return render_template ("edit_author.html",author=a, form=f)

@app.route("/delete/author/<int:id>")
@login_required
def delete_author(id):
    """ Supprime un auteur"""
    a=get_author(id)
    for b in a.books:
        db.session.delete(b)
    db.session.delete(a)
    db.session.commit()
    return redirect(url_for('gestion_author'))


###Gestion connexion
class LoginForm (FlaskForm ):
    """ Formulaire de connexion"""
    username = StringField ('Username')
    password = PasswordField ('Password')
    def get_authenticated_user (self ):
        """ Renvoie l'utilisateur authentifié ou None"""
        user = User.query.get(self.username.data)
        if user is None:
            return None
        m = sha256()
        m.update(self.password.data.encode())
        passwd = m.hexdigest()
        return user if passwd == user.password else None
    
@app.route("/login/", methods =("GET","POST" ,))
def login():
    """ Page de connexion"""
    f = LoginForm()
    if f.validate_on_submit():
        user = f.get_authenticated_user()
        if user:
            login_user(user)
            return redirect(url_for("home"))
    return render_template ("login.html",form=f)


@app.route("/logout/")
def logout ():
    """ Déconnexion"""
    logout_user ()
    return redirect(url_for('home'))


###Gestion des livres
class BookForm(FlaskForm):
    """ formulaire pour ajouter un livre"""
    id = HiddenField('id')
    title = StringField('Titre',
            [validators.InputRequired(),
            validators.length(min=2,max=100,
            message="Le titre doit avoir entre 2 et 100 caractères!"), 
            #validators.Regexp('^[a-zA-Z0-9 \(\)\.\-]+$',message = "Le titre doit contenir seuleument des lettres, chiffres, espaces,parenthèses, accents ou tirets et points"),
            ])
    price = FloatField( "Prix", [validators.InputRequired()])
    url = URLField('URL',   [validators.InputRequired(),validators.URL()])
    img = FileField('Image',    [FileAllowed(['jpg','png','jpeg'], 'Images only!')])
    author_id = SelectField('Author', coerce=int)

@app.route("/detail/<id>")
def detail(id):
    """ Affiche le détail d'un livre"""
    book=get_book_detail(int(id))
    return render_template( "detail.html",book=book)

@app.route("/edit/book/")
@app.route("/edit/book/<int:id>")
@login_required
def edit_book(id=None):
    """ Ajoute ou modifie un livre"""
    if id is not None : #modification livre existant
        b=get_book_detail(id)
        titre=b.title
        prix=b.price
        url=b.url
        img=b.img
        auteur=b.author_id
    else : #saisie nouveau livre
        b=None
        titre=None
        prix=None
        url=None
        img=None
        auteur=None
    f=BookForm(id=id,title=titre,price=prix,url=url,img=img,author_id=auteur)
    f.author_id.choices = [(a.id, a.name) for a in Author.query.all()]
    return render_template( "edit_book.html",book=b,form=f)


@app.route("/save/book/", methods =("POST" ,))
@login_required
def save_book():
    """ Enregistre un livre"""
    f = BookForm()
    f.author_id.choices = [(a.id, a.name) for a in Author.query.all()]
    # Si en update, on a un id
    if f.id.data!="":
        id = int(f.id.data)
        b = get_book_detail(id)
    else :
        b = Book(title=f.title.data,price=f.price.data,url=f.url.data,img=f.img.data,author_id=f.author_id.data)
        db.session.add(b)
    if f. validate_on_submit ():
        b.title = f.title.data
        b.price = f.price.data
        b.url = f.url.data
        b.author_id = f.author_id.data        
        #il n'y a pas d'image dans le formulaire et qu'il n'y a pas d'image dans la base
        if not f.img.data=="" and b.img is None:
            print("il n'y a pas d'image dans le formulaire")
            b.img = "no_image.png"
        #il y a une image dans le formulaire et une image dans la base de données qui n'est pas no_image.png pour le livre en cours de modification
        if f.img.data and b.img!="no_image.png":
            print('il y a une image dans le formulaire et une image dans la base de données qui n est pas no_image.png pour le livre en cours de modification')
            try :
                os.remove(os.path.join(app.static_folder +'/images/', b.img))
            except:
                pass
            #si image est deja utilisée par un autre livre
            if os.path.exists(os.path.join(app.static_folder +'/images/', f.img.data.filename)):
                #on la renomme 
                f.img.data.filename = str(uuid.uuid4()) + f.img.data.filename
            b.img = f.img.data.filename
            f.img.data.save(os.path.join(app.static_folder +'/images/', f.img.data.filename))
        #il y a une image dans le formulaire et une image dans la base de données qui est no_image.png pour le livre en cours de modification
        if f.img.data and b.img=="no_image.png":
            print(  'il y a une image dans le formulaire et une image dans la base de données qui est no_image.png pour le livre en cours de modification')
            #si image est deja utilisée par un autre livre
            if os.path.exists(os.path.join(app.static_folder +'/images/', f.img.data.filename)):
                #on la renomme 
                f.img.data.filename = str(uuid.uuid4()) + f.img.data.filename
            b.img = f.img.data.filename
            f.img.data.save(os.path.join(app.static_folder +'/images/', f.img.data.filename))
        #il n'y a pas d'image dans le formulaire et une image dans la base de données qui n'est pas no_image.png pour le livre en cours de modification
        if not f.img.data and b.img!="no_image.png":
            print('il n y a pas d image dans le formulaire et une image dans la base de données qui n est pas no_image.png pour le livre en cours de modification')
            pass
        #il n'y a pas d'image dans le formulaire et une image dans la base de données qui est no_image.png pour le livre en cours de modification
        if not f.img.data and b.img=="no_image.png":
            print('il n y a pas d image dans le formulaire et une image dans la base de données qui est no_image.png pour le livre en cours de modification')
            pass
        db.session.commit()
        return redirect(url_for('detail', id=b.id))
    else :  
        return render_template ("edit_book.html",book=b, form=f)


@app.route("/delete/book/<int:id>")
@login_required
def delete_book(id):
    """ Supprime un livre"""
    b=get_book_detail(id)
    if b.img != 'no_image.png': #si l'image n'est pas no_image.png
        try :
            os.remove(os.path.join(app.static_folder +'/images/', b.img))
        except:
            pass
    db.session.delete(b)
    db.session.commit()
    return redirect(url_for('gestion_book'))

### Definition du book de listing des livres
@app.route("/book/")
def gestion_book():
    """ Récupère la liste des livres page 1"""
    numpagecourante=1
    return render_template( "booksbs.html",title="Listes des livres",books=get_sample (numpagecourante),nbpages=getnbpages(),numpagecourante=numpagecourante,chemin='gestion_book2')

@app.route("/book/<numpagecourante>")
def gestion_book2(numpagecourante):
    """ Récupère la liste des livres page numpagecourante"""
    numpagecourante=int(numpagecourante)
    return render_template( "booksbs.html",title="Listes des livres",books=get_sample (numpagecourante),nbpages=getnbpages(),numpagecourante=numpagecourante,chemin='gestion_book2')
    

### Gestion des utilisateurs
class UserForm(FlaskForm):
    """ Formulaire de gestion des utilisateurs"""
    username = StringField('Username',
            [validators.InputRequired(),
            validators.length(min=2,max=255,
            message="Le username doit avoir entre 2 et 255 caractères!"),
            validators.Regexp('^[a-zA-Z\.\-]+$',message = "Le username doit contenir seuleument des lettres ou tirets et points"),]) 
    password = StringField('Password',
            [validators.InputRequired(),
            validators.length(min=2,max=255,
            message="Le password doit avoir entre 2 et 255 caractères!"),
            validators.Regexp('^[a-zA-Z\.\-]+$',message = "Le password doit contenir seuleument des lettres ou tirets et points"),])    


@app.route("/user/")
def gestion_user():
    """ Récupère la liste des utilisateurs"""
    users=User.query.all()
    return render_template( "user.html",users=users)


@app.route("/edit/user/")
@app.route("/edit/user/<username>")
@login_required
def edit_user(username=None):
    """ Ajoute ou modifie un utilisateur"""
    if username is not None : #modification
        u=get_user_detail(username)
        username=u.username
        password=None
    else :  #ajout
        u=None
        username=None
        password=None
    f=UserForm(username=username,password=password)
    return render_template( "edit_user.html",user=u,form=f)

@app.route("/save/user/", methods =("POST" ,))
@login_required
def save_user():
    """ Enregistre un utilisateur"""
    f = UserForm()
    u = get_user_detail(f.username.data)
    # Si en update, on a un id
    if u is None :
        u = User(username=f.username.data,password=f.password.data)
        db.session.add(u)
    if f. validate_on_submit ():
        u.username = f.username.data
        u.password =sha256(f.password.data.encode()).hexdigest()
        db.session.commit()
        return redirect(url_for('gestion_user'))
    u = get_user_detail(f.username.data)
    return render_template ("edit_user.html",user=u, form=f)

@app.route("/delete/user/<username>")
@login_required
def delete_user(username):
    """ Supprime un utilisateur"""
    u=get_user_detail(username)
    db.session.delete(u)
    db.session.commit()
    return redirect(url_for('gestion_user'))
