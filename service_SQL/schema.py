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
    fullname = dtb.Column(dtb.String(80), unique=False, nullable=False)
    password = dtb.Column(dtb.String(80), unique=False, nullable=False)
    emailing = dtb.Column(dtb.String(80), unique=True, nullable=False)

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
    
    # Initialize registrations
    populate_users()
