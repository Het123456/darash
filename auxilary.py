from bitstring import BitStream
import pandas as pd
from datetime import datetime

# Define the auxiliary telemetry table structure
aux_table_structure = [
    ("SCET_BLOCK_WHOLE", 0, 32, "uint"),
    ("SCET_BLOCK_FRAC", 32, 16, "uint"),
    ("EPHEMERIS_TIME", 48, 64, "float"),
    ("GEOMETRY_EPOCH", 112, 184, "date"),
    ("SOLAR_LONGITUDE", 296, 64, "float"),
    ("ORBIT_NUMBER", 360, 32, "int"),
    ("X_MARS_SC_POSITION_VECTOR", 392, 64, "float"),
    ("Y_MARS_SC_POSITION_VECTOR", 456, 64, "float"),
    ("Z_MARS_SC_POSITION_VECTOR", 520, 64, "float"),
    ("SPACECRAFT_ALTITUDE", 584, 64, "float"),
    ("SUB_SC_EAST_LONGITUDE", 648, 64, "float"),
    ("SUB_SC_PLANETOCENTRIC_LATITUDE", 712, 64, "float"),
    ("SUB_SC_PLANETOGRAPHIC_LATITUDE", 776, 64, "float"),
    ("X_MARS_SC_VELOCITY_VECTOR", 840, 64, "float"),
    ("Y_MARS_SC_VELOCITY_VECTOR", 904, 64, "float"),
    ("Z_MARS_SC_VELOCITY_VECTOR", 968, 64, "float"),
    ("MARS_SC_RADIAL_VELOCITY", 1032, 64, "float"),
    ("MARS_SC_TANGENTIAL_VELOCITY", 1096, 64, "float"),
    ("LOCAL_TRUE_SOLAR_TIME", 1160, 64, "float"),
    ("SOLAR_ZENITH_ANGLE", 1224, 64, "float"),
    ("SC_PITCH_ANGLE", 1288, 64, "float"),
    ("SC_YAW_ANGLE", 1352, 64, "float"),
    ("SC_ROLL_ANGLE", 1416, 64, "float"),
    ("MRO_SAMX_INNER_GIMBAL_ANGLE", 1480, 64, "float"),
    ("MRO_SAMX_OUTER_GIMBAL_ANGLE", 1544, 64, "float"),
    ("MRO_SAPX_INNER_GIMBAL_ANGLE", 1608, 64, "float"),
    ("MRO_SAPX_OUTER_GIMBAL_ANGLE", 1672, 64, "float"),
    ("MRO_HGA_INNER_GIMBAL_ANGLE", 1736, 64, "float"),
    ("MRO_HGA_OUTER_GIMBAL_ANGLE", 1800, 64, "float"),
    ("DES_TEMP", 1864, 32, "float"),
    ("DES_5V", 1896, 32, "float"),
    ("DES_12V", 1928, 32, "float"),
    ("DES_2V5", 1960, 32, "float"),
    ("RX_TEMP", 1992, 32, "float"),
    ("TX_TEMP", 2024, 32, "float"),
    ("TX_LEV", 2056, 32, "float"),
    ("TX_CURR", 2088, 32, "float"),
    ("CORRUPTED_DATA_FLAG", 2120, 16, "int"),
]

# Helper function to decode date fields
def decode_date(bytes_value):
    return datetime.strptime(bytes_value.decode("ascii").strip(), "%Y-%m-%dT%H:%M:%S.%f")

# Function to parse a single row
def parse_aux_row(row_bits):
    parsed_row = {}
    for name, start_bit, bit_size, data_type in aux_table_structure:
        field_bits = row_bits[start_bit:start_bit + bit_size]
        if data_type == "uint":
            parsed_row[name] = field_bits.uint
        elif data_type == "int":
            parsed_row[name] = field_bits.int
        elif data_type == "float":
            parsed_row[name] = field_bits.float
        elif data_type == "date":
            parsed_row[name] = decode_date(field_bits.bytes)
    return parsed_row

# Read the binary file
file_path = "e_0168901_001_ss19_700_a_a.dat"
with open(file_path, "rb") as f:
    data = f.read()

# Convert the data to BitStream for bit-level processing
bitstream = BitStream(data)

# Define row size in bits
row_size_bits = 267 * 8  # 267 bytes per row

# Parse all rows
rows = []
num_rows = len(data) * 8 // row_size_bits
for i in range(num_rows):
    start = i * row_size_bits
    end = start + row_size_bits
    row_bits = bitstream[start:end]
    parsed_row = parse_aux_row(row_bits)
    rows.append(parsed_row)

# Convert to DataFrame
df = pd.DataFrame(rows)

# Save to CSV or perform further analysis
df.to_csv("auxiliary_telemetry_table.csv", index=False)
