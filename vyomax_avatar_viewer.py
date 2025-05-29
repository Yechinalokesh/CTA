# Remote_User/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages

# Your models
from .models import ClientRegister_Model, insurance_claim_status, detection_accuracy, detection_ratio

# Python standard libraries
import datetime
import re
import string

# Third-party libraries for Machine Learning part
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn import svm
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, f1_score

# LOGIN VIEW
def login(request):
    print("--- LOGIN VIEW: Top of function ---")
    if request.method == "POST" and 'submit1' in request.POST:
        print("--- LOGIN VIEW: POST request received ---")
        username_from_form = request.POST.get('username')
        password_from_form = request.POST.get('password')
        print(f"--- LOGIN VIEW: Attempting login for username: {username_from_form} ---")

        try:
            user_obj = ClientRegister_Model.objects.get(username=username_from_form)
            print(f"--- LOGIN VIEW: User object found for {username_from_form} ---")
            if check_password(password_from_form, user_obj.password):
                print(f"--- LOGIN VIEW: Password CORRECT for {username_from_form} ---")
                request.session['userid'] = user_obj.id
                request.session['username'] = user_obj.username
                print(f"--- LOGIN VIEW: Session set for userid: {user_obj.id}, username: {user_obj.username} ---")
                messages.success(request, f"Welcome back, {user_obj.username}!")
                print("--- LOGIN VIEW: Attempting to redirect to 'ViewYourProfile' ---")
                return redirect('ViewYourProfile')
            else:
                print(f"--- LOGIN VIEW: Password INCORRECT for {username_from_form} ---")
                messages.error(request, 'Invalid username or password.')
        except ClientRegister_Model.DoesNotExist:
            print(f"--- LOGIN VIEW: User {username_from_form} DOES NOT EXIST ---")
            messages.error(request, 'Invalid username or password.')
        except Exception as e:
            print(f"--- LOGIN VIEW: An unexpected error occurred: {e} ---")
            messages.error(request, 'An unexpected error occurred during login. Please try again.')
    
    print("--- LOGIN VIEW: Rendering login.html ---")
    return render(request, 'RUser/login.html')


# REGISTRATION VIEW
def Register1(request):
    print("--- REGISTER1 VIEW: Top of function ---")
    if request.method == "POST":
        print("--- REGISTER1 VIEW: POST request received ---")
        username = request.POST.get('username')
        email = request.POST.get('email')
        plain_password = request.POST.get('password')
        phoneno = request.POST.get('phoneno')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        print(f"--- REGISTER1 VIEW: Attempting to register username: {username} ---")

        if ClientRegister_Model.objects.filter(username=username).exists():
            print(f"--- REGISTER1 VIEW: Username {username} already exists. ---")
            messages.error(request, f"Username '{username}' already exists. Please choose another.")
            return render(request, 'RUser/Register1.html', {'entered_data': request.POST})

        if ClientRegister_Model.objects.filter(email=email).exists():
            print(f"--- REGISTER1 VIEW: Email {email} already exists. ---")
            messages.error(request, f"Email '{email}' is already registered. Please use another.")
            return render(request, 'RUser/Register1.html', {'entered_data': request.POST})

        hashed_password = make_password(plain_password)
        print(f"--- REGISTER1 VIEW: Password hashed for {username}. ---")

        ClientRegister_Model.objects.create(
            username=username, email=email, password=hashed_password,
            phoneno=phoneno, country=country, state=state, city=city,
            address=address, gender=gender
        )
        print(f"--- REGISTER1 VIEW: User {username} created in database. ---")
        messages.success(request, "Registered Successfully! You can now log in.")
        print(f"--- REGISTER1 VIEW: Redirecting {username} to login page. ---")
        return redirect('login')
    else:
        print("--- REGISTER1 VIEW: GET request, rendering Register1.html ---")
        return render(request, 'RUser/Register1.html')


