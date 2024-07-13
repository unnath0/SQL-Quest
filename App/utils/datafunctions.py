import mysql.connector as m
import re

users_database='sqlquest6'
world_database='sqlquest6_world'
sandbox_database='sqlquest6_sandbox'

connection = m.connect(host='localhost',user='root',password='',database=users_database)
cursor = connection.cursor()
connection_world = m.connect(host='localhost',user='root',password='',database=world_database)
cursor_world = connection_world.cursor()
connection_sandbox = m.connect(host='localhost',user='root',password='',database=sandbox_database)
cursor_sandbox = connection_sandbox.cursor()

def OnSignUP_AddDataToUsersTable(username, email, password):
    add_user = "INSERT INTO users (Username, Email, Password) VALUES (%s, %s, %s)"
    try:
        cursor.execute(add_user, (username, email, password))
        connection.commit()
        print("User added successfully")
        return True
    except Exception as e:
        print(f"Error occurred while adding user: {e}")
        return False
def OnSignIN_CheckForValidUserPassword(username, password):
    try:
        sanitized_username = username.replace("'", "''")
        sanitized_password = password.replace("'", "''")
        query = f"SELECT * FROM users WHERE Username = '{sanitized_username}' AND Password = '{sanitized_password}'"
        cursor.execute(query)
        user = cursor.fetchone()
        if user:
            return user[0]
        else:
            return 0
    except Exception as e:
        print(f"Error occurred while checking user credentials: {e}")
        return 0

def On_LoginLogout_AddDataToLogsTable(userid, logValue):
    try:
        cursor.callproc("InsertLoginLogoutLog", [userid, logValue])
        connection.commit()
        print("Stored procedure called successfully")
    except m.Error as error:
        print(f"Error calling stored procedure: {error}")
        connection.rollback()
    
def GetUserTotalModuleProgressDetails(userID):
    query = f"select sum(CompletedQuestions) as TotalCompletedQuestions,sum(TotalQuestions) as OverallTotalQuestions,(sum(CompletedQuestions)/sum(TotalQuestions))*100 as OverallProgress from usermoduleprogress where UserID = {userID}"
    cursor.execute(query)
    result = cursor.fetchall()
    # Convert list of tuples to list of dictionaries
    columns = [col[0] for col in cursor.description]  # Get column names
    data = dict(zip(columns,result[0])) if result else {}
    """
    #This is how the "data" looks after getting from database
        data= {'TotalCompletedQuestions': <sum(CompletedQuestions)>,
               'OverallTotalQuestions': <sum(TotalQuestions)>,
               'OverallProgress': <Overall_percentage_progress>}
    """
    return data

def GetUserEachModuleProgressDetails(userID):
    query= f"select A.ModuleID,A.Description,B.CompletedQuestions,B.TotalQuestions,B.ProgressPercentage from modules A,usermoduleprogress B where A.ModuleID = B.ModuleID and UserID = {userID}"
    cursor.execute(query)
    result = cursor.fetchall()
    # Convert list of tuples to list of dictionaries
    columns = [col[0] for col in cursor.description]  # Get column names
    alldata = [dict(zip(columns, row)) for row in result]
    return alldata
    """
    #This is how the "alldata" looks after getting from database
        alldata = [
                    {
                        'ModuleID': <value_of_ModuleID_1>,
                        'Description': <value_of_Description_1>,
                        'CompletedQuestions': <value_of_CompletedQuestions_1>,
                        'TotalQuestions': <value_of_TotalQuestions_1>,
                        'ProgressPercentage': <value_of_ProgressPercentage_1>
                    },
                    {
                        'ModuleID': <value_of_ModuleID_2>,
                        'Description': <value_of_Description_2>,
                        'CompletedQuestions': <value_of_CompletedQuestions_2>,
                        'TotalQuestions': <value_of_TotalQuestions_2>,
                        'ProgressPercentage': <value_of_ProgressPercentage_2>
                    },
                    # and so on for each module
                ]
    """

def GetAllModuleInto():
    query="select * from modules;"
    cursor.execute(query)
    result=cursor.fetchall()
    columns = [col[0] for col in cursor.description]  # Get column names
    moduleinfo= [dict(zip(columns, row)) for row in result]
    return moduleinfo
    
def GetAllQuestionsDetailsOfUser(userid):
    # Define the SQL query
    getSideBarInfoOfUser = f"SELECT u.ModuleID, m.Description, u.QuestionID, u.IsCorrect FROM modules m, usertotalprogress u WHERE m.ModuleID = u.ModuleID AND u.UserID = {userid};"
    
    # Execute the query
    cursor.execute(getSideBarInfoOfUser)
    result = cursor.fetchall()

    # Convert list of tuples to list of dictionaries
    columns = [col[0] for col in cursor.description]  # Get column names
    sideBarInfoDict = [dict(zip(columns, row)) for row in result]
    
    return sideBarInfoDict
    # Initialize a dictionary to group by ModuleID and Description
