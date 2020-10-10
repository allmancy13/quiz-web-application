import sqlite3

class User():
    def __init__(self):
        self.first_name = None
        self.last_name = None
        self.email = None
        self.password = None
        self.user_type = None
        self.flag = None  # to store the return value for the functions

    def register(self, first_name, last_name, email, password, user_type):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.user_type = user_type

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("select * from user where email = ? ", (self.email,))
        if cur.fetchall():
            self.flag = False
        else:
            # insert row into the user table
            cur.execute("insert into user (first_name, last_name, email, password, user_type) \
                    values (?, ?, ?, ?, ?)", (self.first_name, self.last_name, self.email, self.password, self.user_type));
            conn.commit()
            self.flag = True

        conn.close()
        return self.flag

    def login(self, email, password):
        self.email = email
        self.password = password

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        res = cur.execute("select first_name, last_name, user_type from user where email = ? and password = ?", (self.email, self.password,))
        rows = res.fetchall()
        if rows:
            self.flag = True
            self.first_name = rows[0][0]
            self.last_name = rows[0][1]
            self.user_type = rows[0][2]
            conn.close()
            return self.flag, self.first_name, self.last_name, self.user_type
        else:
            self.flag = False
            conn.close()
            return self.flag, self.first_name, self.last_name, self.user_type

    def logout(self):
        pass

    def forgot_password(self):
        pass


 # create Teacher class

