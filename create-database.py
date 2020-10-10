import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()


#cur.execute("""create table user
       # (user_id integer primary key autoincrement, first_name text not null, last_name text not null,
        #email text not null, password char(50) not null, user_type char(7) not null)""");
#print("table created successfuly.")
#conn.close()


#cur.execute("""create table quiz
            #(quiz_id integer primary key autoincrement, title text not null, subject text not null,
           # no_questions integer not null, quiz_time integer not null, quiz_creator_id integer not null,
          #  foreign key(quiz_creator_id) references user(user_id) )""");

#print("quiz table created successfully.")

#cur.execute("""
         #create table question (question_id integer primary key autoincrement, question_content text not null,
         #option1 text not null, option2 text not null,
         #option3 text not null, option4 text not null, answer integer not null, question_quiz_id integer,
         #foreign key(question_quiz_id) references quiz(quiz_id) )
#""")

#print("question table created successfully.")

#cur.execute("""
  #        create table quiz_temp (quiz_id integer primary key autoincrement ,title text not null, subject text not null, no_questions integer not null,
 #         quiz_time integer not null, quiz_creator_id integer not null )
#""");

# create temp_question table to store questions temporary until all the questions have entered
#cur.execute("""
  #    create table temp_question (question_content text not null, option1 text not null, option2 text not null,
 #     option3 text not null, option4 text not null, answer integer not null, question_quiz_id integer not null)
#""")

#cur.execute("""
 #    create table myquiz (myquiz_id integer primary key autoincrement, quiz_id integer not null, user_id integer not null,
  #   student_marks integer not null, total_marks integer not null,
   #  foreign key(quiz_id) references quiz(quiz_id), foreign key(user_id) references user(user_id) )
#""")

#res = cur.execute("select name from sqlite_master where type = 'table' ");
#cur.execute("delete from quiz")
#conn.commit()
r = cur.execute("select * from question")
conn.commit()
print(r.fetchall())

print("table quiz_temp created successfully.")
conn.close()