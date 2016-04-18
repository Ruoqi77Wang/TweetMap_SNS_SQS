from flask import Flask,jsonify,render_template,request
import sys
import json
from elasticsearch import Elasticsearch
#from flask_esclient import ESClient
import os
import requests
#from flask.ext.bootstrap import Bootstrap
from flask.ext.socketio import SocketIO, emit
import logging

app = Flask(__name__)
application = app
#app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
#bootstrap = Bootstrap(app)
#esclient = ESClient(app)
esc = Elasticsearch()


#r = requests.get("http://0.0.0.0:5000/sns/_search/?size=5000")
#print r


res_sns=[];
@app.route('/')
def approot():
	return render_template('twitterMap.html')

#websocket
socketio = SocketIO(app)

@app.route('/sns', methods=['POST'])
#http://41bcdb5b.ngrok.io:5000/sns
def subscribe():
	
  headers = request.headers
	
  header_type = headers.get('x-amz-sns-message-type')
  try:
    logging.info("/sns: %s" % request)
    obj = json.loads(request.data)
    if header_type == "SubscriptionConfirmation":
      obj = json.loads(request.data)
      subscribe_url = obj[u'SubscribeURL']
      print subscribe_url
      #r = rget(subscribe_url)
      #print "subscription confirmed"

    elif header_type == 'Notification':
      msg = json.loads(obj['Message'])
      msg_sns = {}
      msg_sns['id_str']=msg['id_str']
      msg_sns['senti']=msg['sentiment']
      msg_i=msg['id_str']
      msg_s=""+msg['sentiment']
      #print "1",msg_sns['senti']
      #print "2",msg['sentiment']
      #logging.info("emit sentiment %s" % msg_sns['id'])
      #print "before dump"
      #data = json.dumps(msg_sns)
      #print "123"
      #mes_con(data)
      socketio.emit('msg', {'data': msg['sentiment']}, namespace='/socket')
      #print "456"

      #logging.info("/sns: %s" % res_sns)

    #data = json.loads(request.data)
    #if data['Type'] == 'SubscriptionConfirmation':
    #  sns.confirm_subscription(topicarn, data['Token'])
    #elif data['Type'] == 'Notification':
    #  msg = json.loads(data['Message'])
    #  msg_sns = {}
    #  msg_sns['id_str']=msg['id_str']
    #  msg_sns['senti']=msg['sentiment']
    #  res_sns.append()
    return ""
  except BaseException as e:
        logging.warning("Exception in /sns: %s" % e)
        return ("Exception in /sns: %s" % e)

    

@app.route('/tweets', methods=['GET', 'POST'])
def hello_world():
  res=[];
  keyword=request.form['keyword']
  print keyword
  response = esc.search(index="tweet", body={"from":0, "size":1000, "query": {"match": {"content": keyword}}})
  for hit in response["hits"]["hits"]:
    lati=hit["_source"]["latitude"]
    longi=hit["_source"]["longitude"]
    pos={}
    pos["latitude"]=lati
    pos["longitude"]=longi
  		#pos_json=json.dumps(pos)
    res.append(pos)
  return jsonify({'data':res})



@socketio.on('connect',namespace='/socket')
def on_connect():
    #logging.info("connect")
    #emit('my response', json)
    print "connect"

@socketio.on('message',namespace='/socket')
def mes_con(msg):
    emit('msg', {'data':'test'})
    print "after mes_con emit"

@socketio.on('disconnect', namespace='/socket')
def test_disconnect():
    print('Client disconnected')



if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0')
    socketio.run(app, host='0.0.0.0',port=5000)



