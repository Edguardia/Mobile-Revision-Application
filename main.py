
import sys

sys.path.append("\\johnmason\\jmshome\\Students\\16pratte\\Desktop\\NEA\\Packages\\Packages")
print(sys.path)
import configparser
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
from kivy.uix.spinner import Spinner
import mysql.connector
import random
import atexit

def exitClose():
    cnx.close()

atexit.register(exitClose)
# Window.size = (1920,1080)

#Stores database login
config = configparser.ConfigParser()
config.read('config.ini')
#Opens Connection to Database
cnx = mysql.connector.connect(host = config['Credentials']['host'],
password=config['Credentials']['password'],
user=config['Credentials']['user'],
port=config['Credentials']['port'],
database=config['Credentials']['database'],
raise_on_warnings=config['Credentials']['warnings'])




#Gets login information from database and stores to lists

cursor = cnx.cursor()

query = ("SELECT username, password FROM user")
cursor.execute(query)
usernames = []
passwords = []
for (username, password) in cursor:
    usernames.append(username)
    passwords.append(password)

    

cursor.close()

#Class for the login screen which contains functions to check your username and password
class LoginScreen(Screen):
    
#Checks password inputted against stored list
    def login(self):
        if self.ids.UsernameBox.text in usernames:
            if self.ids.PasswordBox.text in passwords:
                print("Authenticated")
                self.manager.current = "MainSelectScreen"  #If authenticated moves to main screen
            else:
                self.manager.current = "FailedAuthentication"
                Clock.schedule_once(self.loginReset, 5) #if authentication fails stick on a failure screen for 5 seconds
        else:
            self.manager.current = "FailedAuthentication"
            Clock.schedule_once(self.loginReset, 5)
        
    def loginReset(self, dt):
        self.manager.current = "LoginScreen"

    
    pass


#Class for screen with all main options
class MainSelectScreen(Screen):
    def addQuestion(self): #Selects screen to add questions
        self.manager.current = "AddQuestionScreen"
    
    def delQuestion(self): #Selects screen to delete questions
        self.manager.current = "DeleteQuestionScreen"
    
    def answerQuestion(self): #Selects screen to answer questions
        self.manager.current = "AnsweringScreen"
    pass

#Empty Screen Class for failed authentication
class FailedAuthentication(Screen):
    pass

#Class for the answering questions screen
class AnsweringScreen(Screen):
    #stores id's of each button for answering
    global group
    group=["answer0", "answer1", "answer2", "answer3"]
    
    
    #Gets questions from database and displays it
    def getQuestion(self):
        questions = []
        answers = []
        #Database query for getting questions and answers
        cursor = cnx.cursor()
        query = ("SELECT question, answer FROM questions")
        cursor.execute(query)
        for (question, answer) in cursor:
            questions.append(question)
            answers.append(answer)

        cursor.close()
        
        quesansDict = dict(zip(questions, answers))
        questionSelected = random.randrange(0, len(questions))
        
        self.ids.questiontoAnswer.text = str(questions[questionSelected])
        
        correctAnswer = str(quesansDict[questions[questionSelected]])
        #Selects 4 other multi choice answers
        for i in range(0,4):
            self.ids[group[i]].text = answers[random.randint(0, (len(answers)-1))]
        #Puts multi choice selected answers into box
        randomed = random.randint(0,3)
        self.ids[group[randomed]].text = quesansDict[questions[questionSelected]]

        
    #Checks if the sumbitted answer is the correct answer
    def checkAns(self, button):
        
        if self.ids[group[int(button)]].text == AnsweringScreen.getQuestion.correctAnswer:
            userScore == 0
            userScore+=1
            print(userScore)
        else:
            print("Incorrect Answer")
            pass
        
    


        

    #Makes sure that the getQuestion function runs whenever the screen in selected
    def on_enter(self):
        self.getQuestion()
       

    


    pass


#Class for the screen where you add questions
class AddQuestionScreen(Screen):
    def uploadQuestion(self):
        question = self.ids.QuestionBox.text
        answer = self.ids.AnswerBox.text
        print(question, answer)
       #Database query to upload the inputted question
        cursor = cnx.cursor()
        query = ("INSERT INTO questions (question, answer) VALUES (%s, %s)")
        val = (question, answer)
        cursor.execute(query, val)
        cnx.commit()
        cursor.close()
        
        return

    pass
#Class for deleting the questions
class DeleteQuestionScreen(Screen):
    
    def retrieveQuestions(self):
        
        cursor = cnx.cursor()
        query = ("SELECT question from questions")
        cursor.execute(query)
        questions = []
        for question in cursor:
            questions.append(question)

        cursor.close()
        

#        self.dropdown = DropDown()
#        for question in questions:
#            btn = Button(text=question, size_hint_y=0, height=20)
#            btn.bind(on_release=lambda btn:self.dropdown.select(btn.text))
#            self.dropdown.add_widget(Button)
#            self.ids.button_release.bind(on_release=self.dropdown.open)

    def deleteQuestions(self):
        cursor = cnx.cursor()
        query = ("DELETE FROM questions WHERE question= %s")
        cursor.execute(query, self.ids.SpinnerSelect.text)
        cursor.commit()
        cursor.close()

#Class that contains the manager for all seperate screens
class WindowManager(ScreenManager):
    
    
    pass
    
    



#Loads the .kv file which contains GUI preferences
sm=Builder.load_file("mobile.kv")
class MobileApp(App):
    #Creates the application screen
    def build(self):
        WindowManager()
        return sm
    #Sets the app up for keyboard inputs
    def __init__(self, **kwargs):
        super(MobileApp, self).__init__(**kwargs)
        Window.bind(on_keyboard=self._key_handler)
    #If escape or back is pressed run set_previous_screen
    def _key_handler(self, instance, key, *args): 
        if key is 27:
            self.set_previous_screen()
            return True
    #Changes screen to go back to main select screen or to login screen
    def set_previous_screen(self):
        if sm.current == "MainSelectScreen" or sm.current == "FailedAuthentication":
            sm.direction = "left"
            sm.current ="LoginScreen"

        elif sm.current != "LoginScreen":
            sm.direction = "left"
            sm.current = "MainSelectScreen"

        

       
    
    

if __name__ == '__main__':
    
    MobileApp().run()



