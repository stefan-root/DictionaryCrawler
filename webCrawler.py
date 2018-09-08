import requests
from html.parser import HTMLParser
from urllib.parse import urlparse
import locale

class MyWebCrawler(HTMLParser):

    def __init__(self, sUrl, iTargetLevel):
        HTMLParser.__init__(self)
        if iTargetLevel > 0:
            print(sUrl) # print current website
            self.links = []
            self.words = []
            self.body = False
            code = self.retrieveWebsite(sUrl)
            self.feed(code) # HTML parsing
            if iTargetLevel > 1: # parsing lower levels
                for link in self.links:
                    if "http" not in link:
                        link = self.getBaseUrl(sUrl) + link # build full link for relative referneces
                    w = MyWebCrawler(link, iTargetLevel - 1)
                    for word in w.words:
                        self.addWord(word) # add words from lower levels

    def handle_starttag(self, tag, attrs): # eventhandler, triggered by parser at starttags
        if tag == "a": # find links
            sLink = attrs[0][1]
            if "http" in sLink  or sLink[0] == "/":
                self.addLink(sLink)
        elif tag == "body": # only use words from body
            self.body = True

    def handle_endtag(self, tag): # eventhandler, triggered by parser at endtag
        if tag == "body":
            self.body = False

    def handle_data(self, data): #eventhandler, triggered by parser at data
        if self.body:
            self.getWords(data) # get words from body

    def getBaseUrl(self, sUrl): # get base Url (without path)
        oUrl = urlparse(sUrl)
        return(oUrl.scheme + "://" + oUrl.netloc)

    def retrieveWebsite(self, sUrl): # get full code of website
        sCode = requests.get(sUrl)
        return sCode.text

    def addWord(self, sWord): # add word to catalog, no duplicates
        if sWord not in self.words:
            self.words.append(sWord)

    def addLink(self, sLink): # add link to catalog, no duplicates
        if sLink not in self.links:
            self.links.append(sLink)        

    def getWords(self, sText): # find words in text
        sWord = ""
        sAlphabet = "abcdefghijklmnopqrstuvwxyzäüößABCDEFGHIJKLMNOPQRSTUVWXYZÄÜÖ-"
        sCapital = "ABCDEFGHIJKLMNOPQRSTUVWXYZÄÜÖ"

        for cLetter in sText:
            if (cLetter == " " or cLetter in sCapital):  # start new word at space or capital letter
                if len(sWord) > 0: # add old word to catalog
                    self.addWord(sWord)
                if cLetter == " ": # start new word
                    sWord = ""
                else:
                    sWord = cLetter
            elif cLetter in sAlphabet: # add letter to word
                sWord += cLetter

    def writeToFile(self, aArray, sFilename): # write word-catalog to file
        oFile = open(sFilename, "w", encoding = locale.getpreferredencoding())
        sFileText = ""
        for sElement in aArray:
            sFileText+= sElement + "\n"
        oFile.write(sFileText)
        oFile.close()

#Main

w = MyWebCrawler("https://de.wikipedia.org/wiki/Berlin", 2)
w.words.sort()
w.writeToFile(w.words, "test")