#clear && docker run -it --rm --name my-test-script -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python compare_mc_and_io.py \
#    compare \
#    files/finish/2020-11-22_16.55_all_mc_exported_members.xlsx \
#    files/finish/2020-11-22_18.05_all_io_exported_members.xlsx

#clear && docker run -it --rm --name my-test-script -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python compare_mc_and_io.py \
#    compare_persons \
#    files/finish/2020-11-24_23.35_all_mc_exported_members.xlsx \
#    files/finish/2020-11-24_23.30_all-io-members_export.xlsx

# 2020-11-26
clear && docker run -it --rm --name my-test-script -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python compare_mc_and_io.py \
    compare_persons \
    files/exports/2020-11-26_23.40_mc_all_export.xlsx \
    files/exports/2020-11-26_io_mc_alla_export.xlsx