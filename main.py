from ast import main
from multiprocessing import Manager
import kivy
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.clock import Clock
from kivy.properties import ObjectProperty, ListProperty, StringProperty
from kivy.lang.builder import Builder
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
import mysql.connector
import random

# Window.size = (1920,1080)

databaseConfig = {
    'user': 'MobileRevisionApp',
    'password': '3EhaR02J0*Vg',
    'host': '82.14.184.252',
    'port': '3306',
    'database': 'mobileapp',
    'raise_on_warnings': True
}
"""
databaseConfig = {
    'user': 'sql8522668',
    'password': 'FQj7wMyXws',
    'host': 'sql8.freemysqlhosting.net',
    'database': 'sql8522668',
    'raise_on_warnings': True
}
"""
cnx = mysql.connector.connect(**databaseConfig)
cursor = cnx.cursor()

query = ("SELECT username, password FROM user")
cursor.execute(query)
usernames = []
passwords = []
for (username, password) in cursor:
    usernames.append(username)
    passwords.append(password)

    

cursor.close()
cnx.close()

class LoginScreen(Screen):
    

    def login(self):
        if self.ids.UsernameBox.text in usernames:
            if self.ids.PasswordBox.text in passwords:
                print("Authenticated")
                self.manager.current = "MainSelectScreen"
            else:
                self.manager.current = "FailedAuthentication"
                Clock.schedule_once(self.loginReset, 5)
        else:
            self.manager.current = "FailedAuthentication"
            Clock.schedule_once(self.loginReset, 5)
        
    def loginReset(self, dt):
        self.manager.current = "LoginScreen"

    
    pass

class MainSelectScreen(Screen):
    def addQuestion(self):
        self.manager.current = "AddQuestionScreen"
    
    def delQuestion(self):
        self.manager.current = "DeleteQuestionScreen"
    
    def answerQuestion(self):
        self.manager.current = "AnsweringScreen"
    pass

class FailedAuthentication(Screen):
    pass

class AnsweringScreen(Screen):
    #stores id's of each button for answering
    global group
    group=["answer0", "answer1", "answer2", "answer3"]
    
    

    def getQuestion(self):
        questions = []
        answers = []
        cnx = mysql.connector.connect(**databaseConfig)
        cursor = cnx.cursor()
        query = ("SELECT question, answer FROM questions")
        cursor.execute(query)
        for (question, answer) in cursor:
            questions.append(question)
            answers.append(answer)

        cursor.close()
        cnx.close()
        quesansDict = dict(zip(questions, answers))
        questionSelected = random.randrange(0, len(questions))
        
        self.ids.questiontoAnswer.text = str(questions[questionSelected])
        global correctAnswer
        correctAnswer = str(quesansDict[questions[questionSelected]])

        for i in range(0,4):
            self.ids[group[i]].text = answers[random.randint(0, (len(answers)-1))]

        randomed = random.randint(0,3)
        self.ids[group[randomed]].text = quesansDict[questions[questionSelected]]

        

    def checkAns(self, button):
        """
        if self.ids[group[int(button)]].text == correctAnswer:
            userScore == 0
            userScore+=1
            print(userScore)
        else:
            pass
        """

    pass


        


    def on_enter(self):
        self.getQuestion()
       

    


    pass



class AddQuestionScreen(Screen):
    def uploadQuestion(self):
        question = self.ids.QuestionBox.text
        answer = self.ids.AnswerBox.text
        print(question, answer)
        cnx = mysql.connector.connect(**databaseConfig)
        cursor = cnx.cursor()
        query = ("INSERT INTO questions (question, answer) VALUES (%s, %s)")
        val = (question, answer)
        cursor.execute(query, val)
        cnx.commit()
        cursor.close()
        cnx.close()
        return

    pass

class DeleteQuestionScreen(Screen):
    pass

class WindowManager(ScreenManager):
    
    
    pass
    
    




sm=Builder.load_file("mobile.kv")
class MobileApp(App):
    
    def build(self):
        WindowManager()
        return sm
        
    def __init__(self, **kwargs):
        super(MobileApp, self).__init__(**kwargs)
        Window.bind(on_keyboard=self._key_handler)

    def _key_handler(self, instance, key, *args):
        if key is 27:
            self.set_previous_screen()
            return True

    def set_previous_screen(self):
        if sm.current == "MainSelectScreen":
            sm.direction = "left"
            sm.current ="LoginScreen"

        elif sm.current != "LoginScreen":
            sm.direction = "left"
            sm.current = "MainSelectScreen"

        

       
    
    

if __name__ == '__main__':
    
    MobileApp().run()
