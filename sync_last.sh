#clear && docker run -it --rm --name my-test-script -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python from_mc_to_io.py \
#    sync_last
#    files/2020-11-22_17.55_mc_2-err_member_export.xlsx \
#    files/2020-11-13_MyClub_invoice_export.xls \
#    files/2020-11-22_17.55_all-io-members_export.xlsx

# 2020-11-25 ~00:20 Migration 5 persons
clear && docker run -it --rm --name my-test-script -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python from_mc_to_io.py \
    sync_last
    files/2020-11-25_mc_5-err_member_export.xlsx \
    files/2020-11-13_MyClub_invoice_export.xls \
    files/finish/2020-11-24_23.30_all-io-members_export.xlsx