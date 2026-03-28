import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="bincom_test"
    )

# ---------------- Question 1 ----------------
def get_polling_unit_results():
    pu_id = input("Enter Polling Unit ID: ")
    conn = connect_db()
    cursor = conn.cursor()

    query = """
    SELECT party_abbreviation, COALESCE(party_score,0) as party_score
    FROM announced_pu_results
    WHERE polling_unit_uniqueid = %s
    ORDER BY party_abbreviation
    """
    cursor.execute(query, (pu_id,))
    results = cursor.fetchall()

    if results:
        print(f"\nResults for Polling Unit {pu_id}:\n")
        for party, score in results:
            print(f"{party}: {score}")
    else:
        print(f"No results found for Polling Unit {pu_id}.")
    conn.close()

# ---------------- Question 2 ----------------
def get_lga_results():
    conn = connect_db()
    cursor = conn.cursor()

    print("\nAvailable LGAs:")
    cursor.execute("SELECT lga_id, lga_name FROM lga")
    for lga_id, lga_name in cursor.fetchall():
        print(f"{lga_id}: {lga_name}")

    lga_id = input("\nEnter LGA ID to see total results: ")

    query = """
    SELECT apr.party_abbreviation, SUM(COALESCE(apr.party_score,0)) as total_score
    FROM announced_pu_results apr
    JOIN polling_unit pu ON pu.uniqueid = apr.polling_unit_uniqueid
    WHERE pu.lga_id = %s
    GROUP BY apr.party_abbreviation
    ORDER BY apr.party_abbreviation
    """
    cursor.execute(query, (lga_id,))
    results = cursor.fetchall()

    if results:
        print(f"\nTotal Results for LGA {lga_id}:\n")
        for party, total in results:
            print(f"{party}: {total}")
    else:
        print(f"No results found for LGA {lga_id}. Check LGA ID.")
    conn.close()

# ---------------- Question 3 ----------------
def insert_polling_unit_results():
    conn = connect_db()
    cursor = conn.cursor()

    pu_name = input("Enter new Polling Unit Name: ")
    lga_id = int(input("Enter LGA ID for new PU: "))
    ward_id = int(input("Enter Ward ID for new PU: "))

    cursor.execute("SELECT MAX(polling_unit_id) FROM polling_unit")
    max_id = cursor.fetchone()[0] or 0
    new_id = max_id + 1

    cursor.execute(
        "INSERT INTO polling_unit (polling_unit_id, ward_id, lga_id, polling_unit_name) VALUES (%s, %s, %s, %s)",
        (new_id, ward_id, lga_id, pu_name)
    )
    conn.commit()

    cursor.execute("SELECT MAX(uniqueid) FROM polling_unit")
    pu_uniqueid = cursor.fetchone()[0]
    print(f"New Polling Unit ID = {pu_uniqueid}")

    parties = ["PDP", "DPP", "ACN", "PPA", "CDC", "JP"]
    entered_by = "Admin"
    user_ip = "127.0.0.1"

    for party in parties:
        while True:
            try:
                score = int(input(f"Enter score for {party}: "))
                break
            except ValueError:
                print("Please enter a valid integer.")

        cursor.execute(
            """
            INSERT INTO announced_pu_results 
            (polling_unit_uniqueid, party_abbreviation, party_score, entered_by_user, date_entered, user_ip_address)
            VALUES (%s, %s, %s, %s, NOW(), %s)
            """,
            (pu_uniqueid, party, score, entered_by, user_ip)
        )

    conn.commit()
    conn.close()
    print("Polling unit results successfully saved!")

# ---------------- Menu ----------------
def main_menu():
    while True:
        print("\n--- Bincom Python Internship ---")
        print("1. Display results for a Polling Unit")
        print("2. Display summed results for an LGA")
        print("3. Insert results for a new Polling Unit")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")
        if choice == "1":
            get_polling_unit_results()
        elif choice == "2":
            get_lga_results()
        elif choice == "3":
            insert_polling_unit_results()
        elif choice == "4":
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main_menu()