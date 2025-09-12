import inspect
import employee

def test_add_employee_query():
    db=employee.EmployeeDB
    expected_query="insert into employees(employee_id,name,department) values(%s,%s,%s)"
    actual_query=inspect.getsource(db.add_employee)
    assert expected_query in actual_query

def test_check_in_query():
    db = employee.EmployeeDB()
    expected_query = "INSERT INTO attendance (employee_id, check_in) VALUES (%s, NOW())"
    actual_query = inspect.getsource(db.check_in)
    assert expected_query in actual_query

def test_check_out_query():
    db = employee.EmployeeDB()
    expected_query = "UPDATE attendance SET check_out = NOW(), total_hours = TIMESTAMPDIFF(MINUTE, check_in, NOW()) / 60 WHERE employee_id = %s AND check_out IS NULL"
    actual_query = inspect.getsource(db.check_out)
    assert expected_query in actual_query

def test_show_attendance_query():
    db = employee.EmployeeDB()
    expected_query = "SELECT * FROM attendance"
    actual_query = inspect.getsource(db.show_attendance)
    assert expected_query in actual_query

def test_list_incomplete_attendance_query():
    db = employee.EmployeeDB()
    expected_query = "SELECT e.employee_id, e.name, a.check_in FROM employees e JOIN attendance a ON e.employee_id = a.employee_id WHERE a.check_out IS NULL"
    actual_query = inspect.getsource(db.list_incomplete_attendance)
    assert expected_query in actual_query


def test_add_employee_signature():
    sig = inspect.signature(employee.EmployeeDB.add_employee)
    assert list(sig.parameters.keys()) == ["self","employee_id", "name", "department"]

def test_check_in_signature():
    sig = inspect.signature(employee.EmployeeDB.check_in)
    assert list(sig.parameters.keys()) == ["self", "employee_id"]

def test_check_out_signature():
    sig = inspect.signature(employee.EmployeeDB.check_out)
    assert list(sig.parameters.keys()) == ["self", "employee_id"]

def test_show_attendance_signature():
    sig = inspect.signature(employee.EmployeeDB.show_attendance)
    assert list(sig.parameters.keys()) == ["self"]

def test_list_incomplete_attendance_signature():
    sig = inspect.signature(employee.EmployeeDB.list_incomplete_attendance)
    assert list(sig.parameters.keys()) == ["self"]