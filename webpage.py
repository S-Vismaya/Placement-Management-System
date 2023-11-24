import streamlit as st
import pandas as pd
import mysql.connector
import re
import matplotlib.pyplot as plt
from datetime import date


def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="vis20adm",
        database="final_placements"
    )
    return connection 



def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(pattern, email):
        return True
    else:
        return False




def is_valid_srn(srn):
    pattern = r'^PES(1|2)(UG|PG)\d{2}(CS|EC|EE|CE|ME|BT)\d{3}$'
    return bool(re.match(pattern, srn))



def add_new_student():
    connection = get_db_connection()
    cursor = connection.cursor()

    st.subheader("Add New Student")
    SRN = st.text_input("Enter SRN:")
    first_name = st.text_input("Enter First Name:")
    last_name = st.text_input("Enter Last Name:")   
    cgpa = st.number_input("Enter CGPA:", min_value=0.0, max_value=10.0, step=0.01, format="%.2f")

    email = st.text_input("Enter Email:")
    phone_number = st.number_input("Enter Phone Number:")
    phone_number = int(phone_number)
    address = st.text_area("Enter Address:")
    department_options = ['cse', 'ece', 'eee', 'me', 'bt', 'ce']
    department = st.selectbox("Enter your branch:", department_options)
    options = ['Yes','No']
    placement_status = st.selectbox("Placement Status:(Yes/No)",options)
    placedyear = st.number_input("Year of placement:", key="placedyear")
    placedyear = int(placedyear)
    ctc = int(st.number_input("Enter the ctc:", key="ctc"))

    if st.button("Add"):

        last_name = last_name if last_name is not None else None
        ctc_value = ctc if ctc is not None else None
        placedyear_value = placedyear if placedyear is not None else None

        placement_status = placement_status.lower()
        values = ["yes","no"]
        if placement_status not in values:
            st.error("Invalid Placement Status")

        elif  not is_valid_srn(SRN):
            st.error("SRN is invalid.")

        elif phone_number < 1000000000 or phone_number > 9999999999:
            st.error("Please enter a 10-digit phone number.")

        elif placedyear < 1950 or placedyear > 2100:
            st.error("Enter valid placed year")

        elif not is_valid_email(email):   
            st.error("Enter valid email")    

        elif SRN and first_name and cgpa and email and phone_number and address:
                try:
                    sql_query = "INSERT INTO students (SRN, first_name, last_name, cgpa, email, phone_number, address, department, placement_status, placedyear,ctc,password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"
                    values = (SRN, first_name, last_name, cgpa, email, phone_number, address, department, placement_status, placedyear_value, ctc_value,SRN)

                    cursor.execute(sql_query, values)
                    connection.commit()
                    st.success("Student added successfully!")
                except mysql.connector.Error as err:
                    st.error("Invalid input. Details: %s" % err)
                except Exception as e:
                    st.error("Invalid input : %s" %e)  

        else:
            st.error("SRN, First Name, CGPA, Email, Phone Number, and Address are required!")

    cursor.close()
    connection.close()


def is_srn_in_database(srn):
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM students WHERE srn = %s"
    cursor.execute(query, (srn,))
    result = cursor.fetchone()
    connection.close()
    return result is not None

def modify_students():
    connection = get_db_connection()
    cursor = connection.cursor()

    st.subheader("Modify Student Details")
    srn_input = st.text_input("Enter SRN for Modification:", key="modify_srn_input")
    attribute_to_modify = st.selectbox("Select Attribute to Modify:", ["first_name", "last_name", "cgpa", "email", "phone_number", "address", "department", "placement_status", "placedyear", "ctc"], key="attribute_selectbox")
    new_value = st.text_input(f"Enter New {attribute_to_modify.capitalize()}:", key="new_value_input")

    if st.button("Modify"):
        if srn_input and attribute_to_modify and new_value:
            if not is_valid_srn(srn_input):
                st.error("SRN is invalid.")

            elif not is_srn_in_database(srn_input):
                st.error("SRN not found in the students table.")

            elif attribute_to_modify != "placement_status" or (attribute_to_modify == "placement_status" and new_value == "yes"):    
                try:
                    update_query = f"UPDATE students SET {attribute_to_modify} = %s WHERE SRN = %s"
                    cursor.execute(update_query, (new_value, srn_input))
                    connection.commit()
                    st.success(f"Student with SRN {srn_input} has been updated successfully. {attribute_to_modify} changed to {new_value}")

                except mysql.connector.Error as err:
                        st.error("Invalid input %s" %err)
                except Exception as e:
                        st.error("Invalid input %s" %e)

            else:
                st.warning("Invalid input")    
        else:
            st.warning("SRN, attribute, and new value are required.")

    cursor.close()
    connection.close()        

