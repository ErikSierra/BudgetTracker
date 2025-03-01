import os
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


def get_category_classifier(training_file):
    """
    Loads training data from an Excel file and returns a trained text classification pipeline.
    The Excel file must have columns "Description" and "Category".
    """
    df_train = pd.read_excel(training_file)
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('clf', LogisticRegression(solver='liblinear'))
    ])
    pipeline.fit(df_train["Description"], df_train["Category"])
    return pipeline


def rule_based_category(description):
    """
    Checks for specific keywords in the description to determine the category.
    Returns the matched category if found; otherwise, returns None.
    """
    description_upper = description.upper()
    if "MCDONALD" in description_upper:
        return "Food"
    elif "MICROCENTER" in description_upper:
        return "Shopping"
    elif "WALMART" in description_upper:
        return "Shopping"
    elif "BP" in description_upper or "EXXON" in description_upper:
        return "Gas"
    elif "BILL" in description_upper:
        return "Bills"
    elif "H&M" in description_upper or "ZARA" in description_upper or "MACY'S" in description_upper:
        return "Clothing"
    else:
        return None


def get_category_for_description(description, classifier):
    """
    Returns the category for a given description.
    It first applies rule-based matching; if no rule matches, it uses the classifier's prediction.
    """
    rule_category = rule_based_category(description)
    if rule_category is not None:
        return rule_category
    else:
        return classifier.predict([description])[0]


def main():
    # Define file paths
    training_file_path = r"C:\Coding Stuff\Python Projects\AzureSQLdb\TrainingModels\AIex.xlsx"
    input_csv_file = r"C:\Coding Stuff\Python Projects\AzureSQLdb\DataStorage\Archive\Apple Card Transactions - April 2023.csv"
    output_csv_path = r"C:\Coding Stuff\Python Projects\AzureSQLdb\TrainingModels\test_predictions.csv"

    # Train the classifier using your training Excel file.
    classifier = get_category_classifier(training_file_path)

    # Load the test CSV file.
    df_test = pd.read_csv(input_csv_file)

    # Check that the file has a Description column.
    if "Description" not in df_test.columns:
        raise ValueError("The input CSV does not have a 'Description' column.")

    # Apply our combined rule-based and classifier approach.
    df_test["Predicted Category"] = df_test["Description"].apply(lambda x: get_category_for_description(x, classifier))

    # Export the results to a CSV file.
    df_test.to_csv(output_csv_path, index=False)
    print(f"Test predictions exported to {output_csv_path}")


if __name__ == "__main__":
    main()
