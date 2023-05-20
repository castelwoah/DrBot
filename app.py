from flask import Flask, render_template, request, jsonify
import openai
# import time

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
messages = [{"role" : "system", "content" : f"{ai_doctor_persona}"}]


app = Flask(__name__)

# welcome message
# @app.route("/")
# def welcomeMessage():
#     welcome = '안녕하세요, Dr.Bot입니다. 의료 치료에 대한 권장 사항을 제공하는 것을 포함하여 다양한 작업을 수행할 수 있습니다. 저는 물리적인 몸이나 의료 학위를 가지고 있지 않지만, 연구와 일반적인 의료 관행을 기반으로 정보를 제공할 수 있습니다. 제가 제공하는 권장 사항은 면허를 받은 의료 전문가의 조언을 대체해서는 안 됩니다.'
#     return welcome

# 파일 불러오기(ex: index.html)
@app.route("/")
def home():
    return render_template('index.html')



@app.route('/answer', methods=['POST'])
def get_answer():
    question = request.form['question']

    messages.append({"role": "user", "content": f"{question}"})
    answer = get_response(messages)

    db.test.insert_one(messages[len(messages)-1])
    messages.append({"role": "assistant", "content": f"{answer}"})
    db.test.insert_one(messages[len(messages)-1])

    return jsonify({'answer': answer})

# completion 제작 및 반환
def get_response(messages):
    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=messages,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.0,
        top_p=1.0
    )

    return response.choices[0].message["content"].strip()


# 대화 기록 출력부
@app.route("/chatbot/hist", methods=["POST"])
def chatbot_hist_get():
    hist = list(db.test.find({}, {'_id': False}))

    return jsonify({"history": hist})






# # 회원가입
# @app.route("/signin")
# def signin():
#     # 이름, 아이디, 비밀번호 받기
#     name_receive = request.form['name_give']
#     id_receive = request.form['id_give']
#     pwd_receive = request.form['pwd_give']
#
#     # DB에 저장
#     doc = {
#         'name' : name_receive,
#         'id' : id_receive,
#         'pwd' : pwd_receive
#     }
#     db.user.insert_one(doc)
#
#     return jsonify({'msg': '회원가입 완료'})



# # 회원가입
# @app.route('/register', methods=['POST'])
# def api_register():
#     id_receive = request.form['id_give']
#     pw_receive = request.form['pw_give']
#     name_receive = request.form['name_give']
#
#     db.user.insert_one({'id': id_receive, 'pw': pw_receive, 'name': name_receive})
#
#     return jsonify({'result': 'success'})




# # 로그인
# @app.route("/login")
# def login():
#     pass









if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)
