import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from flask_script import Manager, Shell, Server
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField, IntegerField, DateField, SelectMultipleField,PasswordField, BooleanField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_login import UserMixin
from flask_login import LoginManager
from flask_login import login_required

from flask_wtf import Form
from wtforms.validators import Required, Length, Email
from werkzeug.security import generate_password_hash, check_password_hash

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'mysql://root:password@localhost/inventory'
    #'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

manager = Manager(app)
manager.add_command("runserver", Server(use_debugger=True))
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.init_app(app)
login_manager.login_view = 'login'


class Product(db.Model):
    __tablename__ = 'products'
    pid = db.Column(db.Integer, primary_key=True)
    pname = db.Column(db.String(64), unique=True, index=True, nullable=False)
    pprice = db.Column(db.Numeric(15,2), nullable=False)
    storeinb = db.relationship('StoreIn', backref=db.backref('product'))
    proinstoreb = db.relationship('ProInStore', backref=db.backref('product'))
    storesearchb = db.relationship('StoreSearch', backref=db.backref('product'))

    def __repr__(self):
        return '<Product %r>' % self.pname

class Storehouse(db.Model):
    __tablename__ = 'storehouses'
    sid = db.Column(db.Integer, primary_key=True)
    sname = db.Column(db.String(50), unique=True, index=True, nullable=False)
    splace = db.Column(db.String(100), nullable=False)
    storeinb = db.relationship('StoreIn', backref=db.backref('storehouse'))
    proinstoreb = db.relationship('ProInStore', backref=db.backref('storehouse'))
    storesearchb = db.relationship('StoreSearch', backref=db.backref('storehouse'))

    def __repr__(self):
        return '<Storehouse %r>' % self.sname

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, index=True, nullable=False)
    name = db.Column(db.String(40),nullable=False)
    user_type = db.Column(db.Integer, nullable=False)

    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
   # storein = db.relationship('StoreIn', backref=db.backref('username'))

    def __repr__(self):
        return '<User %r>' % self.username


class StoreIn(db.Model):
    __tablename__ = 'storein'
    pid = db.Column(db.Integer, db.ForeignKey('products.pid'), primary_key=True)
    pnum = db.Column(db.Integer, nullable=False)
    sid = db.Column(db.Integer, db.ForeignKey('storehouses.sid'), primary_key=True)
    empname = db.Column(db.String(50), db.ForeignKey('users.username'))
    optdate = db.Column(db.Date, nullable=False, primary_key=True)

class Takeout(db.Model):
    __tablename__ = 'takeout'
    #id = db.Column(db.String(5), primary_key=True)
    pid = db.Column(db.Integer, db.ForeignKey('products.pid'), primary_key=True)
    pnum = db.Column(db.Integer, nullable=False)
    sid = db.Column(db.Integer, db.ForeignKey('storehouses.sid'), primary_key=True)
    empname = db.Column(db.String(50), db.ForeignKey('users.username'))
    optdate = db.Column(db.Date, nullable=False, primary_key=True)

class ProInStore(db.Model):
    __tablename__ = 'proinstore'
    pid = db.Column(db.Integer, db.ForeignKey('products.pid'), primary_key=True)
    pnum = db.Column(db.Integer)
    sid = db.Column(db.Integer, db.ForeignKey('storehouses.sid'), primary_key=True)
    storeupper = db.Column(db.Integer, nullable=False)
    storelower = db.Column(db.Integer, nullable=False)

class StoreSearch(db.Model):
    __tablename__ = 'storesearch'
    pid = db.Column(db.Integer, db.ForeignKey('products.pid'), primary_key=True)
    pnum = db.Column(db.Integer)
    sid = db.Column(db.Integer, db.ForeignKey('storehouses.sid'), primary_key=True)
    storeupper = db.Column(db.Integer, nullable=False)
    storelower = db.Column(db.Integer, nullable=False)


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

class productForm(FlaskForm):
    pid = IntegerField('pid')
    pname = StringField('pname')
    pprice = DecimalField('pprice')
    submit = SubmitField('submit')

class storeinForm(FlaskForm):
    pid = IntegerField('入库产品编号')
    pnum = IntegerField('入库产品数量')
    sid = IntegerField('仓库编号')
    empname = StringField('经办人')
    optdate = DateField('入库日期')
    submit = SubmitField('提交')

