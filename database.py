import pymysql
from os import environ

class DatabaseConnection():
    def createConnection(self):
        #dbEndpoint = environ['dbEndpoint']
        dbEndpoint = '13.48.86.228'
        dbPass = environ['mysqlpass']
        dbCon = pymysql.connect(dbEndpoint,'admin',dbPass,'mysql',3306)
        return dbCon
    
class CreateEnvironment():
    def __init__(self,databaseName):
        self.dbConnection = DatabaseConnection()
        self.dbCon = self.dbConnection.createConnection()
        self.dbCursor = self.dbCon.cursor()
        self.databaseName = databaseName
        self.createDatabase()
        self.createTables()

    def createDatabase(self):
        try:
            queryDb = f"CREATE DATABASE {self.databaseName}"
            self.dbCursor.execute(queryDb)
        except:
            return "Error while creating database"
        return "Database successfully created"

    def createTables(self):
        try:
            self.dbCursor.execute(f"USE {self.databaseName}")
            queryTherapists = "CREATE TABLE therapists (\
                ID int PRIMARY KEY AUTO_INCREMENT,\
                FirstName varchar(255),\
                LastName varchar(255),\
                Speciality varchar(255),\
                Shift varchar(255)\
            )"
            self.dbCursor.execute(queryTherapists)
            queryPatients = "CREATE TABLE patients (\
                ID int PRIMARY KEY AUTO_INCREMENT,\
                FirstName varchar(255),\
                LastName varchar(255),\
                Street varchar(255),\
                TherapistID int,\
                FOREIGN KEY (TherapistID) REFERENCES therapists (ID)\
            )"
            self.dbCursor.execute(queryPatients)
            queryVisits = "CREATE TABLE visits (\
                ID int PRIMARY KEY AUTO_INCREMENT,\
                Date DATE,\
                Reason varchar(255),\
                PatientID int,\
                TherapistID int,\
                FOREIGN KEY (PatientID) REFERENCES patients (ID),\
                FOREIGN KEY (TherapistID) REFERENCES therapists (ID)\
            )"
            self.dbCursor.execute(queryVisits)
        except:
            return "Error while creating table"
        self.dbCon.close()
        return "Table successfully created"

class GetInformationFromDB():
    def __init__(self,databaseName):
        self.dbConnection = DatabaseConnection()
        self.databaseName = databaseName
        self.dbCon = self.dbConnection.createConnection()
        self.dbCursor = self.dbCon.cursor()
        self.dbCursor.execute(f"USE {self.databaseName}")

    def getAllVisits(self):
        query = "SELECT vst.Date, vst.Reason, CONCAT(pt.FirstName,' ',pt.LastName), \
                CONCAT(tr.FirstName,' ',tr.LastName)\
                FROM visits as vst\
                JOIN patients as pt ON pt.ID = vst.PatientID\
                JOIN therapists as tr ON tr.ID = vst.TherapistID"
        self.dbCursor.execute(query)
        data = self.dbCursor.fetchall()
        self.dbCon.close()
        return data

    def requestProducers(self):
        query = "SELECT Name FROM persons"
        self.dbCursor.execute(query)
        data = self.dbCursor.fetchall()
        self.dbCon.close()
        return data

    def requestProducer(self,producer):
        query = f"SELECT ID FROM persons WHERE Name = '{producer}' LIMIT 1"
        self.dbCursor.execute(query)
        data = self.dbCursor.fetchone()
        self.dbCon.close()
        return data

class AddNewInformationToDB():
    def __init__(self,databaseName):
        self.dbConnection = DatabaseConnection()
        self.dbCon = self.dbConnection.createConnection()
        self.dbCursor = self.dbCon.cursor()
        self.databaseName = databaseName
        self.dbCursor.execute(f"USE {self.databaseName}")

    def addPerson(self,name,country):
        query = f"INSERT INTO persons(Name,Country) VALUES('{name}','{country}')"
        try:
            self.dbCursor.execute(query)
            self.dbCon.commit()
        except:
            self.dbCon.rollback()
        self.dbCon.close()

    def addSouvenir(self,name,price,year,producer):
        getInfo = GetInformationFromDB(self.databaseName)
        idOfProducer = getInfo.requestProducer(producer)
        query = f"INSERT INTO artifacts(Name,Price,YearOfMade,OwnerID) \
                VALUES('{name}',{price},{year},{idOfProducer[0]})"
        try:
            self.dbCursor.execute(query)
            self.dbCon.commit()
        except:
            self.dbCon.rollback()
        self.dbCon.close()

class DeleteInfo():
    def __init__(self,databaseName):
        self.dbConnection = DatabaseConnection()
        self.dbCon = self.dbConnection.createConnection()
        self.dbCursor = self.dbCon.cursor()
        self.databaseName = databaseName
        self.dbCursor.execute(f"USE {self.databaseName}")

    def removeProducer(self,producer):
        queryArtifacts = f"DELETE artifacts\
                        FROM artifacts \
                        JOIN persons ON persons.ID = artifacts.OwnerID\
                        WHERE persons.Name = '{ producer }'"
        self.dbCursor.execute(queryArtifacts)
        self.dbCon.commit()
        self.dbCon.close()
        return self.dbCursor.fetchone()