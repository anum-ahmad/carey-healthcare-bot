import re
import pandas as pd
import pyttsx3
import spacy
import numpy as np
from sklearn import preprocessing
from sklearn.tree import DecisionTreeClassifier, _tree
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC
import csv
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

training = pd.read_csv('Data/Training.csv')
testing = pd.read_csv('Data/Testing.csv')
cols = training.columns
cols = cols[:-1]
x = training[cols]
y = training['prognosis']
y1 = y

reduced_data = training.groupby(training['prognosis']).max()

# Mapping strings to numbers
le = preprocessing.LabelEncoder()
le.fit(y)
y = le.transform(y)

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)
testx = testing[cols]
testy = testing['prognosis']
testy = le.transform(testy)

clf1 = DecisionTreeClassifier()
clf = clf1.fit(x_train, y_train)

# Cross-validation scores
scores = cross_val_score(clf, x_test, y_test, cv=3)
print("Cross-validation scores:", scores.mean())

model = SVC()
model.fit(x_train, y_train)
print("SVM accuracy:", model.score(x_test, y_test))

importances = clf.feature_importances_
indices = np.argsort(importances)[::-1]
features = cols

def check_pattern(dis_list, inp):
    pred_list = []
    inp = inp.replace(' ', '_')
    patt = f"{inp}"
    regexp = re.compile(patt)
    pred_list = [item for item in dis_list if regexp.search(item)]
    if len(pred_list) > 0:
        return 1, pred_list
    else:
        return 0, []

def sec_predict(symptoms_exp):
    df = pd.read_csv('Data/Training.csv')
    X = df.iloc[:, :-1]
    y = df['prognosis']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=20)
    rf_clf = DecisionTreeClassifier()
    rf_clf.fit(X_train, y_train)

    symptoms_dict = {symptom: index for index, symptom in enumerate(X)}
    input_vector = np.zeros(len(symptoms_dict))
    for item in symptoms_exp:
        input_vector[[symptoms_dict[item]]] = 1

    return rf_clf.predict([input_vector])

def print_disease(node):
    node = node[0]
    val = node.nonzero()
    disease = le.inverse_transform(val[0])
    return list(map(lambda x: x.strip(), list(disease)))

def tree_to_code(tree, feature_names):
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature
    ]

def readn(nstr):
    engine = pyttsx3.init()
    engine.setProperty('voice', "english+f5")
    engine.setProperty('rate', 130)
    engine.say(nstr)
    engine.runAndWait()
    engine.stop()

severityDictionary = dict()
description_list = dict()
precautionDictionary = dict()

symptoms_dict = {}

for index, symptom in enumerate(x):
    symptoms_dict[symptom] = index

def calc_condition(exp, days):
    sum = 0
    for item in exp:
        sum = sum + severityDictionary[item]
    if (sum * days) / (len(exp) + 1) > 13:
        print("You should seek consultation from a doctor.")
    else:
        print("It might not be that bad, but you should take precautions.")

