import tabula
from downloader import update_file
from pickle import load, dump
from logger import logging
from prettytable import PrettyTable

def check_new_students(faculty):
    logging.info("checking new students...")
    with open('tmp/students', 'rb') as f:
        students_arr = load(f)
    
    file_path = update_file()
    df = tabula.read_pdf(file_path, pages='all', multiple_tables=True, lattice=True)

    count_faculty = 0
    count_target = 0
    count_paid = 0
    count = 0
    paid = ''

    table_faculty = PrettyTable()
    table_faculty.padding_width = 0
    table_faculty.field_names = ["№", "ФИО", "📄", "💸"]

    table_new_students = PrettyTable()
    table_new_students.padding_width = 0
    table_new_students.field_names = ["№", "ФИО", "📄", "💸"]

    for table in df:
        for i in range(1, len(table)):
            if table.iloc[i][3] == faculty:
                fio = table.iloc[i][1].split("\r")[0]
                if table.iloc[i][5] == 'да':
                    count_paid += 1
                    paid = 'да'
                else:
                    paid = 'нет'

                if table.iloc[i][1].split("\r")[0] not in students_arr:
                    students_arr.append(table.iloc[i][1].split("\r")[0])
                    count += 1
                    table_new_students.add_row([count, "{} {}.{}.".format(fio.split(" ")[0], fio.split(" ")[1][0], fio.split(" ")[2][0]), table.iloc[i][4], paid])

                if table.iloc[i][4] == 'ЦП':
                    count_target += 1
                count_faculty += 1
                table_faculty.add_row([count_faculty, "{} {}.{}.".format(fio.split(" ")[0], fio.split(" ")[1][0], fio.split(" ")[2][0]), table.iloc[i][4], paid])
    
    with open('tmp/students_faculty', 'wb') as f:
        dump([str(table_faculty), count_faculty, count_paid, count_target], f)
    with open('tmp/students', 'wb') as f:
        dump(students_arr, f)
    logging.info("checking students - success!")
    return str(table_new_students), count
