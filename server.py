import socket, string, random, threading
import logger
from error_code import code as ERROR_CODE
from operator import itemgetter

GAME_LIST = {}
CLIENT_CODE = 'amJP8xVQ68'
ADMIN_CODE = '05JFusup1r'


def randomStringDigits(length=6):
    """Generate a random string of letters and digits """
    temp = string.ascii_letters + string.digits
    return ''.join(random.choice(temp) for i in range(length))


class Question:
    def __init__(self, no, soal, point, pil_a, pil_b, pil_c, pil_d, jawaban_benar):
        self.no = no
        self.soal = soal
        self.point = point
        self.pil_a = pil_a
        self.pil_b = pil_b
        self.pil_c = pil_c
        self.pil_d = pil_d
        self.jawaban_benar = jawaban_benar

    def get_no(self):
        return self.no

    def get_soal(self):
        return self.soal

    def get_point(self):
        return self.point

    def get_pil_a(self):
        return self.pil_a

    def get_pil_b(self):
        return self.pil_b

    def get_pil_c(self):
        return self.pil_c

    def get_pil_d(self):
        return self.pil_d

    def get_jawaban_benar(self):
        return self.jawaban_benar

    def get_soal_for_user(self):
        return "|".join([self.no, self.soal, self.pil_a, self.pil_b, self.pil_c, self.pil_d])


class Game:
    def __init__(self):
        global GAME_LIST
        self.id = randomStringDigits()
        self.client = {}
        self.question = []
        self.answer = {}
        self.time = []
        self.admin = None
        self.number = 0
        GAME_LIST[self.id] = self

    def set_admin(self, admin):
        self.admin = admin

    #
    # def set_path(self, path):
    #     self.path = path

    def add_client(self, new_client):
        self.client[new_client.get_id()] = new_client

    def add_question(self, question):
        self.question.append(question)

    def get_next_question(self):
        if self.number == 10:
            self.calculate_score()
            self.number = self.number + 1
            return self.get_all_score()
        else:
            if self.number != 0:
                self.calculate_score()
            result = self.question[self.number].get_soal_for_user()
            self.number = self.number + 1
            return result

    def get_game_id(self):
        return self.id

    def get_all_client(self):
        return self.client

    def get_admin(self):
        return self.admin

    def get_number(self):
        return self.number

    def calculate_score(self):
        result = sorted(self.time, key=itemgetter(1))
        jawaban_benar = self.question[self.number - 1].get_jawaban_benar()
        for user_id, time in result:
            if self.answer[user_id] == jawaban_benar:
                self.client[user_id].add_score(self.question[self.number - 1].get_point())
                break
        self.answer = {}

    def get_all_score(self):
        result = ''
        for user_id, user in self.client.items():
            result = result + '{},{}|'.format(user.get_name(), user.get_score())
        return result

    def add_answer(self, time, answer, user_id):
        self.answer[user_id] = answer
        self.time.append((user_id, time))


class Admin(threading.Thread):
    def __init__(self, address, socket, game):
        super().__init__()
        self.address = address
        self.socket = socket
        self.game = game

    def run(self):
        while True:
            data = self.socket.recv(1024)
            data = data.decode().split('#')
            if data[0] == '10':
                del GAME_LIST[self.game.get_game_id()]
                self.socket.sendall(bytes('10#200', 'UTF-8'))
                logger.info(self.address, 'Disconnected!')
                break
            elif data[0] == '3':
                data_question = data[1].split('|')
                self.game.add_question(Question(data_question[0], data_question[1], data_question[2],
                                                data_question[3], data_question[4], data_question[5],
                                                data_question[6], data_question[7].rstrip("\n")))
                self.socket.sendall(bytes('4#200', 'UTF-8'))
                logger.info(self.address, 'Send a question file for game id ({}) with content: {}'
                            .format(self.game.get_game_id(), data[1]))
            elif data[0] == '7':
                question = self.game.get_next_question()
                if self.game.get_number() > 10:
                    self.socket.sendall(bytes('8#{}'.format(question), 'UTF-8'))
                    for key, user in self.game.client.items():
                        user.send_final_result_to_client(question)
                    logger.info(self.address, 'Successfully distribute the score to all client!')
                else:
                    for key, user in self.game.client.items():
                        user.send_question_to_client(question)
                    self.send_question_to_admin(question)
                    logger.info(self.address, 'Successfully distribute the question to all client!')
        self.socket.close()

    def send_question_to_admin(self, question):
        self.socket.sendall(bytes('5#{}'.format(question), 'UTF-8'))


