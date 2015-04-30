# PyPhishTank
Python wrapper for the PhishTank Check URL API.

Example Usage
=============

```python

from pyphishtank import PhishTank

p = PhishTank()

result = p.check("http://example.com")

if result.in_database:
  if result.valid:
    print("{url} is a phish!".format(url=result.url))
  else:
    print("{url} is not a phish!".format(url=result.url))
else:
  print("{url} is not in the PhishTank database".format(url=result.url))
  
```
