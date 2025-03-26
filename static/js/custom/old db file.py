

def insert_baptism(fname: str, mname: str, lname: str, birthday: str, birthplace: str, ligitivity: str, address: str,
                   mother_fname: str, mother_mname: str, mother_lname: str, mother_birthday: str, mother_bplace: str, mother_address: str, 
                   father_fname: str, father_mname: str, father_lname: str, father_birthday: str, father_bplace: str, father_address: str, 
                   date: str, priest: str, sponsor1: str, sponsor1_residence: str, sponsor2: str, sponsor2_residence: str):
    connection = get_db_connection()
    print("INSERTING DATA START")

    if connection is None:
        raise Exception("Could not connect to the database.")

    # Check if the combination of first and last name already exists
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM client WHERE fname = %s AND lname = %s;",
        (fname, lname)
    )
    existing_user = cursor.fetchone()

    if existing_user:
        raise UsernameAlreadyExistsException("Data Exists")
    else:
        print("No Existing User!")

    # Insert into client table
    cursor.execute("""
        INSERT INTO client (fname, mname, lname, birthday, ligitivity, birthplace, address)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (fname, mname, lname, birthday, ligitivity, birthplace, address))
    connection.commit()
    client_id = cursor.lastrowid
    print("Data inserted successfully, here is the client ID: ", client_id)

    # Check if parents already exist
    existing_parents = db.check_existing_parents(mother_fname, mother_mname, mother_lname, mother_birthday, mother_bplace, father_fname, father_mname, father_lname, father_birthday, father_bplace)
    mother_id = None
    father_id = None

    for parent in existing_parents:
        if parent['role'] == 'mother':
            mother_id = parent['parent_id']
        if parent['role'] == 'father':
            father_id = parent['parent_id']

    connection = db.get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Insert mother if not exists
    if mother_id is None:
        cursor.execute("""
            INSERT INTO parents (fname, mname, lname, birthday, birthplace, address)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (mother_fname, mother_mname, mother_lname, mother_birthday, mother_bplace, mother_address))
        connection.commit()
        mother_id = cursor.lastrowid

    # Insert father if not exists
    if father_id is None:
        cursor.execute("""
            INSERT INTO parents (fname, mname, lname, birthday, birthplace, address)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (father_fname, father_mname, father_lname, father_birthday, father_bplace, father_address))
        connection.commit()
        father_id = cursor.lastrowid

    # Insert into the relationship table with roles
    cursor.execute("SELECT 1 FROM relationship WHERE child_id = %s", (client_id,))
    if cursor.fetchone() is None:
        cursor.execute("""
            INSERT INTO relationship (child_id, parent_id, role) 
            VALUES (%s, %s, 'mother')
        """, (client_id, mother_id))
        connection.commit()

        cursor.execute("""
            INSERT INTO relationship (child_id, parent_id, role) 
            VALUES (%s, %s, 'father')
        """, (client_id, father_id))
        connection.commit()

    # Insert into the baptism table
    cursor.execute("""
        INSERT INTO baptism (baptism_date, client_id, sponsorA, residenceA, sponsorB, residenceB, priest_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (date, client_id, sponsor1, sponsor1_residence, sponsor2, sponsor2_residence, priest))

    connection.commit()
    print('Data inserted')

    # Close the cursor and connection
    cursor.close()
    connection.close()

def delete_baptism(user_id):
    connection = get_db_connection()
    print('DB: Delete Data')
    print('ID')
    print(user_id)
    
    if connection is None:
        raise Exception("Could not connect to the database.")

    # Check if name if already exists
    cursor = connection.cursor(dictionary=True)
    cursor.execute("DELETE FROM baptism WHERE id = %s", (user_id,))


    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()

def update_baptism(baptism_id: str, client_id: str, fname: str, mname: str, lname: str, birthday: str, birthplace: str, ligitivity: str, address: str,
                   mother_fname: str, mother_mname: str, mother_lname: str, mother_birthday: str, mother_bplace: str, mother_address: str, 
                   father_fname: str, father_mname: str, father_lname: str, father_birthday: str, father_bplace: str, father_address: str, 
                   date: str, priest: str, sponsor1: str, sponsor1_residence: str, sponsor2: str, sponsor2_residence: str):
    connection = get_db_connection()
    print("UPDATING DATA START")

    if connection is None:
        raise Exception("Could not connect to the database.")

    cursor = connection.cursor(dictionary=True)

    # Check if the client exists
    cursor.execute("SELECT * FROM client WHERE id = %s;", (client_id,))
    existing_user = cursor.fetchone()

    if not existing_user:
        raise Exception("Client not found.")

    # Update client table
    cursor.execute("""
        UPDATE client
        SET fname = %s, mname = %s, lname = %s, birthday = %s, ligitivity = %s, birthplace = %s, address = %s
        WHERE id = %s
    """, (fname, mname, lname, birthday, ligitivity, birthplace, address, client_id))
    connection.commit()
    print("Client data updated successfully.")

    # Update parents table for mother
    cursor.execute("""
        UPDATE parents
        SET fname = %s, mname = %s, lname = %s, birthday = %s, birthplace = %s, address = %s
        WHERE id = (
            SELECT parent_id 
            FROM relationship 
            WHERE child_id = %s AND role = 'mother'
        )
    """, (mother_fname, mother_mname, mother_lname, mother_birthday, mother_bplace, mother_address, client_id))
    connection.commit()
    print("Mother data updated successfully.")

    # Update parents table for father
    cursor.execute("""
        UPDATE parents
        SET fname = %s, mname = %s, lname = %s, birthday = %s, birthplace = %s, address = %s
        WHERE id = (
            SELECT parent_id 
            FROM relationship 
            WHERE child_id = %s AND role = 'father'
        )
    """, (father_fname, father_mname, father_lname, father_birthday, father_bplace, father_address, client_id))
    connection.commit()
    print("Father data updated successfully.")

    # Update baptism table
    cursor.execute("""
        UPDATE baptism
        SET baptism_date = %s, sponsorA = %s, residenceA = %s, sponsorB = %s, residenceB = %s, priest_id = %s
        WHERE id = %s
    """, (date, sponsor1, sponsor1_residence, sponsor2, sponsor2_residence, priest, baptism_id))
    connection.commit()
    print("Baptism data updated successfully.")

    # Close the cursor and connection
    cursor.close()
    connection.close()
    print("Data updated.")
