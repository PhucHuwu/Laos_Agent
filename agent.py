func = {"rag", "ocr", "turn_on_camera", "regcog_face"}

def rag():
    pass

def ocr():
    pass

def turn_on_camera():
    pass

def regcog_face():
    pass

def agent(func):
    if func == "rag":
        rag()
    elif func == "ocr":
        ocr()
    elif func == "turn_on_camera":
        turn_on_camera()
    elif func == "regcog_face":
        regcog_face()
        
while True:
    func = input("Enter a function: ")
    agent(func)
