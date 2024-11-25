import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text

# Connect to the SQLite database
db_path = 'sqlite:///C:/Users/maxog/DataGripProjects/WhoAbove/show_data'
engine = create_engine(db_path)

def get_dob_from_wikipedia(name, reverse=False):
    if reverse:
        name = name.split(' ')[::-1]
        name = ' '.join(name)
    url = f"https://uk.wikipedia.org/wiki/{name.replace(' ', '_')}"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    dob = None

    for line in soup.find_all('span', {'class': 'bday'}):
        dob = line.text
        break

    return dob

# Query the database
query = """
SELECT name
FROM Participants
WHERE dob IS NULL
"""

with engine.connect() as connection:
    result = connection.execute(text(query))
    celebrities = [row[0] for row in result]

for celebrity in celebrities:
    #dob = get_dob_from_wikipedia(celebrity)
    dob = get_dob_from_wikipedia(celebrity, reverse=True)
    if dob:
        update_query = text("""
        UPDATE Participants
        SET dob = :dob
        WHERE name = :name
        """)
        with engine.connect() as connection:
            try:
                connection.execute(update_query, {"dob": dob, "name": celebrity})
                print(f"Updated {celebrity} with DOB {dob}")
            except Exception as e:
                print(f"Failed to update {celebrity}: {e}")
            connection.commit()