# Adidas Captcha Product Finder /// Sitekey Fetcher
# made by @donnersyt

from classes.openfile import openfile
file = openfile()
file = file.readfile("config.json")

from classes.fetch import fetch
fetch = fetch(file)