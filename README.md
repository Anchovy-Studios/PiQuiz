# PiQuiz

![](https://img.shields.io/github/issues/Anchovy-Studios/PiQuiz) ![](https://img.shields.io/github/license/Anchovy-Studios/PiQuiz) ![](https://img.shields.io/github/v/release/Anchovy-Studios/PiQuiz) ![](https://img.shields.io/github/languages/code-size/Anchovy-Studios/PiQuiz)

PiQuiz is a simple python socket application quiz game which is similiar to [Kahoot](https://kahoot.it/).

## Installation

1. **Clone** the repository

   using **SSH**:

   ```bash
   git clone git@github.com:Anchovy-Studios/PiQuiz.git
   ```

   or using **HTTPS**:

   ```bash
   git clone https://github.com/Anchovy-Studios/PiQuiz.git
   ```

2. **Change** the ip address and port number

   - In `client.py` and `admin.py` file, change the value of variable `SERVER` and `PORT` to your need.
   - In `server.py` file, change the value of variable `ADDRESS` and `PORT` to your need

   ***Note***: *make sure the ip address and port number same for all files*

3. Start the server, admin, and client files.

## Tutorial

### Admin

1. After running the file, press `START` button to generate the game ID
2. In the next window, insert the question file  and press `START` button when all the client has been connected with the game ID
3. Manually press `NEXT` button every time you want to give next question

### Client

1. Insert the game ID you get from the admin
2. Insert your name
3. Press `START` button to join the room

## Documentation

All of the codes regarding the communication between client and server is available in `code.txt`

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[AGPLv3](https://choosealicense.com/licenses/agpl-3.0/)