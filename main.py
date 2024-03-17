import os
import sys

import pandas
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = Flask(__name__)
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
    data = {'ParticipantName': [],
            'EpisodesCount': []}
    participants = Participant.query.all()
    # episodes = Episode.query.all()
    for participant in participants:
        participant_name = participant.name
        if not participant.capitan:
            if participant.sex:
                episodes_count = Episode.query.filter_by(male1=participant.ID).count()
                episodes_count += Episode.query.filter_by(male2=participant.ID).count()
                episodes_count += Episode.query.filter_by(male3=participant.ID).count()
            else:
                episodes_count = Episode.query.filter_by(female1=participant.ID).count()
                episodes_count += Episode.query.filter_by(female2=participant.ID).count()
                episodes_count += Episode.query.filter_by(female3=participant.ID).count()
        else:
            if participant.sex:
                episodes_count = Episode.query.filter_by(male_capitan=participant.ID).count()
            else:
                episodes_count = Episode.query.filter_by(female_capitan=participant.ID).count()
        data['ParticipantName'].append(participant_name)
        data['EpisodesCount'].append(episodes_count)
    df_part = pd.DataFrame(data)
    print(df_part[df_part['EpisodesCount'] > 1])


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
