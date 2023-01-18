from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from model.Availability import Availability
from model.Availability import Availability_list

from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


# check the username
def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


# check the username
def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver



def search_caregiver_schedule(tokens):
    # tokens = date
    # check 1: check the login condition
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]

    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    d = datetime.date(year, month, day)

    print("/")
    print(d)
    print("/")

    # list the available caregivers
    try:
        available_caregiver = None
        available_caregiver = Availability_list(d).caregiver_list()
    except pymssql.Error as e:
        print("Error occurred when searching schedule")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when searching schedule")
        print("Error:", e)
        return

    # if this date has no available caregiver, shows this message
    if available_caregiver is None:
        print("No caregiver is available, please select another day!")
    print("/")

    # list all vaccine and doses
    try:
        Vaccine(None, None).vaccine_list()
    except pymssql.Error as e:
        print("Error occurred when listing vaccine")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when listing vaccine")
        print("Error:", e)
        return



def reserve(tokens):
    # tokens = <date> <vaccine_name>
    # check 1: check the login condition
    global current_patient
    if current_patient is None:
        print("Please login as a patient frist!")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return
    
    date = tokens[1]
    vaccine_name = tokens[2]

    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    d = datetime.date(year, month, day)

    # checking the vaccine exists or not and the dose is empty or not (vaccine_check returns the number of dose)
    vaccine_check = None
    try:
        vaccine_check = Vaccine(vaccine_name, None).get_dose()
    except pymssql.Error as e:
        print("Error occurred when searching vaccine")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when searching vaccine")
        print("Error:", e)
        return

    if vaccine_check is None:
        print("Vaccine name is wrong, please type again!")
        return
    elif vaccine_check == 0:
        print("This vaccine is unavailable, please select another vaccine!")
        return

    # checking the date exists or not (date_check returns the first available caregiver)
    date_check = None
    try:
        date_check = Availability_list(d).first_caregiver()
    except pymssql.Error as e:
        print("Error occurred when searching date")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when searching date")
        print("Error:", e)
        return
    
    if date_check is None:
        print("No caregiver is available, please select another day!")
        return

    # generate an appointment ID and save to table 'Appointments' with the name of caregiver 
    else:
        # use year+month+day+caregiver to create an id
        appointmentID = str(year) + str(month) + str(day) + date_check
        caregiver_name = date_check

        try:
            current_patient.save_to_appointment(appointmentID, caregiver_name, vaccine_name, d) 
        except pymssql.Error as e:
            print("Error occurred when making appointment")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when making appointment")
            print("Error:", e)
            return 
        
        # make an appointment and delete the data from table 
        try:
            Availability(d, caregiver_name).delete_db()
        except pymssql.Error as e:
            print("Error occurred when delete data")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when delete data")
            print("Error:", e)
            return

        # decrease the vaccine number after making an appointment (vaccine_check returns the number of dose)
        try:
            Vaccine(vaccine_name, vaccine_check).decrease_available_doses(1)
        except pymssql.Error as e:
            print("Error occurred when decreasing vaccine number")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when decreasing vaccine number")
            print("Error:", e)
            return 

        print('Appointment ID: ', appointmentID)
        print('Caregiver name: ', date_check)
    


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])

    try:
        d = datetime.date(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        print("")
        print("Please upload again or another date")
        return
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")



def cancel(tokens):
    # cancel <appointment_id>
    # check 1: the length for tokens need to be exactly 2 to include all information
    if len(tokens) != 2:
        print("Please try again!")
        return

    # check 2: check if the current logged-in user is a caregiver or a patient
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    appointment_id = tokens[1]

    # cancel caregiver's appointment
    if current_caregiver is not None:
        # output date and caregiver from table Appointments 
        try:
            date_and_caregiver = None # date_and_caregiver = (date, caregiver_name)
            date_and_caregiver = current_caregiver.select_date_from_appointment(appointment_id)
        except pymssql.Error as e:
            print("Error occurred when selecting date 'd")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when selecting date 'd")
            print("Error:", e)
            return
        
        # output vaccine from table Appointments
        try:
            vaccine_and_dose = None # vaccine_and_dose = (vaccine, dose)
            vaccine_and_dose = current_caregiver.select_vaccine_from_appointment(appointment_id)
        except pymssql.Error as e:
            print("Error occurred when selecting date 'v")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when selecting date 'v")
            print("Error:", e)
            return

        # add back one dose
        try:
            Vaccine(vaccine_and_dose[0], vaccine_and_dose[1]).increase_available_doses(1)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return

        # re-upload the availability information
        try:
            current_caregiver.upload_availability(date_and_caregiver[0])
        except pymssql.Error as e:
            print("Upload Availability Failed")
            print("Db-Error:", e)
            return
        except ValueError:
            print("Please enter a valid date!")
            return
        except Exception as e:
            print("Error occurred when uploading availability")
            print("Error:", e)
            return

        # remove the appointment from table
        try:
            current_caregiver.cancel_appointment(appointment_id)
        except pymssql.Error as e:
            print("Fail to cancel caregiver's appointment")
            print("Db-Error:", e)
            return
        except Exception as e:
            print("Error occurred when cancel caregiver's appointment")
            print("Error:", e)
            return
        print('Successfully cancel the appointment ID: ', appointment_id)

    # cancel patient's appointment
    if current_patient is not None:
        # output date and caregiver from table Appointments 
        try:
            date_and_caregiver = None # date_and_caregiver = (date, caregiver_name)
            date_and_caregiver = current_patient.select_date_from_appointment(appointment_id)
        except pymssql.Error as e:
            print("Error occurred when selecting date 'd")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when selecting date 'd")
            print("Error:", e)
            return

        # output vaccine from table Appointments
        try:
            vaccine_and_dose = None # vaccine_and_dose = (vaccine, dose)
            vaccine_and_dose = current_patient.select_vaccine_from_appointment(appointment_id)
        except pymssql.Error as e:
            print("Error occurred when selecting date 'v")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when selecting date 'v")
            print("Error:", e)
            return

        # add back one dose
        try:
            Vaccine(vaccine_and_dose[0], vaccine_and_dose[1]).increase_available_doses(1)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return

        # re-upload the availability information
        try:
            current_patient.upload_availability(date_and_caregiver[0], date_and_caregiver[1])
        except pymssql.Error as e:
            print("Upload Availability Failed")
            print("Db-Error:", e)
            return
        except ValueError:
            print("Please enter a valid date!")
            return
        except Exception as e:
            print("Error occurred when uploading availability")
            print("Error:", e)
            return

        # remove the appointment from table
        try:
            current_patient.cancel_appointment(appointment_id)
        except pymssql.Error as e:
            print("Fail to cancel patient's appointment")
            print("Db-Error:", e)
            return
        except Exception as e:
            print("Error occurred when cancel paitent's appointment")
            print("Error:", e)
            return
        print('Successfully cancel the appointment ID: ', appointment_id)



def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])

    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")



