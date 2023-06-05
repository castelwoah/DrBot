from flask import Flask, render_template, request, jsonify, redirect, session, url_for
# from flask_socketio import SocketIO, emit
import openai
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin


# DB 초기화
from pymongo import MongoClient
import certifi
ca = certifi.where()
client = MongoClient('mongodb+srv://amollang97:VJdEb3wQs7SUwiUq@cluster0.kynn6ln.mongodb.net/?retryWrites=true&w=majority', tlsCAFile = ca)
# db 이름 = chatbot
db = client.chatbot



# Set up OpenAI API credentials
openai.api_key = "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"

# Set up the model name
model_engine = "gpt-3.5-turbo"

# set persona
ai_doctor_persona = """
I want you to act as an AI assisted doctor. Your name is 'Dr.Bot'.
I will provide you with details of a patient's symptom, and your task is to use the latest artificial intelligence tools such as medical imaging software and other machine learning programs in order to diagnose the most likely cause of their symptoms.
You should ask details or explanations of patient's pain or injury if you can't get enough information.
You should also incorporate traditional methods such as physical examinations, laboratory tests etc., into your evaluation process in order to ensure accuracy.
You have to announce at the end of the answer that if the pain or symptom last for a long time patients should see a doctor.
Non-medical questions could be answered, but you should recommend that you can answer more properly when medical questions be asked.
"""

# messages 변수 초기화
messages = [{"role": "system", "content": f"{ai_doctor_persona}"}]


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# 파일 불러오기(ex: index.html)
@app.route("/")
def home():
    """홈 화면 출력"""
    print("home")
    return render_template('login.html')


# 사용자 모델 정의
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

users = []

@login_manager.user_loader
def load_user(username):
    # MongoDB에서 사용자 정보 가져오기
    user_data = db.users.find_one({'username': username})
    if user_data:
        user = User(user_data['_id'], username, user_data['password'])
        return user
    return None


# @app.route('/')
# def home():
#     return 'Welcome to the Home Page'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 사용자 인증
        user_data = db.users.find_one({'username': username})
        if user_data and bcrypt.check_password_hash(user_data['password'], password):
            user = User(user_data['_id'], user_data['username'], user_data['password'])
            login_user(user)
            users.append(username)
            return redirect(url_for('chat'))

        return 'Invalid username or password'

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 비밀번호 해싱
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        # 사용자 정보 DB에 저장
        user_data = {'username': username, 'password': hashed_password}
        db.users.insert_one(user_data)


        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# @app.route('/chat')
# @login_required
# def chat():
#     return 'Welcome to the Chat Page'






# 대화 기록 출력부
@app.route("/hist", methods=["GET"])
def chatbot_hist():
    username = users[-1]
    hist = list(db[username].hist.find({}, {'_id': False}))

    for i in hist:
        messages.append(i)

    print("history api activated")

    return jsonify({"history": hist})


# 채팅 실행부
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    """json 형식으로 "question"으로 사용자 입력값을 받아온다.
    DrBot/chatbot/hist DB 경로에 저장한다.
    answer변수에 답변을 저장하고 "answer"키로 값을 전달한다."""

    # DB에 저장된 기록 가져오기
    # username = request.form['username']
    username = users[-1]
    print("사용자:", username)
    if request.method == 'POST':
        question = request.form['question']

        print("질문: ", question)

        messages.append({"role": "user", "content": f"{question}"})

        # 사용자 입력 저장
        doc = {
            "role": "user",
            "content": f"{question}"
        }
        db[username].hist.insert_one(doc)

        answer = get_response(messages)
        print("답변: ", answer)
        messages.append({"role": "assistant", "content": f"{answer}"})

        # 답변 저장
        doc = {
            "role": "assistant",
            "content": f"{answer}"
        }
        db[username].hist.insert_one(doc)

        return jsonify({'answer': answer})

    return render_template('index.html')

# completion 제작 및 반환
def get_response(messages):
    """사용자 입력을 매개변수로 받아 답변을 생성한다.
    return type: string"""
    print("함수호출까지 완료")
    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=messages,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.0,
        top_p=1.0
    )
    return response['choices'][0]['message']['content']





if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)
