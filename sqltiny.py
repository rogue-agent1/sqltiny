#!/usr/bin/env python3
"""sqltiny - Tiny SQL database CLI using sqlite3."""
import sqlite3, argparse, csv, json, sys, os

def main():
    p = argparse.ArgumentParser(description='Tiny SQL database CLI')
    p.add_argument('-d', '--db', default=':memory:', help='Database file (default: in-memory)')
    p.add_argument('-f', '--format', choices=['table','csv','json','tsv'], default='table')
    
    sub = p.add_subparsers(dest='cmd')
    
    q = sub.add_parser('query', help='Run SQL query')
    q.add_argument('sql')
    
    imp = sub.add_parser('import', help='Import CSV into table')
    imp.add_argument('file', help='CSV file')
    imp.add_argument('-t', '--table', default='data')
    
    sch = sub.add_parser('schema', help='Show database schema')
    
    sh = sub.add_parser('shell', help='Interactive SQL shell')
    
    args = p.parse_args()
    if not args.cmd: p.print_help(); return
    
    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    
    def output(cursor):
        rows = cursor.fetchall()
        if not rows: return
        cols = [d[0] for d in cursor.description]
        if args.format == 'json':
            print(json.dumps([dict(r) for r in rows], indent=2, default=str))
        elif args.format == 'csv':
            w = csv.writer(sys.stdout); w.writerow(cols)
            for r in rows: w.writerow(list(r))
        elif args.format == 'tsv':
            print('\t'.join(cols))
            for r in rows: print('\t'.join(str(v) for v in r))
        else:
            widths = [max(len(str(c)), max(len(str(r[i])) for r in rows)) for i, c in enumerate(cols)]
            fmt = ' | '.join(f'{{:<{w}}}' for w in widths)
            print(fmt.format(*cols))
            print('-+-'.join('-'*w for w in widths))
            for r in rows: print(fmt.format(*[str(v) for v in r]))
            print(f"\n({len(rows)} rows)")
    
    if args.cmd == 'query':
        try:
            cur = conn.execute(args.sql)
            if cur.description: output(cur)
            else: print(f"OK ({conn.total_changes} rows affected)")
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error: {e}", file=sys.stderr); sys.exit(1)
    elif args.cmd == 'import':
        with open(args.file) as f:
            reader = csv.DictReader(f)
            cols = reader.fieldnames
            conn.execute(f"CREATE TABLE IF NOT EXISTS {args.table} ({', '.join(f'{c} TEXT' for c in cols)})")
            for row in reader:
                placeholders = ','.join(['?']*len(cols))
                conn.execute(f"INSERT INTO {args.table} VALUES ({placeholders})", [row[c] for c in cols])
            conn.commit()
            print(f"Imported to {args.table}")
    elif args.cmd == 'schema':
        for row in conn.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL"):
            print(row[0])
    elif args.cmd == 'shell':
        print("sqltiny shell (Ctrl+D to exit)")
        while True:
            try:
                sql = input("sql> ").strip()
                if not sql: continue
                cur = conn.execute(sql)
                if cur.description: output(cur)
                else: print(f"OK ({conn.total_changes})")
                conn.commit()
            except EOFError: break
            except sqlite3.Error as e: print(f"Error: {e}")

if __name__ == '__main__':
    main()
