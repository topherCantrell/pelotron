import time
import json
import sys

from onepeloton import PeolotonStudios

with open('creds.json') as f:
    creds = json.load(f)

USER = sys.argv[1].upper()
DAY = 23

studio = PeolotonStudios(wait_between_refreshes=5)
studio.login(creds[USER]["username"], creds[USER]["password"])
studio.pick_book_date("April", DAY)

while True:

    # Get all classes for the week with the selected date
    all_classes = studio.get_classes()

    # Find NOT-FULL CYCLING after 1300 on Thursday
    # TODO sort with available on top (join waitlist second)
    # TODO prefer available at 3:00 or 3:30

    potentials = []
    for c in all_classes:
        if c['weekday'] != 'THURSDAY':
            continue
        if c['course'] != 'CYCLING':
            continue
        print(">>> cycling class:", c)       
        if c['time'] < 1300:
            continue        
        if c['status'] == 'FULL':
            continue
        
        potentials.append(c)

    if potentials:
        # There is a class. Let's go get it.
        break

    print(">>> No acceptable class found. Refreshing and looking again.")
    studio.refresh()

print(">>> Found potential classes:")
for p in potentials:
    print('    ', p)

print(">>> Joining class:", potentials[0])
studio.click_on_class(potentials[0])

while True:
    time.sleep(10)
