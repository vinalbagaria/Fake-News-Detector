from django.db import models


class ArticleExample(models.Model):
    # This will hold the visible text for this example
    body_text = models.TextField()
    # This bias score is a left-right bias provided by Media Bias Chart, but not used in this project.
    bias_score = models.FloatField()
    bias_class = models.IntegerField()
    # quality_score comes from the Media Bias Chart data
    quality_score = models.FloatField()
    # quality_class is based on the bias score and allows us to then integrate politifact data in their
    # 4-class way, True = 4, Mostly True = 3, Mostly Fake = 2, Fake = 1
    quality_class = models.IntegerField()
    
    origin_url = models.TextField()
    origin_source = models.TextField()

class DictEntry(models.Model):
    canonWord = models.TextField()
    
class UserEntry(models.Model):
    entryURL = models.URLField(verbose_name='URL of news article')

    
    
from bs4 import BeautifulSoup
from bs4.element import Comment
from urllib3.exceptions import HTTPError
import urllib3
import re, string
import json
import html
from io import StringIO
from nltk.stem import PorterStemmer 

class SoupStrainer():
    englishDictionary = {}
    haveHeadline = False
    recHeadline = ''
    locToGet = ''
    extractText = ''
    pageData = None
    errMsg = None
    soup = None
    msgOutput = True

    def init(self):
        with open('newsbot/words_dictionary.json') as json_file:
            self.englishDictionary = json.load(json_file)


    def tag_visible(self, element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def find_headline(self, soup):
        reOgTitle = re.compile('og:title', re.IGNORECASE)
        reTwTitle = re.compile('twitter:title', re.IGNORECASE)
        haveHeadline = False
        
        tstLine = soup.title(string=True)
        if(tstLine is not None):
            self.recHeadline = tstLine[0]
            haveHeadline = True
        
        if((not haveHeadline)):
            for meta in soup.find_all('meta'):
                if( ((meta.get('property') is not None) or (meta.get('name') is not None)) and (meta.get('content') is not None)):
                    if(meta.get('property') is not None):
                        prp = meta.get('property')
                    else:
                        prp = meta.get('name')
                
                if(reOgTitle.match(prp)):
                    haveHeadline = True
                    self.recHeadline = meta.get('content')

                if((not self.haveHeadline)):
                    if(reTwTitle.match(prp)):
                        haveHeadline = True
                        self.recHeadline = meta.get('content')
        
                if(haveHeadline):
                    break
                


    def loadAddress(self, address):
        self.locToGet = address
        self.haveHeadline = False

        htmatch = re.compile('.*http.*')
        user_agent = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'}
        ps = PorterStemmer() 

        if(htmatch.match(self.locToGet) is None):
            self.locToGet = "http://" + self.locToGet
        
        if(len(self.locToGet) > 5):
            if(self.msgOutput):
                print("Ready to load page data for: " + self.locToGet + " which was derived from " + address)

            try:
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                http = urllib3.PoolManager(2, headers=user_agent)
                r = http.request('GET', self.locToGet)
                self.pageData = r.data
                if(self.msgOutput):
                    print("Page data loaded OK")
                    #print(self.pageData)
            except:
                self.errMsg = 'Error on HTTP request'
                if(self.msgOutput):
                    print("Problem loading the page")
                return False
            self.extractText = ''
            self.recHeadline = self.locToGet
            self.soup = BeautifulSoup(self.pageData, 'html.parser')
            self.find_headline(self.soup)
            ttexts = self.soup.findAll(text=True)
            viz_text = filter(self.tag_visible, ttexts)
            allVisText = u"".join(t.strip() for t in viz_text)
            for word in allVisText.split():
                canonWord = word.lower()
                canonWord = canonWord.translate(str.maketrans('', '', string.punctuation))
                canonWord = canonWord.strip(string.punctuation)
                if(canonWord in self.englishDictionary):
                    canonWord = ps.stem(canonWord)
                    self.extractText = self.extractText + canonWord + " "
#                else:
#                    print("Excluded word: " + canonWord)

            return True


# Harvester.py: 
# Grab, parse, and store the examples provided by ad fontes media and apply their scores to the articles.
from django.contrib.gis.views import feed

import pandas as pd

ss = SoupStrainer()
print("Initializing dictionary...")
ss.init()

def harvest_Politifact_data():
    print("Ready to harvest Politifact data.")
    input("[Enter to continue, Ctl+C to cancel]>>")
    print("Reading URLs file")
    df_csv = pd.read_csv("politifact_data.csv", error_bad_lines=False, quotechar='"', thousands=',', low_memory=False)
    for index, row in df_csv.iterrows():
        print("Attempting URL: " + row['news_url'])
        if(ss.loadAddress(row['news_url'])):
            print("Loaded OK")
            # some of this data loads 404 pages b/c it is a little old, some load login pages. I've found that
            # ignoring anything under 500 characters is a decent strategy for weeding those out.
            if(len(ss.extractText)>500):
                ae = ArticleExample()
                ae.body_text = ss.extractText
                ae.origin_url = row['news_url']
                ae.origin_source = 'politifact data'
                ae.bias_score = 0 # Politifact data doesn't have this
                ae.bias_class = 5 # on this 1 to 4 scale, 5 is 'no data'
                ae.quality_score = row['score']
                ae.quality_class = row['class']
                ae.save()
                print("Saved, napping for 1...")
                time.sleep(1)
            else:
                print("**** This URL produced insufficient data.")
        else:
            print("**** Error on that URL ^^^^^")
    
    
    
def harvest_MBC_data():
    print("Ready to harvest Media Bias Chart data.")
    input("[Enter to continue, Ctl+C to cancel]>>")
    print("Reading URLs file")
    df_csv = pd.read_csv("MediaBiasChartData.csv", error_bad_lines=False, quotechar='"', thousands=',', low_memory=False)
    for index, row in df_csv.iterrows():
        print("Attempting URL: " + row['Url'])
        if(ss.loadAddress(row['Url'])):
            print("Loaded OK")
            ae = ArticleExample()
            ae.body_text = ss.extractText
            ae.origin_url = row['Url']
            ae.origin_source = row['Source']
            ae.bias_score = row['Bias']
            ae.quality_score = row['Quality']
            ae.bias_class = 5
            if(ae.quality_score <= 16.25):
                ae.quality_class = 1
            elif(ae.quality_score <= 32.50):
                ae.quality_class = 2
            elif(ae.quality_score <= 48.75):
                ae.quality_class = 3
            else:
                ae.quality_class = 4
            ae.save()
            print("Saved, napping for 1...")
            time.sleep(1)
        else:
            print("Error on that URL ^^^^^")
    
    

harvest_MBC_data()
harvest_Politifact_data()