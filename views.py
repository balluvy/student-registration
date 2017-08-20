"""
Routes and views for the flask application.
"""
from forms import VoteForm
import config
import pydocumentdb.document_client as document_client

from datetime import datetime
from flask import render_template,request,session, redirect, url_for
from FKWebProject2 import app
import pydocumentdb.errors as errors


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    """Renders the home page."""
    if request.method == 'POST':
         config.DOCUMENTDB_NAMEMAIN = request.form.get('name')
         config.DOCUMENTDB_PASSMAIN = request.form.get('passw')
    return render_template(
        'index.html',
        title='Login Page',
        year=datetime.now().year,
        message='' 
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='My Profile.'
    )


@app.route('/create', methods=['GET', 'POST'])
def create():
    if(config.DOCUMENTDB_NAME != "" or config.DOCUMENTDB_FACULTY != "" or config.DOCUMENTDB_PHONE != "" or config.DOCUMENTDB_PASSWORD != ""): 
        client = document_client.DocumentClient(config.DOCUMENTDB_HOST, {'masterKey': config.DOCUMENTDB_KEY})
        try:
            num = 0
            user = ''
            db = next((data for data in client.ReadDatabases() if data['id'] == config.DOCUMENTDB_DATABASE))
            for data in client.ReadDatabases():
                tmp = data['id']
                num +=  1
                user = user+','+tmp
        

            db_id = config.DOCUMENTDB_DATABASE
            coll_id = config.DOCUMENTDB_COLLECTION


            #Check database and collection exist
            database_link = 'dbs/' + db_id
            database = client.ReadDatabase(database_link)
            
        
            collection_link = database_link + '/colls/{0}'.format(coll_id)
            collection = client.ReadCollection(collection_link)
          
        
            #find userNumber in database
            db_query = "select * from r where r.id = '{0}'".format(db_id)
            db = list(client.QueryDatabases(db_query))[0]
            db_link = db['_self']

            coll_query = "select * from r where r.id = '{0}'".format(coll_id)
            coll = list(client.QueryCollections(db_link, coll_query))[0]
            coll_link = coll['_self']

            docs = client.ReadDocuments(coll_link)
            lst = list(docs)
            longest = len(lst)
            if(longest == 0):
                num = 1
            else:
                lt = lst[longest-1]
                num = int(lt['id'])
                num += 1
            userNumber = str(num)

            # Create document
            document = client.CreateDocument(collection['_self'],
            { 'id': userNumber,
            'Faculty': config.DOCUMENTDB_FACULTY,
            'Password':config.DOCUMENTDB_PASSWORD,
            'Phone': config.DOCUMENTDB_PHONE,
            'username': config.DOCUMENTDB_NAME,
            'Subject' : 0
            })


        except errors.DocumentDBError as e:
            if e.status_code == 404:
                print('A database with id \'{0}\' does not exist'.format(id))
            elif e.status_code == 409:
                print('A database with id \'{0}\' already exists'.format(id))
            else: 
                raise errors.HTTPFailure(e.status_code)

        return render_template(
            'create.html',
            title='Create Page',
            year=datetime.now().year,
            message='You created new account successfully [Account Name: '+str(user)+'][ number of user: '+str(num)+' ] ' )
    else:
        return render_template(
            'account.html',
            title='Create your account.',
            year=datetime.now().year,
            message='please input all information!!' )

@app.route('/account', methods=['GET', 'POST'])
def account():
    if request.method == 'POST':
         config.DOCUMENTDB_NAME = request.form.get('username')
         config.DOCUMENTDB_FACULTY = request.form.get('fac')
         config.DOCUMENTDB_PHONE = request.form.get('phone')
         config.DOCUMENTDB_PASSWORD = request.form.get('pass')

    return render_template(
       'account.html',
        title='Create your account.',
        year=datetime.now().year,
        message='' )

@app.route('/study', methods=['GET', 'POST'])
def study(): 
    client = document_client.DocumentClient(config.DOCUMENTDB_HOST, {'masterKey': config.DOCUMENTDB_KEY})
    checkValue = False
    if (config.DOCUMENTDB_NAMEMAIN != "" or config.DOCUMENTDB_PASSMAIN != ""):
        msgg =''
        
        db_id = config.DOCUMENTDB_DATABASE
        coll_id = config.DOCUMENTDB_COLLECTION
        
        #find userNumber in database
        db_query = "select * from r where r.id = '{0}'".format(db_id)
        db = list(client.QueryDatabases(db_query))[0]
        db_link = db['_self']
       
        coll_query = "select * from r where r.id = '{0}'".format(coll_id)
        coll = list(client.QueryCollections(db_link, coll_query))[0]
        coll_link = coll['_self']
       
        docs = client.ReadDocuments(coll_link)
        lst = list(docs)
        longest = len(lst)
        realUsername = ''
        if(longest == 0):
            msgg = 'your account does not exist!!'
        else:
            for i in lst:
              if(config.DOCUMENTDB_NAMEMAIN == str(i['username']) and config.DOCUMENTDB_PASSMAIN == str(i['Password'])):
                  msgg = i
                  realUsername = str(i['username'])
                  checkValue = True
        if (checkValue == True):
             return render_template(
                    'study.html',
                    title='Study Page',
                    year= datetime.now().year,
                    message = realUsername)
        else:
             #incorrect username or password
             return render_template(
                    'index.html',
                     title='Login Page',
                    year= datetime.now().year,
                     message='incorrect username or password' )
       
    else:
        #please input username&pass
        return render_template(
            'index.html',
            title='Login Page',
            year= datetime.now().year,
            message='please input username & password' )