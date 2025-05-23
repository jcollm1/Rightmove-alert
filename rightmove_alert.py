
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import sqlite3
from urllib.parse import quote
import datetime

# --- CONFIG ---
EMAIL_ADDRESS = 'rightmovealert45@gmail.com'
EMAIL_PASSWORD = 'caoliitqdcjhnxfi'  # App Password
RECIPIENT = 'rightmovealert45@gmail.com'

# Your search
LOCATION_ID = quote('USERDEFINEDAREA^{"polylines":"mz~sIjxlYu_D_xA~`C}jK~eBdhBhc@vD}a@_z@jcAbZdr@a@d`@vu@aNnhDufBjp@_`AsdFyh@lGueAnaJ"}')
URL = f"https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier={LOCATION_ID}&maxPrice=260000&minPrice=150000&minBedrooms=2&maxBedrooms=3&propertyTypes=flat&includeSSTC=false&sortType=6"

# --- DB SETUP ---
conn = sqlite3.connect("seen_listings.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS seen (id TEXT PRIMARY KEY)")
conn.commit()

# --- GET LISTINGS ---
def fetch_listings():
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(URL, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    results = soup.find_all('div', class_='l-searchResult')
    listings = []

    for res in results:
        link_tag = res.find('a', class_='propertyCard-link')
        if not link_tag:
            continue
        url = "https://www.rightmove.co.uk" + link_tag['href']
        title = link_tag.get_text(strip=True)
        listing_id = url.split('/')[-1]
        listings.append({'id': listing_id, 'title': title, 'url': url})

    return listings

# --- EMAIL SENDER ---
def send_email(new_listings):
    body = "\n\n".join([f"{x['title']}\n{x['url']}" for x in new_listings])
    msg = MIMEText(body)
    msg['Subject'] = f"[Rightmove] {len(new_listings)} New Listings Found"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

# --- MAIN LOGIC ---
def main():
    listings = fetch_listings()
    new = []

    for l in listings:
        cursor.execute("SELECT id FROM seen WHERE id=?", (l['id'],))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO seen (id) VALUES (?)", (l['id'],))
            new.append(l)

    conn.commit()

    if new:
        send_email(new)

# --- RUN ---
if __name__ == "__main__":
    main()
