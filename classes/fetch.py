import os, time, requests, sys, math
from datetime import datetime
try:
    try:
        from bs4 import BeautifulSoup
    except:
        pass
    try:
        from BeautifulSoup4 import BeautifulSoup
    except:
        pass
except:
    pass

class fetch():
    def __init__(self, file):
        try:
            self.sleeptime = float(file["delayInSeconds"])
        except:
            self.exiting("Sleep time is not in seconds/not a number")
        if "com.au" in file["adidas_url"]:
            file["adidas_url"] = "https://www.adidas.com.au/men-shoes"
            self.region = "AU"
            print("Using www.adidas.com.au (AU)")
        elif "co.uk" in file["adidas_url"]:
            file["adidas_url"] = "http://www.adidas.co.uk/men-shoes"
            self.region = "UK"
            print("Using www.adidas.co.uk (UK/GB)")
        elif "com" in file["adidas_url"]:
            file["adidas_url"] = "http://www.adidas.com/us/men-shoes"
            self.region = "US"
            print("Using www.adidas.com (US)")
        elif "ca" in file["adidas_url"]:
            file["adidas_url"] = "http://www.adidas.ca/en/men-shoes"
            self.region = "CA"
            print("Using www.adidas.ca (CA)")

        else:
            self.exiting("Only .co.uk .com .com.au .ca are currently supported. Please update config.json")
        self.kount = 1
        self.file = file
        self.s = requests.session()
        self.s.headers.update({"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"})
        self.totalProducts = None
        self.startTime = datetime.now().strftime("%H:%M:%S")
        self.format = "%H:%M:%S"
        self.run()

    def tprint(self, string):
        sys.stdout.write('\r' + str(string))

    def fetch(self, num, firstrun=False):
        params = {
            "sz":"120",
            "start":num
        }
        page = self.s.get(self.file["adidas_url"], params=params)
        if page.status_code != 200:
            print("Error code %s" % (page.status_code))
            time.sleep(10)
            self.fetch(num, firstrun)
        try:
            soup = BeautifulSoup(page.text, "html.parser")
        except:
            soup = BeautifulSoup(page.text, "lxml")
        if firstrun is True:
            try:
                self.totalProducts = int(soup.find("p",{"class":"count"}).string.strip().replace("(","").replace(")","").replace("Products","").replace(",",""))
                print("There are %s products to check" % self.totalProducts)
            except:
                self.exiting("Error loading total products")
        products = soup.find("div",{"id":"product-grid"})
        productslist = products.find_all("div",{"class":"product-info-inner-content clearfix with-badges"})
        productslist += products.find_all("div",{"class":"product-info-inner-content clearfix "})
        for product in productslist:
            product = product.find("a").get("href")

            self.tprint("Checking %s / %s | %s" % (self.kount, self.totalProducts, self.diff_times_in_seconds(datetime.strptime(self.startTime, self.format).time(),datetime.strptime( datetime.now().strftime(self.format), self.format).time()) ))
            self.kount += 1
            self.checkforrecap(product)
            time.sleep(self.sleeptime)

    def checkforrecap(self, product):
        page = self.s.get(product)
        if page.status_code != 200:
            self.tprint("Error code on prod page %s (%s/%s)" % (page.status_code, self.kount, self.totalProducts))
            time.sleep(10)
            self.checkforrecap(product)
        try:
            soup = BeautifulSoup(page.text, "html.parser")
        except:
            soup = BeautifulSoup(page.text, "lxml")
        cap = soup.find("div",{"class":"g-recaptcha"})
        if cap is not None:

            try:
                cap = cap.get("data-sitekey")
            except:
                cap = None

            if cap is not None:
                self.tprint("%s/%s | %s - %s" % (self.kount, self.totalProducts, cap, page.url))
                print()
                self.recordkey(cap, soup, page.url)

    def recordkey(self, cap, soup, pageURL):
        try:
            prodName = soup.find("meta", {"property":"og:title"}).get("content")
        except:
            prodName = None
        try:
            pid = pageURL.split("/")[-1].replace(".html","")
            if len(pid) != 6:
                pid = None
        except:
            pid = None
        nowTime = time.strftime("%H:%M:%S")
        lineToWrite = "[%s] %s | " % (self.region, nowTime)
        if prodName is None:
            if pid is None:
                lineToWrite += """%s - %s""" % (cap, pageURL)
            if pid is not None:
                lineToWrite += """%s - %s""" % (cap, pid)
        if prodName is not None:
            if pid is None:
                lineToWrite += """%s - %s""" % (cap, prodName)
            if pid is not None:
                lineToWrite += """%s - %s - %s""" % (cap, prodName, pid)
        try:
            with open("sitekeys.txt", "a") as f:
                f.write(lineToWrite)
        except:
            pass

    def exiting(self, message=""):
        if message != "":
            print(message)
        for i in range(3):
            i = 3 - i
            self.tprint("Exiting in %s" % (i))
            time.sleep(1)
        self.tprint("Exited")
        os._exit(1)

    def diff_times_in_seconds(self, t1, t2):
        # caveat emptor - assumes t1 & t2 are python times, on the same day and t2 is after t1
        h1, m1, s1 = t1.hour, t1.minute, t1.second
        h2, m2, s2 = t2.hour, t2.minute, t2.second
        t1_secs = s1 + 60 * (m1 + 60 * h1)
        t2_secs = s2 + 60 * (m2 + 60 * h2)
        return (time.strftime(self.format, time.gmtime(t2_secs - t1_secs)))

    def run(self):
        self.fetch("0", True)
        for x in range(math.ceil((self.totalProducts / 120) - 1)):
            x = (x+1) * (120)
            self.fetch(str(x), False)
        leftover = self.totalProducts - self.kount
        if leftover > 0:
            print()
            print("%s products left over... Adidas page loading broke somewhere! ^_^" %(leftover))
        elif leftover < 0:
            print()
            print("%s products too many... Adidas page loading broke somewhere! ^_^" % (leftover * (-1)))