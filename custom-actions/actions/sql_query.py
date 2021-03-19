import sqlite3
from datetime import datetime

database = "../rasa.db"

# Parameter: Database pointer, sql command, and the data used for the command
# Function: Run the sql command
def run_sql_command(cursor, sql_command, data):

    try:
        if data is not None:
            cursor.execute(sql_command, data)
        else:
            cursor.execute(sql_command)

        record = cursor.fetchall()

        return record

    except sqlite3.Error as error:
        print(
            "\nError while running this command: \n", sql_command, "\n", error, "\n",
        )
        return None


# Function: Add a new search entry in the database
def add_new_search_query(
    conversation_id, keywords_user, flag_activate_sql_query_commit
):

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:

        sqliteConnection = sqlite3.connect(database)
        cursor = sqliteConnection.cursor()

        sqlite_insert_feedback_query = (
            "INSERT INTO search(conversation_id, keywords_user, date) VALUES(?, ?, ?);"
        )
        run_sql_command(
            cursor,
            sqlite_insert_feedback_query,
            (conversation_id, keywords_user, date),
        )

        if flag_activate_sql_query_commit:
            sqliteConnection.commit()
        cursor.close()
        sqliteConnection.close()

    except sqlite3.Error as error:
        print("-ADD_NEW_SEARCH_QUERY-\nError while connecting to sqlite", error, "\n")


# Function: Add the keyword proposed in the database
def add_keyword_proposed(
    conversation_id,
    keywords_user,
    keyword_proposed,
    feedback,
    flag_activate_sql_query_commit,
):

    try:

        sqliteConnection = sqlite3.connect(database)
        cursor = sqliteConnection.cursor()

        search_id = get_search_id(conversation_id, keywords_user)

        if search_id is not None:

            sqlite_check_keyword_proposed_exist_query = "SELECT id FROM search_augmentation WHERE search_id = ? and keyword_proposed = ?"

            record = run_sql_command(
                cursor,
                sqlite_check_keyword_proposed_exist_query,
                (search_id, keyword_proposed),
            )

            if len(record) > 0:

                augmentation_id = record[0][0]

                sqlite_update_result_query = (
                    "UPDATE search_augmentation SET feedback = ? WHERE id = ?"
                )

                run_sql_command(
                    cursor, sqlite_update_result_query, (feedback, augmentation_id)
                )

            else:

                sqlite_insert_result_query = "INSERT INTO search_augmentation(search_id, keyword_proposed, feedback) VALUES(?, ?, ?);"

                run_sql_command(
                    cursor,
                    sqlite_insert_result_query,
                    (search_id, keyword_proposed, feedback),
                )

            if flag_activate_sql_query_commit:
                sqliteConnection.commit()

        cursor.close()
        sqliteConnection.close()

    except sqlite3.Error as error:
        print(
            "-ADD_FEEDBACK_AUGMENTATION-\nError while connecting to sqlite", error, "\n"
        )


# Parameter: result_data = (results_title, results_url)
# Function: Add the results of a query in the database
def add_result(
    conversation_id,
    keywords_user,
    result_data,
    feedback,
    flag_activate_sql_query_commit,
):

    try:

        sqliteConnection = sqlite3.connect(database)
        cursor = sqliteConnection.cursor()

        search_id = get_search_id(conversation_id, keywords_user)

        if search_id is not None:

            sqlite_check_result_exist_query = "SELECT id FROM search_results WHERE search_id = ? and result_title = ? and result_url = ?"

            record = run_sql_command(
                cursor,
                sqlite_check_result_exist_query,
                (search_id, result_data[0], result_data[1]),
            )

            if len(record) > 0:

                result_id = record[0][0]

                sqlite_update_result_query = (
                    "UPDATE search_results SET feedback = ? WHERE id = ?"
                )

                run_sql_command(
                    cursor, sqlite_update_result_query, (feedback, result_id)
                )

            else:

                sqlite_insert_result_query = "INSERT INTO search_results(search_id, result_title, result_url, feedback) VALUES(?, ?, ?, ?);"

                run_sql_command(
                    cursor,
                    sqlite_insert_result_query,
                    (search_id, result_data[0], result_data[1], feedback),
                )

            if flag_activate_sql_query_commit:
                sqliteConnection.commit()

        cursor.close()
        sqliteConnection.close()

    except sqlite3.Error as error:
        print("-ADD_FEEDBACK_RESULTS-\nError while connecting to sqlite", error, "\n")


# Return the search_id corresponding to these parameters
def get_search_id(conversation_id, keywords_user):

    try:

        sqliteConnection = sqlite3.connect(database)
        cursor = sqliteConnection.cursor()

        sqlite_get_search_id_query = "SELECT id FROM search where conversation_id = ? and keywords_user = ? ORDER BY id DESC;"
        record = run_sql_command(
            cursor, sqlite_get_search_id_query, (conversation_id, keywords_user)
        )

        if len(record) > 0:
            return record[0][0]
        else:
            return None

    except sqlite3.Error as error:
        print("-GET_SEARCH_ID-\nError while connecting to sqlite", error, "\n")
