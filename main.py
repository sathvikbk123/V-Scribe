import speech_recognition as sr
import playsound
from gtts import gTTS
from io import BytesIO
from io import StringIO
import pymongo
import re
from flask import Flask,render_template,request,url_for,redirect,jsonify
from pygame import mixer
import requests,json
from gtts import gTTS
import tempfile
from tempfile import TemporaryFile
import os
from flask_cors import CORS, cross_origin
import time, docx
import sys
import cv2
import face_recognition

num = 1
exam_time = time.time()
review = [False,False,False]
uri = "mongodb://6d0d9a0d-0ee0-4-231-b9ee:DFKoNQdEIptsjmR5eAQlJO64FlQryGYipb4BTeb4CXh4uKI6OBCU93c6kaLM2AP2IGSgrRkAkcc91J1nK1QwUA==@6d0d9a0d-0ee0-4-231-b9ee.documents.azure.com:10255/?ssl=true&replicaSet=globaldb"
myclient = pymongo.MongoClient(uri)
mydb = myclient["vscribe"]
mycol = mydb["qna"]
marks= ["2","5","1"]

def punc(text):
    url = "http://bark.phon.ioc.ee/punctuator"
    payload = {"text" : text}
    response = requests.post(url, data=payload)
    return response.text

def scribe_speaks(output):
    global num
    num +=1
    print("V-Scribe : ", output)
    toSpeak = gTTS(text=output, lang='en-US', slow=False)
    file = str(num)+".mp3"
    toSpeak.save(file)
    playsound.playsound(file, True)
    os.remove(file)

def get_audio(time_limit = None,isstop = False):
    r = sr.Recognizer()
    audio = ''
    with sr.Microphone() as source:
        print("Begin speaking")
        audio = r.listen(source, phrase_time_limit=time_limit)
    print("Stop speaking")
    try:
        text = r.recognize_google(audio,language='en-US')
        print("You : ", text)
        return text
    except:
        if isstop == False:
            scribe_speaks("Could not understand your audio, PLease try again!")
        return '0'

def mark(qno):
    review[qno] = True

def read_question(question,num):
    print("entered")
    if num == "3":
        print("entered if")
        scribe_speaks("The question is Tomato is a fruit and your options are option A true and option B false")
    else:
        scribe_speaks("Reading question number "+str(num)+" \n"+question)



def read_answer(answer,qon=None):
    if qon != None:
        scribe_speaks("Option chosen : "+answer)
    else:
        flag_ind = 0
        print(answer)
        answer = answer.split(".")
        scribe_speaks("Reading...")
        j = 0
        for i in range(len(answer)):
            if len(answer[i])!=0:
                scribe_speaks("Line "+str(j+1)+": "+answer[i])
                j+=1
                stop = get_audio(5,True)
                if stop!=0 and ("stop" in stop):
                    flag_ind = i+1
                    break
        return flag_ind

def read_line(answer,line):
    answer = answer.split(".")
    scribe_speaks("Reading...line "+str(line))
    scribe_speaks(answer[line-1])

def choose_answer():
    choice = get_audio(5)
    if "option A" in choice:
        scribe_speaks("option A selected")
        return "option A"
    elif "option B" in choice:
        scribe_speaks("option B  selected")
        return "option B"
    else:
        scribe_speaks("No appropriate option selected")
        return ""

def write_answer():
    final_dict_ans = ""
    flag = 1
    while flag==1:
        scribe_speaks("You may start dictating the answer now!")
        dict_ans = get_audio(10)
        if dict_ans!=0:
            final_dict_ans += super_punc(dict_ans)
            scribe_speaks("your answer is recorded successfully")
            # print("Wait! last word recorded is "+dict_ans.split()[-1]) #Remove
            # scribe_speaks("Wait, last word recorded is "+dict_ans.split()[-1])
            while True:
                scribe_speaks("Do you wish to continue?")
                choice = get_audio(5)
                if choice!=0:
                    if "yes" in choice.lower():
                        if "list" in choice.lower():
                            final_dict_ans,ch = point_wise_answer(final_dict_ans)
                            if ch == 'no':
                                flag = 0
                        break
                    elif "no" in choice.lower():
                        flag=0
                        break
                    else:
                        scribe_speaks("Didn't get you there, try again!")

    return final_dict_ans

