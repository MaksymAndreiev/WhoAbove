import os
import sys
from datetime import datetime

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__, template_folder='templates')
db_path = os.path.join(r'C:/Users/maxog/DataGripProjects/WhoAbove/show_data')
print(db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

db = SQLAlchemy(app)

with app.app_context():
    db.Model.metadata.reflect(bind=db.engine, schema='main')
    table_names = db.Model.metadata.tables.keys()

    print(table_names)

app.app_context().push()


class Participant(db.Model):
    __table__ = db.Model.metadata.tables['main.Participants']


class Episode(db.Model):
    __table__ = db.Model.metadata.tables['main.Episodes']


@app.route('/')
def index():
    # Fetch raw data
    result = db.session.execute(text("SELECT * FROM Participants"))
    participants = result.fetchall()
    return render_template('index.html', participants=participants)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
