
#clear && docker run -it --rm --name my-test-script -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python \
#    compare_mc_and_io.py \
#    compare \
#    files/exports/2020-12-03_23.30_mc_all_export.xlsx \
#    files/exports/2020-12-07_23.45_io_all_export.xlsx

# 1. Export all Members
# 2. Exportera till Excel, välj kolumner
# 3. Exportera med personnummer/födelsedatum + Inkludera målsman + Markera allt

clear && docker run -it --rm --name my-test-script -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python \
    handle_members.py \
    contact_list \
    files/contact-list/2021-11-11_All_OL_Members_incl_parents.xlsx

# For Frisksporttidningen
clear && docker run -it --rm --name my-test-script -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python \
    handle_members.py \
    frisksport \
    files/exports/to-mc-ht2021/2021-11-15_all_members_from_io.xlsx