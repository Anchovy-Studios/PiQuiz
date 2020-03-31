from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from pathlib import Path
from utilities import centering_window
from utilities import authorized
import socket


ADMIN_CODE = '05JFusup1r'
SERVER = "127.0.0.1"
PORT = 7372
SOCKET = None


class HomeWindow:
    def __init__(self):
        self.root = Tk()
        self.root.resizable(FALSE, FALSE)
        self.root.iconbitmap('logo.ico')
        self.root.title('PiQuiz - By: DarKnight98')

        self.container = Frame(self.root)
        Label(self.container, text='Welcome to PiQuiz!', font=('arial', 20, 'bold')).pack(fill='x', pady=20)
        start = Button(self.container, text='START', font=('arial', 15, 'bold'), bg='BLUE', fg='WHITE',
                       relief=RAISED, command=self.start)
        start.bind("<Enter>", lambda event: start.configure(bg='RED'))
        start.bind("<Leave>", lambda event: start.configure(bg='BLUE'))
        start.pack(pady=10, ipady=20, ipadx=20)
        self.container.pack(expand=TRUE)

        centering_window(self.root, 300, 300)

        self.root.mainloop()

    def quit(self):
        self.root.destroy()

    def start(self):
        global SOCKET
        SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        SOCKET.connect((SERVER, PORT))
        SOCKET.sendall(bytes("1#{}".format(ADMIN_CODE), 'UTF-8'))
        response = SOCKET.recv(1024)
        response = response.decode().split('#')
        if response[0] == '2' and response[1] == '200':
            authorized(self, SoalWindow, game_id=response[2])
        else:
            messagebox.showerror('Error!', response[2])


class SoalWindow:
    def __init__(self, **args):
        self.game_id = args['game_id']
        self.has_start = FALSE
        self.game_window = None
        self.filename = None
        self.root = Tk()
        self.root.resizable(FALSE, FALSE)
        self.root.iconbitmap('logo.ico')
        self.root.title('PiQuiz - By: DarKnight98')

        Label(self.root, text='Quiz id:'+self.game_id, font=('arial', 20, 'bold')).pack(fill='x', pady=20)
        Label(self.root, text='Pilih file pertanyaan', font=('arial', 12)).pack(fill='x', pady=20)
        filechooser = Button(self.root, text='Pilih', font=('arial', 12, 'bold'), command=self.chooser)
        filechooser.pack()
        self.path_label = Label(self.root, font=('arial', 12), wraplength=200)
        self.path_label.pack(fill='x', pady=20)

        start = Button(self.root, text='START', font=('arial', 15, 'bold'), bg='BLUE', fg='WHITE',
                       relief=RAISED, command=self.start)
        start.bind("<Enter>", lambda event: start.configure(bg='RED'))
        start.bind("<Leave>", lambda event: start.configure(bg='BLUE'))
        start.pack(pady=10, ipady=20, ipadx=20)

        centering_window(self.root, 300, 300)

        self.root.protocol("WM_DELETE_WINDOW", self.close_handler)
        self.root.mainloop()

    def close_handler(self):
        global SOCKET
        if messagebox.askokcancel("Quit", "Do you really wish to quit?"):
            SOCKET.sendall(bytes("10#"+self.game_id, 'UTF-8'))
            response = SOCKET.recv(1024)
            response = response.decode().split('#')
            if response[0] == '10' and response[1] == '200':
                SOCKET.close()
                self.root.destroy()

    def chooser(self):
        self.filename = filedialog.askopenfilename(initialdir="/", title="Select file")
        self.path_label['text'] = self.filename

    def start(self):
        global SOCKET
        if self.filename is None or self.filename == '':
            messagebox.showerror('Error!', 'File soal kosong!')
        else:
            file = open(Path(self.filename))
            line = file.readline()

            while True:
                if not line:
                    break
                SOCKET.sendall(bytes("3#{}".format(line), 'UTF-8'))
                response = SOCKET.recv(1024)
                response = response.decode().split('#')
                if response[0] == '4' and response[1] == '200':
                    print(response)
                    line = file.readline()
            SOCKET.sendall(bytes('7', 'UTF-8'))
            authorized(self, GameWindow, game_id=self.game_id)

    def quit(self):
        self.root.destroy()


