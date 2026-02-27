from faster_whisper import WhisperModel
#from inventory_db import init_db, update_inventory
from regex import extract_info   # correct import
from inventory_db import init_db, update_inventory, show_inventory

# ---------------- INIT DATABASE ----------------
init_db()

# ---------------- LOAD MODEL ----------------
model_size = "medium"
model = WhisperModel(model_size, device="cpu", compute_type="int8")

inventory_context = (
    "This is an inventory system. "
    "The user is speaking about quantities of fruits and vegetables."
)

print("Processing inventory audio...")

# ---------------- TRANSCRIBE AUDIO ----------------
segments, info = model.transcribe(
    "voice-commands\\telugu2.ogg",   # use forward slash
    task="translate",
    initial_prompt=inventory_context,
    vad_filter=True,
    beam_size=5
)

print(f"Detected Source Language: {info.language}")

# ---------------- COLLECT TEXT ----------------
inventory_data = []

for segment in segments:
    print(f"Log: {segment.text}")
    inventory_data.append(segment.text)

final_output = " ".join(inventory_data)

print("\n--- Final English Inventory List ---")
print(final_output)

# ---------------- EXTRACT INFO ----------------
quantity, unit, item, action = extract_info(final_output)

print("\nExtracted Data:")
print(quantity, unit, item, action)

# ---------------- UPDATE DATABASE ----------------
update_inventory(quantity, unit, item, action)

show_inventory()