def super_punc(ans):
    try:
        ans = punc(ans)
    except:
        scribe_speaks("Cannot punctuate answer")
    return ans

def point_wise_answer(ans):
    scribe_speaks("dictate point wise...")
    line_num = 0
    same = False
    while True:
        scribe_speaks("Dictate Point ")
        dict_ans = get_audio()
        if dict_ans!=0:
            if same == False:
                line_num+=1
                ans += '\n'+str(line_num)+") "
            ans += super_punc(dict_ans)
            scribe_speaks("your point is recorded successfully")
            # scribe_speaks("Wait, last word recorded for point "+str(line_num)+" is "+dict_ans.split()[-1])
            while True:
                scribe_speaks("continue point? or next point? or para mode? or exit")
                choice = get_audio(5)
                if choice!=0:
                    if "continue" in choice.lower():
                        same = True
                        break
                    elif "next" in choice.lower():
                        same = False
                        break
                    elif "para" in choice.lower():
                        print(ans)
                        return [ans,'yes']
                    elif "exit" in choice.lower():
                        print(ans)
                        return [ans,'no']
                    else:
                        scribe_speaks("Didn't get you there, try again!")


def erase_line(answer, index):
    answer = answer.split(".")
    try:
        removed = answer[index-1]
        answer.pop(index-1)
        scribe_speaks("Removed line : "+removed)
    except:
        scribe_speaks("No such line")
    return ".".join(answer)

def erase_till_word(answer,index,word):
    answer = answer.split(".")
    try:
        removed = answer[index-1].split(" ")
        try:
            find = removed.index(word)
            answer[index-1] = re.sub(r''+word+'.*', word, answer[index-1])
            scribe_speaks("Updated answer")
        except:
            scribe_speaks("Could'nt find "+word+" in this line")
    except:
        scribe_speaks("No such line")
    return ".".join(answer)

def add_line(answer, index = None, append = False):
    answer = answer.split(".")
    while True:
        scribe_speaks("Speak line to be added!")
        addline = get_audio()
        if addline!=0:
            if index!=None:
                if append == False:
                    answer.insert(index-1,super_punc(addline))
                else:
                    answer[index-1] += str(" "+super_punc(addline))
            else:
                answer.append(super_punc(addline))
            scribe_speaks("line added was : "+super_punc(addline))
            break
    return ".".join(answer)

def del_answer():
    scribe_speaks("Are you sure? Deleting will permanently remove the answer")
    choice = get_audio(5)
    if "no" in choice.lower():
        scribe_speaks("Cancelled deletion")
        return 0
    scribe_speaks("Deleted successfully")
    return 1

