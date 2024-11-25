import os
import pickle
import re
import sys
from datetime import datetime

import numpy as np
import pandas as pd
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sqlalchemy import text
from tensorflow.keras.models import load_model
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__, template_folder='templates')
db_path = os.path.join(os.path.dirname(__file__), 'data', 'show_data')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

db = SQLAlchemy(app)

with app.app_context():
    db.Model.metadata.reflect(bind=db.engine, schema='main')
    table_names = db.Model.metadata.tables.keys()

app.app_context().push()


class Participant(db.Model):
    __table__ = db.Model.metadata.tables['main.Participants']


@app.route('/')
def index():
    logging.debug("Index route accessed")
    # Fetch raw data
    result = db.session.execute(text("SELECT * FROM Participants"))
    participants = result.fetchall()
    logging.debug(f"Fetched participants: {participants}")
    return render_template('index.html', participants=participants)


@app.route('/submit', methods=['POST'])
def predict():
    male1 = request.form['male_1']
    male2 = request.form['male_2']
    male3 = request.form['male_3']
    female1 = request.form['female_1']
    female2 = request.form['female_2']
    female3 = request.form['female_3']
    male_capitan = request.form['male_capitan']
    female_capitan = request.form['female_capitan']

    print(f"Male 1: {male1}, Male 2: {male2}, Male 3: {male3}")
    print(f"Female 1: {female1}, Female 2: {female2}, Female 3: {female3}")
    print(f"Male Capitan: {male_capitan}, Female Capitan: {female_capitan}")

    male1 = Participant.query.filter_by(ID=male1).first()
    male2 = Participant.query.filter_by(ID=male2).first()
    male3 = Participant.query.filter_by(ID=male3).first()
    female1 = Participant.query.filter_by(ID=female1).first()
    female2 = Participant.query.filter_by(ID=female2).first()
    female3 = Participant.query.filter_by(ID=female3).first()
    male_capitan = Participant.query.filter_by(ID=male_capitan).first()
    female_capitan = Participant.query.filter_by(ID=female_capitan).first()

    data = {
        'p1_name': male1.name,
        'p2_name': male2.name,
        'p3_name': male3.name,
        'mc_name': male_capitan.name,
        'p4_name': female1.name,
        'p5_name': female2.name,
        'p6_name': female3.name,
        'fc_name': female_capitan.name,
        'p1_sex': male1.sex,
        'p2_sex': male2.sex,
        'p3_sex': male3.sex,
        'mc_sex': male_capitan.sex,
        'p4_sex': female1.sex,
        'p5_sex': female2.sex,
        'p6_sex': female3.sex,
        'fc_sex': female_capitan.sex,
        'p1_age': int(datetime.now().year - male1.dob.year),
        'p2_age': int(datetime.now().year - male2.dob.year),
        'p3_age': int(datetime.now().year - male3.dob.year),
        'mc_age': int(datetime.now().year - male_capitan.dob.year),
        'p4_age': int(datetime.now().year - female1.dob.year),
        'p5_age': int(datetime.now().year - female2.dob.year),
        'p6_age': int(datetime.now().year - female3.dob.year),
        'fc_age': int(datetime.now().year - female_capitan.dob.year)
    }

    df = pd.DataFrame(data, index=[0])

    # Encode the name columns
    with open('saves/label_encoder.pkl', 'rb') as f:
        label_encoder = pickle.load(f)
    label_encoder_classes = {}
    name_columns = re.findall(r'p\d_name|mc_name|fc_name', ' '.join(df.columns))

    # Encode the columns
    for col in name_columns:
        df[col] = label_encoder.transform(df[col])
        label_encoder_classes[col] = label_encoder.classes_

    with open('saves/scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)

    #Uploading the model
    model = load_model('saves/model.h5')
    test_data = df.values.astype(np.float32).reshape(1, -1)
    test_data = scaler.transform(test_data)
    prediction = model.predict(test_data)

    test_data = scaler.inverse_transform(test_data)
    names_indexes = test_data[0][:8]
    names = []
    le = LabelEncoder()
    for col in name_columns:
        le.classes_ = label_encoder_classes[col]
        names = le.inverse_transform([int(name) for name in names_indexes])
    males = names[:4]
    females = names[4:]
    male_team = ', '.join(males)
    female_team = ', '.join(females)
    winner = 'female' if prediction < 0.5 else 'male'
    return (f"The winner team is {winner} with the following members of "
            f"male team: {male_team} and female team: {female_team}")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