def GetQuestionID_fromModuleID(moduleid):
    GetQuestionIDFromSelectedModule=f"select questionid from questions where moduleid={moduleid} limit 1"
    cursor.execute(GetQuestionIDFromSelectedModule)
    questionID = cursor.fetchone()[0]
    return questionID
def GetSelectedQuestionDetails(questionID,userID,moduleid):
  if(not questionID):
    GetQuestionIDFromSelectedModule=f"select questionid from questions where moduleid={moduleid} limit 1"
    cursor.execute(GetQuestionIDFromSelectedModule)
    questionID = cursor.fetchone()[0]
 
  getQuestionInfo = f"select A.Description,B.CompletedQuestions,B.TotalQuestions,B.ProgressPercentage,C.QuestionID,C.QuestionText,C.CorrectAnswer from modules A, usermoduleprogress B, questions C where A.ModuleID = B.ModuleID and A.ModuleID = C.ModuleID and B.UserID = {userID} and C.QuestionId = {questionID}"
  
  cursor.execute(getQuestionInfo)
  result = cursor.fetchall()

  # Convert list of tuples to single dictionary
  columns = [col[0] for col in cursor.description]  # Get column names
  questionInfoDict = dict(zip(columns,result[0])) if result else {}

  return questionInfoDict


def CheckSyntaxErrorInUserQuery(userquery,user_id,question_id):
    myquery = f"SELECT ModuleID, CorrectAnswer FROM Questions WHERE QuestionID = {question_id}"
    cursor.execute(myquery)
    result = cursor.fetchone()
    module_id, answerquery = result

    forbidden_words = [
        'truncate', 'use','delete', 'drop', 'alter', 'rename', 'modify', 'create', 'insert','show','databases','database',
        'grant', 'revoke', 'shutdown', 'flush', 'set', 'analyze', 'optimize', 'repair', 'load',
        'outfile', 'infile', 'shutdown', 'create user'
    ]
    obj_data_query = {'Check': False, 'ErrorMsg': "None"}
    found_forbidden_words = [word for word in forbidden_words if re.search(r'\b{}\b'.format(word), userquery, re.IGNORECASE)]

    if found_forbidden_words:
        #msg=f"HACKER Abhinava Trying Hacking - Try better shorty: {', '.join(found_forbidden_words)}"
        msg=f"SQL-Injection Detected in query : {', '.join(found_forbidden_words)}"
        obj_data_query['ErrorMsg'] = msg

        insert_query = "INSERT INTO QuestionAttemptLogs (UserID, QuestionID,ModuleID,IsCorrect,User_Answer) VALUES (%s,%s, %s, %s, %s)"
        cursor.execute(insert_query, (user_id, question_id,module_id,0,userquery))
        connection.commit()  # Commit the transaction
        print("New entry inserted into QuestionAttemptLogs successfully")

        return obj_data_query
    try:
        # Execute the userquery
        cursor_world.execute(userquery)
        cursor_world.fetchall()
        obj_data_query['Check'] = True
        is_correct=CheckCorrectnessOfUserQuery(userquery,user_id,question_id)
        insert_query = "INSERT INTO QuestionAttemptLogs (UserID, QuestionID,ModuleID,IsCorrect,User_Answer) VALUES (%s,%s, %s, %s, %s)"
        cursor.execute(insert_query, (user_id, question_id,module_id,is_correct,userquery))
        connection.commit()  # Commit the transaction
        print("New entry inserted into QuestionAttemptLogs successfully")
    except m.Error as e:
        print("User query error:", e)
        obj_data_query['ErrorMsg'] = e
        insert_query = "INSERT INTO QuestionAttemptLogs (UserID, QuestionID,ModuleID,IsCorrect,User_Answer) VALUES (%s,%s, %s, %s, %s)"
        cursor.execute(insert_query, (user_id, question_id,module_id,0,userquery))
        connection.commit()  # Commit the transaction
        print("New entry inserted into QuestionAttemptLogs successfully")
    return obj_data_query

def CheckCorrectnessOfUserQuery(userquery,user_id,question_id):
    myquery = f"SELECT ModuleID, CorrectAnswer FROM Questions WHERE QuestionID = {question_id}"
    cursor.execute(myquery)
    result = cursor.fetchone()
    module_id, answerquery = result
    try:
        # Execute the user query
        cursor_world.execute(userquery)
        result1 = cursor_world.fetchall()
    except m.Error as e:
        print(f"Error executing user queries: {e}")
        result1=[]

    # Execute the answer query 
    cursor_world.execute(answerquery)
    result2 = cursor_world.fetchall()
    # Check if the result sets are the same
    if result1 == result2:
        print("Results are the same")
        return True
    else:
        print("Results are different")
        return False

