# OS Specific

## Linux / Mac
#clear && docker run -it --rm --name sfk_members -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python \
#    from_io_to_mc.py \
#    compare \
#    files/exports/2021-10-30_all_members_from_mc.xlsx \
#    files/exports/2021-10-30_all_members_from_io.xlsx

## Win
docker run -it --rm --name sfk-members -v "$(pwd):/home/me" -w /home/me python-slim-buster python from_io_to_mc.py compare 'files/exports/2021-10-30_all_members_from_mc.xlsx' 'files/exports/2021-10-30_all_members_from_io.xlsx'

## Interactive bash
# docker run -it --rm --name sfk-members python-slim-buster bash 

## Interactive python
# docker run -it --rm --name sfk-members python-slim-buster

## Copy file from Win to docker instance
# Ex: docker container cp C:\temp\index.html sfk_members:C:\inetpub\wwwroot\index.html

# Common actions

## To stop
# docker container stop sfk_members

## To remove
# docker container rm sfk_members