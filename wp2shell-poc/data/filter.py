import csv

def get_first_column(path):
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        return [row[0] for row in reader if row and row[1] in ('6.9.0', '6.9.1', '6.9.2', '6.9.3', '6.9.4', '7.0.0', '7.0.1')]

values = get_first_column('wordpress_websites.csv')
filename = 'wp_domain.txt'

with open(filename, 'w', encoding='utf-8') as f:
    for v in values[1:]:
        f.write(v + '\n')

print(f'Total {len(values)} domain')