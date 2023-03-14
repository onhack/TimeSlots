import icalendar
from uuid import uuid4
from typing import Optional, Tuple, NamedTuple
from datetime import datetime, timedelta
from dateutil.rrule import rrule, rruleset, rrulestr, WEEKLY, MO, TU, WE, TH, FR, SA, SU

class BusinessHours(NamedTuple):
    """"
    Business hours for a given day of the week retuns a tuple with start time and end time or None if the day hasn't to be used.
    """
    monday: Optional[Tuple[str, str]] = ("08:00", "18:00")
    tuesday: Optional[Tuple[str, str]] = ("08:00", "18:00")
    wednesday: Optional[Tuple[str, str]] = ("08:00", "18:00")
    thursday: Optional[Tuple[str, str]] = ("08:00", "18:00")
    friday: Optional[Tuple[str, str]] = ("08:00", "18:00")
    saturday: Optional[Tuple[str, str]] = None
    sunday: Optional[Tuple[str, str]] = None

    def is_in_business_hours(self, dt_after: datetime, dt_before: datetime) -> bool:
        """
        Check if a given datetime is in business hours.
        
        :param dt_after: datetime to check after at
        :param dt_before: datetime to check before at
        :return: True if the datetime is in business hours, False otherwise
        """
        if self[dt_after.weekday()] is not None:
            _after = datetime.strptime(self[dt_after.weekday()][0], '%H:%M').time()
            _before =datetime.strptime(self[dt_after.weekday()][1], '%H:%M').time()
            return _after <= dt_after.time() and dt_before.time() <= _before
        else:
            return False

