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


def add_participant(team, sex_label):
    ids = []
    for team_member in team:
        if team_member == 'Аліна Завальська':
            team_member = 'Ангеліна Завальська'
        elif team_member == '​​Даша Малахова':
            team_member = 'Дарія Малахова'
        elif team_member == 'Тереза ​​Балашова':
            team_member = 'Тереза Балашова'
        elif team_member == 'Анна "Ахава" Тесленко':
            team_member = 'Анна Тесленко'
        team_member = team_member.replace('  ', ' ')
        participants = Participant.query.filter_by(name=team_member).all()
        if len(participants) == 1:  # found before
            participant = participants[0]
            if team_member == team[-1]:  # the last member of team is always a capitan
                if participant.capitan == 0:  # if he was before as participant
                    new_participant = Participant(name=team_member, sex=sex_label,
                                                  capitan=1)  # add him as a new participant as capitan
                    db.session.add(new_participant)
                    db.session.commit()
                    participant = Participant.query.filter_by(name=team_member).first()
            participant_id = participant.ID
            ids.append(participant_id)
        elif len(participants) == 0:
            capitan_label = 0
            if team_member == team[-1]:  # capitan
                capitan_label = 1
            new_participant = Participant(name=team_member, sex=sex_label, capitan=capitan_label)
            db.session.add(new_participant)
            db.session.commit()
            participant = Participant.query.filter_by(name=team_member).first()
            participant_id = participant.ID
            ids.append(participant_id)
        elif len(participants) == 2:
            if team_member == team[-1]:
                participant = Participant.query.filter_by(name=team_member, capitan=1).first()
            else:
                participant = Participant.query.filter_by(name=team_member, capitan=0).first()
            participant_id = participant.ID
            ids.append(participant_id)
    return ids


with open('scrapped_data.csv', newline='\n') as csvfile:
    episode_reader = csv.reader(csvfile)
    next(episode_reader)
    for row in episode_reader:
        season = row[0]
        episode = row[1]
        date = datetime.datetime.strptime(row[2], '%Y-%m-%d')
        men = row[3].split(';')
        women = row[6].split(';')
        men_id = add_participant(men, 1)
        women_id = add_participant(women, 0)
        if len(men_id) == 4 and len(women_id) == 4:
            episode_data = Episode(season=season, date=date, male1=men_id[0], female1=women_id[0],
                                   female2=women_id[1], female3=women_id[2], female_capitan=women_id[3],
                                   male2=men_id[1], male3=men_id[2], male_capitan=men_id[3])
        else:
            for i in range(len(men_id)):
                man = Participant.query.filter_by(ID=men_id[i]).first()
                print(man.name)
            for i in range(len(women_id)):
                woman = Participant.query.filter_by(ID=women_id[i]).first()
                print(woman.name)
        db.session.add(episode_data)
        db.session.commit()
