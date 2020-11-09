
# Idea
https://pythonspeed.com/articles/base-image-python-docker-images/
https://hub.docker.com/_/python

# Build
docker build -t python-slim-buster .

# Run single scripts
# docker run -it --rm --name my-running-script -v "$PWD":/usr/src/myapp -w /usr/src/myapp python-slim-buster python your-daemon-or-script.py
docker run -it --rm --name my-test-script -v "$PWD":/usr/src/myapp -w /usr/src/myapp python-slim-buster python test.py

docker run -it --rm --name my-test-script -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python test.py

clear && docker run -it --rm --name my-test-script -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python test.py