from config import get_connection
from mysql.connector import Error


class EmployeeDB:
    def add_employee(self,employee_id, name, department):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "insert into employees(employee_id,name,department) values(%s,%s,%s)",
                (employee_id, name, department)
            )
            conn.commit()
            print(f"Employee name is {name} from {department}")
            cursor.close()
            conn.close()
        except Error as e:
            print(f"Error: {e}")

    def check_in(self, employee_id):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO attendance (employee_id, check_in) VALUES (%s, NOW())", (employee_id,))
            conn.commit()
            print("Checked in.")
            cursor.close()
            conn.close()
        except Error as e:
            print("Error:", e)

    def check_out(self, employee_id):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE attendance SET check_out = NOW(), total_hours = TIMESTAMPDIFF(MINUTE, check_in, NOW()) / 60 WHERE employee_id = %s AND check_out IS NULL",
                (employee_id,))
            conn.commit()
            if cursor.rowcount > 0:
                print("Checked out.")
            else:
                print("No active check-in found.")
            cursor.close()
            conn.close()
        except Error as e:
            print("Error:", e)

    def show_attendance(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("select * from attendance")
            for row in cursor.fetchall():
                print(row)
            cursor.close()
            conn.close()
        except Error as e:
            print("Error:", e)

    def list_incomplete_attendance(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT e.employee_id, e.name, a.check_in FROM employees e JOIN attendance a ON e.employee_id = a.employee_id WHERE a.check_out IS NULL"
            )
            rows = cursor.fetchall()
            for row in rows:
                print(row)
            cursor.close()
            conn.close()
        except Error as e:
            print(f"Error: {e}")








