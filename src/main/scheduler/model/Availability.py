import sys
sys.path.append("../db/*")
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


class Availability:
    def __init__(self, available_date, caregiver_name):
        self.available_date = available_date
        self.caregiver_name = caregiver_name

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_availability = "INSERT INTO Availabilities VALUES (%s, %s)"
        try:
            cursor.execute(add_availability, (self.available_date, self.caregiver_name))
            conn.commit()
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()
    
    # remove the data when patient makes an appointment
    def delete_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        delete_caregiver = "DELETE FROM Availabilities WHERE Time = %s and Username = %s"
        try:
            cursor.execute(delete_caregiver, (str(self.available_date), str(self.caregiver_name)))
            conn.commit()
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()

# class for list and caregiver name
class Availability_list:
    def __init__(self, available_date):
        self.available_date = available_date

    # list the caregiver by date
    def caregiver_list(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        get_carefiver = "SELECT Time, Username FROM Availabilities WHERE Time = %s ORDER BY Username ASC"
        try:
            cursor.execute(get_carefiver, str(self.available_date))
            row = cursor.fetchone()
            while row:
                print("Caregiver Name %s" % (row[1]))
                row = cursor.fetchone()
            
            conn.cursor().execute(get_carefiver, str(self.available_date))
            for roww in cursor:
                return roww[1] # return a value to make sure this output is not None

            conn.close()     
        except pymssql.Error:
            print("Error occurred when getting Name")
            raise
        finally:
            cm.close_connection()

    def get_available_date(self):
        return self.available_date

    # date check
    def first_caregiver(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        get_carefiver = "SELECT Time, Username FROM Availabilities WHERE Time = %s"
        try:
            cursor.execute(get_carefiver, str(self.available_date))
            for row in cursor:
                return row[1]

            conn.close()     
        except pymssql.Error:
            print("Error occurred when getting Name")
            raise
        finally:
            cm.close_connection()