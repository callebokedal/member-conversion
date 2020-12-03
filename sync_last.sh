#clear && docker run -it --rm --name my-test-script -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python from_mc_to_io.py \
#    sync_last
#    files/2020-11-22_17.55_mc_2-err_member_export.xlsx \
#    files/2020-11-13_MyClub_invoice_export.xls \
#    files/2020-11-22_17.55_all-io-members_export.xlsx

# 2020-11-25 ~00:20 Migration 5 persons
#clear && docker run -it --rm --name my-test-script -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python from_mc_to_io.py \
#    sync_last
#    files/2020-11-25_mc_5-err_member_export.xlsx \
#    files/2020-11-13_MyClub_invoice_export.xls \
#    files/finish/2020-11-24_23.30_all-io-members_export.xlsx

# 2020-11-25 ~23:40 Get all MC_Alla from IO and create import to add MedlemsId for each member in IO 
#clear && docker run -it --rm --name my-test-script -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python from_mc_to_io.py \
#    sync_last
#    files/2020-adas \ # MC in
#    files/2020-sf \   # MC Invoices
#    files/finish/2020-11-24_23.30_all-io-members_export.xlsx # IO in

# 2020-11-26 00:00 Get all MC_Alla from IO and create import to add MedlemsId for each member in IO 
clear && docker run -it --rm --name my-test-script -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python from_mc_to_io.py \
    update_medlemsid \
    files/exports/2020-11-26_23.40_mc_all_export.xlsx \
    files/2020-11-13_MyClub_invoice_export.xls \
    files/exports/2020-11-26_io_mc_alla_export.xlsx 
    #files/exports/2020-11-28_00.14_membersid_before_io_import