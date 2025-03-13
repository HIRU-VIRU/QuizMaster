from flask import Flask, render_template,request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime,date
import uuid
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
from sqlalchemy import extract
import matplotlib.pyplot as plt


curr_dir=os.path.abspath(os.path.dirname(__file__))

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///QUIZMASTER.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
app.config['SECRET_KEY']='secret_key'
app.config["UPLOAD_FOLDER"]= os.path.join(curr_dir, 'static','imgs')

db=SQLAlchemy()
db.init_app(app)
app.app_context().push()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    fullname = db.Column(db.String(255), nullable=False)
    qualification = db.Column(db.String(255), nullable=False)
    dob = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)
    score_list = db.relationship('Score', back_populates='user_name', cascade='all, delete-orphan')


class Subject(db.Model):
    __tablename__= 'subject'
    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(255), unique=True, nullable=False)
    description= db.Column(db.String(255), nullable=False)
    chapter_list= db.relationship('Chapter',back_populates='subject_name',cascade='all, delete-orphan')


class Chapter(db.Model):
    __tablename__= 'chapter'
    id=db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(255), nullable=False)
    description= db.Column(db.String(255), nullable=False)
    subject_id= db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    subject_name= db.relationship('Subject',back_populates='chapter_list')
    quiz_list= db.relationship('Quiz',back_populates='chap_name',cascade='all, delete-orphan')

class Quiz(db.Model):
    __tablename__= 'quiz'
    id=db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)  
    date_of_quiz= db.Column(db.String(255), nullable=False)
    time_duration= db.Column(db.Integer, nullable=False)
    remarks= db.Column(db.String(255), nullable=False)  
    chapter_id= db.Column(db.String(255), db.ForeignKey("chapter.id"), nullable=False)
    chap_name= db.relationship('Chapter',back_populates='quiz_list')
    question_list= db.relationship('Question',back_populates='quiz_name',cascade='all, delete-orphan')
    score_list= db.relationship('Score',back_populates='quiz_name',cascade='all, delete-orphan')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_statement = db.Column(db.String(255), nullable=False)
    option1 = db.Column(db.String(255), nullable=False)
    option2 = db.Column(db.String(255), nullable=False)
    option3 = db.Column(db.String(255), nullable=False)
    option4 = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(255), nullable=False)  # Store actual answer text
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    quiz_name = db.relationship('Quiz', back_populates='question_list')


