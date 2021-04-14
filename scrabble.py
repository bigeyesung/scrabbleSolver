from utils import Utils
from common import Coord, Move, Dirs
import collections
import copy
import sys
import time

class Scrabble():
    def __init__(self):
        self.words=set()
        self.wordGrid=[]
        self.wordDict={}
        self.scoreTable={}
        self.wordsMaxScore=collections.defaultdict(list)
        self.highest=[]
        self.dirs=Dirs()

    def Init(self, wordDict, wordGrid, wordPanel, scoreTable, filterOpen):
        self.wordDict=wordDict
        self.wordGrid=wordGrid
        self.scoreTable=scoreTable
        self.SetWords(wordPanel, filterOpen)


    def IsValidWord(self, word):
        if self.wordDict.get(word)!=None:
            return True
        else:
            return False

    def IsValidLoc(self, row, col, size):
        limit=size-1
        if col<len(self.wordGrid[row])-limit or \
           row<len(self.wordGrid)-limit:
           return True
        else:
           return False

    def SetWords(self, panel, filterOpen):
        #recursive functions to get all permutation of words
        used = [False]*len(panel)

        def MakeWord(length, word):
            if len(word)==length:
                self.words.add(tuple(word))
                return
            
            for ind in range(len(panel)):
                if used[ind]:
                    continue
                used[ind]=True
                word.append(panel[ind])
                MakeWord(length,word)
                word.pop()
                used[ind]=False

        for length in range(1,len(panel)+1):
            MakeWord(length,[])
        self.words=list(self.words)
        validWords=[]
        for ind in range(len(self.words)):
            self.words[ind]=list(self.words[ind])
            wordStr="".join(self.words[ind])
            if self.wordDict.get(wordStr)!=None:
                validWords.append(self.words[ind])

        #filter only for valid words
        #Test for performance issue
        #not sure if the game is asking valid words from panel
        #development temp funs
        if filterOpen:
            self.words=validWords



    def GetScores(self, words):
        scores=0
        #valid words
        for word in words:
            for ch in word:
                scores+=self.scoreTable[ch]
        return scores
    def GetHighest(self):
        if self.highest:
            return self.highest[0]
        else:
            return ["None","None","None","None","None"]
    def Plot(self,word):
        locs=self.wordsScore[word]
        #(score,y,x,vertical,word)
        for loc in locs:
            score,y,x,vertical,_=loc
            plotGrid=copy.deepcopy(self.wordGrid)
            if not vertical:
                for ind in range(len(word)):
                    plotGrid[x][y+ind]=word[ind].upper()
            else:
                for ind in range(len(word)):
                    plotGrid[x+ind][y]=word[ind].upper()
            # print(plotGrid)

    def FillWord(self, row, col, dir, queue, mainWord, seen):
        if len(queue)==0:
            return
        #get new rol and col based on dirs
        if 0<=row<len(self.wordGrid) and 0<=col<len(self.wordGrid[0]):
            if self.tmpGrid[row][col]=="-":
                char=queue.pop(0)
                self.tmpGrid[row][col]=char
                mainWord.append(char)
                seen[(row,col)]=(row,col)
            else:
                mainWord.append(self.tmpGrid[row][col])
            newRow=row+dir[Coord.X.value]
            newCol=col+dir[Coord.Y.value]
            self.FillWord(newRow, newCol, dir, queue, mainWord, seen)

    def ExpandWord(self, row, col, dir, words):
        #check if current row and col are in valid location and it is chars
        if not (0<=row<len(self.wordGrid) and 0<=col<len(self.wordGrid[0]) and \
        self.wordGrid[row][col]!="-"):
            return
        words.append(self.wordGrid[row][col])
        row+=dir[Coord.X.value]
        col+=dir[Coord.Y.value]
        self.ExpandWord(row, col, dir, words)

    def GetMainWord(self, seen, filledWord, oriWord, move, otherWord=False):
        #first char and last char as two sides
        firCh=list(seen)[0]
        lasCh=list(seen)[-1]
        prefix=[]
        suffix=[]
        mainWords=[]
        #check horizontal directions
        if move==Move.Hori.value:
            self.ExpandWord(firCh[Coord.X.value], firCh[Coord.Y.value]-1, self.dirs.leftDir, prefix)
            self.ExpandWord(lasCh[Coord.X.value], lasCh[Coord.Y.value]+1, self.dirs.rightDir, suffix)
        #check vertical directions
        else:
            self.ExpandWord(firCh[Coord.X.value]-1, firCh[Coord.Y.value], self.dirs.upDir, prefix)
            self.ExpandWord(lasCh[Coord.X.value]+1, lasCh[Coord.Y.value], self.dirs.downDir, suffix)

        #if both prefix and suffix are empty->not valid word
        #if otherWord is not empty->valid
        #if prefix or suffix or len(filledWord)!=len(oriWord) or otherWord:
        #!!Confusing comments
        #tricking part for otherWord: the reason it is empty is either they don't have it/ or they are not valid
        #find another way to express "non-valid words"
        if prefix or suffix or otherWord or filledWord:
            prefix.reverse()
            candidate="".join(prefix+filledWord+suffix)
            if self.IsValidWord(candidate):
                mainWords.append(candidate)
                # print("final main word: ", candidate)
        return mainWords

    def GetOtherWord(self, seen, filledWord, move):
        locs=list(seen)
        otherWords=[]
        for ind in range(len(locs)):
            #for each char, check horizontal/vertical movement
            prefix=[]
            suffix=[]
            if move==Move.Hori.value:
                self.ExpandWord(locs[ind][Coord.X.value], locs[ind][Coord.Y.value]+1, self.dirs.rightDir, suffix)
                self.ExpandWord(locs[ind][Coord.X.value], locs[ind][Coord.Y.value]-1, self.dirs.leftDir, prefix)
            else:
                self.ExpandWord(locs[ind][Coord.X.value]-1, locs[ind][Coord.Y.value], self.dirs.upDir, prefix)
                self.ExpandWord(locs[ind][Coord.X.value]+1, locs[ind][Coord.Y.value], self.dirs.downDir, suffix)
            #if touching other letters in adjacent rows/cols, those must also form complete words
            if prefix or suffix:
                prefix.reverse()
                candidate="".join(prefix+[filledWord[ind]]+suffix)
                if self.IsValidWord(candidate):
                    otherWords.append(candidate)
                    # print("other formed word: ",candidate)
                else:
                    otherWords=[]
                    break
        return otherWords

    def Play(self):
        maxScore=0
        for word in self.words:
            wordMaxScore=0
            curWord="".join(word)
            for row in range(len(self.wordGrid)):
                for col in range(len(self.wordGrid[row])):
                    # print("row: ",row,"col: ",col) 
                    if self.wordGrid[row][col]=="-" and self.IsValidLoc(row, col, len(word)):
                        filledWord=[]
                        seen={}
                        #horizontal direction check 
                        #deep copy needs to be changed(TBC)
                        self.tmpGrid=copy.deepcopy(self.wordGrid)
                        self.FillWord(row, col, self.dirs.rightDir, word.copy(), filledWord, seen)
                        #if length of filledWord==original,which means we have filled out the empty 
                        #grid with the whole chosen word
                        if len(filledWord)==len(word):
                            #check vertical dirs
                            oterWords=self.GetOtherWord(seen, filledWord, Move.Vert.value)
                            mainWords=self.GetMainWord(seen, filledWord, word, Move.Hori.value, len(oterWords))
                            if not mainWords:
                                scoresHori=0
                            else:
                                scoresHori=self.GetScores(mainWords)+self.GetScores(oterWords)
                        else:
                            scoresHori=0

                        #vertical direction check 
                        filledWord=[]
                        seen={}
                        self.tmpGrid=copy.deepcopy(self.wordGrid)
                        self.FillWord(row, col, self.dirs.downDir, word.copy(), filledWord, seen)
                        if len(filledWord)==len(word):
                            #check horizontal dirs
                            oterWords=self.GetOtherWord(seen, filledWord, Move.Hori.value)
                            mainWords=self.GetMainWord(seen, filledWord, word, Move.Vert.value, len(oterWords))
                            if not mainWords:
                                scoresVerti=0
                            else:
                                scoresVerti=self.GetScores(mainWords)+self.GetScores(oterWords)
                        else:
                            scoresVerti=0

                        #compare vertical/horizontal scores, and get higher scores.
                        vertical=True
                        wordCurScore=0
                        if scoresHori>scoresVerti:
                            vertical=False
                            wordCurScore=scoresHori
                        else:
                            wordCurScore=scoresVerti

                        #check word value in this row and col in the following format: (score, y, x, vertical, word)
                        if wordCurScore>wordMaxScore:
                            self.wordsMaxScore[curWord]=[wordCurScore, str(col),str(row),str(vertical),curWord]
                            wordMaxScore=wordCurScore

            if self.wordsMaxScore.get(curWord)!=None:
                score = self.wordsMaxScore[curWord][0]
                if score>maxScore:
                    self.highest=[self.wordsMaxScore[curWord]]
                    maxScore=score
                elif score==maxScore:
                    self.highest.append(self.wordsMaxScore[curWord])
        print("highest: ",self.highest)

        
def main(argv):
    if len(argv)<2:
        print("please type python scrabble.py yourBoard.txt")
        return
    # print("boardFile: ",str(argv[1]) )
    game=Scrabble()
    tool=Utils()

    if tool.Init(str(argv[1])):
        filterOpen=False
        '''
        The function is doing too much. It should be split into several smaller functions, 
        each which have a smaller parameter set.
        There is another object hiding in there. You may need to create another object or data structure 
        that includes these parameters.
        '''
        game.Init(tool.GetDict(), tool.GetGrid(), tool.GetPanel(), tool.GetTable(), filterOpen)
        game.Play()
        tool.SaveFile(game.GetHighest())
    else:
        print("Init error")

if __name__ == "__main__":
    start=time.time()
    main(sys.argv[0:])
    end=time.time()
    print("time: ",end-start)

