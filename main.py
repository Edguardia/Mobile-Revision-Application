
import sys
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
import kivy.utils
import mysql.connector
import random
import atexit

#Window.size = (1920,1080)

#Stores database login

config = configparser.ConfigParser()
config.read('config.ini')
#Opens Connection to Database
cnx = mysql.connector.connect(host = config.get('Credentials', 'host'),
password=config['Credentials']['password'],
user=config['Credentials']['user'],
port=config.getint('Credentials', 'port'),
database=config['Credentials']['database'],
raise_on_warnings=config.getboolean('Credentials', 'warnings')
)

#On program exit closes the connection with database saving resources on hosting device
def exitClose():
    cnx.close()


atexit.register(exitClose)

#Gets login information from database and stores to lists



#Class for the login screen which contains functions to check your username and password
class LoginScreen(Screen):
    
#Checks password inputted against stored list
    def login(self):
        cursor = cnx.cursor()
        query = ("SELECT username, password FROM user")
        cursor.execute(query)
        usernames = []
        passwords = []
        for (username, password) in cursor:
            usernames.append(username)
            passwords.append(password)
        cursor.close()

        #Checks text of box against list of downloaded usernames
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
    
    def toRegister(self):
        self.manager.current = "RegisterScreen"

    
    pass
#Class for creating new users
class RegisterScreen(Screen):
    def registerUser(self):
        newUsername = self.ids.newUsername.text
        newPassword = self.ids.newPassword.text
        cursor = cnx.cursor
        query = ("INSERT INTO user (username, password) VALUES (%s, %s)" % newUsername, newPassword)
        cursor.execute(query)#Runs query to update database with new user credentials
        cnx.commit()
        cursor.close()
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

    def leaderboardScreen(self):
        self.manager.current = "LeaderBoard"
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
        #questionSelected = random.sample(range(len(questions)), 4)
        
        self.ids.questiontoAnswer.text = str(questions[questionSelected])
        global correctAnswer
        correctAnswer = str(quesansDict[questions[questionSelected]])
        #Selects 4 other multi choice answers
        for i in range(0,4):
            self.ids[group[i]].text = answers[random.randint(0, (len(answers)-1))]
        #Puts multi choice selected answers into box
        randomed = random.randint(0,3)
        self.ids[group[randomed]].text = quesansDict[questions[questionSelected]]

        
    #Checks if the sumbitted answer is the correct answer
    def checkAns(self, button):
        
        if self.ids[group[int(button)]].text == correctAnswer:
            self.manager.current = "CorrectAnswer"
        else:
            print("Incorrect Answer")
            self.manager.current = "IncorrectAnswer"
            pass
        
        
    #Makes sure that the getQuestion function runs whenever the screen in selected
    def on_enter(self):
        self.getQuestion()
       

    pass

#Displays and updates the users current score
class CorrectAnswer(Screen):
    def increaseUserScore(self): #Retrieves current user score
        cursor = cnx.cursor()
        usersName = self.manager.screens[0].ids.UsernameBox.text
        query = ("SELECT usersScore FROM user WHERE username='%s'" % usersName)
        cursor.execute(query)
        usersCurrentScore = int(cursor.fetchone()[0])
        usersCurrentScore +=1
        usertext = ("Your current score is:", usersCurrentScore)
        self.ids.UsersScore.text = str(usertext) #Outputs users new score

        query = ("UPDATE user SET usersScore = %s WHERE username=%s")
        val = (usersCurrentScore, usersName)#Updates database with users new score
        cursor.execute(query, val)
        cnx.commit()
        print(cursor.rowcount, "record(s) affected")
        cursor.close()


    def backToAnswer(self, dt):
        self.manager.current="AnsweringScreen"


    def on_enter(self, *args):
        self.increaseUserScore()
        Clock.schedule_once(self.backToAnswer, 5)


#Class for if user gets incorrect answer
class IncorrectAnswer(Screen):
    def updateIncorrectAnswer(self):
        self.ids.AnswerLabel.text = correctAnswer
    
    
    def backToAnswer(self, dt):
        self.manager.current="AnsweringScreen"

    
    def on_enter(self, *args):
        self.updateIncorrectAnswer()
        Clock.schedule_once(self.backToAnswer, 5)






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
        #Gets all question names
        self.ids.values = "" #Empties the list of questions before reappending
        cursor = cnx.cursor()
        query = ("SELECT question from questions")
        cursor.execute(query)
        questions = []
        
        #Adds question names to dropdown
        for question in cursor:
            questions.append(question)
        cursor.close()
        self.ids.spinner.values = ""
        for i in range (0, len(questions)):
            questions1 = questions[i][0]
            self.ids.spinner.values.append(str(questions1))


    def deleteQuestions(self):
        cursor = cnx.cursor()
        query = ("DELETE FROM questions WHERE question= %s")
        qtodelete = [(self.ids.spinner.text)]

        cursor.execute(query, qtodelete)
        cnx.commit()
        cursor.close()

    def on_enter(self, *args):
        self.retrieveQuestions()

class ErrorScreen(Screen):
    pass
#Class that contains the manager for all seperate screens

class LeaderBoard(Screen):
    def on_enter(self, *args):
        userDataUnsorted = []
        cursor = cnx.cursor()
        query = ("SELECT username, UsersScore FROM user")
        cursor.execute(query)
        for row in cursor:
            userDataUnsorted.append(row)
        cursor.close()
        print(userDataUnsorted)
        userDataSorted = sorted(userDataUnsorted, key=lambda x:x[1], reverse=True)
        LeaderBoardList = self.ids.LeaderBoardList
        for i in range(len(userDataSorted)):
            for j in range(2):
                label = Label(text=str(userDataSorted[i][j]))
                LeaderBoardList.add_widget(label)
        
    pass




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
    #If escape or back is pressed run set_previous_screen, ESC is key 27
    def _key_handler(self, instance, key, *args): 
        if key == 27:
            self.set_previous_screen()
            return True
    
    #Changes screen to go back to main select screen or to login screen
    def set_previous_screen(self):
        if sm.current == "MainSelectScreen" or sm.current == "FailedAuthentication": #Stops bypassing login screen
            sm.direction = "left"
            sm.current = "LoginScreen"

        elif sm.current == "LoginScreen":
            quit()

        elif sm.current != "LoginScreen":
            sm.direction = "left"
            sm.current = "MainSelectScreen"

        

       
    
    

if __name__ == '__main__':
    
    MobileApp().run()



