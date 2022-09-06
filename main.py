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

# Window.size = (1920,1080)


class LoginScreen(Screen):
    

    def login(self):
        if self.ids.UsernameBox.text == "Enter Username":
            if self.ids.PasswordBox.text == "Enter Password":
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
    
    pass

class FailedAuthentication(Screen):
    pass


class AddQuestionScreen(Screen):
    def uploadQuestion(self):
        return

    pass

class DeleteQuestionScreen(Screen):
    pass

class WindowManager(ScreenManager):
    pass





class MobileApp(App):
    def build(self):
        WindowManager()
        
    

        

       
    
    

if __name__ == '__main__':
    
    
    
        

    MobileApp().run()
