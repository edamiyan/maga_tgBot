import tabula
from downloader import update_file
from pickle import load, dump
from logger import logging

def check_new_students(faculty):
    logging.info("checking new students...")
    with open('tmp/students', 'rb') as f:
        students_arr = load(f)
    
    file_path = update_file()
    df = tabula.read_pdf(file_path, pages='all', multiple_tables=True, lattice=True)
    list = ''
    list_faculty = ''
    count_faculty = 0
    count_target = 0
    count_paid = 0
    count = 0

    for table in df:
        for i in range(1, len(table)):
            if table.iloc[i][3] == faculty:
                if table.iloc[i][1].split("\r")[0] not in students_arr:
                    students_arr.append(table.iloc[i][1].split("\r")[0])
                    count += 1
                    list +="{}) {} {} {}\n".format(count, table.iloc[i][1].split("\r")[0], table.iloc[i][3], table.iloc[i][4])
                if table.iloc[i][5] == 'да':
                    count_paid += 1
                if table.iloc[i][4] == 'ЦП':
                    count_target += 1
                count_faculty += 1
                list_faculty += "{}) {} {} {}\n".format(count_faculty, table.iloc[i][1].split("\r")[0], table.iloc[i][3], table.iloc[i][4])

    with open('tmp/students_faculty', 'wb') as f:
        dump([list_faculty, count_faculty, count_paid, count_target], f)
    
    with open('tmp/students', 'wb') as f:
        dump(students_arr, f)
    logging.info("checking students - success!")
    return list
