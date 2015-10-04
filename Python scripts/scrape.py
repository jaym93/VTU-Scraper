__author__ = 'jaym93'
__version__ = '1.0'
__date__ = '13-09-2015'

from bs4 import BeautifulSoup
import pymysql
from urllib.request import urlopen

# Change these to suit your DB connection string
server = 'localhost'
username = 'db_user_name'
password = 'db_password'
database = 'db_name'
con = pymysql.connect(server, username, password, database)
cur = con.cursor()
# list to store USNs whose results are to be fetched
usns = []

# students is the table that contains the pool of USNs to fetch results for
cur.execute('select usn from students')
for res in cur.fetchall():
    usns.append(str(res)[2:-3])
print("Fetching results for USNs: " + str(usns))

for usn in usns:
    rows = []
    url = 'http://results.vtu.ac.in/vitavi.php?rid=' + usn + '&submit=SUBMIT'
    soup = BeautifulSoup(urlopen(url))
    # Find the HTML table that contains the text "Subject"
    results_table = soup.find(text="Subject").find_parent("table")
    # Ectract all the content of <tr> tags
    results = results_table.find_all("tr")
    for row in results:
        # remove extra whitespaces and store <td> content as results in variable rows
        rows.append([cell.get_text(strip=True) for cell in row.find_all("td")])
    for i in range(0, rows.__len__()):
        # All <tr>s with subject names contain an opening round bracket
        if "(" in rows[i][0]:
            subject = rows[i][0]
            internal = rows[i][1]
            external = rows[i][2]
            total = rows[i][3]
            result = rows[i][4]
            print(usn, subject, internal, external, total, result)
            # will throw an error if duplicates are found - truncate the marks table if error is thrown
            try:
                cur.execute(
                    "insert into marks(usn,subject,internals,externals,total,result) values (%s,%s,%s,%s,%s,%s)", (usn, subject, internal, external, total, result))
            except pymysql.err.IntegrityError:
                print("Error while inserting results of" + usn)
            continue
    con.commit()

