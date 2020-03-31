def centering_window(window, height, width):
    window.update_idletasks()
    width = width
    height = height
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))


def authorized(home_window, GameWindow, **params):
    home_window.quit()
    if len(params) == 0:
        GameWindow()
    else:
        GameWindow(**params)
