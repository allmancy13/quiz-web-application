from flask import Flask, request, render_template
from flask import redirect, url_for, session, escape
from models import User, Teacher, Student
import os

app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return redirect(url_for('register'))

@app.route('/register', methods = ['GET', 'POST'])
def register():

    if 'email' in session:
        session.pop('email', None)

    if request.method == 'GET':
        pass

    msg = None
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')

        user = User()  # create an object of User class
        flag = user.register(first_name, last_name, email, password, user_type)

        if flag:
            session['register_msg'] = "Congratulations! Registration completed successfully."
            session['email'] = email
            session['name'] = first_name
            session['user_type'] = user_type
            if user_type == 'student':
                return redirect(url_for('student_dashboard', choice = 'ViewQuizes'))
            elif user_type == 'teacher':
                return redirect(url_for('teacher_dashboard', choice = 'CreateQuiz'))
        else:
            msg = "User already exists."

    return render_template('register.html', msg = msg)

@app.route('/login', methods = ['GET', 'POST'])
def login():

    if 'email' in session:
        session.pop('email', None)

    login_err_msg = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User() # create an object of User class
        flag, first_name, last_name, user_type = user.login(email, password) # call the login method to check authentication
        if flag:
            # create sessions to store username and password and redirect to dashboard page
            session['email'] = email
            session['name'] = first_name.title()
            session['user_type'] = user_type
            if user_type == 'student':
                 return redirect(url_for('student_dashboard', choice = 'ViewQuizes'))
            elif user_type == 'teacher':
                return redirect(url_for('teacher_dashboard', choice = 'CreateQuiz'))
        else:
            login_err_msg = "Incorrect email or password."

    return render_template('login.html', response = login_err_msg)

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('email', None)
    session.pop('name', None)
    session.pop('user_type', None)
    if 'register_msg' in session:
        session.pop('register_msg', None)

    if 'response' in session:
        session.pop('response', None)

    if 'ViewCreatedQuiz_err_msg' in session:
        session.pop('ViewCreatedQuiz_err_msg', None)

    if 'ViewCreatedQuiz_data' in session:
        session.pop('ViewCreatedQuiz_data', None)

    if 'create_quiz_perm_msg' in session:
        session.pop('create_quiz_perm_msg',None)

    if ('quiz_questions' in session) or ('quiz_details' in session):
        session.pop('quiz_questions', None)
        session.pop('quiz_details', None)

    if ('ViewDetails_quiz_details' in session) or ('ViewDetails_quiz_questions' in session):
        session.pop('ViewDetails_quiz_details', None)
        session.pop('ViewDetails_quiz_questions', None)
    if 'Viewdetails_err_msg'in session:
        session.pop('ViewDetails_err_msg', None)

    return redirect(url_for('login'))




