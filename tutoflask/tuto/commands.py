import click
from .app import app, db
from .models import Author, Book, load_user
import yaml
from .models import User
from hashlib import sha256

@app.cli.command()
def syncdb():
    """crée les tables correspondant aux classes définies dans models.py"""
    db.create_all()

@app.cli.command()          #ajout nouvelle commandes à flask
@click.argument('filename')
def loaddb(filename):
    '''Creates the tables and populates them with data.'''
    # création de toutes les tables
    db.create_all()
    # chargement de notre jeu de données
    import yaml
    books = yaml.load(open(filename),Loader=yaml.FullLoader)
    
    # import des modèles
    from .models import Author,Book
    # première passe: création de tous les auteurs
    authors = {}
    for b in books:
        nom = b["author"]
        if nom not in authors:
            o = Author(name=nom)
            #on ajoute l'objet o à la session (en mémoire):
            db.session.add(o)
            authors[nom] = o
    #on dit à la DB d'intégrer toutes les nouvelles données:
    db.session.commit ()
    
    # deuxième passe: création de tous les livres
    for b in books:
        # on récupère l'auteur du livre
        #courant dans le dico authors
        a = authors[b["author"]]
        o = Book(price = b["price"],
            title = b["title"],
            url = b["url"],
            img = b["img"],
            author_id = a.id)
        db.session.add(o)
    db.session.commit ()
    
    

@app.cli.command()    
@click.argument('username')
@click.argument('password')
def newuser(username, password):
        '''Add a new user to the database.'''
        m = sha256()
        m.update(password.encode())
        u = User(username=username , password=m.hexdigest())
        db.session.add(u)
        db.session.commit ()
        
@app.cli.command()
@click.argument('username')
@click.argument('password')
def passwd(username, password):
        '''Change a user password'''
        m = sha256()
        m.update(password.encode())
        u = load_user(username)
        u.password = m.hexdigest()
        db.session.commit()
