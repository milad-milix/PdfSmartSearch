'''
Created on Nov 23, 2017

@author: Milad
'''

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox
import re, os
 
class PdfMinerWrapper(object):
    def __init__(self, pdf_doc, pdf_pwd=""):
        self.pdf_doc = pdf_doc
        self.pdf_pwd = pdf_pwd
 
    def __enter__(self):
        #open the pdf file
        self.fp = open(self.pdf_doc, 'rb')
        # create a parser object associated with the file object
        parser = PDFParser(self.fp)
        # create a PDFDocument object that stores the document structure
        doc = PDFDocument(parser, password=self.pdf_pwd)
        # connect the parser and document objects
        parser.set_document(doc)
        self.doc=doc
        return self
    
    def _parse_pages(self):
        rsrcmgr = PDFResourceManager()
        laparams = LAParams(char_margin=3.5, all_texts = True)
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
    
        for page in PDFPage.create_pages(self.doc):
            interpreter.process_page(page)
            # receive the LTPage object for this page
            layout = device.get_result()
            # layout is an LTPage object which may contain child objects like LTTextBox, LTFigure, LTImage, etc.
            yield layout
    def __iter__(self): 
        return iter(self._parse_pages())
    
    def __exit__(self, _type, value, traceback):
        self.fp.close()
            
def search(filename,wordList = []):
    page_list = []
    count_match=0
    word_container = []
    page_container = []
    doc = TextFileToArray(filename)
    for page in doc: #each page in the pdf
        page_container = [] # reset
        count_match = 0  # reset 
        page_is_complete = 0    
        for word in wordList: # for each word queried by user
            splat = page.split("<paragraph></paragraph>") #split by paragraph
            for number, tbox in enumerate(splat, 1): #get each paragraph in the page
                paragraph  = tbox.encode("ascii", "ignore").decode("ascii")
                if(page_is_complete != 1):
                    page_container.append(paragraph) #keep the paragraph for performance
                if re.search(word, paragraph, re.IGNORECASE): #increment if word exists
                    if word in word_container:
                        pass
                    else:
                        word_container.append(word)
                        count_match+=1
            page_is_complete = 1
        word_container = []
        if(count_match==len(wordList)): #if all our words are in the page
            for tbox2 in page_container: #get each paragraph in the page
                count_match2 = 0
                paragraph2  = tbox2
                for word2 in wordList: #check each word in the list
                    if re.search(word2, paragraph2, re.IGNORECASE):
                        count_match2+=1
                if(count_match2>0): #if the paragraph has any of the words
                    for word3 in wordList:
                        try:
                            sourceCaseMatch = re.findall(word3, paragraph2, re.IGNORECASE)[0]
                            paragraph2 = paragraph2.replace(sourceCaseMatch, "<b><font size='3' color='red'>"+word3+"</font></b>")
                        except:
                            pass                            
                        #paragraph2 = paragraph2.replace(word3, "<b><font size='3' color='red'>"+word3+"</font></b>")
                    page_list.append(paragraph2) #append this paragraph
            page_list.append('############## Page: ##############')
    result = ""
    for page in page_list:
        result += page
    return result

#retrieve pages from text file
def TextFileToArray(filename):
    file_path = os.path.join('C:\Users\Sara\workspace\PdfSearchEngine\ui', filename)
    f = open(file_path+'.txt', 'r')
    data = f.read()
    listOfPages = []
    splat = data.split("<splitter></splitter>")
    for number, page in enumerate(splat, 1):
        listOfPages.append(page)
    del listOfPages[-1]
    return listOfPages

#convert pdf to text file
def PdfToTextFile(filename):
    page_list = []
    file_path = os.path.join('C:\Users\Sara\workspace\PdfSearchEngine\ui', filename)
    with PdfMinerWrapper(file_path) as doc: #get the pdf doc
        for page in doc: #each page in the pdf
            for tbox in page: #get each paragraph in the page
                    if not isinstance(tbox, LTTextBox):
                        continue
                    paragraph  = tbox.get_text().encode("ascii", "ignore").decode("ascii")
                    page_list.append(paragraph)
                    page_list.append('<paragraph></paragraph>')
            page_list.append('<splitter></splitter>')
    textFile = open(filename+'.txt', "w") #make text file
    for item in page_list:  #write text to text file
        textFile.write("%s\n\n\n" % item)
    