# sqltiny
Tiny SQL database CLI: query, import CSV, interactive shell.
```bash
python sqltiny.py -d test.db query "CREATE TABLE users (id INT, name TEXT)"
python sqltiny.py -d test.db import data.csv -t sales
python sqltiny.py -d test.db query "SELECT * FROM users" -f json
python sqltiny.py -d test.db shell
```
## Zero dependencies. Python 3.6+.