import streamlit as st
import pandas as pd

def show_students():
    connection = get_db_connection()
    cursor = connection.cursor()

    st.subheader("Search Students by SRN")
    student_id = st.text_input("Enter SRN:", key="srn_input")

    if student_id:
        if not is_valid_srn(student_id):
            st.error("SRN is invalid.")
        else:
            cursor.execute("SELECT SRN, first_name, last_name, cgpa, email, phone_number, address, department, placement_status, placedyear, ctc FROM students WHERE SRN=%s", (student_id,))
            student_data = cursor.fetchone()

            if student_data:
                # Fetch the column names excluding the last column ("password")
                column_names = [i[0] for i in cursor.description]
                # Exclude the last column ("password") from the DataFrame
                df = pd.DataFrame([student_data], columns=column_names)
                st.write("Student Details")
                st.table(df)
            else:
                st.write("No student found with the provided SRN.")

    st.subheader("All Students Details")
    cursor.execute("SELECT SRN, first_name, last_name, cgpa, email, phone_number, address, department, placement_status, placedyear, ctc FROM students")
    students_data = cursor.fetchall()
    
    # Fetch the column names excluding the last column ("password")
    column_names = [i[0] for i in cursor.description]

    # Exclude the last column ("password") from the DataFrame
    df = pd.DataFrame(students_data, columns=column_names)
    st.table(df.to_records(index=False))

    
        
    cursor.close()
    connection.close()

def delete_student():
    connection = get_db_connection()
    cursor = connection.cursor()

    st.subheader("Delete Student")
    student_id = st.text_input("SRN: ")

    check_query = "SELECT COUNT(*) FROM students WHERE SRN = %s"
    cursor.execute(check_query, (student_id,))
    count = cursor.fetchone()[0]

    if st.button("Delete"):
        try:
            if is_valid_srn(student_id):
                if(count > 0):
                    cursor.execute("DELETE FROM students WHERE SRN=%s", (student_id,))
                    connection.commit()
                    st.success("Student deleted successfully!")
                else:
                    st.error("Student not found.")
            else:
                st.error("SRN is invalid.")
        except Exception as e:
            st.error(f"Error deleting student: {e}")

    cursor.close()
    connection.close()        


