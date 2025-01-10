from bitstring import BitStream
import pandas as pd

# Define the structure for the ancillary header
header_structure = [
    ("SCET_BLOCK_WHOLE", 32),
    ("SCET_BLOCK_FRAC", 16),
    ("TLM_COUNTER", 32),
    ("FMT_LENGTH", 16),
    ("SPARE1", 16),
    ("SCET_OST_WHOLE", 32),
    ("SCET_OST_FRAC", 16),
    ("SPARE2", 8),
    ("OST_LINE_NUMBER", 8),
    ("OST_LINE", 128),  # Custom decoding for this field
    ("SPARE3", 8),
    ("DATA_BLOCK_ID", 24),
    ("SCIENCE_DATA_SOURCE_COUNTER", 16),
    ("PACKET_SEGMENTATION_AND_FPGA_STATUS", 16),
    ("SPARE4", 8),
    ("DATA_BLOCK_FIRST_PRI", 24),
    ("TIME_DATA_BLOCK_WHOLE", 32),
    ("TIME_DATA_BLOCK_FRAC", 16),
    ("SDI_BIT_FIELD", 16),
    ("TIME_N", 32),
    ("RADIUS_N", 32),
    ("TANGENTIAL_VELOCITY_N", 32),
    ("RADIAL_VELOCITY_N", 32),
    ("TLP", 32),
    ("TIME_WPF", 32),
    ("DELTA_TIME", 32),
    ("TLP_INTERPOLATE", 32),
    ("RADIUS_INTERPOLATE", 32),
    ("TANGENTIAL_VELOCITY_INTERPOLATE", 32),
    ("RADIAL_VELOCITY_INTERPOLATE", 32),
    ("END_TLP", 32),
    *[(f"S_COEFF_{i+1}", 32) for i in range(8)],
    *[(f"C_COEFF_{i+1}", 32) for i in range(7)],
    ("SLOPE", 32),
    ("TOPOGRAPHY", 32),
    ("PHASE_COMPENSATION_STEP", 32),
    ("RECEIVE_WINDOW_OPENING_TIME", 32),
    ("RECEIVE_WINDOW_POSITION", 32),
]

# Define the subfields within `OST_LINE`
ost_line_structure = [
    ("PULSE_REPETITION_INTERVAL", 4),
    ("PHASE_COMPENSATION_TYPE", 4),
    ("SPARE1", 2),
    ("DATA_TAKE_LENGTH", 22),
    ("OPERATIVE_MODE", 8),
    ("MANUAL_GAIN_CONTROL", 8),
    ("COMPRESSION_SELECTION", 1),
    ("CLOSED_LOOP_TRACKING", 1),
    ("TRACKING_DATA_STORAGE", 1),
    ("TRACKING_PRE_SUMMING", 3),
    ("TRACKING_LOGIC_SELECTION", 1),
    ("THRESHOLD_LOGIC_SELECTION", 1),
    ("SAMPLE_NUMBER", 4),
    ("SPARE2", 1),
    ("ALPHA_BETA", 2),
    ("REFERENCE_BIT", 1),
    ("THRESHOLD", 8),
    ("THRESHOLD_INCREMENT", 8),
    ("SPARE3", 4),
    ("INITIAL_ECHO_VALUE", 3),
    ("EXPECTED_ECHO_SHIFT", 3),
    ("WINDOW_LEFT_SHIFT", 3),
    ("WINDOW_RIGHT_SHIFT", 3),
    ("SPARE4", 32),
]

# Function to parse OST_LINE
def parse_ost_line(bits):
    parsed = {}
    position = 0
    for name, bit_length in ost_line_structure:
        # Use .uint for unsigned fields
        parsed[name] = bits[position:position + bit_length].uint
        position += bit_length
    return parsed

# Read the binary data
file_path = "e_0168901_001_ss19_700_a_s.dat"
with open(file_path, "rb") as f:
    data = f.read()

# Convert to a BitStream for bit-level operations
bitstream = BitStream(data)

# Define the number of rows and the ancillary header size in bits
row_size_bits = 3786 * 8  # Each row is 3786 bytes
header_size_bits = 186 * 8  # Ancillary header is 186 bytes

rows = []
num_rows = len(data) * 8 // row_size_bits  # Total rows based on file size

for i in range(num_rows):
    start = i * row_size_bits
    end = start + header_size_bits
    header_bits = bitstream[start:end]  # Extract header bits
    parsed_row = {}
    
    position = 0
    for name, bit_size in header_structure:
        if name == "OST_LINE":
            ost_line_bits = header_bits[position:position + bit_size]
            parsed_row.update(parse_ost_line(ost_line_bits))  # Add OST_LINE subfields
        else:
            # Use .uint for unsigned fields
            parsed_row[name] = header_bits[position:position + bit_size].uint
        position += bit_size

    rows.append(parsed_row)

# Convert to DataFrame
df = pd.DataFrame(rows)

# Save to CSV or further analysis
df.to_csv("decoded_ancillary_headers_with_ost_line.csv", index=False)
