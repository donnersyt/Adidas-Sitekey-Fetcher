import json, os

class openfile:
    def __init__(self):
        self.filename = None

    def readfile(self, filename):
        self.filename = filename
        try:
            with open(self.filename) as f:
                if "json" in filename:
                    return json.load(f)
                elif "txt" in filename:
                    return f.readlines()
                else:
                    pass
        except:
            if os.path.isfile("config.json"):
                print("File with the name [%s] could not be read. Please check your formatting." % (self.filename))
            else:
                print("File with the name [%s] could not be read. It is not in the working directory" % (self.filename))
            from time import sleep
            from os import _exit
            sleep(2)
            _exit(1)