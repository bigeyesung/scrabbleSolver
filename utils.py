import os
class Utils():
    def __init__(self):
        self.wordDict={}
        self.wordGrid=[]
        self.wordPanel=""
        self.rootDir=""
        self.fileName=""
        self.scoreTable={}
        self.validChars={
            "a":"a","f":"f","k":"k","p":"p","u":"u","z":"z",
            "b":"b","g":"g","l":"l","q":"q","v":"v","-":"-",
            "c":"c","h":"h","m":"m","r":"r","w":"w",
            "d":"d","i":"i","n":"n","s":"s","x":"x",
            "e":"e","j":"j","o":"o","t":"t","y":"y"
        }
    def Init(self, filePath):
        self.rootDir, self.fileName = os.path.split(filePath)
        self.SetDict(self.rootDir+ "/dict.txt")
        self.SetGrid(filePath)
        self.SetScoreTable()
        if self.wordDict and self.wordGrid and self.wordPanel:
            return True
        else:
            return False

    def SetGrid(self, filePath):
        try:
            with open(filePath,"r") as f:
                lines=f.readlines()
                for ind in range(len(lines)-1):
                    newLine=lines[ind].strip()
                    if all([self.validChars.get(ch) for ch in newLine]):
                        self.wordGrid.append(list(newLine))
                    else:
                        self.wordGrid.clear()
                        raise ValueError('char is not valid')
                #Set Panel
                if lines:
                    lastLine=lines[-1].strip()
                    if all([ch.islower() for ch in lastLine]):
                        self.SetPanel(lastLine)
                    else:
                        raise ValueError('char is not valid')
        except IOError:
            print("could not read file:",filePath)
        except ValueError as e:
            print(e) 

    def SetScoreTable(self):
        scores=[
        "EAIONRTLSU",
        "DG",
        "BCMP",
        "FHVWY",
        "K",
        "JX",
        "QZ"
        ]
        for score in range(len(scores)):
            for char in scores[score]:
                if score<=4:
                    self.scoreTable[char.lower()]=score+1
                elif score==5:
                    self.scoreTable[char.lower()]=8
                else:
                    self.scoreTable[char.lower()]=10

    def SetPanel(self, panel):
        self.wordPanel=panel

    def SetDict(self, filePath):
        try:
            with open(filePath,"r") as f:
                lines=f.readlines()
                for word in lines:
                    newWord=word.strip()
                    if all([self.validChars.get(ch) for ch in newWord]):
                        self.wordDict[newWord]=newWord
                    else:
                        self.wordDict.clear()
                        raise ValueError('char is not valid')
        except IOError:
            print("could not read file:",filePath)
        except ValueError as e:
            print(e)

    def SaveFile(self, record):
        fiepath=self.rootDir+"/"+self.fileName+".answer"
        f = open(fiepath, "a")
        record=record[1:]
        record=",".join(record)
        f.write("(" + record + ")")
        f.close()

    def GetGrid(self):
        return self.wordGrid

    def GetPanel(self):
        return self.wordPanel

    def GetDict(self):
        return self.wordDict

    def GetTable(self):
        return self.scoreTable

