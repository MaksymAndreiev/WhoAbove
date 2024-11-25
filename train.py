import pickle
import re
import pandas as pd
from keras.layers import Dropout
from keras.regularizers import l2
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sqlalchemy import create_engine
from imblearn.over_sampling import SMOTE

# disable warnings
import warnings

warnings.filterwarnings('ignore')

# Connect to the SQLite database
db_path = 'sqlite:///data/show_data'
engine = create_engine(db_path)

# Query the database
query = """
SELECT e.*,
       p1.name AS p1_name, p2.name AS p2_name, p3.name AS p3_name, p4.name AS mc_name,
       p5.name AS p4_name, p6.name AS p5_name, p7.name AS p6_name, p8.name AS fc_name,
       p1.sex AS p1_sex, p2.sex AS p2_sex, p3.sex AS p3_sex, p4.sex AS mc_sex,
       p5.sex AS p4_sex, p6.sex AS p5_sex, p7.sex AS p6_sex, p8.sex AS fc_sex,
       p1.dob AS p1_dob, p2.dob AS p2_dob, p3.dob AS p3_dob, p4.dob AS mc_dob,
       p5.dob AS p4_dob, p6.dob AS p5_dob, p7.dob AS p6_dob, p8.dob AS fc_dob,
       f.sex_team
FROM Episodes e
LEFT JOIN Participants p1 ON e.participant1 = p1.id
LEFT JOIN Participants p2 ON e.participant2 = p2.id
LEFT JOIN Participants p3 ON e.participant3 = p3.id
LEFT JOIN Participants p4 ON e.male_capitan = p4.id
LEFT JOIN Participants p5 ON e.participant4 = p5.id
LEFT JOIN Participants p6 ON e.participant5 = p6.id
LEFT JOIN Participants p7 ON e.participant6 = p7.id
LEFT JOIN Participants p8 ON e.female_capitan = p8.id
JOIN FinalResults f ON e.ID = f.episode
"""

df = pd.read_sql(query, engine)

# Drop unnecessary columns
drop_columns = ['ID', 'season', 'male_capitan', 'female_capitan']
drop_columns.extend([col for col in df.columns if re.match(r'participant\d', col)])
df.drop(columns=drop_columns, inplace=True)

dates_columns = ['date']
dates_columns.extend([col for col in df.columns if re.match(r'p\d_dob|mc_dob|fc_dob', col)])
for col in dates_columns:
    df[col] = pd.to_datetime(df[col], format='mixed')

df['p1_age'] = ((df['date'] - df['p1_dob']).dt.days // 365).astype(int)
df['p2_age'] = ((df['date'] - df['p2_dob']).dt.days // 365).astype(int)
df['p3_age'] = ((df['date'] - df['p3_dob']).dt.days // 365).astype(int)
df['mc_age'] = ((df['date'] - df['mc_dob']).dt.days // 365).astype(int)
df['p4_age'] = ((df['date'] - df['p4_dob']).dt.days // 365).astype(int)
df['p5_age'] = ((df['date'] - df['p5_dob']).dt.days // 365).astype(int)
df['p6_age'] = ((df['date'] - df['p6_dob']).dt.days // 365).astype(int)
df['fc_age'] = ((df['date'] - df['fc_dob']).dt.days // 365).astype(int)

df.drop(columns=[col for col in df.columns if re.match(r'p\d_dob|mc_dob|fc_dob', col)], inplace=True)
df.drop(columns=['date'], inplace=True)

# Encode the name columns
label_encoder = LabelEncoder()
label_encoder_classes = {}

# Define the columns to encode
name_columns = re.findall(r'p\d_name|mc_name|fc_name', ' '.join(df.columns))
combined_series = pd.concat([df[col] for col in name_columns])

label_encoder.fit(combined_series)

# Encode the columns
for col in name_columns:
    df[col] = label_encoder.transform(df[col])
    label_encoder_classes[col] = label_encoder.classes_

# Define the target variable
Y = df['sex_team']
X = df.drop(columns=['sex_team'])

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

smote = SMOTE()
X_train, y_train = smote.fit_resample(X_train, y_train)
class_weights = compute_class_weight('balanced', classes=[0, 1], y=y_train)
class_weights = {i: class_weights[i] for i in range(len(class_weights))}

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model1 = Sequential()
model1.add(Dense(8, input_dim=X_train.shape[1], activation='relu'))
model1.add(Dense(4, activation='relu'))
model1.add(Dense(1, activation='sigmoid'))
model1.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model1.fit(X_train, y_train, epochs=100, batch_size=10)
_, accuracy = model1.evaluate(X_test, y_test)
print('Accuracy: %.2f' % (accuracy * 100))

learning_rates = [0.01, 0.001, 0.0001, 0.00001, 0]
dropouts = [0.1, 0.2, 0.3, 0.4, 0.5]
accuracies = []
model2 = None
for lr in learning_rates:
    for dropout in dropouts:
        model = Sequential()
        model.add(Dense(32, input_dim=X_train.shape[1], activation='relu', kernel_regularizer=l2(0.01)))
        model.add(Dropout(dropout))
        model.add(Dense(16, activation='relu', kernel_regularizer=l2(0.01)))
        model.add(Dropout(dropout))
        model.add(Dense(1, activation='sigmoid'))

        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        # early_stopping = EarlyStopping(monitor='accuracy', patience=10, restore_best_weights=True)
        model.fit(X_train, y_train, epochs=100, batch_size=16, class_weight=class_weights, verbose=0)
        _, accuracy = model.evaluate(X_test, y_test, verbose=0)
        if model2 is None or accuracy > max(accuracies):
            model2 = model
        accuracies.append(accuracy)

for lr, i in zip(learning_rates, range(len(learning_rates))):
    for dropout, j in zip(dropouts, range(len(dropouts))):
        print(f'Learning rate: {lr}, Dropout: {dropout}, Accuracy: {accuracies[i * len(dropouts) + j]}')
best_accuracy = max(accuracies)
lr = learning_rates[accuracies.index(best_accuracy) // len(dropouts)]
dropout = dropouts[accuracies.index(best_accuracy) % len(dropouts)]
print(f'Best accuracy: {best_accuracy}, Best learning rate: {lr}, Best dropout: {dropout}')
_, accuracy = model2.evaluate(X_test, y_test)
print('Accuracy: %.2f' % (accuracy * 100))

clf = RandomForestClassifier()
clf.fit(X_train, y_train)
print(clf.score(X_test, y_test))

models = [model1, model2, clf]
accuracies = [model.evaluate(X_test, y_test)[1] for model in models[0:2]]
accuracies.append(clf.score(X_test, y_test))
model = models[accuracies.index(max(accuracies))]

# Save the model, label encoder, and scaler
model.save('saves/model.h5')
with open('saves/label_encoder.pkl', 'wb') as f:
    pickle.dump(label_encoder, f)
with open('saves/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
