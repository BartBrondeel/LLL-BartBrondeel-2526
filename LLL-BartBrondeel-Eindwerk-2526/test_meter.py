# Tijdelijk testscript
# terminal: python test_meter.py

from meter import HomeWizardMeter

meter = HomeWizardMeter()

print("=== Meterinformatie ===")
info = meter.get_info()
print(info)

print("\n=== Actuele meterdata ===")
data = meter.get_data()
print(data)

print("\n=== Samenvatting ===")
samenvatting = meter.get_samenvatting()
for sleutel, waarde in samenvatting.items():
    print(f"  {sleutel}: {waarde}")