def is_valid_integer(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

def is_appid_in_database(appid):
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM application WHERE application_id = %s"
    cursor.execute(query, (appid,))
    result = cursor.fetchone()
    connection.close()
    return result is not None

def is_jobid_in_database(jobid):
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM job WHERE job_id = %s"
    cursor.execute(query, (jobid,))
    result = cursor.fetchone()
    connection.close()
    return result is not None


def modify_application_details():
    connection = get_db_connection()
    cursor = connection.cursor()
    id_input = st.text_input("Enter Application ID for Modification:", key="modify_app_input")
    attribute_to_modify = st.selectbox("Select Attribute to Modify:", ["Round 1", "Round 2", "Round 3","Application Status"], key="attribute_selectbox")
    new_value = st.text_input(f"Enter {attribute_to_modify.capitalize()} value :", key="new_value_input")

    if st.button("Modify"):

        if not is_valid_integer(id_input):
            st.error("Invalid Application ID")

        elif not is_appid_in_database(id_input):
            st.error("Application ID not present")    

        elif id_input and attribute_to_modify and new_value:
            new_value = new_value.lower()
            if attribute_to_modify == "Round 1":
                round_no = 1
            elif attribute_to_modify == "Round 2":
                round_no = 2
            elif attribute_to_modify == "Round 3":  
                round_no = 3

            if attribute_to_modify == "Round 1" or attribute_to_modify == "Round 2" or attribute_to_modify == "Round 3":
                yn = ['yes','no']

                if new_value in yn:
                    try:
                        update_query = f"UPDATE rounds SET pass_value = %s WHERE application_id = %s and round_id = %s"
                        cursor.execute(update_query,(new_value,id_input,round_no))    
                        connection.commit()
                        st.success('Application updated successfully')
                    except mysql.connector.Error as err:
                        st.error("Invalid input %s" %err)
                    except Exception as e:
                        st.error("Invalid input : %s" %e)  
                else:
                    st.error("Invalid input")

            elif attribute_to_modify == "Application Status":
                valid = ['accepted','rejected','waiting']
                if new_value in valid:
                    try:
                        check_query = "SELECT (SELECT s.placement_status FROM students s WHERE s.srn = a.SRN) AS placement_status FROM application a WHERE a.application_id = %s"

                        cursor.execute(check_query, (id_input,))
                        result = cursor.fetchone()

                        if result and result[0] == 'no':

                            update_query = f"UPDATE application SET application_status = %s WHERE application_id = %s"
        
                            cursor.execute(update_query, (new_value, id_input))
                            connection.commit()
                            st.success('Application updated successfully')

                        else:
                            st.warning('Cannot update the status of an application to yes as the student is already placed')
                    except mysql.connector.Error as err:
                        st.error("Invalid input %s" %err)
                    except Exception as e:
                        st.error("Invalid input %s" %e)    
                else:
                    st.error("Invalid Input")

            

        else:
            st.warning("Unable to update")

    cursor.close()
    connection.close()        

def add_application():
    connection = get_db_connection()
    cursor = connection.cursor()

    

    st.subheader("Add Application Details")

    app_id = st.text_input("Enter Application ID:")
    srn = st.text_input("Enter SRN:")
    jobid = st.text_input("Enter Job ID:")
    dateapplied = st.date_input("Enter the date applied:")
    round1 = 'no'
    round2 = 'no'
    round3 = 'no'

    app_status = 'waiting'



    if st.button("Add"):
        round1 = round1 if round1 else 'no'
        round2 = round2 if round2 else 'no'
        round3 = round3 if round3 else 'no'
        app_status = app_status if app_status is not None else None
        app_status = app_status.lower()
        round1 = round1.lower()
        round2 = round2.lower()
        round3 = round3.lower()
        
        success_flag = True

        if not is_valid_srn(srn):
            st.error("Invalid SRN")


        else:    
            query = "SELECT placement_status FROM students WHERE srn = %s"
            cursor.execute(query, (srn,))
            placement_status = cursor.fetchone()

        allowed_statuses = ["accepted","waiting","rejected"]
        yn = ["yes","no"]

        if not is_valid_srn(srn):
            st.error("Invalid SRN")

        elif not is_valid_integer(app_id):
            st.error("Invalid Application ID")

        elif not is_valid_integer(jobid):
            st.error("Invalid Job ID")  

        elif not is_srn_in_database(srn):
            st.error("SRN does not exist in database")

        elif not is_jobid_in_database(jobid):
            st.error("Job ID does not exist in database")

        elif placement_status and placement_status[0] == 'no' and srn and app_id and jobid and dateapplied and app_status in allowed_statuses and round1 in yn and round2 in yn and round3 in yn :
            try:
                sql_query = "INSERT INTO application (application_id,SRN,date_applied,application_status,job_id) VALUES (%s, %s, %s, %s, %s)"
                values = (app_id, srn, dateapplied,app_status, jobid)
                cursor.execute(sql_query, values)
                connection.commit()
            except mysql.connector.Error as err:
                st.error("Invalid input %s" %err)
                success_flag = False
            except Exception as e:
                st.error("Invalid input %s" %e)   
                success_flag = False   

            if round1:
                try:
                    sql_query = "INSERT INTO rounds (round_id,application_id,pass_value)  VALUES (%s,%s,%s)"
                    values = ("1",app_id,round1)
                    cursor.execute(sql_query, values)
                    connection.commit()
                except mysql.connector.Error as err:
                    st.error("Invalid input %s" %err)
                    success_flag = False
                except Exception as e:
                    st.error("Invalid input %s" %e)  
                    success_flag = False    
            
            if round2:
                try:
                    sql_query = "INSERT INTO rounds (round_id,application_id,pass_value)  VALUES (%s,%s,%s)"
                    values = ("2",app_id,round2)
                    cursor.execute(sql_query, values)
                    connection.commit()
                except mysql.connector.Error as err:
                    st.error("Invalid input %s" %err)
                    success_flag = False
                except Exception as e:
                    st.error("Invalid input %s" %e) 
                    success_flag = False     

            if round3:
                try:
                    sql_query = "INSERT INTO rounds (round_id,application_id,pass_value)  VALUES (%s,%s,%s)"
                    values = ("3",app_id,round3)
                    cursor.execute(sql_query, values)
                    connection.commit()
                except mysql.connector.Error as err:
                    st.error("Invalid input %s" %err)
                    success_flag = False
                except Exception as e:
                    st.error("Invalid input %s" %e) 
                    success_flag = False     

            if success_flag == True:
                st.success("Application added successfully!")

        elif placement_status and placement_status[0] == 'yes':
            st.error("You are placed cant apply again")
        else:
            st.error("All fields are required!")

    cursor.close()
    connection.close()


def add_company():
    connection = get_db_connection()
    cursor = connection.cursor()

    company_id = st.text_input("Enter company id: ")
    company_name = st.text_input("Enter Company Name:")
    industry = st.text_input("Enter Industry type:")
    location = st.text_input("Enter Location:")
    studentsselected = st.number_input("Enter the number of students selected:", min_value=0, step=1, key="studentsselected")
    
    cutoff = st.number_input("Enter the cutoff::", min_value=0.0, max_value=10.0, step=0.01, format="%.2f")
    
    year = st.number_input("Enter the year:")
    website = st.text_input("Enter Website:")

    if st.button("Add"):

        if year < 1950 or year > 2100:
            st.error("Enter valid placed year")

        elif company_id and company_name and industry and location and cutoff and year and website:
                year = int(year)
                studentsselected = studentsselected if studentsselected is not None else None
                try:
                    cursor.execute("INSERT INTO company(cid, cname, industry, location, students_selected, cutoff, yearvisited, website,password) VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s)",(company_id, company_name, industry, location, studentsselected, cutoff, year, website,company_id))
                    connection.commit()
                    st.success("Company added successfully!")
                except mysql.connector.Error as err:
                        st.error("Invalid input %s" %err)
                except Exception as e:
                        st.error("Invalid input %s" %e)    
        else:
            st.error("Company Name, Industry, cutoff, and Location are required fields!")

    cursor.close()
    connection.close()


def view_companies():
    connection = get_db_connection()
    cursor = connection.cursor()

    st.subheader("Search Company by CompanyID")
    company_id = st.text_input("Enter Company ID:")

    if company_id:
        cursor.execute("SELECT * FROM company WHERE cid=%s", (company_id,))
        company_data = cursor.fetchone()

        if company_data:
            column_names = [i[0] for i in cursor.description]
            df = pd.DataFrame([company_data], columns=column_names)
            st.write("Company Details")
            st.table(df)
        else:
            st.write("No company found with the provided ID.")


    st.subheader("View Companies")
    cursor.execute("SELECT * FROM company")
    company_data = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]
    df = pd.DataFrame(company_data, columns=column_names)
    st.table(df.to_records(index=False))

    cursor.close()
    connection.close()    

