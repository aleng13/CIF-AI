import psycopg2
import numpy as np
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
from rag.embeddings import embed_query


load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def chunk_text(text, chunk_size=300):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks

def insert_document(cur, source, name, text):
    cur.execute(
        "INSERT INTO documents (source, name) VALUES (%s, %s) RETURNING id",
        (source, name)
    )
    document_id = cur.fetchone()[0]

    chunks = chunk_text(text)

    for idx, chunk in enumerate(chunks):
        # Use the real embedding function with is_search_query=False
        embedding = embed_query(chunk, is_search_query=False)
        
        cur.execute(
            """
            INSERT INTO document_chunks
            (document_id, chunk_index, content, embedding)
            VALUES (%s, %s, %s, %s)
            """,
            (document_id, idx, chunk, embedding)
        )

    print(f"Inserted '{name}' with {len(chunks)} chunks using Nomic embeddings")

def main():
    url = urlparse(DATABASE_URL)
    conn = psycopg2.connect(
        host=url.hostname,
        port=url.port,
        user=url.username,
        password=url.password,
        database=url.path.lstrip('/')
    )
    cur = conn.cursor()

    # Enable pgvector extension
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # Drop tables if exist
    cur.execute("DROP TABLE IF EXISTS document_chunks;")
    cur.execute("DROP TABLE IF EXISTS documents;")

    # Create tables
    cur.execute("""
        CREATE TABLE documents (
            id SERIAL PRIMARY KEY,
            source VARCHAR(50) NOT NULL,
            name VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT true
        );
    """)

    cur.execute("""
        CREATE TABLE document_chunks (
            id SERIAL PRIMARY KEY,
            document_id INTEGER REFERENCES documents(id),
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            embedding vector(768)
        );
    """)

    conn.commit()

    # ---------- PRIVACY POLICY ----------
    privacy_policy = """
    We value your privacy and are committed to protecting your personal data.
    We collect personal information such as name, email address, and payment
    details only for order processing and customer support purposes.
    We do not sell or share personal information with third parties except
    where required by law or for essential service providers.
    """

    insert_document(
        cur,
        source="policy",
        name="Privacy Policy",
        text=privacy_policy
    )

    # ---------- TERMS & CONDITIONS ----------
    terms_conditions = """
    By accessing and using our website, you agree to comply with these terms
    and conditions. Products are subject to availability and pricing changes
    without notice. Returns are accepted within 7 days of delivery if the
    product is unused and in original packaging.
    """

    insert_document(
        cur,
        source="policy",
        name="Terms and Conditions",
        text=terms_conditions
    )

    # ---------- SHIPPING POLICY ----------
    shipping_policy = """
    We offer standard and express shipping options for all orders.
    Standard shipping typically takes 3 to 5 business days, while express
    shipping takes 1 to 2 business days depending on the delivery location.
    Shipping charges are calculated at checkout based on the order value
    and delivery address.

    Once an order is shipped, customers will receive a tracking number
    via email to monitor delivery status. Delays may occur due to
    unforeseen circumstances such as weather conditions or logistics issues.
    """

    insert_document(
        cur,
        source="policy",
        name="Shipping Policy",
        text=shipping_policy
    )
    refund_return_policy = """
    Customers may request a return or refund within 7 days of receiving
    the product. To be eligible for a return, the item must be unused,
    undamaged, and in its original packaging with all accessories included.

    Refunds will be processed after the returned product is inspected
    and approved by our quality assurance team. Once approved, the refund
    will be issued to the original payment method within 5 to 7 business days.

    Certain products such as clearance items or products damaged due to
    misuse are not eligible for return or refund. Customers are responsible
    for return shipping costs unless the product was defective or incorrect.
    """

    insert_document(
        cur,
        source="policy",
        name="Refund and Return Policy",
        text=refund_return_policy
    )
    # ---------- PRODUCT DESCRIPTIONS ----------
    products = {
        "Smartphone X200": """
        The Smartphone X200 features a 6.5-inch AMOLED display, 128GB storage,
        and a 5000mAh battery. It supports fast charging and 5G connectivity,
        making it ideal for power users.
        """,

        "Wireless Headphones Pro": """
        Wireless Headphones Pro offer active noise cancellation, 30 hours of
        battery life, and high-fidelity sound. Designed for comfort during
        long listening sessions.
        """,

        "4K Smart Television 55-inch": """
        This 55-inch 4K Smart TV delivers ultra-high-definition visuals with
        HDR support. It includes built-in streaming apps and voice control
        functionality.
        """,
        "Bluetooth Speaker 01": """
        Bluetooth Speaker 01 delivers clear audio with enhanced bass in a compact
        portable design. It supports wireless connectivity up to 10 meters and
        offers up to 12 hours of continuous playback on a single charge.
        """,

        "Laptop Pro 14": """
        Laptop Pro 14 features a 14-inch Full HD display, Intel Core i7 processor,
        16GB RAM, and 512GB SSD storage. Designed for productivity, it offers fast
        performance and long battery life.
        """,

        "Wireless Mouse 02": """
        Wireless Mouse 02 provides precise cursor control with adjustable DPI
        settings. It connects via a USB receiver and is compatible with most
        operating systems.
        """,

        "Mechanical Keyboard 03": """
        Mechanical Keyboard 03 features tactile mechanical switches, customizable
        RGB backlighting, and a durable metal frame. Suitable for both gaming and
        professional use.
        """,

        "Smartwatch Active 04": """
        Smartwatch Active 04 includes fitness tracking features such as heart rate
        monitoring, step counting, and sleep analysis. It is water-resistant and
        supports smartphone notifications.
        """,

        "Noise Cancelling Earbuds 05": """
        Noise Cancelling Earbuds 05 offer immersive sound with active noise
        cancellation technology. They provide up to 6 hours of playback and come
        with a charging case for extended use.
        """,

        "External Hard Drive 1TB": """
        External Hard Drive 1TB provides reliable storage for backups and file
        transfers. It supports USB 3.0 connectivity for fast data transfer speeds.
        """,

        "Gaming Monitor 27": """
        Gaming Monitor 27 features a 27-inch Quad HD display with a 144Hz refresh
        rate. It supports low-latency performance and adaptive sync technology for
        smooth gameplay.
        """,

        "WiFi Router AX3000": """
        WiFi Router AX3000 supports high-speed wireless connectivity with dual-band
        WiFi 6 technology. It is suitable for streaming, gaming, and multiple device
        connections.
        """,

        "Power Bank 20000mAh": """
        Power Bank 20000mAh provides high-capacity portable charging for smartphones
        and tablets. It supports fast charging and multiple device connections.
        """,

        "USB-C Hub 07": """
        USB-C Hub 07 expands a single USB-C port into multiple connections including
        HDMI, USB-A, and SD card slots. Ideal for laptops with limited ports.
        """,

        "Smart Home Camera 08": """
        Smart Home Camera 08 offers 1080p video recording with night vision and
        motion detection. It supports remote monitoring via a mobile application.
        """,

        "Electric Kettle 09": """
        Electric Kettle 09 features a 1.7-liter capacity with automatic shut-off
        and boil-dry protection. Designed for fast and safe water heating.
        """,

        "Air Purifier Compact 10": """
        Air Purifier Compact 10 removes airborne particles such as dust, pollen,
        and allergens. Suitable for small to medium-sized rooms.
        """,

        "4K Streaming Device 11": """
        4K Streaming Device 11 enables streaming of high-definition content from
        popular platforms. It supports voice control and WiFi connectivity.
        """
    }

    for name, desc in products.items():
        insert_document(
            cur,
            source="product",
            name=name,
            text=desc
        )

    conn.commit()
    cur.close()
    conn.close()

    print("✅ Vector DB successfully populated with test documents.")

if __name__ == "__main__":
    main()
