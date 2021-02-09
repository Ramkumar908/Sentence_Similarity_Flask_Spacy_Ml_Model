from flask import Flask,request,jsonify
from flask_restful import Api,Resource
import bcrypt
app=Flask(__name__)
api=Api(app)
from pymongo  import MongoClient
client=MongoClient("mongodb://127.0.0.1:27017")
db=client.SimilarityCheck
user=db['Users']
import spacy


@app.route("/")
def helloTest():
    return "Lets Start a new Projects with Ml Model"

#Metod for verify user existance 
def verifyUser(username):
    existuser=user.find({"Username":username}).count()
    if existuser==1:
        #print("username return true")
        return True
    else:
        #print("username verify return false")
        return False   


#Method for verify user password                    
def verifypsw(username,Password):
    if not verifyUser(username):
        print("verify psw return false")
        return False
        
    hashed_pass=user.find({"Username":username})[0]['Password']
    if bcrypt.checkpw(Password.encode("utf8"),hashed_pass):
        print("verify psw return True")
        return True
    else:
        return False     
def tokenCount(username):
    tokens=user.find({"Username":username})[0]['Tokens']
    return tokens        
#Reister user first time
#@Param username password
class Register(Resource):
    def post(self):
        posted_json=request.get_json()
        username=posted_json['username']
        password=posted_json['password']
        Tokens=6
        hashed_pass=bcrypt.hashpw(password.encode("utf8"),bcrypt.gensalt())
        if verifyUser(username):
            retjson={
                'status':301,

                "Message":"Sorry invalid Username"
                  
                }

            return jsonify(retjson)   
        else:

            user.insert({
                "Username":username,"Password":hashed_pass,
                "Tokens":Tokens
                   })
            retjson={
                "status":200,
                "Msg":"You have sucessfully registered"
                }
            return jsonify(retjson)    



#Detect the similarity between two point 
#Param username ,password,text1,text2
class Detect(Resource):
    def post(self):
        posted_json=request.get_json()
        username=posted_json['username']
        password=posted_json['password']
        text1=posted_json['text1']
        text2=posted_json['text2']

        #check invalid user response 301
        if  not verifyUser(username):
            retjson={
                "status":301,
                "Message":"invalid Username  or user doesnot exist"
            }
            return jsonify(retjson)
        if not verifypsw(username,password):
            retjson={
                'status':302,
                'Message':"Password Innvaid"
            }    
            return jsonify(retjson)
        tokens=tokenCount(username)
        if tokens<1:

            retjson={
                'status':304,
                'Message':"Out of Tokens"
            }
            return jsonify(retjson)
        nlp = spacy.load("en_core_web_sm")
        #print("the nlp is printing here and also ")           
        #nlp = spacy.load("/path/to/en_core_web_sm") 

        #doc = nlp("This is a sentence.")
        #nlp =spacy.load("en_core_web_sm")
        text1=nlp(text1)
        text2=nlp(text2)
        ratio=text1.similarity(text2)
        retjson={
        'status':200,
        'Similarity Ratio':ratio,
        'Message':"you have successfully calculates similarity"
         }

        user.update({
        "Username":username
            },{
                "$set":{"Tokens":tokens-1}
            })
        return jsonify(retjson)

class Refil(Resource):
    def post(self):
        posted_json=request.get_json()
        username=posted_json['username'] 
        password=posted_json['password']
        refil_count=posted_json['refil_count']
        if verifyUser(username):
            retjson={
                'status':301,
                'Message':"the user not found"
            }
        admin_psw="abc123"
        if password==admin_psw:
            user.update({
                "Username":username
            },{
                "$set":{"Tokens":refil_count}
            })
            retjson={
                "status":200,
                "Message":"your jsut refil your account"
            }
            return jsonify(retjson)
        else:
            retjson={
                "status":304,
              
                "message":"You dont have admin paswword access"
            } 
            return jsonify(retjson)


            



        
api.add_resource(Register,'/register')
api.add_resource(Detect,'/detect')
api.add_resource(Refil,'/refil')
if __name__=='__main__':
    app.run(debug=True)    