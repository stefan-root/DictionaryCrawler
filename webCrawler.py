import requests
from html.parser import HTMLParser
from urllib.parse import urlparse

class MyWebCrawler(HTMLParser):

    def __init__(self, sUrl, iTargetLevel):
        HTMLParser.__init__(self)
        if iTargetLevel > 0:
            print(iTargetLevel)
            print(sUrl)
            self.links = []
            self.words = []
            self.body = False
            code = self.retrieveWebsite(sUrl)
            self.feed(code)
            if iTargetLevel > 1:
                for link in self.links:
                    if "http" not in link:
                        link = self.getBaseUrl(sUrl) + link
                    w = MyWebCrawler(link, iTargetLevel - 1)
                    for word in w.words:
                        self.addWord(word)
                    for link in w.links:
                        self.addLink(link)

    def handle_starttag(self, tag, attrs):
        if tag == "a": 
            sLink = attrs[0][1]
            if "http" in sLink  or sLink[0] == "/":
                self.addLink(sLink)
        elif tag == "body":
            self.body = True

    def handle_endtag(self, tag):
        if tag == "body":
            self.body = False

    def handle_data(self, data):
        if self.body:
            self.getWords(data)

    def getBaseUrl(self, sUrl):
        oUrl = urlparse(sUrl)
        return(oUrl.scheme + "://" + oUrl.netloc)

    def retrieveWebsite(self, sUrl):
        sCode = requests.get(sUrl)
        return sCode.text

    def addWord(self, sWord):
        if sWord not in self.words:
            self.words.append(sWord)

    def addLink(self, sLink):
        if sLink not in self.links:
            self.links.append(sLink)        

    def getWords(self, sText):
        bIgnore = False
        sWord = ""
        sAlphabet = "abcdefghijklmnopqrstuvwxyzäüößABCDEFGHIJKLMNOPQRSTUVWXYZÄÜÖ-"
        sCapital = "ABCDEFGHIJKLMNOPQRSTUVWXYZÄÜÖ"

        for cLetter in sText:
            if cLetter == "<":
                bIgnore = True
            elif cLetter == ">":
                bIgnore = False
            elif (cLetter == " " or cLetter in sCapital) and bIgnore == False:
                if len(sWord) > 0:
                    self.addWord(sWord)
                if cLetter == " ":
                    sWord = ""
                else:
                    sWord = cLetter
            elif bIgnore == False and cLetter in sAlphabet:
                sWord += cLetter

    def writeToFile(self, aArray, sFilename):
        oFile = open(sFilename, "w")
        sFileText = ""
        for sElement in aArray:
            sFileText+= sElement + "\n"
        oFile.write(sFileText)
        oFile.close()

#Main

w = MyWebCrawler("https://de.wikipedia.org/wiki/Nico_Kuhn", 2)