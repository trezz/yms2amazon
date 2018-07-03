"""
Convert a CSV file extracted from the G7 software into a proper
CSV file compatible with Excel.
"""

import sys
import os
import subprocess
import csv
import re

def create_row_iterator(filepath):
   '''Load the given CSV file and yield an iterator on the contained rows'''
   with open(filepath, encoding='utf-8', newline='') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            yield row

def filter_article(ref, name, storage, num, price):
    '''Given an article, filter the articles according to their
    availability, storage, etc...
    Return True if the article need to be kept, False otherwise.
    '''
    # p = re.compile('^G.*|^VITRINE.*|^MOTO EXPO.*|^PALETTE.*')
    return  (int(ref[0:2])>= 96) # and (num > 0) and (None != re.match(p, storage))

def get_img_url(ref, title):
    '''Given a product's reference, returns an image URL that should correspond
    to this reference and its title.
    '''
    scriptpath = os.path.realpath(__file__)
    scriptdir = os.path.dirname(scriptpath)
    cmd = [
        'python',
        os.path.join(scriptdir, 'resources', 'google_images_download.py'),
        '--limit', '1',
        '--keywords="' + ref + '"',
        '-p'
    ]
    cmd = ' '.join(cmd)
    output = subprocess.check_output(cmd, shell=True).decode('utf-8')
    for line in output.splitlines():
        line = re.findall(r'^Image URL.*', line)
        if line:
            return line[0].split()[2]
    print(output, file=sys.stderr)
    raise Exception("Invalid output from google image download")

def create_dict(filepath):
    '''Create a dictionary from the input CSV file'''
    d = {
        'num_articles' : 0,
        'ref' : [],
        'name' : [],
        'image' : [],
        'storage' : [],
        'num' : [],
        'bying_price_ht' : [],
    }
    csv_row_iter = create_row_iterator(filepath)
    i = 0
    for row in csv_row_iter:
        try:
            reference = row[0].strip()
            product_name = row[1].strip()
            # storage = row[2].strip()
            num_available = float(row[7])
            price = float(row[4])

            if not filter_article(reference, product_name, None, num_available, price):
                continue

            imgurl = get_img_url(reference, product_name)

        except Exception as e:
            print('error:{}:{}: invalid line detected'.format(i, row), file=sys.stderr)
            print(e, file=sys.stderr)
            continue

        i += 1
        d['ref'].append(reference)
        d['name'].append(product_name)
        d['image'].append(imgurl)
        # d['storage'].append(storage)
        d['num'].append(num_available)
        d['bying_price_ht'].append(price)
    d['num_articles'] = i
    return d

def write_csv(d):
    '''Write the converted CSV from the input dictionary'''
    writer = csv.writer(sys.stdout, delimiter=';')
    writer.writerow(['Reference', 'Title', 'Image', 'Availability', 'Price HT', 'Price'])
    for i in range(d['num_articles']):

        price_ht = d['bying_price_ht'][i]
        customer_price_ht = price_ht + price_ht * 20 / 100
        customer_price = customer_price_ht + customer_price_ht * 20 / 100

        writer.writerow(
            [
                d['ref'][i],
                d['name'][i],
                d['image'][i],
                # d['storage'][i],
                int(d['num'][i]),
                d['bying_price_ht'][i],
                "{0:.2f}".format(customer_price),
            ]
        )



def main(args):
    filepath = args[1]
    articles = create_dict(filepath)
    write_csv(articles)

if __name__ == "__main__":
    main(sys.argv)

