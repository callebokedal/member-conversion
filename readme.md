# SFK Members
Scripts to move members from My Club into IdrottOnline.

```from_mc_to_io.py``` is meant for moving Members from My Club to IdrottOnline. Lots of manual executions performed, code changed/imrpoved during the process.
This means that the code needs to be validated before anyone should re-use it. But "all" necessary functions, examples etc. are in place (just verify before executing live).

```from_io_to_mc.py``` is for moving members from Idrott Online into My Club.

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
clear && docker run -it --rm --name my-test-script -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python convert_members.py \
	files/2020-11-14_MyClub_all_member_export.xls \
	files/2020-11-13_MyClub_invoice_export.xls \
	files/2020-11-11_all-io-members2.xlsx
```