# VIEW USER PROFILE
def ViewYourProfile(request):
    print("--- VIEWYOURPROFILE VIEW: Top of function ---")
    if 'userid' not in request.session:
        print("--- VIEWYOURPROFILE VIEW: 'userid' NOT in session. Redirecting to login. ---")
        messages.error(request, "You must be logged in to view your profile.")
        return redirect('login')

    userid = request.session['userid']
    print(f"--- VIEWYOURPROFILE VIEW: 'userid' in session: {userid} ---")
    try:
        obj = ClientRegister_Model.objects.get(id=userid)
        print(f"--- VIEWYOURPROFILE VIEW: User object {obj.username} found. Rendering ViewYourProfile.html ---")
        return render(request, 'RUser/ViewYourProfile.html', {'object': obj})
    except ClientRegister_Model.DoesNotExist:
        print(f"--- VIEWYOURPROFILE VIEW: User with id {userid} DOES NOT EXIST. Clearing session and redirecting to login. ---")
        messages.error(request, "User profile not found.")
        if 'userid' in request.session: del request.session['userid']
        if 'username' in request.session: del request.session['username']
        return redirect('login')
    except Exception as e:
        print(f"--- VIEWYOURPROFILE VIEW: An unexpected error: {e} ---")
        messages.error(request, "An error occurred viewing your profile.")
        return redirect('login')


# ADD DATASET DETAILS
def Add_DataSet_Details(request):
    print("--- ADDDATASETDETAILS VIEW: Top of function ---")
    if 'userid' not in request.session: # Basic login check
        messages.error(request, "You must be logged in to add dataset details.")
        return redirect('login')
    val = ''
    return render(request, 'RUser/Add_DataSet_Details.html', {"excel_data": val})


