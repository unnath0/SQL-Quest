from django.shortcuts import render
from App.utils import datafunctions as obje
# Create your views here.
def index(request):
    return render(request,'index.html')
def homepage(request):
    return render(request,'home.html')
def helppage(request):
    return render(request,'help.html')
def aboutpage(request):
    return render(request,'about_us.html') 

def sandboxpage(request):
    if request.method == 'POST':
        user_query=request.POST.get('userSQL_query')
        TextToDisplayInBox=user_query
        RowsCanBeShown=True
        Display_SuccesMessage=''
        CheckTypeAndError_Sandbox=obje.CheckOnlySyntaxError_sandbox(user_query)
        if(CheckTypeAndError_Sandbox['Check']):
            if(CheckTypeAndError_Sandbox['Type'] not in ('SELECT','SHOW TABLES','DESC')):
                Display_SuccesMessage=CheckTypeAndError_Sandbox['SuccessMsg']
                Display_Table_Data=[[]]
                Display_Table_headings=[]
                Display_Table_RowCount="Number of ROWS Affected: "+str(CheckTypeAndError_Sandbox['AffectedRowCount'])
            else:
                Display_SuccesMessage=''
                QueryTableDictionary=obje.get_data_fromQuery_sandbox(user_query)
                Display_Table_headings=QueryTableDictionary["TableColumnHeadings"]
                Display_Table_Data=QueryTableDictionary["TableRowData"]
                Display_Table_RowCount="Number of ROWS Retreived: "+str(QueryTableDictionary["RowCount"])
                
        else:
            Display_Table_headings=["Syntax error"]
            Display_Table_Data=[[CheckTypeAndError_Sandbox['ErrorMsg']]]
            RowsCanBeShown=False
            Display_Table_RowCount=''
  
        return render(request,'sandbox.html',{'Display_SuccesMessage':Display_SuccesMessage,'RowsCanBeShown':RowsCanBeShown,'Display_Table_RowCount':Display_Table_RowCount,'SubmitBoxContent':TextToDisplayInBox,'Display_table_data':Display_Table_Data,'Display_Table_head':Display_Table_headings})

    return render(request,'sandbox.html')
    
def solvepage(request):
    userid = request.session.get('Current_UserID', 0)

    UserTotalModuleProgressInfo=obje.GetUserTotalModuleProgressDetails(userid)
    UserEachModuleProgressInfo=obje.GetUserEachModuleProgressDetails(userid)
    return render(request,'solve.html', {'OverallProgressData':UserTotalModuleProgressInfo,'EachModuleProgressData':UserEachModuleProgressInfo})

def questionspage(request):
    userid=request.session['Current_UserID']
    AllQuestionsDetails=obje.GetAllQuestionsDetailsOfUser(userid)
    ALLModuleDetail=obje.GetAllModuleInto()
    selected_moduleID = request.GET.get('module_id')
    selected_questionID = request.GET.get('question_id')
    if(selected_questionID is None):
        selected_questionID =obje.GetQuestionID_fromModuleID(selected_moduleID)
    userid=request.session['Current_UserID']
    Selected_QuestionDetails=obje.GetSelectedQuestionDetails(selected_questionID,userid,selected_moduleID)
    request.session['Current_SelectedQuestion']=Selected_QuestionDetails['QuestionID']
    TextToDisplayInBox=obje.GetUserAnswer(userid,selected_questionID)
    print(TextToDisplayInBox)
    #need to get the first 5 values of the table based on questionid
    #and then pass them into paramters
    TableAtTop_Data=obje.GetTableToShowDetails_5rows(selected_questionID)
    TableAtTop_ColumnHeadings=TableAtTop_Data["TableColumnHeadings"]
    TableAtTop_RowsData=TableAtTop_Data["TableRowData"]
    TableAtTop_RowCount=TableAtTop_Data["RowCount"]
    TableAtTop_Name=TableAtTop_Data["TableName"]
    return render(request,'questions.html',{'TableAtTop_Name':TableAtTop_Name,'TableAtTop_RowCount':TableAtTop_RowCount,'TableAtTop_RowsData':TableAtTop_RowsData,'TableAtTop_ColumnHeadings':TableAtTop_ColumnHeadings,'SubmitBoxContent':TextToDisplayInBox,'ModuleInfo':ALLModuleDetail,'question_id':selected_questionID,'SideBarData': AllQuestionsDetails, 'questionInfo': Selected_QuestionDetails})

