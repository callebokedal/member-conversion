clear && docker run -it --rm --name my-test-script -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python compare_mc_and_io.py \
    compare \
    files/finish/2020-11-22_16.55_all_mc_exported_members.xlsx \
    files/finish/2020-11-22_18.05_all_io_exported_members.xlsx