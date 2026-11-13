from sample_records import SOIL_RECORDS

def get_all_records():
    return SOIL_RECORDS

def add_soil_record(new_record):
    SOIL_RECORDS.append(new_record)
    return True

def search_by_location(location_name):
    return [r for r in SOIL_RECORDS if r["location"].lower() == location_name.lower()]

def filter_by_ph_range(min_ph, max_ph):
    return [r for r in SOIL_RECORDS if min_ph <= r["ph"] <= max_ph]