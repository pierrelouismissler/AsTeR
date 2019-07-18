# Author:  DINDIN Meryll
# Date:    09 July 2019
# Project: AsTeR

try: from service_SQL.utils import *
except: from utils import *

con = Flask('DTB')
con.config['SQLALCHEMY_DATABASE_URI'] = format_url('sqlite')
con.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# Set the whole structure
dtb = SQLAlchemy(con)

# Database architecture

class User(dtb.Model):
    
    username = dtb.Column(dtb.String(80), primary_key=True, unique=True, nullable=False)
    firstname = dtb.Column(dtb.String(80), unique=False, nullable=False)
    lastname = dtb.Column(dtb.String(80), unique=False, nullable=False)
    password = dtb.Column(dtb.String(80), unique=False, nullable=False)
    email = dtb.Column(dtb.String(80), unique=True, nullable=False)

class Call(dtb.Model):

    call_id = dtb.Column(dtb.String(80), primary_key=True, unique=True, nullable=False)
    length = dtb.Column(dtb.Float, unique=False, nullable=False)
    timestamp = dtb.Column(dtb.Integer, unique=False, nullable=False)
    longitude = dtb.Column(dtb.Float, unique=False, nullable=False)
    latitude = dtb.Column(dtb.Float, unique=False, nullable=False)
    transcript = dtb.Column(dtb.Text, unique=False, nullable=True)
    priority = dtb.Column(dtb.Float, unique=False, nullable=True)

class Unit(dtb.Model):

    unit_id = dtb.Column(dtb.String(80), primary_key=True, unique=True, nullable=False)
    target = dtb.Column(dtb.String(80), unique=False, nullable=False)
    path = dtb.Column(dtb.Text, unique=False, nullable=False)
    longitude = dtb.Column(dtb.Float, unique=False, nullable=False)
    latitude = dtb.Column(dtb.Float, unique=False, nullable=False)
    unit_type = dtb.Column(dtb.String(80), unique=False, nullable=False)
    unit_name = dtb.Column(dtb.String(80), unique=False, nullable=False)
    status = dtb.Column(dtb.String(80), unique=False, nullable=False)

if __name__ == '__main__':

    # Initialize structure
    dtb.reflect()
    dtb.drop_all()
    dtb.create_all()

    # Run iterative population
    def populate_users(config='configs/initialization.yaml'):

        with open(config) as raw: pop = yaml.safe_load(raw)['users']
        for user in pop: dtb.session.add(User(**user))
        dtb.session.commit()

    # Run iterative population
    def populate_units(config='configs/initialization.yaml'):

        with open(config) as raw: pop = yaml.safe_load(raw)['units']
        for unit in pop: dtb.session.add(Unit(**unit))
        dtb.session.commit()

    # Initialize registrations
    populate_users()
    populate_units()