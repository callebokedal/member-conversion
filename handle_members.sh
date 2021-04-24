
#clear && docker run -it --rm --name my-test-script -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python \
#    compare_mc_and_io.py \
#    compare \
#    files/exports/2020-12-03_23.30_mc_all_export.xlsx \
#    files/exports/2020-12-07_23.45_io_all_export.xlsx

clear && docker run -it --rm --name my-test-script -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python \
    handle_members.py \
    contact_list \
    files/contact-list/2021-04-25_Exported-OL-All.xlsx 