class Score(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    time_stamp= db.Column(db.String(255), nullable=False)
    score= db.Column(db.Integer, nullable=False)
    user_id= db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quiz_id= db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    quiz_name=db.relationship('Quiz',back_populates='score_list')
    user_name= db.relationship('User',back_populates='score_list')

def create_admin():
    admin_user = User.query.filter(User.is_admin == True).first()
    if not admin_user:
        admin = User(username='admin', password='admin', email='admin@gmail.com', fullname='Admin', qualification='bsc', dob='1990-01-01', is_admin=True)
        db.session.add(admin)
        db.session.commit()

db.create_all()
create_admin()

@app.route('/')
def index():
    
    return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            if user.is_admin:

                session['admin_id']= user.id
                session['is_admin']= user.is_admin
                flash('successfully logged in', 'success')
                return redirect('/admin')
            else:
                session['user_id']= user.id
                session['is_admin']= user.is_admin
                flash('successfully logged in', 'success')
                return redirect('/dashboard')
        else:
            flash('Invalid username or password', 'error')
            return redirect('/login')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        fullname = request.form.get('fullname')
        qualification = request.form.get('qualification')
        dob = request.form.get('dob')
        user = User(username=username, email=email, password=password, fullname=fullname, qualification=qualification, dob=dob, is_admin=False)
        db.session.add(user)
        db.session.commit()
        flash('User registered successfully', 'success')
        return redirect('/login')
  
@app.route('/admin', methods=['POST', 'GET'])
def admin_dashboard():
    if session.get('is_admin'):
        user=User.query.filter_by(id=session['admin_id']).first()
        subjects = Subject.query.all()
        return render_template('admin_dashboard.html',all_subjects=subjects,user=user)
    return redirect('login')


@app.route('/create_subject', methods=['POST', 'GET'])
def create_subject():
    if session.get('is_admin'):
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            subject = Subject(name=name, description=description)
            db.session.add(subject)
            db.session.commit()
            return redirect('/admin')
        else:
            return render_template('create_subject.html')
    return redirect('login')

@app.route('/edit_subject/<int:subject_id>', methods=['POST', 'GET'])
def edit_subject(subject_id):
    if session.get('is_admin'):
        subject = Subject.query.filter_by(id=subject_id).first()
        if not subject:
            flash('Subject not found', 'error')
            return redirect('/admin')
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            # subject = Subject(name=name, description=description)
            subject.name = name
            subject.description = description
            db.session.commit()
            return redirect('/admin')
        else:
            return render_template('edit_subject.html', subject=subject)
    return redirect('login')

@app.route('/view_subject/<int:subject_id>', methods=['POST', 'GET'])
def view_subject(subject_id):
    if session.get('is_admin'):
        subject = Subject.query.filter_by(id=subject_id).first()
        chapters=Chapter.query.filter_by(subject_id=subject_id).all()
        return render_template('view_subject.html',subject=subject,all_chapters=chapters)
    return redirect('login')

@app.route('/delete_subject/<int:subject_id>', methods=['POST', 'GET'])
def delete_subject(subject_id):
    if session.get('is_admin'):
        subject = Subject.query.filter_by(id=subject_id).first()
        if not subject:
            flash('Subject not found', 'error')
            return redirect('/admin')
        db.session.delete(subject)
        db.session.commit()
        return redirect(f'/admin')
    return redirect('login')

@app.route('/logout',methods=['POST', 'GET'])
def logout():
    session.clear()
    return redirect('/login')


#CRUD : subject
@app.route('/create_chapter/<int:subject_id>', methods=['POST', 'GET'])
def create_chapter(subject_id):
    if session.get('is_admin'):
        subject=Subject.query.filter_by(id=subject_id).first()
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            new_chapter = Chapter(name=name, description=description,subject_id=subject_id)
            db.session.add(new_chapter)
            db.session.commit()
            return redirect(f'/view_subject/{subject.id}')
        else:
            return render_template('create_chapter.html',subject_id=subject_id)
    return redirect('login')


@app.route('/edit_chapter/<int:chapter_id>', methods=['POST', 'GET'])
def edit_chapter(chapter_id):
    if session.get('is_admin'):
        chapter=Chapter.query.filter_by(id=chapter_id).first()
        if not chapter:
            return redirect('/admin')
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            chapter.name=name
            chapter.description=description
            db.session.commit()
            return redirect(f'/view_subject/{chapter.subject_id}')
        else:
            return render_template('edit_chapter.html', chapter=chapter)
    return redirect('login')

@app.route('/delete_chapter/<int:chapter_id>', methods=['POST', 'GET'])
def delete_chapter(chapter_id):
    if session.get('is_admin'):
        chapter = Chapter.query.filter_by(id=chapter_id).first()
        if not chapter:
            flash('chapter not found', 'error')
            return redirect('/admin')
        db.session.delete(chapter)
        db.session.commit()
        return redirect(f'/view_subject/{chapter.subject_id}')
    return redirect('login')

@app.route('/view_chapter/<int:chapter_id>', methods=['POST', 'GET'])
def view_chapter(chapter_id):
    if session.get('is_admin'):
        chapters=Chapter.query.filter_by(id=chapter_id).first()
        quizs=Quiz.query.filter_by(chapter_id=chapter_id).all()
        return render_template('view_chapter.html',chapter=chapters,quizs=quizs)
    return redirect('login')




#CRUD : Quiz
@app.route('/create_quiz/<int:chapter_id>', methods=['POST', 'GET'])
def create_quiz(chapter_id):
    if session.get('is_admin'):
        chapter=Chapter.query.filter_by(id=chapter_id).first()
        if request.method == 'POST':
            name= request.form['name'] 
            date_of_quiz = request.form.get('date_of_quiz')
            time_duration = request.form.get('time_duration')
            remarks = request.form.get('remarks')
            new_quiz = Quiz(name=name,date_of_quiz=date_of_quiz, time_duration=time_duration, remarks=remarks,chapter_id=chapter_id)
            doq= datetime.strptime(date_of_quiz, '%Y-%m-%d').date()
            toq= datetime.strptime(time_duration, '%H:%M').time()
            db.session.add(new_quiz)
            db.session.commit()
            return redirect(f'/view_chapter/{chapter.id}') 
        else:
            return render_template('create_quiz.html',chapter_id=chapter_id)
    return redirect('login')




@app.route('/edit_quiz/<int:quiz_id>', methods=['POST', 'GET'])
def edit_quiz(quiz_id):
    if session.get('is_admin'):
        quiz=Quiz.query.filter_by(id=quiz_id).first()
        chapter = Chapter.query.filter_by(id=quiz.chapter_id).first()
        if not quiz:
            return redirect('/admin')
        if request.method == 'POST':
            name = request.form.get('name')
            date_of_quiz = request.form.get('date_of_quiz')
            time_duration = request.form.get('time_duration')
            remarks = request.form.get('remarks')
            if date_of_quiz:  
                doq = datetime.strptime(date_of_quiz, '%Y-%m-%d').date()
            else:
                doq = None 

            quiz.name=name
            quiz.date_of_quiz=doq
            quiz.time_duration=time_duration
            quiz.remarks=remarks
            db.session.commit()
            return redirect(f'/view_chapter/{quiz.chapter_id}')
        else:
            return render_template('edit_quiz.html', quiz=quiz)
    return redirect('login')

@app.route('/delete_quiz/<int:quiz_id>', methods=['POST', 'GET'])
def delete_quiz(quiz_id):
    if session.get('is_admin'):
        quiz = Quiz.query.filter_by(id=quiz_id).first()
        if not quiz:
            flash('quiz not found', 'error')
            return redirect('/admin')
        db.session.delete(quiz)
        db.session.commit()
        return redirect(f'/view_chapter/{quiz.chapter_id}')
    return redirect('login')

@app.route('/view_quiz/<int:quiz_id>', methods=['POST', 'GET'])
def view_quiz(quiz_id):
    if session.get('is_admin'):
        quiz=Quiz.query.filter_by(id=quiz_id).first()
        questions=Question.query.filter_by(quiz_id=quiz_id).all()
        return render_template('view_quiz.html',quiz=quiz,questions=questions)
    return redirect('login')

# #CRUD OPERATIONS QUESIONS:
@app.route('/create_question/<int:quiz_id>', methods=['POST', 'GET'])
def create_question(quiz_id):
    if session.get('is_admin'):
        quiz= Quiz.query.filter_by(id=quiz_id).first()
        if request.method == 'POST':
            # id = str(uuid.uuid4()) 
            question_statement=request.form.get('question_statement')
            option1=request.form.get('option1')
            option2=request.form.get('option2')
            option3=request.form.get('option3')
            option4=request.form.get('option4')
            answer=request.form.get('answer')
            if None in [question_statement, option1, option2, option3, option4, answer]:
                return "Error: Some form fields are missing.", 400
            new_question = Question(question_statement=question_statement, option1=option1, option2=option2, option3=option3, option4=option4, answer=answer, quiz_id=quiz_id)
            db.session.add(new_question)
            db.session.commit()
            return redirect(f'/view_quiz/{quiz.id}')
        else:
            return render_template('create_question.html', quiz_id=quiz_id)
    return redirect('login')
@app.route('/delete_question/<int:question_id>', methods=['POST', 'GET'])
def delete_question(question_id):
    if session.get('is_admin'):  # Ensure only admins can delete
        flash("Unauthorized access", "error")
        return redirect('/dashboard')

    question = Question.query.filter_by(id=question_id).first()

    if not question:
        flash("Question not found", "error")
        return redirect('/dashboard')

    quiz_id = question.quiz_id  # Store quiz_id before deletion
    db.session.delete(question)
    db.session.commit()

    flash("Question deleted successfully", "success")
    return redirect(f'/view_quiz/{quiz_id}')


@app.route('/edit_question/<int:question_id>', methods=['POST', 'GET'])
def edit_question(question_id):
    if session.get('is_admin'):
        question=Question.query.filter_by(id=question_id).first()
        quiz = Quiz.query.filter_by(id=question.quiz_id).first()
        if not question:
            return redirect('/admin')
        if request.method == 'POST':
            question_statement = request.form.get('question_statement')
            option1= request.form.get('option1')
            option2 = request.form.get('option2')
            option3 = request.form.get('option3')
            option4 = request.form.get('option4')
            answer = request.form.get('answer')

            question.question_statement=question_statement
            question.option1=option1
            question.option2=option2
            question.option3=option3
            question.option4=option4
            question.answer=answer
            db.session.commit()
            return redirect(f'/view_quiz/{quiz.id}')
        else:
            return render_template('edit_question.html', question=question)
    return redirect('login')


@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    if 'user_id' in session:
        quizzes=Quiz.query.all()
        user=User.query.filter_by(id=session['user_id']).first()
        return render_template('user_dashboard.html',quizzes=quizzes,user=user)
    return redirect('/login')

@app.route('/start_quiz/<int:quiz_id>')
def start_quiz(quiz_id):
    if 'user_id' in session:
        quiz= Quiz.query.filter_by(id=quiz_id).first()
        questions=Question.query.filter_by(quiz_id=quiz_id).all()
        if datetime.strptime(quiz.date_of_quiz, '%Y-%m-%d').date() > date.today() :
            flash("This quiz has not started yet",'info')
            return redirect('/dashboard')

        if len(questions)==0:
            flash("No questions found fromm this quiz",'info')
            return redirect('/dashboard')
        session['timestamp']=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return redirect(f'/quiz/{quiz_id}')
    return redirect("/login")

@app.route('/quiz/<int:quiz_id>',methods=['GET', 'POST'])
def quiz_page(quiz_id):
    if 'user_id' in session:
        quiz= Quiz.query.filter_by(id=quiz_id).first()
        questions=Question.query.filter_by(quiz_id=quiz_id).all()
        user=User.query.filter_by(id=session['user_id']).first()
        return render_template('quiz.html',questions=questions, quiz=quiz, user=user)
    return redirect('/login')
    
@app.route('/submit_quiz/<int:quiz_id>', methods=['POST'])
def submit_quiz(quiz_id):
    if 'user_id' in session:
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        user = User.query.filter_by(id=session['user_id']).first()
        score = 0

        for question in questions:
            selected_answer = request.form.get(f"question_{question.id}")  # Get user's selected answer
            
            if selected_answer:  
                selected_option_key = ""  # Store which option was chosen
                
                # Find which option was selected based on its text value
                if selected_answer == question.option1:
                    selected_option_key = "option1"
                elif selected_answer == question.option2:
                    selected_option_key = "option2"
                elif selected_answer == question.option3:
                    selected_option_key = "option3"
                elif selected_answer == question.option4:
                    selected_option_key = "option4"

                # Now compare the stored option key (option1, option2, etc.) with the correct answer
                if selected_option_key == question.answer:
                    score += 1

        # Store the score in the database
        new_score = Score(user_id=user.id, quiz_id=quiz_id, score=score, time_stamp=session.get('timestamp', ''))
        db.session.add(new_score)
        db.session.commit()

        return render_template('result.html', score=score, user=user, total=len(questions))

    return redirect("/login")
@app.route("/dashboard/history")
def user_history():
    if 'user_id' in session:
        user=User.query.filter_by(id=session["user_id"]).first()
        scores=Score.query.filter_by(user_id=user.id).all()
        return render_template('history.html',scores=scores,user=user)
    return redirect("/login")


@app.route('/admin/search', methods=['GET'])
def admin_search():
    if "admin_id" in session:
        search_query = request.args.get('search_query', '').strip()
        
        if not search_query:  
            return redirect('/admin')

        users = User.query.filter(User.username.ilike(f'%{search_query}%')).all()
        subjects = Subject.query.filter(Subject.name.ilike(f'%{search_query}%')).all()
        chapters = Chapter.query.filter(Chapter.name.ilike(f'%{search_query}%')).all()
        quizs = Quiz.query.filter(Quiz.name.ilike(f'%{search_query}%')).all()
        
        return render_template('admin_search.html', users=users, subjects=subjects, chapters=chapters, quizs=quizs)

    return redirect("/login")

@app.route('/admin_summary')
def admin_summary():
    if 'admin_id' in session:
        # Fetch data
        users = User.query.all()
        subjects = Subject.query.all()
        chapters = Chapter.query.all()

        # Month-wise quiz data
        month_wise_quizzes = (
            db.session.query(extract('month', Quiz.date_of_quiz).label('month'), 
                             db.func.count(Quiz.id).label('count'))
            .group_by(extract('month', Quiz.date_of_quiz))
            .all()
        )
        month_data = {str(q.month): q.count for q in month_wise_quizzes}

        # Subject-wise quiz data
        subject_wise_quizzes = (
            db.session.query(Subject.name.label('subject'), 
                             db.func.count(Quiz.id).label('count'))
            .join(Chapter, Subject.id == Chapter.subject_id)
            .join(Quiz, Chapter.id == Quiz.chapter_id)
            .group_by(Subject.name)
            .all()
        )
        subject_data = {q.subject: q.count for q in subject_wise_quizzes}

        quiz_scores = (
        db.session.query(
        Quiz.name.label('quiz'),
        (db.func.avg(Score.score) / db.func.max(Score.score) * 100).label('average_percentage')
        )
        .join(Score, Quiz.id == Score.quiz_id)
        .group_by(Quiz.name)
        .all()
        )
        score_data = {q.quiz: round(q.average_percentage, 2) for q in quiz_scores}







        return render_template(
            'admin_summary.html',
            users=users,
            subjects=subjects,
            chapters=chapters,
            month_data=month_data,
            subject_data=subject_data,
            score_data=score_data
        )
    return redirect("/login")



if __name__ == '__main__':
    app.run(debug=True)