from datetime import datetime, timedelta
from discord_webhook import DiscordEmbed, DiscordWebhook
from notion_client import Client
from dotenv import load_dotenv
from pytz import timezone
import os

load_dotenv()

def intial_today():
  today = datetime.now(timezone('Asia/Seoul'))
  today = datetime(year=today.year, month=today.month, day=today.day)
  return today

def is_birthday_in_this_week(birthday):
  today = intial_today()

  birthday = birthday.replace(year=today.year)

  if birthday.month == 1 and birthday.day in range(1, 7) :
    birthday.replace(year=birthday.year + 1)

  start_of_week = today - timedelta(days=today.weekday())

  end_of_week = start_of_week + timedelta(days=6)

  return today <= birthday <= end_of_week

notion_key = os.getenv('NOTION_KEY')

notion = Client(auth=notion_key)

database_id = os.getenv('DATABASE_ID')

glutamates = notion.databases.query(
  database_id=database_id
)

birth_glutamates = []
for glutamate in glutamates["results"]:
  if glutamate['properties']['생일']['date'] is None:
    continue
  birthdate = datetime.strptime(glutamate['properties']['생일']['date']['start'], '%Y-%m-%d')

  if is_birthday_in_this_week(birthday=birthdate):
    birth_glutamates.append(glutamate)

webhookURL = os.getenv('WEBHOOK')
webhook = DiscordWebhook(url=webhookURL)

for glutamate in birth_glutamates:
  today = intial_today()
  birthdate = datetime.strptime(glutamate['properties']['생일']['date']['start'], '%Y-%m-%d')
  birthdate = birthdate.replace(year=today.year)
  if birthdate.month == 1 and birthdate.day in range(1, 7) :
    birthdate.replace(year=birthdate.year + 1)

  name = glutamate['properties']['이름']['title'][0]['text']['content']
  diff_date = birthdate - today

  if diff_date.days == 0:
    title = f"🎉🎉 오늘은 {name}님의 생일이에요!! 🎉🎉"
    embed = DiscordEmbed(title=title, description=f"{name}님의 생일을 축하해주세요!!", color="F6C064")
    embed.set_image(url="https://cdn-images-1.medium.com/max/1600/1*xKCFy6L8NZy-eDl2bylXTw.gif")
    webhook.add_embed(embed=embed)

webhook.execute()