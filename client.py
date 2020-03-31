from tkinter import *
from tkinter import messagebox
from utilities import centering_window
from utilities import authorized
import socket, threading, time


CLIENT_CODE = 'amJP8xVQ68'
SERVER = "127.0.0.1"
PORT = 7372
SOCKET = None

FORCE_EXIT = False

class HomeWindow:
    def __init__(self):
        self.root = Tk()
        self.root.resizable(FALSE, FALSE)
        self.root.title('PiQuiz - By: DarKnight98')
        self.root.iconbitmap('logo.ico')

        Label(self.root, text='Welcome to PiQuiz!', font=('arial', 20, 'bold')).pack(fill='x', pady=20)
        Label(self.root, text='Insert your quiz ID:', font=('arial', 12)).pack(fill='x')
        self.quiz_id = Entry(self.root, font=('arial', 15, 'bold'), justify=CENTER)
        self.quiz_id.pack(fill='x', pady=20, padx=20)
        Label(self.root, text='Insert your name:', font=('arial', 12)).pack(fill='x')
        self.name = Entry(self.root, font=('arial', 15, 'bold'), justify=CENTER)
        self.name.pack(fill='x', pady=20, padx=20)
        self.submit = Button(self.root, text='START', font=('arial', 15, 'bold'), bg='BLUE', fg='WHITE', relief=RAISED,
                             command=self.start)
        self.submit.bind("<Enter>", lambda event: self.submit.configure(bg='RED'))
        self.submit.bind("<Leave>", lambda event: self.submit.configure(bg='BLUE'))
        self.submit.pack(pady=10, ipady=20, ipadx=20)

        centering_window(self.root, 320, 300)

        self.root.mainloop()

    def quit(self):
        self.root.destroy()

    def getQuizID(self):
        return self.quiz_id.get()

    def getName(self):
        return self.name.get()

    def start(self):
        global SOCKET
        SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        SOCKET.connect((SERVER, PORT))
        SOCKET.sendall(bytes("1#{}#{}#{}".format(CLIENT_CODE, self.getQuizID(), self.getName()), 'UTF-8'))
        response = SOCKET.recv(1024)
        response = response.decode().split('#')
        if response[0] == '2' and response[1] == '200':
            authorized(self, GameWindow, user_id=response[2], game_id=self.getQuizID())
        else:
            messagebox.showerror('Error!', response[2])