def userquerysubmit_virtual(request):
    userid=request.session['Current_UserID']
    AllQuestionsDetails=obje.GetAllQuestionsDetailsOfUser(userid)
    ALLModuleDetail=obje.GetAllModuleInto()
    selected_moduleID = request.GET.get('module_id')

    selected_questionID = request.session.get('Current_SelectedQuestion')

    TableAtTop_Data=obje.GetTableToShowDetails_5rows(selected_questionID)
    TableAtTop_ColumnHeadings=TableAtTop_Data["TableColumnHeadings"]
    TableAtTop_RowsData=TableAtTop_Data["TableRowData"]
    TableAtTop_RowCount=TableAtTop_Data["RowCount"]
    TableAtTop_Name=TableAtTop_Data["TableName"]
     
    userid=request.session['Current_UserID']
    Selected_QuestionDetails=obje.GetSelectedQuestionDetails(selected_questionID,userid,selected_moduleID)
    TextToDisplayInBox=obje.GetUserAnswer(userid,selected_questionID)

    if request.method == 'POST':
        UserQuery=request.POST.get('userSQL_query')
        TextToDisplayInBox=""
        Answer_Bool=False
        Check_For_Syntax_error=obje.CheckSyntaxErrorInUserQuery(UserQuery,userid,selected_questionID)
        if(Check_For_Syntax_error['Check']):
            Answer_Bool=obje.CheckCorrectnessOfUserQuery(UserQuery,userid,selected_questionID)
            QueryTableDictionary=obje.get_data_fromQuery(UserQuery)
            Display_Table_headings=QueryTableDictionary["TableColumnHeadings"]
            Display_Table_Data=QueryTableDictionary["TableRowData"]
            Display_Table_RowCount=QueryTableDictionary["RowCount"]
        else:
            Display_Table_headings=["Syntax error"]
            Display_Table_Data=[[Check_For_Syntax_error['ErrorMsg']]]
            Display_Table_RowCount=0
        print(Answer_Bool)
        TextToDisplayInBox=obje.GetUserAnswer(userid,selected_questionID)
        userid=request.session['Current_UserID']
        AllQuestionsDetails=obje.GetAllQuestionsDetailsOfUser(userid)
        
        return render(request,'questions.html',{'TableAtTop_Name':TableAtTop_Name,'TableAtTop_RowCount':TableAtTop_RowCount,'TableAtTop_RowsData':TableAtTop_RowsData,'TableAtTop_ColumnHeadings':TableAtTop_ColumnHeadings,'Display_Table_RowCount':Display_Table_RowCount,'SubmitBoxContent':TextToDisplayInBox,'ModuleInfo':ALLModuleDetail,'Userquery_Field':UserQuery,'isQueryCorrect':Answer_Bool,'Display_table_data':Display_Table_Data,'Display_Table_head':Display_Table_headings,'question_id':selected_questionID,'SideBarData': AllQuestionsDetails, 'questionInfo': Selected_QuestionDetails})
             
    return render(request,'questions.html',{'TableAtTop_Name':TableAtTop_Name,'TableAtTop_RowCount':TableAtTop_RowCount,'TableAtTop_RowsData':TableAtTop_RowsData,'TableAtTop_ColumnHeadings':TableAtTop_ColumnHeadings,'Display_Table_RowCount':Display_Table_RowCount,'SubmitBoxContent':TextToDisplayInBox,'ModuleInfo':ALLModuleDetail,'question_id':selected_questionID,'SideBarData': AllQuestionsDetails, 'questionInfo': Selected_QuestionDetails})

def loginpage(request):
    UserAuthenticationConfirmation=''
    if request.method == 'POST':
        username = request.POST.get('Username_Input_Box')
        password = request.POST.get('Password_Input_Box')
        userid=obje.OnSignIN_CheckForValidUserPassword(username,password)
        if(userid):
            UserAuthenticationConfirmation=1
            request.session['Current_UserName']=username
            request.session['Current_UserID'] = userid
            obje.On_LoginLogout_AddDataToLogsTable(userid,'Login')
            return render(request,'log_in.html',{'UserAuthenticationConfirmation':UserAuthenticationConfirmation})
        else:
            UserAuthenticationConfirmation=0
            return render(request,'log_in.html',{'UserAuthenticationConfirmation':UserAuthenticationConfirmation})
        
    return render(request,'log_in.html',{'UserAuthenticationConfirmation':UserAuthenticationConfirmation})
    
def logoutpage_virtual(request):
    userid=request.session['Current_UserID']
    obje.On_LoginLogout_AddDataToLogsTable(userid,'Logout')
    obje.On_Logout_RemoveAllTablesFromSandbox()
    request.session['Current_UserID'] = 0
    request.session['Current_UserName']=""
    return render(request,'home.html')

def signuppage(request):
    UserDataAddedConfirmation=''
    if request.method == 'POST':
        username = request.POST.get('UserName_InputBox')
        email = request.POST.get('UserEmail_InputBox')
        password = request.POST.get('UserPassword_InputBox')
        if(obje.OnSignUP_AddDataToUsersTable(username,email,password)):
            print("user data successfully added")
            UserDataAddedConfirmation=1
            return render(request,'sing_up.html',{'UserDataAddedConfirmation':UserDataAddedConfirmation})
        else:
            print("User already exists")
            UserDataAddedConfirmation=0
            return render(request,'sing_up.html',{'UserDataAddedConfirmation':UserDataAddedConfirmation})
            
    return render(request,'sing_up.html',{'UserDataAddedConfirmation':UserDataAddedConfirmation})
