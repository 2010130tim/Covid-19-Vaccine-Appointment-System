import sys
sys.path.append("../util/*")
sys.path.append("../db/*")
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql


class Caregiver:
    def __init__(self, username, password=None, salt=None, hash=None):
        self.username = username
        self.password = password
        self.salt = salt
        self.hash = hash

    # getters
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_caregiver_details = "SELECT Salt, Hash FROM Caregivers WHERE Username = %s"
        try:
            cursor.execute(get_caregiver_details, self.username)
            for row in cursor:
                curr_salt = row['Salt']
                curr_hash = row['Hash']
                calculated_hash = Util.generate_hash(self.password, curr_salt)
                if not curr_hash == calculated_hash:
                    # print("Incorrect password")
                    cm.close_connection()
                    return None
                else:
                    self.salt = curr_salt
                    self.hash = calculated_hash
                    cm.close_connection()
                    return self
        except pymssql.Error as e:
            raise e
        finally:
            cm.close_connection()
        return None

    def get_username(self):
        return self.username

    def get_salt(self):
        return self.salt

    def get_hash(self):
        return self.hash

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_caregivers = "INSERT INTO Caregivers VALUES (%s, %s, %s)"
        try:
            cursor.execute(add_caregivers, (self.username, self.salt, self.hash))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()

    # Insert availability with parameter date d
    def upload_availability(self, d):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_availability = "INSERT INTO Availabilities VALUES (%s , %s)"
        try:
            cursor.execute(add_availability, (d, self.username))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            # print("Error occurred when updating caregiver availability")
            raise
        finally:
            cm.close_connection()

    # display the appointments
    def show_appointment(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        appointment = "SELECT AppointmentID, Name, Time, pUsername FROM Appointments WHERE cUsername = %s ORDER BY AppointmentID ASC"
        try:
            cursor.execute(appointment, self.username)
            row = cursor.fetchone()
            while row:
                print("AppointmentID:%s Vaccine:%s Date:%s Patient name:%s" % (row[0], row[1], str(row[2]), row[3]))
                row = cursor.fetchone()

            conn.cursor().execute(appointment, self.username)
            for roww in cursor:
                return roww[1] # return a value to make sure this output is not None

            conn.close()     
        except pymssql.Error:
            print("Error occurred when getting Name")
            raise
        finally:
            cm.close_connection()

    # cancel the appointments with parameter date ID
    def cancel_appointment(self, ID):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        remove_appointment = "DELETE FROM Appointments WHERE AppointmentID = %s"
        try:
            cursor.execute(remove_appointment, ID)
            conn.commit()     
        except pymssql.Error:
            print("Error occurred when getting Name")
            raise
        finally:
            cm.close_connection()

    # select the date and caregiver from table Appointments with parameter date ID
    def select_date_from_appointment(self, ID):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        select_appointment = "SELECT Time, cUsername FROM Appointments WHERE AppointmentID = %s"
        try:
            cursor.execute(select_appointment, ID)
            for row in cursor:
                return str(row[0]), row[1]
            conn.commit()     
        except pymssql.Error:
            print("Error occurred when getting Name")
            raise
        finally:
            cm.close_connection()

    # select the vaccine and dose from table Appointments with parameter date ID
    def select_vaccine_from_appointment(self, ID):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        select_appointment = "SELECT V.Name, V.Doses FROM Vaccines V, Appointments A WHERE V.Name = A.Name and A.AppointmentID = %s"
        try:
            cursor.execute(select_appointment, ID)
            for row in cursor:
                return row
            conn.commit()     
        except pymssql.Error:
            print("Error occurred when getting Name")
            raise
        finally:
            cm.close_connection()