def gettime(lapsed=0):
    rem = (3*60*60) - lapsed
    rem_hr = (rem//3600)
    rem_min = (rem//60) - int(rem_hr*60)
    rem_sec = int(rem%60)
    return '{} hours {} minutes {} seconds'.format(rem_hr,rem_min,rem_sec)

def welcome():
    speak = "Hello, I am V-Scribe. Your personal scribe for this session."
    scribe_speaks(speak)

app = Flask(__name__)
CORS(app)
@app.route('/brail',methods = ['GET'])
def braild():
    #if request.method == 'GET':\
    try:
        f  = open('answers.txt','r')
        str = f.read()
    except:
        str = "empty string"
    asciicodes = [' ','!','"','#','$','%','&','','(',')','*','+',',','-','.','/',
          '0','1','2','3','4','5','6','7','8','9',':',';','<','=','>','?','@',
          'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q',
          'r','s','t','u','v','w','x','y','z','[','\\',']','^','_']


    brailles = ['⠀','⠮','⠐','⠼','⠫','⠩','⠯','⠄','⠷','⠾','⠡','⠬','⠠','⠤','⠨','⠌','⠴','⠂','⠆','⠒','⠲','⠢',
        '⠖','⠶','⠦','⠔','⠱','⠰','⠣','⠿','⠜','⠹','⠈','⠁','⠃','⠉','⠙','⠑','⠋','⠛','⠓','⠊','⠚','⠅',
        '⠇','⠍','⠝','⠕','⠏','⠟','⠗','⠎','⠞','⠥','⠧','⠺','⠭','⠽','⠵','⠪','⠳','⠻','⠘','⠸']

    text = ""
    for i in str:
        if i != '\n':
            text += brailles[asciicodes.index(i.lower())]
    d = docx.Document()
    d.add_paragraph(str + "\n--------------------------------------------------------------------------------\n"+text)
    d.save('braille.docx')
    os.startfile('braille.docx')
    return jsonify({"test":"0"})

@app.route('/end',methods = ['GET'])
def endf():
    #if request.method == 'GET':
    scribe_speaks("All the best for results")
    return jsonify({"resu":"1"}) 

@app.route('/error',methods = ['GET'])
def novery():
    #if request.method == 'GET':
    scribe_speaks("User not verified. Click Again to try verifying again.")
    return jsonify({"resu":"0"}) 

@app.route('/time',methods = ['GET','POST'])
def trial():
    return jsonify({"test":"0"})

@app.route('/verify',methods = ['GET','POST'])
def verify():
    if request.method == 'GET':
        scribe_speaks("Click anywhere to verify the user.")
        return jsonify({"test":"0"})
    else:
        video_capture = cv2.VideoCapture(0)
        # Check success
        if not video_capture.isOpened():
            raise Exception("Could not open video device")
            # Read picture. ret === True on success
        ret, frame = video_capture.read()
        # Close device
        video_capture.release()
        frameRGB = frame[:,:,::-1] # BGR => RGB
        cv2.imwrite('check.jpg',frameRGB)
        known_image = face_recognition.load_image_file("picture.jpg")
        unknown_image = face_recognition.load_image_file("check.jpg")
        print("check1")
        biden_encoding = face_recognition.face_encodings(known_image)[0]
        print("check2")
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
        print("check3")
        results = face_recognition.compare_faces([biden_encoding], unknown_encoding)
        print("res is ",results)
        if results[0]:
            scribe_speaks("User verified. You can start the exam now. All the best.")
            welcome()
            scribe_speaks('Your timer has started')
            return jsonify({"resu":"1"})
        else:
            scribe_speaks("User not verified. Click Again to try verifying again.")
            return jsonify({"resu":"0"})


@app.route('/speech',methods = ['POST'])
def process_text():
    question = request.form["question"]
    q_no = request.form["qno"]
    answer = request.form["answer"]
    scribe_speaks("How can I help you?")
    choice = get_audio(8).lower()
    if "question 1" in choice:
        scribe_speaks("alright, going to question 1, question is , when did India get Independence")
        myquery={"qno":"1"}
        mydoc = mycol.find(myquery)
        for x in mydoc:
            return jsonify({"qno":"1","question":"When did India get Independence?","answer":x['answer'],"option1":"true","option2":"false"})
    elif "question 2" in choice:
        scribe_speaks("alright, going to question 2, question is, explain solar energy in points")
        myquery={"qno":"2"}
        mydoc = mycol.find(myquery)
        for x in mydoc:
            return jsonify({"qno":"2","question":"Explain Solar energy in points?","answer":x['answer'],"option1":"true","option2":"false"})
    elif "question 3" in choice:
        scribe_speaks("alright, going to question 3 the question is, Tomato is a fruit? and your options are option A true and option B false")
        myquery={"qno":"3"}
        mydoc = mycol.find(myquery)
        for x in mydoc:
            return jsonify({"qno":"3","question":x['question'],"answer":x['answer'],"option1":"true","option2":"false"})
    elif "score" in choice:
        scribe_speaks("Alloted marks are "+marks[int(q_no)-1])
    elif "time" in choice:
        scribe_speaks('The time remaining is {0}'.format(gettime(time.time()-exam_time)))

    elif "review" in choice and 'check' not in choice:
        quest_no = int(q_no)
        if "mark" in choice and review[quest_no-1] == False:
            review[quest_no-1] = True
            scribe_speaks("Marked for review")
        elif "unmark" in choice and review[quest_no-1] == True:
            review[quest_no-1] = False
            scribe_speaks("Unmarked from review")
    
    elif "check" in choice and "review" in choice:
        rev = ''
        for i in range(len(review)):
            if review[i]==True:
                rev += " ,Question {} marked for review".format(i+1)
        if rev == '':
            rev = 'No Question marked for review!'
        scribe_speaks(rev)

    elif "read" in choice and "answer" in choice and 'edit' not in choice:
        if q_no == '3':
            read_answer(answer,q_no)
        elif len(answer.split())==0:
            scribe_speaks("No answer to read")
        else:
            read_answer(answer)

    elif "read" in choice and 'edit' not in choice:
        read_question(question,q_no)

    elif "answer" in choice and 'edit' not in choice:
        if q_no == "3":
            scribe_speaks("Choose option!")
            answer = choose_answer()
        else:
            answer = write_answer()
        myquery = { "qno": q_no }
        newvalues = { "$set": { "answer": answer } }
        mycol.update_one(myquery, newvalues)
        resp = {"qno":q_no,"question":question,"answer":answer,"option1":"True","option2":"False"}
        return jsonify(resp)

    elif "edit" in choice:
        scribe_speaks("Edit a line or complete answer")
        sub_choice = get_audio(5).lower()

        if "line" in sub_choice:
            ln=-1
            while True:
                scribe_speaks("Specify line number")
                ln = [int(i) for i in get_audio(3).split() if i.isdigit()][0]
                if ln!=None and ln!=0:
                    break
                else:
                    scribe_speaks("Try again!")
            while True:
                scribe_speaks("Read line {0}  or Add before line {0} or Append to line {0} or Remove line {0} or delete line after a word or exit".format(ln))
                sub_choice = get_audio(5).lower()

                if "read" in sub_choice:
                    read_line(answer,ln)
                elif "remove" in sub_choice:
                    answer = erase_line(answer, ln)
                elif "delete" in sub_choice or "word" in sub_choice:
                    while True:
                        scribe_speaks('Specify word')
                        word = get_audio(5)
                        if word!=0:
                            answer = erase_till_word(answer,ln,word)
                            print("----------\n"+answer+"\n--------------")
                            break
                        else:
                            scribe_speaks("Try again!")
                elif "add" in sub_choice:
                    answer = add_line(answer, ln)
                    print("----------\n"+answer+"\n--------------")
                elif "append" in sub_choice:
                    answer = add_line(answer,ln,True)
                    print("----------\n"+answer+"\n--------------")
                elif "exit" in sub_choice.lower():
                    break

        elif "complete" in sub_choice:
            while True:
                scribe_speaks("delete answer or append to answer or exit")
                sub_choice = get_audio(5).lower()
                if 'delete' in sub_choice.lower():
                    if del_answer()==1:
                        answer = write_answer()
                    break
                elif 'append' in sub_choice.lower():
                    answer = add_line(answer)
                    break
                elif 'exit' in sub_choice.lower():
                    break
            resp = {"qno":q_no,"question":question,"answer":answer,"option1":"true","option2":"false"}
            return jsonify(resp)

        else:
            scribe_speaks("Didn't get you there, try again!")

    elif ("done" in choice) or ("paper" in choice):
        scribe_speaks("Thanks for writing the paper.")
        L = []
        file1 = open("answers.txt","w")
        for x in mycol.find():
            L.append('Q '+x['qno']+'> '+x['answer']+'\n\n')
        file1.writelines(L)
        file1.close() #to change file access modes
        return jsonify({"qno":"end"})
    
    else:
        scribe_speaks("Didn't get you there, try again!")
    myquery = { "qno": q_no }
    newvalues = { "$set": { "answer": answer } }
    mycol.update_one(myquery, newvalues)
    resp = {"qno":q_no,"question":question,"answer":answer,"option1":"true","option2":"false"}
    return jsonify(resp)


if __name__ == "__main__":
    app.run()