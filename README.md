Run the following command to install the required packages:
```shell
pip install -r requirements.txt
```

Run the following command to execute the script:
```shell
python3 main.py
```

This will produce a spreadsheet in the `out` directory. Each cell in row `r` column `c` contains the expected time to
complete the achievement with `r` deficit and `c` rolls remaining. The cell is green if you should keep rolling, and
red if you should reset.

An example output spreadsheet is included in the `out` directory.
