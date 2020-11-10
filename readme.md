# SFK Members
Scripts to move members from My Club into IdrottOnline

## Tips
https://pythonspeed.com/articles/base-image-python-docker-images/
https://hub.docker.com/_/python

### Merging
https://pandas.pydata.org/pandas-docs/stable/user_guide/merging.html

# Build
```bash
docker build -t python-slim-buster .
```
# Run single scripts
```bash
docker run -it --rm --name my-test-script -v "$PWD":/usr/src/myapp -w /usr/src/myapp python-slim-buster python test.py
```

```bash
docker run -it --rm --name my-test-script -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python test.py
```
```bash
clear && docker run -it --rm --name my-test-script -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python test.py
```
## Merge MC group export files with files containing full personnummer
```bash
clear && docker run -it --rm --name my-test-script -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python handle_members.py
```
## Convert and join My Club and IO members
```bash
clear && docker run -it --rm --name my-test-script -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python convert_members.py
```

# My Club helper
To get memberId and full Personnummer
Note! Check visible columns - to get them to match the script below

How to?
1. Login to My Club. Go to members. 
2. Make sure all rows/members are visible on the same (one) page
3. Open bowser developer console
4. Paste and execute script below
5. Copy to textfile. See handle_members.py for action (of joining this data)
```js
var s = ""; document.querySelectorAll("#member-list-table tr").forEach(row => {
	if(row.querySelector("td:nth-child(3)")) {
		var mId = row.querySelector("td:nth-child(3)").innerText;
		var pNr = row.querySelector("td:nth-child(4)").innerText;
	  //console.log(mId);
	  //console.log(pNr);
	  //console.info(mId + ", " + pNr);
		s += mId + ", " + pNr + "\n";
	}
}); console.info(s);
```