class Client(threading.Thread):
    def __init__(self, address, socket, game, name):
        super().__init__()
        self.address = address
        self.socket = socket
        self.game = game
        self.name = name
        self.score = 0
        self.id = randomStringDigits()

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_score(self):
        return self.score

    def run(self):
        while True:
            data = self.socket.recv(1024)
            data = data.decode().split('#')
            if data[0] == '10':
                del self.game.client[self.id]
                self.socket.sendall(bytes('10#200', 'UTF-8'))
                logger.info(self.address, 'Disconnected!')
                break
            elif data[0] == '6':
                self.game.add_answer(data[2], data[1], self.id)
                logger.info(self.address, 'Receive the answer from ({}) <{}> with content: {}'
                            .format(self.id, self.name, data))
                self.socket.sendall(bytes('6#200', 'UTF-8'))
        self.socket.close()

    def add_score(self, point):
        self.score = self.score + int(point)
        logger.info(self.address, 'Player ({}) with name ({}) add a score. Total score: {}'
                    .format(self.id, self.name, self.score))

    def send_question_to_client(self, question):
        self.socket.sendall(bytes('5#{}'.format(question), 'UTF-8'))

    def send_final_result_to_client(self, result):

        self.socket.sendall(bytes('8#{}'.format(result), 'UTF-8'))


class TemporaryHandle(threading.Thread):
    def __init__(self, address, socket):
        super().__init__()
        self.socket = socket
        self.address = address
        logger.info(address, "New connection added....")

    def run(self):
        logger.info(self.address, "Connection established....")
        data = self.socket.recv(1024)
        msg = data.decode().split('#')
        if msg[0] == '1':
            if msg[1] == ADMIN_CODE:
                game = Game()
                admin = Admin(self.address, self.socket, game)
                game.set_admin(admin)
                admin.start()
                logger.info(self.address,
                            "Admin connection established; Creating game with id: {}".format(game.get_game_id()))
                self.socket.sendall(bytes('2#200#' + game.get_game_id(), 'UTF-8'))
                return
            elif msg[1] == CLIENT_CODE:
                try:
                    game_id = msg[2]
                    name = msg[3]
                    global GAME_LIST
                    client = Client(self.address, self.socket, GAME_LIST[game_id], name)
                    GAME_LIST[game_id].add_client(client)
                    client.start()
                    logger.info(self.address, "Client connect to game id ({}) with name ({})".format(game_id, name))
                    self.socket.sendall(bytes('2#200#' + client.get_id(), 'UTF-8'))
                    return
                except IndexError:
                    logger.error(self.address, "There is empty field!", ERROR_CODE['C01'])
                    self.socket.sendall(bytes('9#502#There is empty field!', 'UTF-8'))
                    return
                except KeyError:
                    logger.error(self.address, "The game id is not valid!", ERROR_CODE['B01'])
                    self.socket.sendall(bytes('9#502#The game id is not valid!', 'UTF-8'))
                    return
            else:
                logger.error(self.address, "Access Forbidden!", ERROR_CODE['A01'])
                self.socket.sendall(bytes('9#403#Access Forbidden!', 'UTF-8'))


if __name__ == '__main__':
    ADDRESS = "127.0.0.1"
    PORT = 7372

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((ADDRESS, PORT))

    print("Server started ........ ")
    while True:
        server.listen(100)
        clientsock, clientAddress = server.accept()
        new_client = TemporaryHandle(clientAddress, clientsock)
        new_client.start()