@app.route('/teacher_dashboard/<choice>', methods = ['GET', 'POST'])
def teacher_dashboard(choice):
    if ('email' in session) and session['user_type'] == 'teacher':

        if choice == 'CreateQuiz':

            if 'create_quiz_perm_msg' in session:
                 session.pop('create_quiz_perm_msg', None)

            if request.method == 'POST':
                title = request.form.get('title')
                subject = request.form.get('subject')
                no_questions = request.form.get('noquestions')
                quiz_time = request.form.get('quiz_time')
                email = session['email']

                teacher = Teacher(email) # create an object of Teacher class
                flag = teacher.create_temp_quiz(title, subject, no_questions, quiz_time) # call the create_quiz() method of Teacher class to create the quiz
                if flag:
                    session['create_quiz_msg'] = "Quiz created successfully."
                    session['is_create_temp_quiz'] = 'active'
                    return redirect(url_for('teacher_dashboard', choice='AddQuestions'))
                else:
                    session['create_quiz_msg'] = "Quiz already exists."
                    return redirect(url_for('teacher_dashboard', choice='CreateQuiz'))

        elif choice == 'AddQuestions':

            if not('is_create_temp_quiz' in session):
               return redirect(url_for('teacher_dashboard', choice = 'CreateQuiz'))

            email = session['email']
            teacher = Teacher(email)  # create an object of teacher class
            flag, res = teacher.get_temp_quiz_details() # call the get_temp_quiz_details() method to get details about quiz

            if flag:
                if 'create_quiz_msg' in session:
                    session.pop('create_quiz_msg', None)

                session['quiz_temp_details'] = res
                if request.method == 'POST':
                    question_content = request.form.get('question_content')
                    option1 = request.form.get('option1')
                    option2 = request.form.get('option2')
                    option3 = request.form.get('option3')
                    option4 = request.form.get('option4')
                    answer = request.form.get('answer')

                    temp_quiz_id = res["quiz_id"]

                    no_questions = 1
                    #print("this is temp question")
                    # call the add_temp_question() method to add questions to temp table
                    flag, no_questions = teacher.add_temp_question(temp_quiz_id, question_content, option1, option2, option3, option4, answer)
                    session['question_no'] = no_questions + 1

                    if no_questions == session['quiz_temp_details']['no_questions']:
                        #print("for question 1 perm")
                        # move the quiz to quiz table from quiz_temp table
                        flag, perm_quiz_id = teacher.create_perm_quiz()
                        if flag:
                           # move quiz questions from temp_question table to question table
                           flag2 = teacher.add_perm_question(temp_quiz_id, perm_quiz_id)
                           if flag2:
                               session['create_quiz_perm_msg'] = "Congratulations! Quiz created successfully."
                               session.pop('is_create_temp_quiz', None)
                               session.pop('quiz_temp_details', None)
                               session.pop('question_no', None)
                               return redirect(url_for('teacher_dashboard', choice = 'ViewCreatedQuiz'))
                           else:
                               session['create_quiz_perm_msg'] = "Quiz can't be created because some error in questions. Please create quiz gain."
                               return redirect(url_for('teacher_dashboard', choice = 'CreateQuiz'))
                        else:
                            session['create_quiz_perm_msg'] = "Quiz can't be created due to connection error. Please create another quiz."
                            return redirect(url_for('teacher_dashboard', choice = 'CreateQuiz'))

                        return redirect(url_for('teacher_dashboard', choice = 'ViewCreatedQuiz'))

                    else:
                        return redirect(url_for('teacher_dashboard',choice = 'AddQuestions'))

            else:
                return redirect(url_for('teacher_dashboard', choice = 'CreateQuiz'))

        elif choice == 'ViewCreatedQuiz':
            email = session['email']
            teacher = Teacher(email)
            flag, res = teacher.get_created_quizes()

            if flag:
                session['ViewCreatedQuiz_data'] = res
                if 'ViewCreatedQuiz_err_msg' in session:
                    session.pop('ViewCreatedQuiz_err_msg', None)
            else:
                session['ViewCreatedQuiz_err_msg'] = "You haven't created any quiz yet."

        elif choice == 'DeleteQuiz':
            email = session['email']  # get email address from the session
            quiz_id = request.args.get('quiz_id')  # get the quiz_id from the url
            teacher = Teacher(email)  # create an objecr of Teacher class
            flag = teacher.Delete_Quiz(quiz_id)  # call the DeleteQuiz() method to delete the quiz
            if flag:
                session['teacher_dashboard_DeleteQuiz_msg'] = "Quiz deleted successfully"
                return redirect(url_for('teacher_dashboard', choice = 'ViewCreatedQuiz'))
            else:
                session['teacher_dashboard_DeleteQuiz_msg'] = "Quiz can't be deleted."
                return redirect(url_for('teacher_dashboard', choice = 'ViewCreatedQuiz'))

        elif choice == 'ViewDetails':
            email = session['email']
            quiz_id = request.args.get('quiz_id')
            teacher = Teacher(email)
            flag, quiz_details, quiz_questions = teacher.get_quiz_details(quiz_id)
            if flag:
                session['ViewDetails_quiz_details'] = quiz_details
                session['ViewDetails_quiz_questions'] = quiz_questions
            else:
                session['ViewDetails_err_msg'] = "Sorry, Cann't find details abou the quiz."

        return render_template('teacher-dashboard.html', choice='CreateQuiz')
    else:
        return redirect(url_for('login'))



@app.route('/student_dashboard/<choice>', methods = ['GET', 'POST'])
def student_dashboard(choice):
    if ('email' in session) and (session['user_type'] == 'student'):
        if choice == 'ViewQuizes':
            return redirect(url_for('student_dashboard/ViewQuizes'))
        elif choice == 'TakeQuiz':
            quiz_id = request.args.get('quiz_id')
            return redirect(url_for('student_dashboard/TakeQuiz', quiz_id = quiz_id))
        elif choice == 'SubmitQuiz':
            return redirect(url_for('student_dashboard/SubmitQuiz'))
        elif choice == 'MyQuizes':
            return redirect(url_for('student_dashboard/MyQuizes'))
    else:
        return redirect(url_for('login'))