def round_success():
    connection = get_db_connection()
    cursor = connection.cursor()

    round_names = ['Round 1', 'Round 2', 'Round 3']
    pass_percentages = []

    for idx, round_name in enumerate(round_names, start=1):
        sql_query = f"""
            SELECT 
                SUM(CASE WHEN round_id = {idx} AND pass_value = 'yes' THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN round_id = {idx} THEN 1 ELSE 0 END) AS pass_percentage
            FROM 
                rounds
            WHERE 
                round_id = {idx};
        """

        cursor.execute(sql_query)
        result = cursor.fetchone()

        if result:
            pass_percentage = result[0]
            pass_percentages.append(pass_percentage)
            st.write(f"{round_name} pass percentage: {pass_percentage}%")
        else:
            st.write(f"No data found for {round_name}")

    cursor.close()
    connection.close()

    # Plotting bar chart
    plt.figure(figsize=(8, 6))
    plt.bar(round_names, pass_percentages, color='skyblue')
    plt.xlabel('Round')
    plt.ylabel('Pass Percentage')
    plt.title('Pass Percentage for Each Round')
    plt.ylim(0, 100) 
    st.pyplot(plt)

def get_years_from_database():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT DISTINCT yearvisited FROM company") 
    years = [year[0] for year in cursor.fetchall()]
    print(years)
    return years