class EventInfo:
    """
    Event info class.
    
    :param name: name of the event
    :param description: description of the event
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def __str__(self):
        return "{} - {}".format(self.name, self.description)

    def to_json(self):
        return {
            "name": self.name,
            "description": self.description
        }

class EventSlot:
    """
    Event slot class.
    
    :param start_time: start time of the event slot
    :param end_time: end time of the event slot
    :param duration: duration of the event slot
    :param info: info of the event slot
    """
    def __init__(self, start_time: datetime, end_time: datetime = None, duration: timedelta = None, info: EventInfo = None):
        self.duration = duration if duration else timedelta(minutes=30)
        self.start_time = start_time
        self.end_time = end_time if end_time else start_time + self.duration
        self.info = info

    def __str__(self):
        """
        String representation of the event slot.
        
        :return: string representations of the event slot
        
        >>> EventSlot(start_time=datetime(2020, 1, 1, 10, 0, 0), end_time=datetime(2020, 1, 1, 11, 0, 0)).__str__()
        '01/01/2020 from 10:00 to 11:00'
        >>> EventSlot(start_time=datetime(2020, 1, 1, 10, 0, 0), end_time=datetime(2020, 1, 2, 11, 0, 0)).__str__()
        '01/01/2020 from 10:00 to 02/01/2020 at 11:00'
        """
        if self.start_time.date() == self.end_time.date():
            return "{} from {} to {}".format(datetime.date(self.start_time).strftime("%d/%m/%Y"), datetime.time(self.start_time).strftime("%H:%M"), datetime.time(self.end_time).strftime("%H:%M"))
        else:
            return "{} from {} to {} at {}".format(datetime.date(self.start_time).strftime("%d/%m/%Y"), datetime.time(self.start_time).strftime("%H:%M"), datetime.date(self.end_time).strftime("%d/%m/%Y"), datetime.time(self.end_time).strftime("%H:%M"))

    def extends(self, duration: timedelta) -> 'EventSlot':
        """
        Extends the event slot by a given duration.
        
        :param duration: duration to extend the event slot by
        :return: the event slot
        """
        self.end_time = self.end_time + duration
        return self

    def is_overlapping(self, other) -> bool:
        """"
        Check if the event slot is overlapping with another event slot.

        :param other: other event slot to check for overlapping
        :return: True if the event slot is overlapping, False otherwise

        >>> EventSlot(start_time=datetime(2020, 1, 1, 10, 0, 0), end_time=datetime(2020, 1, 1, 11, 0, 0)).is_overlapping(EventSlot(start_time=datetime(2020, 1, 1, 10, 0, 0), end_time=datetime(2020, 1, 1, 11, 0, 0)))
        True
        >>> EventSlot(start_time=datetime(2020, 1, 1, 10, 0, 0), end_time=datetime(2020, 1, 1, 11, 0, 0)).is_overlapping(EventSlot(start_time=datetime(2020, 1, 1, 11, 0, 0), end_time=datetime(2020, 1, 1, 12, 0, 0)))
        False
        """
        return self.start_time < other.end_time and self.end_time > other.start_time

    def to_json(self) -> dict:
        """
        JSON representation of the event slot.
        
        :return: JSON representation of the event slot
        
        >>> EventSlot(start_time=datetime(2020, 1, 1, 10, 0, 0), end_time=datetime(2020, 1, 1, 11, 0, 0)).to_json()
        """
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "info": self.info.to_json() if self.info else None
        }
    
    def to_ics(self) -> icalendar.Event:
        """
        iCal representation of the event slot.
        
        :return: iCal representation of the event slot"""
        event = icalendar.Event()

        self.info.properties = self.info.properties if self.info.properties else {}
        self.info.properties['X-MICROSOFT-CDO-BUSYSTATUS'] = 'BUSY' if self.info.busy else 'FREE'
        self.info.properties['UID'] = uuid4() if 'UID' not in self.info.properties else self.info.properties['UID']

        map(lambda x: event.add(x, self.info.properties[x]), self.info.properties.keys())

        event.add('dtstamp', datetime.utcnow())
        event.begin = self.start_time
        event.end = self.end_time
        return event

class TimeSlot:
    """"
    Time slot class.
    
    :param start_time: start time of the time slot (default: 00:00:00)
    :param end_time: end time of the time slot (default: 23:59:59)
    :param duration: duration of the time slot (default: 30 minutes)
    :param gap: gap between two time slots (default: 0 minutes)
    :param booked_slots: list of booked slots (default: [], i.e. no booked slots are present)
    """
    def __init__(self, start_time: datetime = None, end_time: datetime = None, business_hours: BusinessHours = None, duration: timedelta = None, gap: timedelta = None, booked_slots: list = []):
        __date: datetime = datetime.utcnow()
        self.__start_time = start_time if start_time else datetime(__date.year, __date.month, __date.day, 0, 0, 0)
        self.__end_time = end_time if end_time else datetime(__date.year, __date.month, __date.day, 23, 59, 59)
        
        difference = self.__end_time - self.__start_time
        self.slot_duration = timedelta(minutes=difference.seconds // 60)
        self.__duration = duration if duration else timedelta(minutes=30)
        self.__gap = gap if gap else timedelta(minutes=0)

        self.__business_hours = business_hours
        self.rule = self.__rrulestr()
        self.by()

        self.remove(booked_slots)

    def __iter__(self):
        """
        Iterator for the time slot.
        """
        return self.__slots.__iter__()
    
    def __len__(self):
        """
        Length of the time slot.
        """
        return len(self.__slots)

    def extends(self, duration: timedelta) -> 'TimeSlot':
        """
        Extends the time slot by a given duration.
        
        :param duration: duration to extend the time slot by
        :return: the time slot
        """
        self.slot_duration = duration
        self.__end_time = self.__extends()
        return self
    
    def by(self, duration: timedelta = None) -> 'TimeSlot':
        """
        Sets the duration of the time slot.
        
        :param duration: duration of the time slot (default: 30 minutes)
        :return: the time slot
        """
        self.__duration = duration if duration else self.__duration
        self.__generate()
        return self
    
    def as_event(self) -> 'TimeSlot':
        """
        Converts each time slot to an event slot list.

        :return: the time slot
        """
        if len(self.__slots) > 0 and isinstance(self.__slots[0], datetime):
            self.__slots = list(map(lambda __start: EventSlot(start_time=__start, duration=self.__duration), self.__slots))
        return self
    
    def as_list(self) -> 'TimeSlot':
        """
        Converts each event slot to a time slot list.
        
        :return: the time slot
        """
        if isinstance(self.__slots[0], EventSlot):
            self.__slots = list(map(lambda event: event.start_time, self.__slots))
        return self
    
    def remove(self, object) -> 'TimeSlot':
        """"
        Removes the given object from the time slot.
        
        :param object: object to remove from the time slot (can be a list of objects, an event slot or a time slot)
        :return: the time slot
        """
        if len(self.__slots) == 0:
            return self
        
        slots_type = type(self.__slots[0])
        if slots_type == datetime:
            self.as_event()

        try:
            if isinstance(object, EventSlot):
                return self.remove_event(object)
            elif isinstance(object, list):
                return self.remove_events(object)
            elif isinstance(object, TimeSlot):
                return self.remove_events(object.__slots)
            else:
                raise Exception("Invalid object type")
        finally:
            if slots_type == datetime:
                self.as_list()
        

    def remove_event(self, event) -> 'TimeSlot':
        """
        Removes the given event from the time slot.
        
        :param event: event to remove from the time slot (single event)
        :return: the time slot
        """
        return self.remove_events([event])

    def remove_events(self, events) -> 'TimeSlot':
        """
        Removes the given events from the time slot.
        
        :param events: events to remove from the time slot (list of events)
        :return: the time slot
        """
        self.__slots = list(filter(lambda x: not self.__is_overlapping_events(x, events), self.__slots))
        return self
    
    def __extends(self) -> datetime:
        """
        Extends the time slot by the given duration.
        
        :return: the end time of the time slot
        """
        return self.__start_time + self.slot_duration

    def __rrulestr(self, start_time: datetime = None) -> rrulestr:
        """"
        Returns the rrulestr for the time slot.
        
        :param start_time: start time of the time slot (default: None)
        :return: the rrulestr
        """
        start_time = start_time if start_time else self.__start_time
        interval = (self.__duration + self.__gap).seconds // 60
        freq = "FREQ=MINUTELY;INTERVAL={}".format(interval)
        return rrulestr(freq, dtstart=start_time)
    
    def __generate(self) -> 'TimeSlot':
        """
        Generates the time slot list with events.
        
        :return: the time slot
        """
        self.__slots = self.rule.between(after=self.__start_time, before=self.__end_time, inc=True)

        # iterate over each slot and remove the slots that are not in business hours
        if self.__business_hours is not None:
            self.__slots = list(filter(lambda x: self.__business_hours.is_in_business_hours(x, x + self.__duration), self.__slots))

        self.__slots = list(filter(lambda x: x.date() == (x + self.__duration).date(), self.__slots))
        return self
    
    def __is_overlapping_events(self, slot: EventSlot, events: list) -> bool:
        """
        Checks if the given slot is overlapping with any of the given events.
        
        :param slot: slot to check
        :param events: list of events to check against
        :return: True if the slot is overlapping with any of the events, False otherwise
        """
        for event in events:
            if slot.is_overlapping(event):
                return True
        return False
    
    def to_json(self) -> list:
        """
        Converts the time slot to a JSON list.
        
        :return: JSON list
        """
        return list(map(lambda slot: slot.to_json(), self.__slots))
    
    def to_ics(self) -> list:
        """
        Converts the time slot to an ICS list.
        
        :return: ICS list"""
        return list(map(lambda slot: slot.to_ics(), self.__slots))
    
class Calendar:
    """
    Calendar class.
    
    :param business_hours: business hours of the calendar (default: None)
    """
    def __init__(self, business_hours: BusinessHours = None):
        self.__business_hours = business_hours
        self.__events: list = []
        self.__time_slots: list = []
        self.__start_time: datetime = None
        self.__end_time: datetime = None
        self.__duration: timedelta = None
        self.__gap: timedelta = None

    def add_event(self, event: EventSlot = None, start_time = None, end_time = None, duration: timedelta = None) -> 'Calendar':
        """
        Adds an event to the calendar.
        
        :param event: event to add (default: None)
        :param start_time: start time of the event (default: None)
        :param end_time: end time of the event (default: None)
        :param duration: duration of the event (default: None)
        :return: the calendar
        """
        if event is not None:
            self.__events.append(event)
        else:
            self.__events.append(EventSlot(start_time=start_time, end_time=end_time, duration=duration))

        self._generate_slots()
        return self
    
    def remove_event(self, event: EventSlot) -> 'Calendar':
        """
        Removes the given event from the calendar.

        :param event: event to remove
        :return: the calendar
        """
        self.__events.remove(event)
        self._generate_slots()
        return self
    
    def import_events(self, events: list) -> 'Calendar':
        """
        Imports the given events to the calendar.

        :param events: events to import (list of events)
        :return: the calendar
        """
        self.__events.extend(events)
        self._generate_slots()
        return self
    
    def purge_events(self, events: list):
        """
        Purges the given events from the calendar.
        
        :param events: events to purge (list of events)
        :return: the calendar
        """
        for event in events:
            self.__events.remove(event)
        self._generate_slots()
        return self
    
    def generate_slots(self, start_time: datetime = None, end_time: datetime = None, duration: timedelta = None, gap: timedelta = None) -> 'Calendar':
        """
        Generates the time slots for the calendar.
        
        :param start_time: start time of the time slot (default: None)
        :param end_time: end time of the time slot (default: None)
        :param duration: duration of the time slot (default: None)
        :param gap: gap between the time slots (default: None)
        :return: the calendar
        """
        self.__start_time = start_time if start_time else datetime.utcnow()
        self.__end_time = end_time if end_time else start_time.replace(hour=23, minute=59, second=59, microsecond=999999)
        self.__duration = duration if duration else timedelta(minutes=30)
        self.__gap =  gap if gap else timedelta(minutes=0)

        self._generate_slots()
        return self

    def _generate_slots(self) -> 'Calendar':
        """
        Generates the time slots for the calendar.
        
        :return: the calendar
        """
        self.__time_slots = TimeSlot(start_time=self.__start_time, end_time=self.__end_time, business_hours=self.__business_hours, duration=self.__duration, gap=self.__gap, booked_slots=self.__events)
        return self

    def get_slots(self) -> TimeSlot:
        """
        Returns the time slots of the calendar.
        
        :return: the time slots
        """
        return self.__time_slots
    
    def get_events(self) -> list:
        """
        Returns the events of the calendar.
        
        :return: the events (list of events)
        """
        return self.__events
    
    def to_json(self) -> dict:
        """
        Converts the calendar to a JSON object.
        
        :return: JSON object
        """
        return {
            "events": list(map(lambda x: x.to_json(), self.__events)),
            "slots": self.__time_slots.to_json()
        }
    
    def from_ical(self, ical: str) -> 'Calendar':
        """
        Imports the events from the given ICS object.
        
        :param ical: ICS object
        :return: the calendar
        """
        calendar = icalendar.Calendar.from_ical(ical)
        
        for event in calendar.walk('vevent'):
            info = EventInfo(event.get('summary'), event.get('description'), event.get('location'))
            self.add_event(start_time=event.get('dtstart').dt, end_time=event.get('dtend').dt, duration=event.get('duration').dt, info=info)
        
        return self
    
    def to_ics(self) -> bytes:
        """
        Converts the calendar to an ICS object.
        
        :return: ICS object"""
        calendar = icalendar.Calendar()
        
        calendar.add('prodid', '-//TimeSlot//TimeSlot//EN')
        calendar.add('version', '2.0')
        calendar.add('method', 'PUBLISH')
        
        for event in self.__events:
            calendar.add_component(event.to_ics(busy=True))
        
        for slot in self.__time_slots.to_ics():
            calendar.add_component(slot.to_ics(busy=False))

        return calendar.to_ical()