def getDescription():
    global description_list
    with open('MasterData/symptom_Description.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            _description = {row[0]: row[1]}
            description_list.update(_description)

def getSeverityDict():
    global severityDictionary
    with open('MasterData/symptom_severity.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        try:
            for row in csv_reader:
                _diction = {row[0]: int(row[1])}
                severityDictionary.update(_diction)
        except:
            pass

def getprecautionDict():
    global precautionDictionary
    with open('MasterData/symptom_precaution.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            _prec = {row[0]: [row[1], row[2], row[3], row[4]]}
            precautionDictionary.update(_prec)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def process_text_with_spacy(text):
    doc = nlp(text)
    entities = [{"text": ent.text, "start": ent.start_char, "end": ent.end_char, "label": ent.label_}
                for ent in doc.ents]
    return entities

def get_symptoms():
    while True:
        print("\nWhat symptom are you experiencing?")
        user_input = input("-> ")

        entities = process_text_with_spacy(user_input)

        if entities:
            print("Detected entities:")
            for entity in entities:
                print(f"{entity['label']}: {entity['text']}")
            return user_input
        else:
            print("I'm sorry, I couldn't understand the symptom. Please try again.")

def getInfo():
    def introduce_chatbot():
        print("-----------------------------------HealthCare ChatBot-----------------------------------")
        print("\nHello! I am Carey: The Get Well Bot, and I am here to ensure you that All is Well!!")

    introduce_chatbot()

    print("What can I help you with today?")
    print("1. Do you want health tips?")
    print("2. Do you want a diagnosis?")
    print("3. Do you want medicine information?")

    user_choice = input("Enter the number of your choice: ")

    if user_choice == "2":
        print("Great! Let's proceed with the diagnosis.")
    
        user_input = get_symptoms()

        entities = process_text_with_spacy(user_input)

        if entities:
            print("Detected entities:")
            for entity in entities:
                print(f"{entity['label']}: {entity['text']}")

            chk_dis = ",".join(features).split(",")
            symptoms_present = []
            disease_input = "" 

            while disease_input == "":
                print("\nWhat symptom are you experiencing?  \t\t", end="->")
                disease_input = input("")
                conf, cnf_dis = check_pattern(chk_dis, disease_input)
                if conf == 1:
                    print("Hmm.. your symptoms seem to be related to the following: ")
                    for num, it in enumerate(cnf_dis):
                        print(num, ")", it)
                    if num != 0:
                        print(f"Can you please clarify which symptom did you mean by selecting it? (0 - {num}):  ", end="")
                        conf_inp = int(input(""))
                    else:
                        conf_inp = 0

                    disease_input = cnf_dis[conf_inp]
                    break
                else:
                    print("I am sorry, I don't seem to be knowledgeable about this. Can you re-enter your symptom?")

            while True:
                try:
                    num_days = int(input("I see... for how many days have you been experiencing this ? : "))
                    break
                except:
                    print("I am sorry I didn't get that.")

            def recurse(node, depth):
                indent = "  " * depth
                if tree_.feature[node] != _tree.TREE_UNDEFINED:
                    name = feature_name[node]
                    threshold = tree_.threshold[node]

                    if name == disease_input:
                        val = 1
                    else:
                        val = 0
                    if val <= threshold:
                        recurse(tree_.children_left[node], depth + 1)
                    else:
                        symptoms_present.append(name)
                        recurse(tree_.children_right[node], depth + 1)
                else:
                    present_disease = print_disease(tree_.value[node])
                    red_cols = reduced_data.columns
                    symptoms_given = red_cols[reduced_data.loc[present_disease].values[0].nonzero()]
                    print("Are you experiencing any ")
                    symptoms_exp = []
                    for syms in list(symptoms_given):
                        inp = ""
                        print(syms, "? : ", end='')
                        while True:
                            inp = input("")
                            if inp == "yes" or inp == "no":
                                break
                            else:
                                print("provide proper answers i.e. (yes/no) : ", end="")
                        if inp == "yes":
                            symptoms_exp.append(syms)

                    second_prediction = sec_predict(symptoms_exp)
                    calc_condition(symptoms_exp, num_days)
                    if present_disease[0] == second_prediction[0]:
                        print("It seems you may have ", present_disease[0])
                        print(description_list[present_disease[0]])

                    else:
                        print("It seems you may have ", present_disease[0], "or ", second_prediction[0])
                        print(description_list[present_disease[0]])
                        print(description_list[second_prediction[0]])

                    precution_list = precautionDictionary[present_disease[0]]
                    print("Please take care and consider the following measures : ")
                    for i, j in enumerate(precution_list):
                        print(i + 1, ")", j)

                recurse(0, 1)

            getSeverityDict()
            getDescription()
            getprecautionDict()
            getInfo()
            tree_to_code(clf, features)

        else:
            print("I'm sorry, I couldn't understand the symptom. Please try again.")

    else:
        print("Okay, feel free to ask if you have any other questions.")