def filter_data_by_year(year):
    connection = get_db_connection()
    cursor = connection.cursor()
    print(type(year))
    yeart=(year,)
    print(type(yeart))
    cursor.execute("SELECT * FROM students WHERE placedyear = %s",yeart)
    rows = cursor.fetchall()
    total_students = len(rows)
    args = [year, 0]
    
    result_args = cursor.callproc('GetPlacedStudentsByYear', args)
    total_placed = result_args[1]
    print("This")
    print(result_args[1])

    # Calculate highest, median, and mean CTC
    ctcs = [row[10] for row in rows if row[10] is not None] 

    cursor.execute("SELECT MAX(ctc) FROM students WHERE placedyear = %s", yeart)
    highest_ctc_result = cursor.fetchone()
    highest_ctc = highest_ctc_result[0] if highest_ctc_result else 0

    print("Highest CTC:", highest_ctc)
    median_ctc = sorted(ctcs)[len(ctcs) // 2] if ctcs else 0
    mean_ctc = sum(ctcs) / len(ctcs) if ctcs else 0
    students_with_ctc_gt_1000000 = len([ctc for ctc in ctcs if ctc > 1000000])

    cursor.execute("SELECT * FROM company WHERE yearvisited = %s",yeart)
    rows2 = cursor.fetchall()
    total_companies_visited = len(rows2)


    return total_students, total_placed, total_companies_visited, highest_ctc, median_ctc, mean_ctc, students_with_ctc_gt_1000000



def analysis():   
    years = get_years_from_database()
    year = st.selectbox("Select Year:", sorted(years))
    print(year)
    if year:
        total_students, total_placed, total_companies_visited, highest_ctc, median_ctc, mean_ctc, students_with_ctc_gt_1000000 = filter_data_by_year(year)

        st.write(f"Total number of students in {year}: {total_students}")
        st.write(f"Total number of students placed: {total_placed}")
        st.write(f"Total number of companies visited: {total_companies_visited}")
        st.write(f"Highest CTC: {highest_ctc}")
        st.write(f"Median CTC: {median_ctc}")
        st.write(f"Mean CTC: {mean_ctc}")
        st.write(f"Total number of students with CTC > 1000000: {students_with_ctc_gt_1000000}")

def is_cid_in_database(cid):
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM company WHERE cid = %s"
    cursor.execute(query, (cid,))
    result = cursor.fetchone()
    connection.close()
    return result is not None

def post_jobs():
    connection = get_db_connection()
    cursor = connection.cursor()

    cid = st.text_input("Enter Company ID:")
    jobid = st.text_input("Enter Job ID:")
    deadline = st.date_input("Select Deadline Date:")  
    roles = st.text_input("Enter Role:")
    gender_options = ["male", "female", "any"]
    gender = st.selectbox("Select Gender Requirement:", gender_options)

    description = st.text_area("Enter Job Description:")
    type_option = ['Internship','Fulltime']
    jtype = st.selectbox("Enter Job Type:",type_option)
    requirement = st.text_input("Enter job requirement:")

    if st.button("Add"):
        if not is_valid_integer(jobid):
            st.error("Invalid Job ID")

        elif not is_cid_in_database(cid):
            st.error("Company Id not registered")

        elif cid and jobid and deadline and roles and gender and description and jtype and requirement:
            try:
                cursor.execute("INSERT INTO job (cid ,job_id ,deadline ,roles ,gender_requirement ,descriptions , jtype ,requirement) VALUES (%s, %s, %s, %s, %s, %s, %s,%s)",(cid ,jobid ,deadline ,roles ,gender ,description , jtype ,requirement))

                connection.commit()
                st.success("Job Posted successfully!")
            except mysql.connector.Error as err:
                st.error("Invalid input %s" %err)
            except Exception as e:
                st.error("Invalid input %s" %err)    


        else:
            st.error("All fields are required!")

    cursor.close()
    connection.close()

def jobs_open():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        today = date.today()
        query = "SELECT * FROM job WHERE deadline >= %s"
        cursor.execute(query, (today,))

        jobs_data = cursor.fetchall()
        if jobs_data:
            st.write("Jobs Open:")
            for job in jobs_data:
                st.write(f"**Job ID:** {job[0]}")
                st.write(f"**Job Title:** {job[3]}")
                st.write(f"**Company ID:** {job[1]}")
                st.write(f"**Deadline:** {job[2]}")
                st.write(f"**Gender Requirement:** {job[4]}")
                st.write(f"**Description:** {job[5]}")
                st.write(f"**Job Type:** {job[6]}")
                st.write(f"**Requirement:** {job[7]}")
                st.write("---")  # Add a horizontal line for better separation
        else:
            st.warning("No open jobs with deadline today or later.")

    except mysql.connector.Error as err:
        st.error(f"Error: {err}")

    finally:
        # Close the database connection
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if 'login' not in st.session_state:
    st.session_state.login = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None

def my_applications():
    connection = get_db_connection()
    cursor = connection.cursor()

    st.title("My Applications")


    my_srn = st.text_input("Enter your SRN: ")

    if my_srn:
        if not is_valid_srn(my_srn):
            st.error("SRN is invalid.")
        else:
            try:
                connection = get_db_connection()
                cursor = connection.cursor()

        # Modified query using GROUP_CONCAT to concatenate pass values for each round
                query = """
                    SELECT a.application_id, a.date_applied, a.application_status, a.job_id,
                    GROUP_CONCAT(r.pass_value ORDER BY r.round_id) AS pass_values
                    FROM application a
                    LEFT JOIN rounds r ON a.application_id = r.application_id
                    WHERE a.SRN = %s
                    GROUP BY a.application_id, a.date_applied, a.application_status, a.job_id
                """
                cursor.execute(query, (my_srn,))
                results = cursor.fetchall()

                if results:
            # Display application details and individual pass values for each round
                    for result in results:
                        application_id, date_applied, application_status, job_id, pass_values = result
                        st.write(f"Application ID: {application_id}")
                        st.write(f"Date Applied: {date_applied}")
                        st.write(f"Application Status: {application_status}")
                        st.write(f"Job ID: {job_id}")

                # Split the concatenated pass values into a list
                        pass_values_list = pass_values.split(',')

                # Display pass values for each round
                        for i, pass_value in enumerate(pass_values_list, start=1):
                            st.write(f"Round {i}: {pass_value}")

                        st.write("------------")

                else:
                    st.warning("No applications found for the given SRN.")

            except Exception as e:
                st.error(f"Error: {e}")

            finally:
                if connection:
                    connection.close()

    cursor.close()
    connection.close()                



def faculty_login():
    st.title("Admin Login")
    username = st.text_input("Username", key="faculty_username")
    password = st.text_input("Password", type="password", key='faculty_password_input')

    if st.button("Login"):
        if username == 'admin' and password == '123':
            st.session_state.login = True
            st.session_state.user_type = 'admin'
            st.empty()
        else:
            # Invalid login
            st.error("Invalid username or password. Please try again.")    


def student_login():
    st.title("Student Login")
    username = st.text_input("Username", key="student_username")
    password = st.text_input("Password", type="password", key='student_password_input')

    if st.button("Login"):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Query to fetch student information based on username and password
            query = "SELECT * FROM students WHERE SRN = %s AND password = %s"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()

            if result:
                # Successful login

                st.session_state.login = True
                st.session_state.user_type = 'student'
                st.success("Login successful!")
                st.empty()
            else:
                # Invalid login
                st.error("Invalid username or password. Please try again.")

        except mysql.connector.Error as err:
            st.error(f"Error: {err}")

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

def company_login():
    st.title("Company Login")
    username = st.text_input("Username", key="student_username")
    password = st.text_input("Password", type="password", key='company_password_input')

    if st.button("Login"):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Query to fetch student information based on username and password
            query = "SELECT * FROM company WHERE cid = %s AND password = %s"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()

            if result:
                # Successful login
                st.session_state.login = True
                st.session_state.user_type = 'company'
                st.success("Login successful!")
                st.empty()
            else:
                # Invalid login
                st.error("Invalid username or password. Please try again.")

        except mysql.connector.Error as err:
            st.error(f"Error: {err}")

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()       

def first_page():
    if not st.session_state.login:
        user_type = st.radio("Select user type:", ["Admin", "Student","Company"])
        
        if user_type == "Admin":
            faculty_login()
        elif user_type == "Student":
            student_login()    
        elif user_type == "Company":
            company_login()

    if st.session_state.login:
        if st.session_state.user_type == 'admin':
            admin_page()
        elif st.session_state.user_type == 'student':
            student_page()
        elif st.session_state.user_type == 'company':
            company_page()    

def student_page():
    logo_image = 'pes.png' 
    st.image(logo_image, use_column_width=False, width=200)
    st.subheader("Student Dashboard") 
    choice ="home"
    menu = ["Home","Jobs Posted","Add Application","My Applications","Analysis", "Round"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Welcome to PES University Placement Database")
        
        st.write("Empowering Career Success with Comprehensive Placement Insights")
        st.write("Welcome to the Placement Database, your one-stop resource for comprehensive placement data and insights. Our database empowers students, faculty, and placement officers to make informed decisions regarding career paths, placement opportunities, and recruitment strategies.")
    elif choice == "Jobs Posted":
        st.subheader("Jobs open")
        jobs_open() 
    elif choice == "Add Application":
        add_application() 
    elif choice == "My Applications":
        my_applications()
    elif choice == "Analysis":
        st.subheader("Analysis ")
        analysis()
    elif choice == "Round":
        st.subheader("Round")
        round_success()
    
def company_page():
    logo_image = 'pes.png'  
    st.image(logo_image, use_column_width=False, width=200)
    st.subheader("Company Dashboard")
    choice ="home"
    menu = ["Home","Students","Post a Job","Modify Application Details"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Welcome to PES University Placement Database")
        
        st.write("Empowering Career Success with Comprehensive Placement Insights")
        st.write("Welcome to the Placement Database, your one-stop resource for comprehensive placement data and insights. Our database empowers students, faculty, and placement officers to make informed decisions regarding career paths, placement opportunities, and recruitment strategies.")

    elif choice == "Students":
        show_students()

    elif choice == "Post a Job":
        st.subheader("Post a job")
        post_jobs()

    elif choice == "Modify Application Details":
        st.subheader("Modify Application")
        modify_application_details()

def admin_page():
    logo_image = 'pes.png'  
    st.image(logo_image, use_column_width=False, width=200)
    st.subheader("Admin Dashboard")
    choice ="home"
    menu = ["Home", "Analysis", "Students", "Add Student", "Companies", "Add Company","Round"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Welcome to PES University Placement Database")
        
        st.write("Empowering Career Success with Comprehensive Placement Insights")
        st.write("Welcome to the Placement Database, your one-stop resource for comprehensive placement data and insights. Our database empowers students, faculty, and placement officers to make informed decisions regarding career paths, placement opportunities, and recruitment strategies.")

    elif choice == "Analysis":
        st.subheader("Analysis ")
        analysis()
    elif choice == "Students":
        show_students()
        modify_students()
        delete_student()

    elif choice == "Add Student":
        add_new_student() 
    elif choice == "Add Company":
        st.subheader("Add New Company")
        add_company() 
    elif choice == "Companies":
        view_companies()
    elif choice == "Round":
        st.subheader("Round")
        round_success()

def main():
    first_page()

if __name__ == "__main__":
    main()

