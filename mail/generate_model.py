import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import pickle

# Loading the data from csv file to a pandas dataframe
raw_mail_data = pd.read_csv('mail_data.csv')

# Assuming your data has two columns: 'text' for the email content and 'label' for the spam/ham label

# Split your data into features (X) and target (Y)
X = raw_mail_data['Message']
Y = raw_mail_data['Category']

# Split your data into training and testing set
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=7)

# Transform your text data into tf-idf features
feature_extraction = TfidfVectorizer()
X_train_features = feature_extraction.fit_transform(X_train)

# Training the model (Logistic Regression model)
model = LogisticRegression()

# Training the Logistic Regression model with the training data
model.fit(X_train_features, Y_train)

# Save the trained model as a pickle string
pickle.dump(model, open("spam_classifier.pkl", "wb"))

# Save the feature_extraction object
pickle.dump(feature_extraction, open("feature_extraction.pkl", "wb"))
