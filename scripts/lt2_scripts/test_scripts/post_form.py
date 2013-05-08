import urllib

params = urllib.urlencode({'entry_312373567': '10 cm', 'entry_941467047': '5 cm', 'ss-submit': 'Submit'})
f = urllib.urlopen('https://docs.google.com/forms/d/1T0ZY1G08LPWRn3M_-yq--PAdrz_8LtqzQJn9AL3qZVs/formResponse', params)
print f.read()