def show_appointments(tokens):
    # the length for tokens need to be exactly 1 to include all information
    if len(tokens) != 1:
        print("Please try again!")
        return

    # find current login condition
    global current_patient
    global current_caregiver
    if current_patient is None and current_caregiver is None:
        print("Please login first")
        return

    # display caregiver's appointments
    if current_caregiver is not None:
        try:
            appointment = None
            appointment = current_caregiver.show_appointment()
        except pymssql.Error as e:
            print("Fail to display caregiver's appointment")
            print("Db-Error:", e)
            return
        except Exception as e:
            print("Error occurred when showing caregiver's appointment")
            print("Error:", e)
            return
        if appointment is None:
            print("You have no appointment!")

    # display patient's appointments
    if current_patient is not None:
        try:
            appointment = None
            appointment = current_patient.show_appointment()
        except pymssql.Error as e:
            print("Fail to display patient's appointment")
            print("Db-Error:", e)
            return
        except Exception as e:
            print("Error occurred when showing paitent's appointment")
            print("Error:", e)
            return
        if appointment is None:
            print("You have no appointment!")


    
def logout(tokens):
    # check type error
    if len(tokens) != 1:
        print("Please try again!")
        return

    # find current login condition
    global current_patient
    global current_caregiver
    if current_patient is None and current_caregiver is None:
        print("Please login first")
        return

    # reset the login condition
    current_caregiver = None
    current_patient = None
    print("Successfully logged out!")
    


def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date: mm-dd-yyyy>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date: mm-dd-yyyy> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date: mm-dd-yyyy>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")



if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()