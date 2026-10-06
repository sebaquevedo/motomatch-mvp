from config import SEED_DOCS_DIR
from db.models import Document, User
from rag.embeddings import EmbeddingService
from rag.vector_store import VectorStore


def seed_database(engine, SessionLocal):
    session = SessionLocal()
    try:
        # Create demo user (plaintext password is intentional: local demo only).
        demo_user = User(
            email="demo@motomatch.local",
            password_hash="DemoMotoMatch2024!",
        )
        session.add(demo_user)
        session.commit()
        session.refresh(demo_user)
        print("[OK] Created demo user: demo@motomatch.local")

        # Load seed documents (create them on first run if missing).
        if not SEED_DOCS_DIR.exists() or not any(SEED_DOCS_DIR.glob("*.txt")):
            print("[..] No seed docs found, creating sample catalog...")
            SEED_DOCS_DIR.mkdir(parents=True, exist_ok=True)
            create_sample_docs(SEED_DOCS_DIR)

        doc_files = sorted(SEED_DOCS_DIR.glob("*.txt"))
        print(f"[..] Found {len(doc_files)} seed documents")

        embedding_service = EmbeddingService()
        vector_store = VectorStore()
        # Start from a clean vector table so re-seeding never duplicates chunks.
        vector_store.reset()

        for doc_file in doc_files:
            content = doc_file.read_text(encoding="utf-8")
            doc = Document(
                title=doc_file.stem.replace("_", " ").title(),
                content=content,
                user_id=demo_user.id,
                file_size=len(content),
            )
            session.add(doc)
            session.commit()
            session.refresh(doc)

            # Generate embeddings for each chunk and store them.
            chunks = chunk_text(content, chunk_size=500, overlap=50)
            embeddings = embedding_service.embed_batch(chunks)
            vector_store.add_embeddings(
                doc_id=doc.id,
                chunks=chunks,
                embeddings=embeddings,
            )
            print(f"  [OK] {doc.title}: {len(chunks)} chunks indexed")

        print("[OK] Database seeding complete!")
    finally:
        session.close()


def chunk_text(text, chunk_size=500, overlap=50):
    step = max(1, chunk_size - overlap)
    chunks = []
    for i in range(0, len(text), step):
        chunk = text[i : i + chunk_size]
        if chunk.strip():
            chunks.append(chunk)
    return chunks


def create_sample_docs(seed_docs_path):
    docs = {
        "honda_cb650f_alternator.txt": """PRODUCT CATALOG ENTRY
Product: Honda CB650F Alternator
Brand: Honda
Model: CB650F
Year: 2020

SPECIFICATIONS:
- Output: 50A at 14.5V
- Terminal Type: 3-pin connector
- Weight: 1.2 kg
- Mounting: Direct bolt-on

COMPATIBILITY:
Compatible: CB650F (2017-2022), CB500F (2013-2015)
With modification: CB600F (2011-2013) - voltage regulator required
Not compatible: CBR650R

NOTES:
Widely available, excellent reliability for commuter bikes.""",
        "honda_cb650f_starter.txt": """PRODUCT CATALOG ENTRY
Product: Honda CB650F Starter Motor
Brand: Honda
Model: CB650F
Year: 2020

SPECIFICATIONS:
- Power: 0.8 kW
- Voltage: 12V DC
- Mounting: Under engine, right side
- Weight: 1.6 kg
- Rotation: Counter-clockwise

COMPATIBILITY:
Compatible: CB650F (2017-2022), CB500F (2013-2022)
With modification: CB400 (2008-2015)
Not compatible: CBR650R, CB1000R""",
        "honda_cb650f_fuel_pump.txt": """PRODUCT CATALOG ENTRY
Product: Honda CB650F Fuel Pump
Brand: Honda
Model: CB650F
Year: 2020

SPECIFICATIONS:
- Flow rate: 50L/hour
- Pressure: 3.5 Bar
- Power consumption: 12A
- Weight: 0.5 kg

COMPATIBILITY:
Direct fit: CB650F (2017-2022)
Compatible with aftermarket: CB500F, CB400""",
        "honda_cb650f_battery.txt": """PRODUCT CATALOG ENTRY
Product: Honda CB650F Battery
Brand: Honda
Model: CB650F
Year: 2020

SPECIFICATIONS:
- Type: YTZ12S (Lithium)
- Voltage: 12V
- Capacity: 11Ah
- Weight: 1.6 kg

COMPATIBILITY:
Direct fit: CB650F (2017-2022)
Alternative: CB500F (2013-2022)""",
        "honda_cb650f_ignition_coil.txt": """PRODUCT CATALOG ENTRY
Product: Honda CB650F Ignition Coil
Brand: Honda
Model: CB650F
Year: 2020

SPECIFICATIONS:
- Primary coil resistance: 0.5 Ohm
- Secondary coil resistance: 10.5 kOhm
- Spark plug wire: 5mm
- Weight: 0.3 kg

COMPATIBILITY:
CB650F (2017-2022)
CB500F (parts compatible)""",
        "honda_cb650f_carburetor.txt": """PRODUCT CATALOG ENTRY
Product: Honda CB650F Carburetor (per cylinder)
Brand: Honda
Model: CB650F
Year: 2020

SPECIFICATIONS:
- Bore: 30mm
- Needle position: 3rd groove
- Jet needle: 5H23
- Main jet: #118
- Pilot jet: #38
- Air jet: #125

COMPATIBILITY:
CB650F (2017-2022) - 4 units per bike
CB500F compatible carburetors available""",
        "honda_cb650f_clutch_cable.txt": """PRODUCT CATALOG ENTRY
Product: Honda CB650F Clutch Cable
Brand: Honda
Model: CB650F
Year: 2020

SPECIFICATIONS:
- Length: 1560mm
- Inner wire diameter: 1.5mm
- Material: Steel braided
- Weight: 0.2 kg

COMPATIBILITY:
Direct fit: CB650F (2017-2022)
Aftermarket universal: CB500F""",
        "honda_cb650f_brake_pads.txt": """PRODUCT CATALOG ENTRY
Product: Honda CB650F Brake Pads (Front/Rear)
Brand: Honda
Model: CB650F
Year: 2020

SPECIFICATIONS:
- Type: Semi-metallic
- Thickness: 5mm
- Friction coefficient: 0.45
- Weight per set: 0.4 kg

COMPATIBILITY:
CB650F (2017-2022)
Compatible aftermarket: Brembo, EBC""",
        "honda_cb650f_air_filter.txt": """PRODUCT CATALOG ENTRY
Product: Honda CB650F Air Filter
Brand: Honda
Model: CB650F
Year: 2020

SPECIFICATIONS:
- Type: Paper element
- Dimensions: 150x130x100mm
- Flow capacity: 200 CFM
- Weight: 0.15 kg

COMPATIBILITY:
CB650F (2017-2022)
Aftermarket alternatives: K&N, DNA""",
        "honda_cbr650r_alternator.txt": """PRODUCT CATALOG ENTRY
Product: Honda CBR650R Alternator (Electronic)
Brand: Honda
Model: CBR650R
Year: 2021

SPECIFICATIONS:
- Output: 60A at 14.5V
- Type: Electronic regulator
- Terminal Type: 4-pin connector
- Weight: 1.4 kg

COMPATIBILITY:
Direct fit: CBR650R (2019-2024)
NOT compatible with: CB650F (different connector)
Reason: CBR uses electronic voltage regulation vs mechanical in CB650F""",
    }

    for filename, content in docs.items():
        (seed_docs_path / filename).write_text(content, encoding="utf-8")
    print(f"[OK] Created {len(docs)} sample documents")
