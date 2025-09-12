from employee import EmployeeDB

db=EmployeeDB()

db.add_employee(3,"tausifa","fs")
db.add_employee(4,"balaji","bfs")

db.check_in(3)
db.check_in(4)

db.check_out(3)
db.check_out(4)

db.show_attendance()