class takeoutForm(FlaskForm):
    pid = IntegerField('出库产品编号')
    pnum = IntegerField('出库产品数量')
    sid = IntegerField('仓库编号')
    empname = StringField('经办人')
    optdate = DateField('出库日期')
    submit = SubmitField('提交')

class inquireForm(FlaskForm):
    #每个项是(值，显示)
    pname_choices = [('手机', '手机'), ('电脑', '电脑'), ('书包', '书包')]
    sname_choices = [('仓库1', '仓库1(广州)'), ('仓库2', '仓库2(深圳)'), ('仓库3', '仓库3(杭州)')]
    pname = SelectMultipleField('产品名称',choices = pname_choices)
    sname = SelectMultipleField('仓库名称',choices = sname_choices)
    submit = SubmitField('提交')

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[Required(), Length(1, 64)])
    password = PasswordField('密码', validators=[Required()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')




def make_shell_context():
    #return dict(app=app, db=db, User=User, Role=Role)
    return dict(app=app, db=db, User=User)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    form = productForm()
    product = Product.query.filter_by(pid=1).first()
    if form.validate_on_submit():
        product_new = Product(pid=form.pid.data, pname=form.pname.data, pprice=form.pprice.data)
        db.session.add(product_new)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return redirect(url_for('index'))
    #a = Product.query.filter_by(pid=1).frist()
    return render_template('index.html')
    #     user = User.query.filter_by(username=form.name.data).first()
    #     if user is None:
    #         user = User(username=form.name.data)
    #         db.session.add(user)
    #         session['known'] = False
    #     else:
    #         session['known'] = True
    #     session['name'] = form.name.data
    #     form.name.data = ''
    #     return redirect(url_for('index'))
    # return render_template('index.html', form=form, name=session.get('name'),
    #                        known=session.get('known', False))
@app.route('/storein', methods=['GET', 'POST'])
def storein_show():
    form = storeinForm()
    if form.validate_on_submit():
        StoreIn_new = StoreIn(pid=form.pid.data, pnum=form.pnum.data, sid=form.sid.data, empname=form.empname.data, optdate=form.optdate.data)
        ProInStore_oj = ProInStore.query.filter_by(pid=form.pid.data, sid=form.sid.data).first()
        if ProInStore_oj.pnum < ProInStore_oj.storeupper:
            ProInStore_oj.pnum += form.pnum.data
            db.session.add(StoreIn_new)
            db.session.add(ProInStore_oj)
            try:
                db.session.commit()
            except:
                db.session.rollback()
        else:
            flash('库存量大于最大库存量，不允许入库操作')
        return redirect(url_for('storein_show'))
    storeIns = StoreIn.query.order_by(StoreIn.optdate.desc()).all()
    return render_template( 'storein.html',form=form , storeIns=storeIns)

@app.route('/takeout', methods=['GET', 'POST'])
def takeout_show():
    form = takeoutForm()
    if form.validate_on_submit():
        Takeout_new = Takeout(pid=form.pid.data, pnum=form.pnum.data, sid=form.sid.data, empname=form.empname.data, optdate=form.optdate.data)
        ProInStore_oj = ProInStore.query.filter_by(pid=form.pid.data, sid=form.sid.data).first()
        if form.pnum.data <= ProInStore_oj.pnum:
            ProInStore_oj.pnum -= form.pnum.data
            db.session.add(ProInStore_oj)
            db.session.add(Takeout_new)
            try:
                db.session.commit()
            except:
                db.session.rollback()
        else:
            flash('库存量不足')
        return redirect(url_for('takeout_show'))
    takeouts = Takeout.query.order_by(Takeout.optdate.desc()).all()
    #return render_template( 'storein.html',form=form, pid = storeIns.pid, pnum = storeIns.pnum, sid = storeIns.sid, empname=storeIns.empname, optdate=storeIns.optdate)
    return render_template( 'takeout.html',form=form , takeouts=takeouts)

@app.route('/proinstore', methods=['GET', 'POST'])
def proinstore_show():
    proinstores = ProInStore.query.order_by(ProInStore.pid.asc()).all()
    return render_template( 'proinstore.html', proinstores=proinstores)

@app.route('/inquire', methods=['GET', 'POST'])
def inquire_show():
    form = inquireForm()

    if form.validate_on_submit():
        for storesearch in StoreSearch.query.all():
            db.session.delete(storesearch)
        products = Product.query.filter_by(pname=form.pname.data[0]).first()
        storehouses = Storehouse.query.filter_by(sname=form.sname.data[0]).first()
        proinstore_st = ProInStore.query.filter_by(pid=products.pid, sid=storehouses.sid).first()
        storesearch_new = StoreSearch(pid=proinstore_st.pid, pnum=proinstore_st.pnum, sid=proinstore_st.sid, storeupper=proinstore_st.storeupper, storelower=proinstore_st.storelower)
        db.session.add(storesearch_new)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return redirect(url_for('inquire_show'))

    if StoreSearch.query.all():
        proinstores = StoreSearch.query.all()
        return render_template('inquire.html', form=form, proinstores=proinstores)
    else:
        return render_template('inquire.html', form=form)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/secret')
@login_required
def secret():
    return '登录用户才可用'

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        # if user is not None and user.verify_password(form.password.data):
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('index'))
        flash('无效的用户名和密码')
        # login_user(User.query.filter_by(username = form.username.data).first())
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('你已经登出帐号')
    return redirect(url_for('index'))


@app.route('/backup', methods=['GET', 'POST'])
def back_show():
    import os
    import time
    import datetime

    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_USER_PASSWORD = 'lzt2615237'
    # DB_NAME = '/backup/dbnames.txt'
    DB_NAME = 'inventory'
    BACKUP_PATH = 'D:\pycharmProjects\projects'

    # Getting current datetime to create seprate backup folder like "12012013-071334".
    DATETIME = time.strftime('%m%d%Y-%H%M%S')

    BEFOREBACKUPPATH = BACKUP_PATH + "\\" + DATETIME
    TODAYBACKUPPATH = BACKUP_PATH + "\\" + "lastbackup"

    # Checking if backup folder already exists or not. If not exists will create it.
    print("creating backup folder")
    if not os.path.exists(TODAYBACKUPPATH):
        os.makedirs(TODAYBACKUPPATH)
    else:
        os.rename(TODAYBACKUPPATH, BEFOREBACKUPPATH)
        os.makedirs(TODAYBACKUPPATH)

    # Code for checking if you want to take single database backup or assinged multiple backups in DB_NAME.
    print("checking for databases names file.")
    if os.path.exists(DB_NAME):
        file1 = open(DB_NAME)
        multi = 1
        print("Databases file found...")
        print("Starting backup of all dbs listed in file " + DB_NAME)
    else:
        print("Databases file not found...")
        print("Starting backup of database " + DB_NAME)
        multi = 0

    # Starting actual database backup process.
    if multi:
        in_file = open(DB_NAME, "r")
        flength = len(in_file.readlines())
        in_file.close()
        p = 1
        dbfile = open(DB_NAME, "r")

        while p <= flength:
            db = dbfile.readline()  # reading database name from file
            db = db[:-1]  # deletes extra line
            dumpcmd = "mysqldump -u " + DB_USER + " -p" + DB_USER_PASSWORD + " " + db + " > " + TODAYBACKUPPATH + "/" + db + ".sql"
            os.system(dumpcmd)
            p = p + 1
        dbfile.close()
    else:
        db = DB_NAME
        dumpcmd = "mysqldump -u " + DB_USER + " -p" + DB_USER_PASSWORD + " " + db + " > " + TODAYBACKUPPATH + "/" + db + ".sql"
        os.system(dumpcmd)

    print("Backup script completed")
    print("Your backups has been created in '" + TODAYBACKUPPATH + "' directory")
    return render_template('backup.html')#, form=form, name=product.pname)

@app.route('/backup', methods=['GET', 'POST'])
def cover_show():
    import os

    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_USER_PASSWORD = 'lzt2615237'
    # DB_NAME = '/backup/dbnames.txt'
    DB_NAME = 'inventory'
    BACKUP_PATH = 'D:\pycharmProjects\projects\lastbackup'

    # CREATE DATABASE `inventory` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;

    dumpcmd = "mysql -u" + DB_USER + " -p" + DB_USER_PASSWORD + " --default-character-set=utf8 -f " + DB_NAME + "<" + BACKUP_PATH + "\\" + DB_NAME + ".sql"

    os.system(dumpcmd)

    #flash("cover script completed")
    return redirect(url_for('backup.html'))

if __name__ == '__main__':
    manager.run()
