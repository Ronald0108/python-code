# my description of the code
python code that reeads a shapefile and outputs a txt file using functions that:
-compares addresses from the shapefile against dictionaries for existence through the use of loops
-"filters" data by changing them from:
--half width characters to fullwidth
--strings to integers
--manipulating strings
⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# ChatGPT description of the code
This Python script processes a shapefile (.shp) containing Japanese geographic address data and converts it into a structured .txt format. It begins by loading configurations and optionally merging shapefiles. The script reads geographic and address information using geopandas, reprojects the data to WGS84 (EPSG:4326), and iterates through each record. Depending on the data format (linkkey, columns, or linkkey_column), it extracts address components such as the aza (small area unit) and branch (land parcel number), cleans and normalizes the text, and optionally matches the address against a master dataset to standardize the names. If address matching fails, the entry is flagged. For each entry, the script calculates the centroid coordinates and geometry string, then writes a formatted line (with address, branch, coordinates, and geometry) to an output text file. It also logs any address matching errors to a separate file and prints processing statistics at the end.

🔁 Control Flow
	•	if / elif / else statements – for conditional logic throughout.
	•	for loops – iterating over rows of the GeoDataFrame (shp_file.iterrows()).
	•	continue – skips an iteration when a condition is met.
	•	break – not explicitly used, but logic could be extended to include it.

⸻

🧰 Functions & Modules
	•	Function imports: from ... import ... for reusable functions like pre_processing, match_address, etc.
	•	User-defined modules: likely custom Python files such as pre_process.py and util.py.
	•	External libraries:
	•	geopandas: reading and manipulating spatial data.
	•	shapely.geometry: working with geometry like polygons and centroids.
	•	json: potentially for reading configuration or masterdata.
	•	sys: for early termination via sys.exit().

⸻

🗂️ Data Structures
	•	Lists: e.g., linkkey_list, branch_value_arr.
	•	Dictionaries:
	•	config: configuration parameters.
	•	printed_errors, count_instances: used to track errors or unique entries.
	•	Tuples: implicit when returning multiple values (e.g., from match_address()).

⸻

📦 File I/O
	•	open(): used to write output .txt and error files.
	•	f.write() and error_file.write(): writing data to files.
	•	f.close(): explicitly closing files after writing.

⸻

📊 Geospatial Data Handling
	•	geopandas.read_file() – reads a shapefile.
	•	.to_crs() – changes coordinate reference system.
	•	.centroid – gets centroid of a geometry.
	•	Custom get_geometry_string() – likely converts polygon to a text-friendly format.

⸻

🧠 String Manipulation
	•	.split(), .join(), .startswith(), .find(), string slicing – for parsing and cleaning address components.
	•	str(), round() – for formatting numerical data.
	•	fullWidthToHalfWidth() – converts full-width Japanese characters to half-width (likely).

⸻

🧮 Numerical Operations
	•	round() – to limit precision of latitude and longitude.
	•	Arithmetic – basic calculations with offsets and coordinates.

⸻

📊 Status Tracking & Logging
	•	Counters (status, aza_unknown, etc.) to monitor progress and issues.
	•	Print statements for logging and progress display.

⸻

🛑 Error Handling
	•	Not using try/except, but handles potential missing values (None, 0) and uses defensive programming patterns like:
	•	if linkkey is not None
	•	if line[branch_header] is not None

⸻

🧪 Type Checking and Filtering
	•	Checking for None, 0, and empty strings to ensure data integrity.
	•	Conditional logic to sanitize address strings (e.g., removing symbols like +, --).

⸻

🧹 Data Cleaning & Normalization
	•	Functions like dynamic_filtername() and fullWidthToHalfWidth() imply normalization.
	•	Conditional transformations for Japanese-specific address formatting.
