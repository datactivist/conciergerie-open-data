import sqlite3


# Parameter: Database pointer and sql command
# Function: Run the sql command
def run_sql_command(cursor, sql_command, data):

    try:
        if data is not None:
            cursor.execute(sql_command, data)
        else:
            cursor.execute(sql_command)

        print(sql_command, data)

        record = cursor.fetchall()

        print(record, "\n")

        return record

    except sqlite3.Error as error:
        print(
            "\nError while running this command: \n",
            sql_command,
            "\n",
            error,
            "\n",
        )
        return None


# Parameter: search_data = (conversation_id, keywords_user)
# Function: Add a new search entry in the database
def add_new_search_query(search_data):
    database = "rasa.db"

    conversation_id = search_data[0]
    keywords_user = search_data[1]

    try:

        sqliteConnection = sqlite3.connect(database)
        cursor = sqliteConnection.cursor()

        sqlite_check_feedback_exist_query = (
            'SELECT * FROM feedback_user_search where conversation_id = "'
            + conversation_id
            + '" and keywords_user = "'
            + keywords_user
            + '";'
        )

        record = run_sql_command(cursor, sqlite_check_feedback_exist_query, None)

        if len(record) == 0:

            sqlite_insert_feedback_query = "INSERT INTO feedback_user_search(conversation_id, keywords_user) VALUES(?, ?);"
            run_sql_command(
                cursor, sqlite_insert_feedback_query, (conversation_id, keywords_user)
            )

        sqliteConnection.commit()
        cursor.close()

    except sqlite3.Error as error:
        print("-ADD_NEW_SEARCH_QUERY-\nError while connecting to sqlite", error, "\n")


# Parameter: search_data = (conversation_id, keywords_user)
#            feedback_augmentation_results = (keywords_augmentation, keywords_chosen)
# Function: Add the feedback in the database
def add_feedback_augmentation(search_data, feedback_augmentation_data):

    database = "rasa.db"

    conversation_id = search_data[0]
    keywords_user = search_data[1]

    try:

        sqliteConnection = sqlite3.connect(database)
        cursor = sqliteConnection.cursor()

        sqlite_insert_feedback_query = "INSERT INTO feedback_search_augmentation(keywords_augmentation, keywords_chosen) VALUES(?, ?);"
        run_sql_command(
            cursor, sqlite_insert_feedback_query, feedback_augmentation_data
        )

        sqlite_get_last_id = (
            'SELECT id FROM feedback_search_augmentation WHERE keywords_augmentation = "'
            + feedback_augmentation_data[0]
            + '" and keywords_chosen = "'
            + feedback_augmentation_data[1]
            + '" ORDER BY id DESC;'
        )

        record = run_sql_command(cursor, sqlite_get_last_id, None)

        feedback_id = record[0][0]

        sqlite_link_feedback_query = (
            "UPDATE feedback_user_search SET search_feedback_id = "
            + str(feedback_id)
            + ' WHERE conversation_id = "'
            + conversation_id
            + '" and keywords_user = "'
            + keywords_user
            + '";'
        )

        run_sql_command(cursor, sqlite_link_feedback_query, None)

        sqliteConnection.commit()
        cursor.close()

    except sqlite3.Error as error:
        print(
            "-ADD_FEEDBACK_AUGMENTATION-\nError while connecting to sqlite", error, "\n"
        )


# Parameter: search_data = (conversation_id, keywords_user)
#            feedback_results_data = (results, feedback_results)
# Function: Add the feedback in the database
def add_feedback_results(search_data, feedback_results_data):

    database = "rasa.db"

    conversation_id = search_data[0]
    keywords_user = search_data[1]

    try:

        sqliteConnection = sqlite3.connect(database)
        cursor = sqliteConnection.cursor()

        sqlite_insert_feedback_query = (
            "INSERT INTO feedback_results(results, feedback_results) VALUES(?, ?);"
        )
        run_sql_command(cursor, sqlite_insert_feedback_query, feedback_results_data)

        sqlite_get_last_id = (
            'SELECT id FROM feedback_results WHERE results = "'
            + feedback_results_data[0]
            + '" and feedback_results = "'
            + feedback_results_data[1]
            + '" ORDER BY id DESC;'
        )

        record = run_sql_command(cursor, sqlite_get_last_id, None)

        feedback_id = record[0][0]

        sqlite_link_feedback_query = (
            "UPDATE feedback_user_search SET results_feedback_id = "
            + str(feedback_id)
            + ' WHERE conversation_id = "'
            + conversation_id
            + '" and keywords_user = "'
            + keywords_user
            + '";'
        )

        run_sql_command(cursor, sqlite_link_feedback_query, None)

        sqliteConnection.commit()
        cursor.close()

    except sqlite3.Error as error:
        print("-ADD_FEEDBACK_RESULTS-\nError while connecting to sqlite", error, "\n")


# sqliteconnect = sqlite3.connect("../rasa.db")
# cursor = sqliteconnect.cursor()
# run_sql_command(
#    cursor,
#    'SELECT results_feedback_id FROM feedback_user_search where conversation_id = "ad48ad0849f04ca7a26aa1fdb2d273e0" and keywords_user = "barrages"; ',
#    None,
# )