# PREDICT INSURANCE CLAIM TYPE
def Predict_Insurance_Claim_Type(request):
    print("--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: Top of function ---")
    if 'userid' not in request.session:
        print("--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: User not logged in. Redirecting. ---")
        messages.error(request, "You must be logged in to make predictions.")
        return redirect('login')

    if request.method == "POST":
        print("--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: POST request received ---")
        
        # VVVVVVVV THIS IS THE CORRECTED SECTION VVVVVVVV
        # Get ALL form data. Ensure the keys ('Account_Code', 'DATE_OF_INTIMATION', etc.)
        # EXACTLY match the 'name' attributes in your HTML form inputs.
        Account_Code = request.POST.get('Account_Code')
        DATE_OF_INTIMATION = request.POST.get('DATE_OF_INTIMATION')
        DATE_OF_ACCIDENT = request.POST.get('DATE_OF_ACCIDENT')
        CLAIM_Real = request.POST.get('CLAIM_Real')
        AGE = request.POST.get('AGE')
        TYPE = request.POST.get('TYPE')
        DRIVING_LICENSE_ISSUE = request.POST.get('DRIVING_LICENSE_ISSUE')
        BODY_TYPE = request.POST.get('BODY_TYPE')
        MAKE = request.POST.get('MAKE')
        MODEL = request.POST.get('MODEL')
        YEAR = request.POST.get('YEAR')
        CHASIS_Real = request.POST.get('CHASIS_Real')
        REG = request.POST.get('REG') 
        SUM_INSURED = request.POST.get('SUM_INSURED')
        POLICY_NO = request.POST.get('POLICY_NO')
        POLICY_START = request.POST.get('POLICY_START')
        POLICY_END = request.POST.get('POLICY_END')
        INTIMATED_AMOUNT = request.POST.get('INTIMATED_AMOUNT')
        INTIMATED_SF = request.POST.get('INTIMATED_SF')
        EXECUTIVE = request.POST.get('EXECUTIVE')
        PRODUCT = request.POST.get('PRODUCT')
        POLICYTYPE = request.POST.get('POLICYTYPE')
        NATIONALITY = request.POST.get('NATIONALITY')
        # ^^^^^^^^ END OF CORRECTED SECTION ^^^^^^^^^^^

        # Updated print statement to check one of the newly added variables
        print(f"--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: Form data received, POLICY_NO: {POLICY_NO}, DATE_OF_INTIMATION: {DATE_OF_INTIMATION} ---")

        # Check if essential data for prediction (POLICY_NO) is present
        if not POLICY_NO:
            print("--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: ERROR - POLICY_NO is missing from form data. ---")
            messages.error(request, "Policy Number is required for prediction.")
            # It's good to pass back the data the user entered so they don't lose it
            return render(request, 'RUser/Predict_Insurance_Claim_Type.html', {'entered_data': request.POST, 'error_message': "Policy Number is required."})

        try:
            print("--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: Starting ML logic ---")
            data = pd.read_csv("Insurance_Claim_Datasets.csv", encoding='latin-1')
            print("--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: CSV loaded ---")

            def apply_results(results):
                if results == 'Fraud': return 0
                elif results == 'Real': return 1
                return None

            if 'Claim_Staus' not in data.columns:
                print("--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: ERROR - 'Claim_Staus' column missing in CSV ---")
                messages.error(request, "'Claim_Staus' column missing in dataset.")
                return render(request, 'RUser/Predict_Insurance_Claim_Type.html', {'entered_data': request.POST, 'error_message': "'Claim_Staus' column missing."})

            data['Results'] = data['Claim_Staus'].apply(apply_results)
            data.dropna(subset=['Results'], inplace=True)

            if 'POLICY_NO' not in data.columns:
                print("--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: ERROR - 'POLICY_NO' column missing in CSV for features ---")
                messages.error(request, "'POLICY_NO' column missing in dataset (for features).")
                return render(request, 'RUser/Predict_Insurance_Claim_Type.html', {'entered_data': request.POST, 'error_message': "'POLICY_NO' column missing for features."})

            x_feature = data['POLICY_NO'].astype(str)
            y_target = data['Results']

            if len(x_feature) == 0 or len(y_target) == 0 or len(x_feature) != len(y_target):
                print("--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: ERROR - Feature or target data is empty or mismatched. ---")
                messages.error(request, "Not enough data to train the model after processing.")
                return render(request, 'RUser/Predict_Insurance_Claim_Type.html', {'entered_data': request.POST, 'error_message': "Insufficient data for training."})

            cv = CountVectorizer(lowercase=False, strip_accents='unicode', ngram_range=(1, 1))
            x_transformed = cv.fit_transform(x_feature)
            print("--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: CountVectorizer fitted ---")

            current_test_size = 0.20
            min_samples_for_split = 2 # Typically need at least 2 samples for a split
            if hasattr(y_target, 'nunique') and y_target.nunique() > 1:
                min_samples_for_split = max(min_samples_for_split, y_target.nunique()) # For stratified split

            if x_transformed.shape[0] < min_samples_for_split:
                print(f"--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: ERROR - Not enough data samples ({x_transformed.shape[0]}) to split. Need at least {min_samples_for_split}. ---")
                messages.error(request, f"Not enough data samples to train (need at least {min_samples_for_split}). Please check dataset.")
                return render(request, 'RUser/Predict_Insurance_Claim_Type.html', {'entered_data': request.POST, 'error_message': "Not enough data to train."})
            
            if x_transformed.shape[0] * current_test_size < 1:
                if x_transformed.shape[0] > 1:
                    current_test_size = 1 / x_transformed.shape[0]
                else:
                     print(f"--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: ERROR - Dataset too small ({x_transformed.shape[0]}) for train/test split. ---")
                     messages.error(request, "Dataset is too small to split for training and testing.")
                     return render(request, 'RUser/Predict_Insurance_Claim_Type.html', {'entered_data': request.POST, 'error_message': "Dataset too small to split."})

            X_train, X_test, y_train, y_test = train_test_split(
                x_transformed, y_target, test_size=current_test_size, random_state=42, 
                stratify=y_target if y_target.nunique() > 1 else None
            )
            print(f"--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: Data split. Train shape: {X_train.shape}, Test shape: {X_test.shape} ---")

            if X_train.shape[0] == 0 or X_test.shape[0] == 0:
                print(f"--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: ERROR - Training or testing set is empty after split. ---")
                messages.error(request, "Training or testing data became empty after splitting.")
                return render(request, 'RUser/Predict_Insurance_Claim_Type.html', {'entered_data': request.POST, 'error_message': "Data split resulted in empty sets."})

            models = []
            nb_model = MultinomialNB()
            nb_model.fit(X_train, y_train)
            models.append(('naive_bayes', nb_model))
            print("--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: Naive Bayes trained ---")

            svm_model = svm.LinearSVC(dual="auto", C=1.0, max_iter=10000) # Increased max_iter
            svm_model.fit(X_train, y_train)
            models.append(('svm', svm_model))
            print("--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: SVM trained ---")
            
            lr_model = LogisticRegression(random_state=0, solver='lbfgs', max_iter=1000)
            lr_model.fit(X_train, y_train)
            models.append(('logistic', lr_model))
            print("--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: Logistic Regression trained ---")

            sgd_model = SGDClassifier(loss='hinge', penalty='l2', random_state=0, max_iter=1000, tol=1e-3)
            sgd_model.fit(X_train, y_train)
            models.append(('SGDClassifier', sgd_model))
            print("--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: SGD Classifier trained ---")

            classifier = VotingClassifier(models)
            classifier.fit(X_train, y_train)
            print("--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: VotingClassifier trained ---")

            input_policy_no_vector = cv.transform([str(POLICY_NO)]).toarray()
            prediction_result = classifier.predict(input_policy_no_vector)
            print(f"--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: Prediction made for {POLICY_NO}: {prediction_result} ---")

            prediction_value = int(prediction_result[0])
            val = 'Fraud Claim' if prediction_value == 0 else 'Real Claim'

            # Now all these variables (DATE_OF_INTIMATION, etc.) should be defined
            insurance_claim_status.objects.create(
                Account_Code=Account_Code, DATE_OF_INTIMATION=DATE_OF_INTIMATION,
                DATE_OF_ACCIDENT=DATE_OF_ACCIDENT, CLAIM_Real=CLAIM_Real, AGE=AGE,
                TYPE=TYPE, DRIVING_LICENSE_ISSUE=DRIVING_LICENSE_ISSUE, BODY_TYPE=BODY_TYPE,
                MAKE=MAKE, MODEL=MODEL, YEAR=YEAR, CHASIS_Real=CHASIS_Real, REG=REG,
                SUM_INSURED=SUM_INSURED, POLICY_NO=POLICY_NO, POLICY_START=POLICY_START,
                POLICY_END=POLICY_END, INTIMATED_AMOUNT=INTIMATED_AMOUNT,
                INTIMATED_SF=INTIMATED_SF, EXECUTIVE=EXECUTIVE, PRODUCT=PRODUCT,
                POLICYTYPE=POLICYTYPE, NATIONALITY=NATIONALITY, PREDICTION=val
            )
            print(f"--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: Insurance claim status saved for {POLICY_NO} with prediction {val} ---")
            messages.success(request, f"Prediction submitted: The claim is predicted as '{val}'.")
            # Pass back entered_data so the form is not completely empty on success, but also show result
            return render(request, 'RUser/Predict_Insurance_Claim_Type.html', {'objs': val, 'prediction_made': True, 'entered_data': request.POST})

        except FileNotFoundError:
            print("--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: ERROR - Dataset file 'Insurance_Claim_Datasets.csv' not found. ---")
            messages.error(request, "Dataset file 'Insurance_Claim_Datasets.csv' not found. Please check the file path.")
            return render(request, 'RUser/Predict_Insurance_Claim_Type.html', {'entered_data': request.POST, 'error_message': "Dataset file not found."})
        except KeyError as e:
            print(f"--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: ERROR - KeyError: {e}. A required column is missing. ---")
            messages.error(request, f"A required column is missing in the dataset: {e}. Please check your CSV file.")
            return render(request, 'RUser/Predict_Insurance_Claim_Type.html', {'entered_data': request.POST, 'error_message': f"Missing column: {e}"})
        except ValueError as e:
            print(f"--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: ERROR - ValueError: {e}. ---")
            messages.error(request, f"A data-related error occurred during prediction: {e}")
            return render(request, 'RUser/Predict_Insurance_Claim_Type.html', {'entered_data': request.POST, 'error_message': f"Data error: {e}"})
        except Exception as e:
            print(f"--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: ERROR - An unexpected error occurred: {e} ---")
            # For debugging, it's useful to see the full traceback in the console for unexpected errors
            import traceback
            traceback.print_exc() 
            messages.error(request, f"An error occurred during prediction. Please check console for details.") # Generic message to user
            return render(request, 'RUser/Predict_Insurance_Claim_Type.html', {'entered_data': request.POST, 'error_message': f"An unexpected error occurred. Admin has been notified."})

    # For GET request
    print("--- PREDICT_INSURANCE_CLAIM_TYPE VIEW: GET request, rendering form ---")
    return render(request, 'RUser/Predict_Insurance_Claim_Type.html')
