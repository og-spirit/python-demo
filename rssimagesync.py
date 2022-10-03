# importing libraries
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import mariadb
import sys
# import csv


print(f"Date {datetime}")
#
# Step 1 scrap list of images from rollies images page
#
print("Step 1 Start - get rss images list")

URL = "http://images.supplierswebsitename.com/main_product_images/"
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')

# Get all the image names on page
x = soup.find_all('a')

# make a list to store results
rss_images = []

for link in x:
    # print(link.text)
    rss_images.append(link.text)

# print(rss_images)
print("Step 1 Completed")

#
# Step 2 Connect to AMC DB and return list of image sin WP_Posts table
#
print("Step 2 Start - get wpposts images list from DB")

# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user="dbuser",
        password="passwordgoeshere",
        host="hostIPorfqdn",
        port=3306,
        database="databasename"

    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()

# sql = """SELECT ID, post_modified, post_parent, guid FROM 'wp_posts'
# WHERE post_type = 'attachment' AND post_mime_type = 'image/jpeg'
# AND guid like 'https://images.supplierswebsitename.com/main_product_images/%';"""

sql = """SELECT guid FROM wp_posts WHERE post_type = 'attachment' AND post_mime_type = 'image/jpeg' AND guid like 'https://images.supplierswebsitename.com/main_product_images/%';"""

cur.execute(sql)

# list of all images in wp_posts table
wppost_images = []

# Add Result-set to wpposts_images list
for (guid) in cur:
    # print(f"ID: {ID}, guid: {guid}")
    # print(guid)
    my_url = ''.join(guid)
    final_guid = my_url.rsplit('/', 1)[-1]
    wppost_images.append(final_guid)

print("Step 2 Completed")
#
# Step 3  Compare items in list, and create new list of missing images
#
print("Step 3 Start - do comparison to get image differences list")

list_difference = []
for item in wppost_images:
    if item not in rss_images:
        list_difference.append(item)

# print(list_difference)
print("Step 3 Completed")


#
# Step 4  Delete records that match the list_difference from step 3 from the wp_posts table
#
print("Step 4 Start - delete from wp_posts table records that match the differences list")

count = 0
for item in list_difference:
    delsql = "delete from wp_posts WHERE post_type = 'attachment' AND post_mime_type = 'image/jpeg' AND guid LIKE '%" + (item) + "'"
    # print(delsql)
    # Get Cursor
    cursor = conn.cursor()
    # print("at cursor")
    cursor.execute(delsql)
    # print("execute delsql")
    conn.commit()
    # print("at commit")
    count = count + 1
    x = count/100
    # print(x - int(x) == 0)
    check_int = (x - int(x) == 0)
    if check_int:
        print(count)

print(f"Total records removed {count}")
print("Step 4 Completed")
