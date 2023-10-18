# phonebook

This system uses OpenCage to do reverse GIS for lat/lon pairs in order
to generate a phonebook for XNET radios.

## Inputs

The inputs for this script are as follows:
	* A CSV of radio uptimes with radio serial number
	* A CSV of SAS data for each radio, keyed by serial number
	* A dump of the XNET django database to get customer/owner information
	
## Output

The output for this script is a CSV in the following format:

| provider_name | country_name | country_code | iso_cc | operator_id | provider_id | venue_name | pref_state_region | city_district | zipcode | address | category | node_type | node_class | node_count | altitude m | latitude | longitude |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| XNETMOBILE | USA | 1 | US | XNET | ZPLN | Beverly Hills Marriott Hotel | California | Los Angeles | 90035 | 1150 S Beverly Drive | H (Hotel) | macro | B / Nova 846 | 2 | 150 | 34.056333 | -118.395855 |
| XNETMOBILE | USA | 1 | US | XNET | LFI | Swan Oyster Depot | California | San Francisco | 94109 | 1517 Polk Street | F(Food) | micro | A / Neutrino 430 | 4 | 10 | 37.78988 | -122.42027 |


