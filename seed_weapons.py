"""
seed_weapons.py
Edit the WEAPONS list below with real entries, then run this once:
    python seed_weapons.py

Fields:
  name           - e.g. "T-90 Bhishma"
  type           - e.g. "Main Battle Tank"
  country        - e.g. "India / Russia (license-built)"
  description    - short 1-2 line summary
  specs          - key specs, plain text (e.g. "Crew: 3 | Speed: 60 km/h | Armament: 125mm smoothbore gun")
  operators      - comma-separated, e.g. "Indian Army, Russian Ground Forces"
  threat_classification - e.g. "High" / "Medium" / "Low"
  drdo_links     - comma-separated URLs to relevant DRDO/public docs, or leave ""
"""

import sqlite3

WEAPONS = [
    {
        "name": "T-90 Bhishma",
        "type": "Main Battle Tank",
        "country": "India (license-built from Russia)",
        "description": "India's primary main battle tank, license-manufactured by HVF Avadi.",
        "specs": "Crew: 3 | Top speed: 60 km/h | Main armament: 125mm smoothbore gun | Weight: 46 tons",
        "operators": "Indian Army",
        "threat_classification": "High",
        "drdo_links": "https://www.drdo.gov.in/"
    },
    {
        "name": "Arjun Mk1A",
        "type": "Main Battle Tank",
        "country": "India",
        "description": "Indigenously developed third-generation main battle tank designed by DRDO.",
        "specs": "Crew: 4 | Top speed: 70 km/h | Main armament: 120mm rifled gun | Weight: 68.6 tons",
        "operators": "Indian Army",
        "threat_classification": "High",
        "drdo_links": "https://www.drdo.gov.in/"
    },
    {
        "name": "K9 Vajra-T",
        "type": "Self-Propelled Howitzer",
        "country": "India / South Korea",
        "description": "155mm tracked self-propelled artillery system manufactured in India.",
        "specs": "Crew: 5 | Range: 40 km | Caliber: 155mm | Weight: 47 tons",
        "operators": "Indian Army",
        "threat_classification": "High",
        "drdo_links": "https://www.drdo.gov.in/"
    },
    {
        "name": "Pinaka",
        "type": "Multi Barrel Rocket Launcher",
        "country": "India",
        "description": "Indigenous multiple rocket launcher system for area saturation.",
        "specs": "Range: 37–90 km | Rockets: 12 | Crew: 5",
        "operators": "Indian Army",
        "threat_classification": "High",
        "drdo_links": "https://www.drdo.gov.in/"
    },
    {
        "name": "BrahMos",
        "type": "Supersonic Cruise Missile",
        "country": "India / Russia",
        "description": "Supersonic cruise missile capable of land, sea, and air launch.",
        "specs": "Speed: Mach 2.8–3 | Range: 450+ km | Payload: 200–300 kg",
        "operators": "Indian Army, Indian Navy, Indian Air Force",
        "threat_classification": "Critical",
        "drdo_links": "https://www.drdo.gov.in/"
    },
    {
        "name": "Akash",
        "type": "Surface-to-Air Missile",
        "country": "India",
        "description": "Medium-range air defense missile system developed by DRDO.",
        "specs": "Range: 30–45 km | Speed: Mach 2.5 | Guidance: Radar",
        "operators": "Indian Army, Indian Air Force",
        "threat_classification": "High",
        "drdo_links": "https://www.drdo.gov.in/"
    },
    {
        "name": "Agni-V",
        "type": "Ballistic Missile",
        "country": "India",
        "description": "Intercontinental-range ballistic missile developed under India's strategic missile program.",
        "specs": "Range: 5000+ km | Payload: 1500 kg | Stages: 3",
        "operators": "Strategic Forces Command",
        "threat_classification": "Critical",
        "drdo_links": "https://www.drdo.gov.in/"
    },
    {
        "name": "Tejas Mk1A",
        "type": "Light Combat Aircraft",
        "country": "India",
        "description": "Single-engine multirole fighter aircraft developed by HAL and ADA.",
        "specs": "Max speed: Mach 1.8 | Range: 1850 km | Crew: 1",
        "operators": "Indian Air Force",
        "threat_classification": "High",
        "drdo_links": "https://www.drdo.gov.in/"
    },
    {
        "name": "HAL Prachand",
        "type": "Light Combat Helicopter",
        "country": "India",
        "description": "Attack helicopter designed for high-altitude warfare.",
        "specs": "Max speed: 268 km/h | Crew: 2 | Ceiling: 6500 m",
        "operators": "Indian Air Force, Indian Army",
        "threat_classification": "High",
        "drdo_links": "https://www.drdo.gov.in/"
    },
    {
        "name": "INS Vikrant",
        "type": "Aircraft Carrier",
        "country": "India",
        "description": "India's first indigenously built aircraft carrier.",
        "specs": "Displacement: 43,000 tons | Length: 262 m | Speed: 28 knots",
        "operators": "Indian Navy",
        "threat_classification": "Critical",
        "drdo_links": "https://www.drdo.gov.in/"
    },
    {
        "name": "INS Arihant",
        "type": "Nuclear Ballistic Missile Submarine",
        "country": "India",
        "description": "India's first indigenous nuclear-powered ballistic missile submarine.",
        "specs": "Displacement: 6000 tons | Propulsion: Nuclear | Armament: SLBMs",
        "operators": "Indian Navy",
        "threat_classification": "Critical",
        "drdo_links": "https://www.drdo.gov.in/"
    },
    {
        "name": "Rafale EH/DH",
        "type": "Multirole Fighter Aircraft",
        "country": "France",
        "description": "Advanced 4.5-generation fighter aircraft inducted into the Indian Air Force.",
        "specs": "Max speed: Mach 1.8 | Combat radius: 1850 km | Crew: 1/2",
        "operators": "Indian Air Force",
        "threat_classification": "High",
        "drdo_links": "https://www.drdo.gov.in/"
    }
]

conn = sqlite3.connect("database/prahar.db")
cursor = conn.cursor()

for w in WEAPONS:
    cursor.execute("""
        INSERT INTO weapons (name, type, country, description, specs, operators, threat_classification, drdo_links)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        w["name"], w["type"], w["country"], w["description"],
        w["specs"], w["operators"], w["threat_classification"], w["drdo_links"]
    ))

conn.commit()
conn.close()
print(f"Inserted {len(WEAPONS)} weapon(s) into the database.")