def GetUserAnswer(userid,questionid):
    if userid is None or questionid is None:
        return None 
    query=f"select User_Answer from usertotalprogress where userid={userid} and questionid={questionid};"
    cursor.execute(query)
    result=cursor.fetchall()
    user_answer = result[0][0].strip()
    return user_answer

def get_data_fromQuery(user_Query):
    Data_dit={"TableColumnHeadings":[],"TableRowData":[],"RowCount":0}
    data=[]
    cursor_world.execute(user_Query)
    column_headings = [col[0] for col in cursor_world.description]
    for i in cursor_world:
        data.append(list(i))
    Data_dit["TableColumnHeadings"]=column_headings
    Data_dit["TableRowData"]=data
    Data_dit["RowCount"]=cursor_world.rowcount
    return Data_dit

def GetTableToShowDetails_5rows(questionID):
    query=f"select TableUsed from questions where QuestionId={questionID};"
    cursor.execute(query)
    result=cursor.fetchall()
    tablename=result[0][0].strip()
    
    Data_dit={"TableName":tablename,"TableColumnHeadings":[],"TableRowData":[],"RowCount":0}
    data=[]
    cursor_world.execute(f"Select * from {tablename} limit 5;")
    column_headings = [col[0] for col in cursor_world.description]
    for i in cursor_world:
        data.append(list(i))
    Data_dit["TableColumnHeadings"]=column_headings
    Data_dit["TableRowData"]=data

    cursor_world.execute(f"select * from {tablename};")
    res=cursor_world.fetchall()
    Data_dit["RowCount"]=cursor_world.rowcount
    return Data_dit    

def get_data_fromQuery_sandbox(user_Query):
    Data_dict = {"TableColumnHeadings": [], "TableRowData": [], "RowCount": 0}
    while cursor_sandbox.fetchone() is not None:
        pass
    cursor_sandbox.execute(user_Query)
    column_headings = [col[0] for col in cursor_sandbox.description]
    Data_dict["TableColumnHeadings"] = column_headings
    data = cursor_sandbox.fetchall()
    row_data = [list(row) for row in data]
    print(row_data)
    print(column_headings)
    Data_dict["TableRowData"] = row_data
    Data_dict["RowCount"] = len(row_data)
    
    return Data_dict

def CheckOnlySyntaxError_sandbox(userquery):
    CheckTypeAndError_Sandbox={'Check':True,'ErrorMsg':'None','Type':'None','SuccessMsg':'None','AffectedRowCount':0}
    
    forbidden_words = [
        'use','drop database','databases','database',
        'grant', 'revoke', 'flush', 'shutdown', 'create user'
    ]
    found_forbidden_words = [word for word in forbidden_words if re.search(r'{}'.format(word), userquery, re.IGNORECASE)]

    if found_forbidden_words:
        msg=f"SQL-Injection Detected in query. Commands not allowed: {', '.join(found_forbidden_words)}"
        msg2="__**YOU CANNOT INTERACT AT DATABASE LEVEL**__"
        CheckTypeAndError_Sandbox['ErrorMsg'] = msg+msg2
        CheckTypeAndError_Sandbox['Check']=False
        return CheckTypeAndError_Sandbox
    try:
        querywords = ['create view','select','show tables','create table','insert into','update','alter table','delete','drop table','desc']
        success_message_for_each_query=[
                'Successfully created new view',
                'Successfully performed Select Operation',
                'Successfully Shown the tables',
                'Successfully created new table',
                'Successfully inserted data into table',
                'Successfully updated data in table',
                'Successfully altered table',
                'Successfully deleted data from table',
                'Successfully dropped table',
                'Describe table'
        ]
        
        cursor_sandbox.execute(userquery)
        result=cursor_sandbox.fetchone()
        CheckTypeAndError_Sandbox['AffectedRowCount']=cursor_sandbox.rowcount

        for queryword,succesmsg in zip(querywords, success_message_for_each_query):
            if re.search(r'{}'.format(queryword), userquery, re.IGNORECASE):
                CheckTypeAndError_Sandbox['Type'] = queryword.upper()
                CheckTypeAndError_Sandbox['SuccessMsg']=succesmsg
                break
        
    except m.Error as e:
        print("User query error:", e)
        CheckTypeAndError_Sandbox['ErrorMsg'] = e
        CheckTypeAndError_Sandbox['Check']=False

    return CheckTypeAndError_Sandbox

def On_Logout_RemoveAllTablesFromSandbox():
    cursor_sandbox.execute(f"SELECT table_name, table_type FROM INFORMATION_SCHEMA.TABLES WHERE table_schema = '{sandbox_database}'")
    tables = cursor_sandbox.fetchall()
    for table in tables:
        table_name = table[0]
        table_type = table[1]
        if table_type == 'BASE TABLE' or table_type == 'VIEW':
            if table_type=='BASE TABLE':
                table_type='TABLE'
            drop_table_query = f"DROP {table_type} {table_name}"
            cursor_sandbox.execute(drop_table_query)
    connection_sandbox.commit()
    