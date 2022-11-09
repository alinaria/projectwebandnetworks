from .app import db
from flask_login import UserMixin

class Author(db.Model):
    """class author avec id et name"""
    id = db.Column(db.Integer, primary_key=True) #primary_key=True means that this column is the primary key of the table. 
    # a primary key is a column (or a group of columns) that uniquely identifies each row in a table.
    name = db.Column(db.String(100))

    def __repr__(self):
        """methode affichage sous forme chaine de caractères"""
        return "<Author (%d)%s>" % (self.id,self.name)   
    #%d faire int et %s faire str
    
    
class Book(db.Model):
    """class book avec id, price, title, url, img, author_id"""
    id=db.Column(db.Integer, primary_key=True)
    price=db.Column(db.Float)
    title=db.Column(db.String(120))
    url=db.Column(db.String(256))
    img=db.Column(db.String(256))
    author_id=db.Column(db.Integer, db.ForeignKey('author.id'))
    author=db.relationship('Author', backref=db.backref('books', lazy='dynamic'))
    
    def __repr__(self ):
        return "<Book (%d) %s>" % (self.id, self.title)

class User(db.Model, UserMixin):
    """ class user avec id, username, password"""
    username = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(64))

    def get_id(self):
        return self.username

def getnbpages():
    """retourne le nombre de pages"""
    #recupere le nombre de livres
    nb_books=Book.query.count()
    nb_pages = nb_books // 18 + (1 if nb_books % 18 else 0)
    return nb_pages

def get_sample(numpagecourante):
    """retourne les livres de la page numpagecourante"""
    return Book.query.order_by(Book.id).limit(18).offset((numpagecourante-1)*18).all()
    #return Book.query.limit(18).all()

def get_book_detail(id):
    """ retourne le livre dont l'id est id"""
    return Book.query.get(id)

def get_author(id):
    """ retourne l'auteur dont l'id est id"""
    return Author.query.get_or_404(id)

def get_user_detail(username):
    """ retourne l'utilisateur dont le username est username"""
    return User.query.get(username)

from .app import login_manager
@login_manager.user_loader
def load_user(username):
    """ charge l'utilisateur dont le username est username"""
    return User.query.get(username)

