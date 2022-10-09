"""
Basic PII Detection and Storage Tool
"""
import urllib.request
from tkinter import *
from pymongo import MongoClient
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import pprint


def search_key_in_content(cont):
    """
    Keyword search in contents stored in database
    """
    key = e1.get()
    adr = key.replace("", "].?[")
    adr = adr[3:-3]
    adr = adr.replace("[ ].?", "")
    ada = "\\b(" + adr + ")\\b"
    ad = re.findall(ada, cont, re.I)
    if ad:
        return "Full"
    else:
        adr = key.replace("", "X].?[")
        adr = adr[4:-3]
        adr = adr.replace("[ X].?", "")
        ada = "\\b(" + adr + ")\\b"
        ad = re.findall(ada, cont, re.I)
        if ad:
            return "Partial"
        else:
            return "Substring"


def categorize(input_string):
    """
    Categorizing into CAPTCHA, LOGIN, OTP
    """
    category = " "
    ad = re.search(r'captcha', input_string, re.I)
    if (ad):
        category = "CAPTCHA"
    ad = re.search(r'log ?in', input_string, re.I)
    if (ad):
        category = category + "LOGIN"
    ad = re.search(r'otp', input_string, re.I)
    if (ad):
        category = category + "OTP"
    return category


def contentsfmpage(url):
    """
    Extracting Contents from a url
    """
    try:
        # op.insert(INSERT, url + "\n")
        print(url)
        headers = {}
        headers['User-Agent'] = "Mozilla/5.0 (X11; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req)
        pagehtml = resp.read()
        pagesoup = BeautifulSoup(pagehtml, "html.parser")
        pagesoup = str(pagesoup)
        print("\n\n")
        return pagesoup
    except Exception as e:
        op.insert(INSERT, str(e))
        op.insert(INSERT, "\n")
        print(e)
        return str(e)
    window.update_idletasks()


def links_to_database():
    """
    Database Connection and Insertion of link, content, categorization, Presence into the database
    """
    window.update_idletasks()
    # database connection and storage
    client = MongoClient('127.0.0.1', 27017)
    db = client.test
    coltn = db.pii
    op.insert(INSERT, "\nDatabase Connection formed successfully \n Inserting into Mongodb...\n")
    op.insert(INSERT, str(url_list))

    try:
        for lnk in url_list:
            cont = contentsfmpage(lnk)
            coltn.insert_one({"Keyword": e1.get(), "SearchUrl": lnk, "Category": categorize(cont),
                          "Presence": search_key_in_content(cont)})
            # op.insert(INSERT, "Successfully Inserted in DB\n")
            window.update_idletasks()
            # print("Successfully Inserted in DB\n")
        coltn = db.key
        coltn.insert_one({"Key": e1.get()})
        op.insert(INSERT, "Keyword inserted in Keys collection in test\n")
        client.close()
        op.insert(INSERT, "\n Insertion Complete...\n Database Connection Terminated")
    except Exception as e:
        op.insert(INSERT, str(e))
        op.insert(INSERT, "\n")
        window.update_idletasks()
        print(e)


def keywordsearch(event):
    op.insert(INSERT, "Processing...\n")
    window.update_idletasks()
    keys = e1.get()
    keys = keys.replace(" ", "+")
    url = "https://www.google.com/search?q=" + keys
    headers = {}

    user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"
    headers['User-Agent'] = user_agent

    req = urllib.request.Request(url, headers=headers)
    op.delete(1.0, END)
    try:
        resp = urllib.request.urlopen(req, timeout=3)
        respData = resp.read()
        soup = BeautifulSoup(respData, "html.parser")
        print(soup)
        # link = soup.find_all("a", {"class": "BNeawe UPmit AP7Wnd"})
        link = []
        for links in soup.findAll('a'):
            link.append(links.get('href'))
        print(link)
        print("\n\n")
        op.insert(INSERT, "Links retrieved from Google:\n")
        for lin in link:
            print(lin)
            # match = re.search(r'href=[\'"]?([^\'" >]+)', str(lin))
            match = re.search(r'(http.+)', str(lin))

            print(match)
            if match:
                # ser = match.group(0)
                # po = ser[6:]
                po = match.group(0)
                print(po)
                op.insert(INSERT, po + "\n")
                url_list.append(po)
        links_to_database()
    except Exception as e:
        print(e)
        op.insert(INSERT, str(e))
        op.insert(INSERT, "\n")


def show_results(event):
    client = MongoClient('127.0.0.1', 27017)
    db = client.test
    coltn = db.adarsh
    a = coltn.find({})
    for doc in a:
        pprint.pprint(doc)
        op.insert(INSERT, doc)
        op.insert(INSERT, "\n")
    client.close()


def retrieval(event):
    op.delete('1.0', END)
    key = e1.get()
    client = MongoClient('127.0.0.1', 27017)
    db = client.test
    coltn = db.adarsh
    try:
        var = varr.get()
        if var == "LOGIN":
            sql = coltn.find({"Keyword": key, "Category": " LOGIN"}, {"Category": 0, "_id": 0, "Presence": 0})
        elif var == "OTP":
            sql = coltn.find({"Keyword": key, "Category": " OTP"}, {"Category": 0, "_id": 0, "Presence": 0})
        elif var == "CAPTCHA":
            sql = coltn.find({"Keyword": key, "Category": " CAPTCHA"}, {"Category": 0, "_id": 0, "Presence": 0})
        elif var == "COMPLETE":
            sql = coltn.find({"Keyword": key, "Presence": "Full"}, {"Category": 0, "_id": 0, "Presence": 0})
        elif var == "PARTIAL":
            sql = coltn.find({"Keyword": key, "Presence": "Partial"}, {"Category": 0, "_id": 0, "Presence": 0})
        elif var == "SUBSTRING":
            sql = coltn.find({"Keyword": key, "Presence": "Substring"}, {"Category": 0, "_id": 0, "Presence": 0})
        for doc in sql:
            pprint.pprint(doc)
            op.insert(INSERT, doc)
            op.insert(INSERT, "\n")
    except Exception as e:
        print(e)
        op.insert(INSERT, "Please Select a category before pressing OK")
    client.close()


#################################################  MAIN  ##############################################################

url_list = []

# UI code

# Main Window Settings
window = Tk()
window.title("Web Enabled Search Tool for Identifying PII")
window.geometry('1200x600+0+0')
window.resizable(width=False, height=False)

l1 = Label(window, text="    ")
l1.grid(row=1, column=0)
l2 = Label(window, text="    ")
l2.grid(row=3, column=0)

# Entry Box-1
e1 = Entry(window)
print(e1.get())
e1.grid(row=2, column=1, sticky=E)
e1.focus()
e1.bind("<Return>", keywordsearch)

# Output Box
op = Text(master=window, height=28, width=145)
op.grid(row=4, column=1, sticky=NSEW, columnspan=2)

# Button GO
but = Button(window, text='GO', font=("Times New Roman", 10))
but.grid(row=2, column=2, sticky=W)
but.bind("<Button-1>", keywordsearch)

# Button View Results
but1 = Button(window, text='OK', font=("Times New Roman", 10))
but1.grid(row=5, column=1, sticky=E)
but1.bind("<Button-1>", retrieval)

varr = StringVar(window)
varr.set('Choose Category')
choices = ['LOGIN', 'OTP', 'CAPTCHA', 'COMPLETE', 'PARTIAL', 'SUBSTRING']
option = OptionMenu(window, varr, *choices)
option.grid(row=5, column=2, sticky=W)

window.mainloop()
