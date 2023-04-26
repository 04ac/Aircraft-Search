import json
import aircraft_search

aircraft_reg_no = "N145DQ"  # aircraft registration number

# show_image enables showing the aircraft image in the default image viewer
# aircraft_data = aircraft_search.aircraft_details_query(
#     aircraft_registration_number, show_image=True)

# # Logging is disabled by default and hence the only output
# is the data about the aircraft being returned as an JSON object

aircraft_data = aircraft_search.aircraft_details_query(
    aircraft_reg_no, logging=True)
print("\nJSON data:\n", json.dumps(aircraft_data, indent=4))