class Teacher(User):
    def __init__(self, email):
        self.title = None
        self.subject = None
        self.no_questions = None
        self.quiz_time = None
        self.user_id = None
        self.email = email


        # get user id
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        res = cur.execute("select user_id from user where email = ?", (self.email, ))
        row = res.fetchall()

        if row:
            self.user_id = row[0][0]
        else:
            print("User does not exist")

    def create_temp_quiz(self, title, subject, no_questions, quiz_time):
        """ create temporary quiz until all the details have been filled properly """
        self.title = title.lower()
        self.subject = subject
        self.no_questions = no_questions
        self.quiz_time = quiz_time

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        # check if quiz already exist with this name
        res = cur.execute("select * from quiz where title = ? and quiz_creator_id = ?", (self.title, self.user_id,))
        rows = res.fetchall()
        if rows:
            self.flag = False
        else:
            cur.execute("delete from quiz_temp where quiz_creator_id = ?", (self.user_id, ))
            conn.commit()
            # store the quiz into quiz_temp table
            cur.execute("insert into quiz_temp (title, subject, no_questions, quiz_time, quiz_creator_id) \
                        values (?, ?, ?, ?, ?)", (self.title, self.subject, self.no_questions, self.quiz_time, self.user_id))
            conn.commit()
            self.flag = True

        conn.close()

        return self.flag

    def get_temp_quiz_details(self):
        """ Get temporary quiz details to show on the add questions page """
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        self.quiz_id = None

        # get temp quiz details
        res = cur.execute("select * from quiz_temp where quiz_creator_id = ?", (self.user_id,))
        row = res.fetchall()
        if row:
            self.quiz_id = row[0][0]
            self.title = row[0][1]
            self.subject = row[0][2]
            self.no_questions = row[0][3]
            self.quiz_time = row[0][4]
            self.flag = True
        else:
            self.flag = False

        res = {
            "quiz_id": self.quiz_id,
            "title": self.title.title(),
            "subject": self.subject.title(),
            "no_questions": self.no_questions,
            "quiz_time": self.quiz_time,
        }

        conn.close()

        return self.flag, res



    def add_temp_question(self, quiz_id, question_content, option1, option2, option3, option4, answer):
        """ add questions to temporary table until user have entered all the questions """
        self.quiz_id = quiz_id
        self.question_content  = question_content
        self.option1 = option1
        self.option2 = option2
        self.option3 = option3
        self.option4 = option4
        self.answer = answer

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        # remove all temporary questions if exists for any other quiz_id
        cur.execute("delete from temp_question where question_quiz_id != ?", (self.quiz_id,))
        conn.commit()

        # insert question to temp_question table
        cur.execute("insert into temp_question (question_content, option1, option2, option3, \
        option4, answer, question_quiz_id) values (?, ?, ?, ?, ?, ?, ?)", (self.question_content, self.option1, self.option2,
                                                      self.option3, self.option4, self.answer, self.quiz_id))

        conn.commit()
        # get number of rows in temp_question table
        res = cur.execute("select count(*) from temp_question where question_quiz_id = ?", (self.quiz_id, ))
        rows = res.fetchall()
        if rows:
            self.no_questions = rows[0][0]
        else:
            self.no_questions = 0

        conn.close()

        return True, self.no_questions


    def create_perm_quiz(self):
        """ Move quiz from quiz_temp to quiz table """
        self.perm_quiz_id = None
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        res = cur.execute("select * from quiz_temp where quiz_creator_id = ?", (self.user_id,))
        row = res.fetchall()
        if row:
            cur.execute("insert into quiz (title, subject, no_questions, quiz_time, quiz_creator_id) \
                        values (?, ?, ?, ?, ?)", (row[0][1], row[0][2], row[0][3], row[0][4], row[0][5]))
            conn.commit()
            # truncate the quiz_temp table
            cur.execute("delete from quiz_temp")
            conn.commit()
            # get quiz id of the permanent quiz
            rs = cur.execute("select * from quiz where quiz_creator_id = ? order by quiz_id desc",(self.user_id, ))
            r = rs.fetchall()
            self.perm_quiz_id = r[0][0]
            self.flag = True
        else:
            self.flag = False

        conn.close()

        return self.flag, self.perm_quiz_id

    def add_perm_question(self, temp_quiz_id, perm_quiz_id):
        """ move questions from temp_question to question"""
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        self.temp_quiz_id = temp_quiz_id
        self.perm_quiz_id = perm_quiz_id

        # get questions from temp_question table
        res = cur.execute("select * from temp_question where question_quiz_id = ?", (self.temp_quiz_id,))
        rows = res.fetchall()
       # print(rows)
        if rows:
            for row in rows:
                #print(row)
                # insert each question into question table
                cur.execute("insert into question (question_content, option1, option2, option3, option4, answer, \
                            question_quiz_id) values (?, ?, ?, ?, ?, ?, ?)",
                            (row[0], row[1], row[2], row[3], row[4], row[5], self.perm_quiz_id))
                #r = cur.execute("select * from question where question_quiz_id = ?", (self.perm_quiz_id, ))
                #print(r.fetchall())
                conn.commit()
            # truncate the temp_question table
            cur.execute("delete from temp_question")
            conn.commit()
            self.flag = True
        else:
            self.flag = False

        conn.close()

        return self.flag

    def get_created_quizes(self):
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        res = cur.execute("select * from quiz where quiz_creator_id = ? order by quiz_id desc", (self.user_id, ))
        rows = res.fetchall()
        if rows:
            self.flag = True
        else:
            self.flag = False

        conn.close()

        return self.flag, rows

    def Delete_Quiz(self, quiz_id):
        """Delete the quiz permanently"""
        self.quiz_id = quiz_id

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        res = cur.execute("delete from quiz where quiz_id = ? and quiz_creator_id = ?", (self.quiz_id, self.user_id,))
        conn.commit()
        cur.execute("delete from question where question_quiz_id = ?", (self.quiz_id,))
        conn.commit()
        cur.execute("delete from myquiz where quiz_id = ?", (self.quiz_id, ))
        conn.commit()
        if res:
            self.flag = True
        else:
            self.flag = False

        conn.close()

        return self.flag

    def get_quiz_details(self, quiz_id):
        """ Get the details about the quiz """
        self.quiz_id = quiz_id
        self.quiz_details = None

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        res = cur.execute("select * from quiz where quiz_id = ?", (self.quiz_id, ))
        row = res.fetchall()
        #quiz_details = {}
        quiz_questions = []
        if row:
            self.title = row[0][1]
            self.subject = row[0][2]
            self.no_questions = row[0][3]
            self.quiz_time = row[0][4]

            self.quiz_details = {
                "quiz_id": self.quiz_id,
                "title": self.title.title(),
                "subject": self.subject.title(),
                "no_questions": self.no_questions,
                "quiz_time": self.quiz_time
            }

            # get quiz questions
            res = cur.execute("select * from question where question_quiz_id = ?", (self.quiz_id,))
            rows = res.fetchall()
            i = 0
            if rows:
                for row in rows:
                    i = i + 1
                    self.question_content = row[1]
                    self.option1 = row[2]
                    self.option2 = row[3]
                    self.option3 = row[4]
                    self.option4 = row[5]
                    self.answer = row[6]

                    question = {
                        "question_no": i,
                        "question_content": self.question_content,
                        "option1": self.option1,
                        "option2": self.option2,
                        "option3": self.option3,
                        "option4": self.option4,
                        "answer": self.answer
                    }
                    quiz_questions.append(question)
                self.flag = True
            else:
                self.flag = False
        else:
            self.flag = False

        return self.flag, self.quiz_details, quiz_questions