class GameWindow:
    def __init__(self, **args):
        self.root = Tk()
        self.root.resizable(FALSE, FALSE)
        self.root.title('PiQuiz - By: DarKnight98')
        self.root.iconbitmap('logo.ico')
        self.user_id = args['user_id']
        self.game_id = args['game_id']
        self.start = 0
        self.end = 0

        self.main_container = Frame(self.root)
        self.title = Label(self.main_container, text='Waiting for other player ...', justify=CENTER, font=('arial', 20, 'bold'))
        self.title.pack(fill='x', pady=(10,0))
        self.soal = Label(self.main_container, wraplength=460, font=('arial', 20), justify=CENTER)
        self.soal.pack(padx=20, pady=20)

        self.pilihan_1 = Button(self.main_container, wraplength=460, font=('arial', 15, 'bold'), relief=RAISED, command=self.pil1)
        self.pilihan_1.pack_forget()

        self.pilihan_2 = Button(self.main_container, wraplength=460, font=('arial', 15, 'bold'), relief=RAISED, command=self.pil2)
        self.pilihan_2.pack_forget()

        self.pilihan_3 = Button(self.main_container, wraplength=460, font=('arial', 15, 'bold'), relief=RAISED, command=self.pil3)
        self.pilihan_3.pack_forget()

        self.pilihan_4 = Button(self.main_container, wraplength=460, font=('arial', 15, 'bold'), relief=RAISED, command=self.pil4)
        self.pilihan_4.pack_forget()

        self.indikator_judul = Label(self.main_container, text='Pilihan Anda:', justify=CENTER, font=('arial', 20, 'bold'))
        self.indikator_judul.pack_forget()
        self.indikator = Label(self.main_container, text=':', justify=CENTER, font=('arial', 20, 'bold'))
        self.indikator.pack_forget()

        self.main_container.pack(fill='x')

        self.result_window = Frame(self.root)
        Label(self.result_window, text='Final Scoreboard', font=('arial', 20, 'bold')).pack(fill='x', pady=20)
        self.result_window.pack_forget()
        centering_window(self.root, 700, 500)

        self.root.protocol("WM_DELETE_WINDOW", self.close_handler)
        ThreadHandler(self).start()
        self.root.mainloop()

    def final_result(self, results):
        results = results.split('|')
        print(results)
        first = True
        for result in results:
            if result == '':
                continue
            else:
                temp = result.split(',')
                if first:
                    Label(self.result_window, text='{} - {}'.format(temp[0], temp[1]), fg='RED',
                          font=('arial', 20, 'bold')).pack(fill='x', pady=20)
                    first = False
                else:
                    Label(self.result_window, text='{} - {}'.format(temp[0], temp[1]), font=('arial', 15)).pack(
                        fill='x',
                        pady=20)
        self.main_container.pack_forget()
        self.result_window.pack(fill='x')

    def ganti_soal(self, soal):
        self.title.pack_forget()
        soal = soal.split('|')
        self.soal['text'] = soal[1]
        self.pilihan_1['text'] = soal[2]
        self.pilihan_2['text'] = soal[3]
        self.pilihan_3['text'] = soal[4]
        self.pilihan_4['text'] = soal[5]
        self.pilihan_1.pack(padx=20, pady=10, fill='x')
        self.pilihan_2.pack(padx=20, pady=10, fill='x')
        self.pilihan_3.pack(padx=20, pady=10, fill='x')
        self.pilihan_4.pack(padx=20, pady=10, fill='x')
        self.indikator_judul.pack_forget()
        self.indikator.pack_forget()
        self.start = time.time()

    def close_handler(self):
        global SOCKET
        if messagebox.askokcancel("Quit", "Do you really wish to quit?"):
            SOCKET.sendall(bytes("10#" + self.game_id, 'UTF-8'))
            response = SOCKET.recv(1024)
            response = response.decode().split('#')
            if response[0] == '10' and response[1] == '200':
                SOCKET.close()
                global FORCE_EXIT
                FORCE_EXIT = True
                self.root.destroy()
                self.root.quit()

    def pil1(self):
        global SOCKET
        self.end = time.time()
        self.indikator['text'] = self.pilihan_1['text']
        self.indikator_judul.pack(fill='x', pady=10)
        self.indikator.pack(fill='x', pady=10)
        SOCKET.sendall(bytes("6#1#{}".format(self.end-self.start), 'UTF-8'))

    def pil2(self):
        global SOCKET
        self.end = time.time()
        self.indikator['text'] = self.pilihan_2['text']
        self.indikator_judul.pack(fill='x', pady=10)
        self.indikator.pack(fill='x', pady=10)
        SOCKET.sendall(bytes("6#2#{}".format(self.end-self.start), 'UTF-8'))

    def pil3(self):
        global SOCKET
        self.end = time.time()
        self.indikator['text'] = self.pilihan_3['text']
        self.indikator_judul.pack(fill='x', pady=10)
        self.indikator.pack(fill='x', pady=10)
        SOCKET.sendall(bytes("6#3#{}".format(self.end-self.start), 'UTF-8'))

    def pil4(self):
        global SOCKET
        self.end = time.time()
        self.indikator['text'] = self.pilihan_4['text']
        self.indikator_judul.pack(fill='x', pady=10)
        self.indikator.pack(fill='x', pady=10)
        SOCKET.sendall(bytes("6#4#{}".format(self.end-self.start), 'UTF-8'))


class ThreadHandler(threading.Thread):
    def __init__(self, game_window):
        super().__init__()
        self.game_window = game_window

    def run(self):
        global SOCKET
        while True:
            if FORCE_EXIT:
                break
            response = SOCKET.recv(1024)
            response = response.decode().split('#')
            print(response)
            if response[0] == '5':
                self.game_window.ganti_soal(response[1])
            elif response[0] == '8':
                self.game_window.final_result(response[1])
                break


if __name__ == '__main__':
    HomeWindow()