class GameWindow:
    def __init__(self, **args):
        global SOCKET
        self.root = Tk()
        self.root.resizable(FALSE, FALSE)
        self.root.iconbitmap('logo.ico')
        self.root.title('PiQuiz - By: DarKnight98')
        # self.user_id = user_id
        self.game_id = args['game_id']

        response = SOCKET.recv(1024)
        print(response.decode())
        response = response.decode().split('#')
        if response[0] != '5':
            print(response)
            messagebox.showerror('Error!', 'UNKNOWN ERROR!')
        else:
            content = response[1].split('|')
            self.soal = Label(self.root, text=content[1], wraplength=460, font=('arial', 20), justify=CENTER)
            self.soal.pack(padx=20, pady=20)

            self.pilihan_1 = Button(self.root, text=content[2], wraplength=460, font=('arial', 15, 'bold'),
                                    relief=RAISED)
            self.pilihan_1.pack(padx=20, pady=10, fill='x')

            self.pilihan_2 = Button(self.root, text=content[3], wraplength=460, font=('arial', 15, 'bold'),
                                    relief=RAISED)
            self.pilihan_2.pack(padx=20, pady=10, fill='x')

            self.pilihan_3 = Button(self.root, text=content[4], wraplength=460, font=('arial', 15, 'bold'),
                                    relief=RAISED)
            self.pilihan_3.pack(padx=20, pady=10, fill='x')

            self.pilihan_4 = Button(self.root, text=content[5], wraplength=460, font=('arial', 15, 'bold'),
                                    relief=RAISED)
            self.pilihan_4.pack(padx=20, pady=10, fill='x')

            self.next = Button(self.root, text='NEXT', font=('arial', 15, 'bold'), bg='BLUE', fg='WHITE',
                           relief=RAISED, command=self.start)
            self.next.bind("<Enter>", lambda event: self.next.configure(bg='RED'))
            self.next.bind("<Leave>", lambda event: self.next.configure(bg='BLUE'))
            self.next.pack(pady=10, ipady=20, ipadx=20)

            centering_window(self.root, 700, 500)

            self.root.protocol("WM_DELETE_WINDOW", self.close_handler)
            self.root.mainloop()

    def close_handler(self):
        if messagebox.askokcancel("Quit", "Do you really wish to quit?"):
            SOCKET.sendall(bytes("10", 'UTF-8'))
            response = SOCKET.recv(1024)
            response = response.decode().split('#')
            if response[0] == '10' and response[1] == '200':
                SOCKET.close()
                self.root.destroy()

    def update_content(self, content):
        print(content)
        content = content.split('|')
        self.soal['text'] = content[1]
        self.pilihan_1['text'] = content[2]
        self.pilihan_2['text'] = content[3]
        self.pilihan_3['text'] = content[4]
        self.pilihan_4['text'] = content[5]
        if content[0] == '10':
            self.next['text'] = "FINISH"

        self.root.update()

    def start(self):
        global SOCKET
        SOCKET.sendall(bytes('7', 'UTF-8'))
        response = SOCKET.recv(1024)
        response = response.decode().split('#')
        if response[0] == '5':
            self.update_content(response[1])
        elif response[0] == '8':
            self.root.destroy()
            ResultWindow(response[1])
        else:
            print(response)
            messagebox.showerror('Error!', 'UNKNOWN ERROR!')


class ResultWindow:
    def __init__(self, results):
        self.root = Tk()
        self.root.resizable(FALSE, FALSE)
        self.root.iconbitmap('logo.ico')
        self.root.title('PiQuiz - By: DarKnight98')
        Label(self.root, text='Final Scoreboard', font=('arial', 20, 'bold')).pack(fill='x', pady=20)
        results = results.split('|')
        first = True
        for result in results:
            if result == '':
                continue
            else:
                temp = result.split(',')
                if first:
                    Label(self.root, text='{} - {}'.format(temp[0], temp[1]), fg='RED',
                          font=('arial', 20, 'bold')).pack(fill='x', pady=20)
                    first = False
                else:
                    Label(self.root, text='{} - {}'.format(temp[0], temp[1]), font=('arial', 15)).pack(
                        fill='x',
                        pady=20)
        centering_window(self.root, 700, 500)
        self.root.protocol("WM_DELETE_WINDOW", self.close_handler)
        self.root.mainloop()

    def close_handler(self):
        if messagebox.askokcancel("Quit", "Do you really wish to quit?"):
            SOCKET.sendall(bytes("10", 'UTF-8'))
            response = SOCKET.recv(1024)
            response = response.decode().split('#')
            if response[0] == '10' and response[1] == '200':
                SOCKET.close()
                self.root.destroy()


if __name__ == '__main__':
    HomeWindow()