# create Student class
class Student(User):

    def __init__(self, email):
        self.email = email
        self.quiz_id = None
        self.title = None
        self.subject = None
        self.no_questions = None
        self.quiz_time = None
        self.quiz_creator_id = None
        self.creator_name = None

        self.question_content = None
        self.option1 = None
        self.option2 = None
        self.option3 = None
        self.option4 = None
        self.answer = None

    def get_all_quizes(self):
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        res = cur.execute("select * from quiz order by quiz_id desc")
        rows = res.fetchall()
        data = []
        self.creator_name = None
        if rows:
            for row in rows:
                self.quiz_id = row[0]
                self.title = row[1]
                self.subject = row[2]
                self.no_questions = row[3]
                self.quiz_time = row[4]
                self.quiz_creator_id = row[5]

                creator_names = cur.execute("select first_name, last_name from user where user_id = ?", (self.quiz_creator_id, ))
                names = creator_names.fetchall()
                for name in names:
                    self.creator_name = name[0].title() + " " + name[1].title()

                data_record = {
                    "quiz_id": self.quiz_id,
                    "title": self.title.title(),
                    "subject": self.subject.title(),
                    "no_questions": self.no_questions,
                    "quiz_time": self.quiz_time,
                    "creator_name": self.creator_name
                }
                data.append(data_record)
            self.flag = True
        else:
            self.flag = False

        conn.close()
        return self.flag, data

    def take_quiz(self, quiz_id):
        self.quiz_id = quiz_id
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        # get quiz details from quiz table
        quiz_details = []
        res = cur.execute("select * from quiz where quiz_id = ?", (self.quiz_id, ))
        rows = res.fetchall()
       # print(rows)
        for row in rows:
            self.title = row[1]
            self.subject = row[2]
            self.no_questions = row[3]
            self.quiz_time = row[4]
            self.quiz_creator_id = row[5]

            # get name of quiz creator from quiz_creator_id
            creator_names = cur.execute("select first_name, last_name from user where user_id = ?",
                                        (self.quiz_creator_id,))
            names = creator_names.fetchall()
            for name in names:
                self.creator_name = name[0].title() + " " + name[1].title()


            quiz_detail = {
                "quiz_id": self.quiz_id,
                "title": self.title.title(),
                "subject": self.subject.title(),
                "no_questions": self.no_questions,
                "quiz_time": self.quiz_time,
                "creator_name": self.creator_name
            }
            quiz_details.append(quiz_detail)

        # get all the questions of the quiz
        quiz_questions= []
        res = cur.execute("select * from question where question_quiz_id = ?", (self.quiz_id, ))
        rows = res.fetchall()
        #print(rows)
        i = 0
        for row in rows:
            i = i + 1
            self.question_id = row[0]
            self.question_content = row[1]
            self.option1 = row[2]
            self.option2 = row[3]
            self.option3 = row[4]
            self.option4 = row[5]
            self.answer = row[6]
            self.quiz_id = row[7]
            quiz_question = {
                "question_no": i,
                "question_content": self.question_content,
                "option1": self.option1,
                "option2": self.option2,
                "option3": self.option3,
                "option4": self.option4,
                "answer": self.answer,
                "question_id": self.question_id,
                "quiz_id": self.quiz_id
            }
            quiz_questions.append(quiz_question)


        return quiz_details, quiz_questions


    def submit_quiz(self, quiz_id, student_marks, total_marks):
        self.quiz_id = quiz_id
        self.student_marks = student_marks
        self.total_marks = total_marks

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        # get user_id from user table
        res = cur.execute("select user_id from user where email = ?", (self.email,))
        rows = res.fetchall()
        self.user_id = rows[0][0]

        # check if user has already taken the quiz
        res = cur.execute("select * from myquiz where quiz_id = ? and user_id = ?", (self.quiz_id, self.user_id,))
        rows = res.fetchall()
        if rows:
            self.flag = False
        else:
           # insert data into myquiz table
           cur.execute("insert into myquiz (quiz_id, user_id, student_marks, total_marks) values\
                       (?,?,?,?)", (self.quiz_id, self.user_id, self.student_marks, self.total_marks))
           conn.commit()
           self.flag = True

        conn.close()
        return self.flag


    def get_my_quizes(self):
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        # get user_id from user table
        res = cur.execute("select user_id from user where email = ?", (self.email,))
        rows = res.fetchall()
        self.user_id = rows[0][0]

        # get all quizes from myquiz for this user_id
        res = cur.execute("select * from myquiz where user_id = ?", (self.user_id,))
        rows = res.fetchall()

        myquizes = []

        if rows:
            for row in rows:
                self.myquiz_id = row[0]
                self.quiz_id = row[1]
                self.student_marks = row[3]
                self.total_marks = row[4]

                # get quiz details from quiz table
                res = cur.execute("select * from quiz where quiz_id = ?", (self.quiz_id, ))
                quiz_details = res.fetchall()
                for quiz_detail in quiz_details:
                    self.title = quiz_detail[1]
                    self.subject = quiz_detail[2]
                    self.no_questions = quiz_detail[3]
                    self.quiz_time = quiz_detail[4]

                myquiz = {
                    "myquiz_id": self.myquiz_id,
                    "student_marks": self.student_marks,
                    "total_marks": self.total_marks,
                    "quiz_id": self.quiz_id,
                    "title":self.title.title(),
                    "subject": self.subject.title(),
                    "no_questions": self.no_questions,
                    "quiz_time": self.quiz_time
                }
                myquizes.append(myquiz)

            self.flag = True

        else:
            self.flag = False

        return self.flag, myquizes



s = Student('ankur@gmail.com')
s.take_quiz(21)