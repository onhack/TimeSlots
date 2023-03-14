from datetime import datetime, timedelta
from timeslots.timely import EventSlot, BusinessHours, TimeSlot, Calendar

format = "%d/%m/%Y %H:%M"

events = []
events.append(EventSlot(start_time=datetime.strptime("13/03/2023 15:00", format), end_time=datetime.strptime("14/03/2023 09:00", format)))
events.append(EventSlot(start_time=datetime.strptime("14/03/2023 12:00", format)))
events.append(EventSlot(start_time=datetime.strptime("15/03/2023 16:00", format), end_time=datetime.strptime("15/03/2023 17:00", format)))
events.append(EventSlot(start_time=datetime.strptime("16/03/2023 08:00", format), duration=timedelta(minutes=30)))
events.append(EventSlot(start_time=datetime.strptime("20/03/2023 08:00", format)).extends(timedelta(minutes=30)))
events.append(EventSlot(start_time=datetime.strptime("24/03/2023 14:00", format), duration=timedelta(hours=1,minutes=45)))

len_events = len(events)
for event in events:
    print("Events --->", event)

start_wknd = datetime.strptime("13/03/2023 12:00", format)
end_wknd = datetime.strptime("31/03/2023 18:00", format)

all_slots = TimeSlot(start_time=start_wknd, end_time=end_wknd, business_hours=BusinessHours()).by(timedelta(hours=1)).as_event()
len_all_slots = len(all_slots)
for slot in all_slots:
    print("Slots Generated --->", slot)

all_slots.remove(events)
len_free_slots = len(all_slots)
for slot in all_slots:
    print("Free Slots --->", slot)

print("Events: {}, Slots Generated: {}, Free Slots: {}".format(len_events, len_all_slots, len_free_slots))


start_wknd = datetime.strptime("14/03/2023 12:00", format)
end_wknd = datetime.strptime("30/04/2023 18:00", format)

business_hours = BusinessHours(
    monday=None,
    thursday=None,
)

calendar = Calendar(business_hours=business_hours)

calendar.add_event(start_time=datetime.strptime("14/03/2023 15:00", format), end_time=datetime.strptime("14/03/2023 09:00", format))
calendar.add_event(start_time=datetime.strptime("15/03/2023 12:00", format))

calendar.generate_slots(start_time=start_wknd, duration=timedelta(minutes=40), gap=timedelta(hours=1, minutes=28))
calendar.add_event(start_time=datetime.strptime("14/03/2023 15:00", format))

slots = calendar.get_slots().as_event()
for slot in slots:
    print("Free Slots --->", slot)