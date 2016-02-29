# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 10:33:28 2016

@author: william.jobs
"""

from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.support.ui import *
from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support.ui import WebDriverWait
import csv
import sys
import time

args = sys.argv[1:]
if len(args) == 2:
	# assumed order is input followed by output
	if args[0][-4:]=='.csv' and args[1][-4:]=='.csv':
		IN_FILE = args[0]
		OUT_FILE = args[1]
	else:
		IN_FILE = "ChemID_search.csv"
		OUT_FILE = "ChemID_results.csv"
elif len(args)==1:
	# assume the one argument passed is the input CSV
	
	# check it ends in .csv before using it
	if args[0][-4:]=='.csv':
		IN_FILE = args[0]	
	else:
		IN_FILE = "ChemID_search.csv"
		
	OUT_FILE = "ChemID_results.csv"	
else:
	IN_FILE = "ChemID_search.csv"
	OUT_FILE = "ChemID_results.csv"


class NotFoundException(Exception):
    """Exception raised when we can't find the searched for CAS or name
    Attributes:
        search -- the search string
        msg  -- explanation of the error
    """
    def __init__(self, search, msg):
        self.search = search
        self.msg = msg

# function to wait until one of the possible_ids shows up
def wait_for_page(driver, possible_ids=[], seconds=20, interval_to_poll=0.5):
	i = 0	
	while(True):
		if i >= seconds/interval_to_poll:
			raise NotFoundException(search = '', msg='Page too slow to load or element never loaded')
			
		page = pq(driver.page_source)
		page = page.remove_namespaces()
		
		for page_id in possible_ids:
			if page('#' + page_id).length > 0:
				return
		
		time.sleep(interval_to_poll)
		i = i + 1
								

intxt=open(IN_FILE)
outtxt=open(OUT_FILE,"wb")
outwriter = csv.DictWriter(outtxt, fieldnames=["Raw Input", "Searched", "CASRN", "Chemical Name", "Problem(s)?"], quoting=csv.QUOTE_ALL)
outwriter.writeheader()

reader=csv.reader(intxt)
row_count = sum(1 for row in reader)
i = 0
intxt.seek(0)

driver = webdriver.Firefox()
driver.implicitly_wait(10)

for row in reader:
	start = time.time()
	outrow = {'Raw Input': row[0], 'Searched': row[0], 'CASRN': '', 'Chemical Name': '', 'Problem(s)?': ''}
	mystr = ""
	element = None
	
	# try to make a CASRN	
	# remove dashes, if any, and format correctly
	outrow['Searched'] = outrow['Searched'].replace("-","")
	if outrow['Searched'].isdigit():
		is_cas = True
		# all digits; it was a CASRN. Format it with dashes correctly
		outrow['Searched'] = outrow['Searched'][:-3] + '-' + outrow['Searched'][-3:-1] + '-' + outrow['Searched'][-1:]
	else:
		# It was not a CASRN. Restore to text as provided, possibly with dashes.
		is_cas = False
		outrow['Searched'] = row[0]		

	driver.get('http://chem.sis.nlm.nih.gov/chemidplus/chemidlite.jsp')
	# element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "QV1"))) # old way to wait, using Selenium
	wait_for_page(driver=driver, possible_ids=['QV1'], seconds=20, interval_to_poll=0.5)
	
	
	select = Select(driver.find_element_by_id('QF1'))
	if is_cas:
		select.select_by_value('number')
	else:
		select.select_by_value('name')
	select = Select(driver.find_element_by_id('QO1'))
	select.select_by_value('equals')
	
	txt=driver.find_element_by_id('QV1')
	txt.send_keys(outrow['Searched'])
	txt.send_keys(Keys.ENTER)
	#driver.find_element_by_css_selector("button.btn.btn-search").click()
	
	try:
		# wait until we load 
		#    (1) the possible results page, listing matched names (which will have an element with id=resultsContent), 
		#    (2) the possible results page, showing structures (which will have an element with id=Record_Span), 
		#    OR (3) the result page itself (which will have an element with id=summary)
		wait_for_page(driver=driver, possible_ids=['resultsContent','Record_Span','summary'], seconds=20, interval_to_poll=0.5)
		page = pq(driver.page_source)
		
	
		if page('#resultsContent').length > 0:
			# we got the page with possible results listing matched names
			
			# look for the div with the suggested option			
			mystr = page("#resultsContent > .eq")
			if mystr.length==0:
				# no suggested option
				raise NotFoundException(search = outrow['Searched'], msg='No match found for searched item')
			else:
				# click the suggestion
				driver.find_element_by_css_selector('#resultsContent > .eq + h3 div a').click()
	
				# wait until we get the result page
				wait_for_page(driver=driver, possible_ids=['summary'], seconds=20, interval_to_poll=0.5)			
				page = pq(driver.page_source)
		elif page('#Record_Span').length > 0:
			# we got the page with possible results listing matched names
			
			# click the FIRST suggestion (usually best match)
			print 'For "' + outrow['Searched'] + '" we clicked "' + page.remove_namespaces()('div.resultCol1 td.innerCol1 a span').html() + '"'
			driver.find_element_by_css_selector('div.resultCol1 td.innerCol1 a span').click()
			
			
			# wait until we get the result page
			wait_for_page(driver=driver, possible_ids=['summary'], seconds=20, interval_to_poll=0.5)
			page = pq(driver.page_source)
			
				
				
		page = page.remove_namespaces()
		element = page("div#summary > div:not(#structure) > h1")
		if element.length==0:
			# we're not on the result page
			raise NotFoundException(search = outrow['Searched'], msg="Either result page HTML doesn't match expected HTML, or we never got to the result page for some reason.")
			
		mystr = element.html().encode('utf8').replace('\xc2\xa0','')
		
		# get the chemical name		
		outrow['Chemical Name'] = mystr[mystr.find('Substance Name:')+len('Substance Name:'):mystr.find('<br')]
		
		# find the CASRN		
		element = page("div#summary > div:not(#structure) > h1 > span")
		for span in element.items():
			if 'RN:' in span.text().encode('ascii','ignore'):
				mystr = span.text().encode('ascii','ignore')
				break		
		outrow['CASRN'] = mystr[mystr.find('RN:')+len('RN:'):]
	
	except Exception as e:
		if type(e).__name__ == 'NotFoundException':
			print e.msg + '; occurred with search: ' + outrow['Searched']
			outrow['Problem(s)?']=e.msg
		else:
			print e
			outrow['Problem(s)?']=type(e).__name__
			
		if outrow['Chemical Name'] == "":
			outrow['Chemical Name'] = "NO MATCH"
		if outrow['CASRN'] == "":
			outrow['CASRN'] = "NO MATCH"
		
	outwriter.writerow(outrow)
		
	print str(i+1) + ' of ' + str(row_count) + ' complete! (' + outrow['Raw Input'] + ')'
	i = i + 1
	

driver.close()
outtxt.close()
intxt.close()