@app.route('/student_dashboard/ViewQuizes', methods = ['GET', 'POST'])
def student_dashboard_ViewQuizes():
    if not ('email' in session) or not(session['user_type'] == 'student'):
        return redirect(url_for('login'))

    email = session['email']
    student = Student(email)  # create an object of Student class
    flag, all_quizes_rows = student.get_all_quizes()  # call the get_all_quizes() method for getting all the quizes
    return render_template('student-dashboard.html', all_quizes_rows = all_quizes_rows)


@app.route('/student_dashboard/TakeQuiz')
def student_dashboard_TakeQuiz():
    if not ('email' in session) or not(session['user_type'] == 'student'):
        return redirect(url_for('login'))

    quiz_id = request.args.get('quiz_id')
    if not(quiz_id):
        return redirect(url_for('student_dashboard', choice = 'ViewQuizes'))

    email = session['email']
    student = Student(email)  # create an object of Student class
    quiz_details, quiz_questions = student.take_quiz(quiz_id)  # call the take_quiz() method to take quiz
    session['quiz_questions'] = quiz_questions
    session['quiz_details'] = quiz_details

    TakeQuiz_err_msg = None
    if not(quiz_details) or not(quiz_questions):
        TakeQuiz_err_msg = "Quiz you are looking for, does not exist"

    return render_template('student_dashboard_TakeQuiz.html', quiz_details = quiz_details,
                           quiz_questions = quiz_questions, TakeQuiz_err_msg = TakeQuiz_err_msg)


@app.route('/student_dashboard/SubmitQuiz', methods = ['GET', 'POST'])
def student_dashboard_SubmitQuiz():
    if not ('email' in session) or not(session['user_type'] == 'student'):
        return redirect(url_for('login'))

    if not ('quiz_questions' in session) or not ('quiz_details' in session):
        return redirect(url_for('student_dashboard', choice = 'MyQuizes'))

    quiz_questions = []
    student_marks = 0
    total_marks = 0
    email = session['email']

    if request.method == 'POST':
        print("bye")
        quiz_questions = session['quiz_questions']
        quiz_details = session['quiz_details']
        session.pop('quiz_questions', None)
        session.pop('quiz_details', None)

        # get quiz_id from quiz_details
        quiz_id = quiz_details[0]["quiz_id"]
        for quiz_question in quiz_questions:
            # quiz_question = eval(quiz_question)
            total_marks = total_marks + 1  # count total no of questions
            question_id = str(quiz_question["question_id"])  # get question_id to access user anser from form
            student_answer = request.form.get(question_id)   # get actual answer to compare user answer and actual answer
            #print('student answer: ', student_answer)
            if student_answer == str(quiz_question['answer']):
                student_marks = student_marks + 1
        #print("student_marks / total_marks: {0} / {1}".format(student_marks, total_marks))
        student_marks = str(student_marks)
        total_marks = str(total_marks)

        # create an object of Student class
        std = Student(email)
        # call the submit_quiz() method to save student quiz result
        flag = std.submit_quiz(quiz_id, student_marks, total_marks)
        if flag:
            student_dashboard_SubmitQuiz_succ_msg = "Thanks for taking the quiz."
            return render_template("student_dashboard_SubmitQuiz.html",quiz_details = quiz_details, student_dashboard_SubmitQuiz_succ_msg = student_dashboard_SubmitQuiz_succ_msg, student_marks = student_marks, total_marks = total_marks)
        else:
            student_dashboard_SubmitQuiz_err_msg = "You have already taken this quiz."
            return render_template('student_dashboard_SubmitQuiz.html', student_dashboard_SubmitQuiz_err_msg = student_dashboard_SubmitQuiz_err_msg)
    else:
        return redirect(url_for('student_dashboard', choice = 'MyQuizes'))

@app.route("/student_dashboard/MyQuizes")
def student_dashboard_MyQuizes():
    if not('email' in session) or not(session['user_type'] == 'student'):
        return redirect(url_for('login'))

    # get email of student from session
    email = session['email']
    # create an object of Student class
    s = Student(email)
    # call the get_my_quizes() method to get details of all quizes taken
    flag, myquizes = s.get_my_quizes()
    if flag:
        return render_template("student_dashboard_MyQuizes.html", myquizes = myquizes)
    else:
        student_dashboard_MyQuizes_err_msg = "You haven't taken any quiz yet. or quiz taken by you does not exist anymore."
        return render_template("student_dashboard_MyQuizes.html", student_dashboard_MyQuizes_err_msg = student_dashboard_MyQuizes_err_msg)


if __name__ == "__main__":
    app.run()