from main import db, app
import csv
import datetime

with app.app_context():
    db.Model.metadata.reflect(bind=db.engine, schema='main')
    table_names = db.Model.metadata.tables.keys()
    db.create_all()


class Participant(db.Model):
    __table__ = db.Model.metadata.tables['main.Participants']


class Episode(db.Model):
    __table__ = db.Model.metadata.tables['main.Episodes']


with open('scrapped_data.csv', newline='\n') as csvfile:
    episode_reader = csv.reader(csvfile)
    next(episode_reader)
    for row in episode_reader:
        season = row[0]
        episode = row[1]
        date = datetime.datetime.strptime(row[2], '%Y-%m-%d')
        men = row[3].split(';')
        women = row[6].split(';')
        men_id = []
        women_id = []
        for man in men:
            participants = Participant.query.filter_by(name=man).all()
            if len(participants) == 1:
                participant = participants[0]
                if man == men[-1]:
                    if participant.capitan == 0:
                        male_participant = Participant(name=man, sex=1, capitan=1)
                        db.session.add(male_participant)
                        participant = Participant.query.filter_by(name=man).first()
                participant_id = participant.ID
                men_id.append(participant_id)
            elif len(participants) == 0:
                capitan_label = 0
                if man == men[-1]:  # capitan
                    capitan_label = 1
                male_participant = Participant(name=man, sex=1, capitan=capitan_label)
                db.session.add(male_participant)
                participant = Participant.query.filter_by(name=man).first()
                participant_id = participant.ID
                men_id.append(participant_id)
        print(men_id)
        for woman in women:
            if woman == 'Аліна Завальська':
                woman = 'Ангеліна Завальська'
            elif woman == '​​Даша Малахова':
                woman = 'Дарія Малахова'
            participants = Participant.query.filter_by(name=woman).all()
            if len(participants) == 1:
                participant = participants[0]
                if woman == women[-1]:
                    if participant.capitan == 0:
                        female_participant = Participant(name=woman, sex=1, capitan=1)
                        db.session.add(female_participant)
                        participant = Participant.query.filter_by(name=woman).first()
                participant_id = participant.ID
                women_id.append(participant_id)
            elif len(participants) == 0:
                capitan_label = 0
                if woman == women[-1]:  # capitan
                    capitan_label = 1
                female_participant = Participant(name=woman, sex=0, capitan=capitan_label)
                db.session.add(female_participant)
                db.session.commit()
                participant = Participant.query.filter_by(name=woman).first()
                participant_id = participant.ID
                women_id.append(participant_id)
        if len(men_id) == 4 and len(women_id) == 4:
            episode_data = Episode(season=season, date=date, male1=men_id[0], female1=women_id[0],
                                   female2=women_id[1], female3=women_id[2], female_capitan=women_id[3],
                                   male2=men_id[1], male3=men_id[2], male_capitan=men_id[3])
        else:
            for i in range(len(men_id)):
                man =Participant.query.filter_by(ID=men_id[i]).first()
                print(man.name)
            for i in range(len(women_id)):
                woman = Participant.query.filter_by(ID=women_id[i]).first()
                print(woman.name)
        db.session.add(episode_data)
        db.session.commit()
