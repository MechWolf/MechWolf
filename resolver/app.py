from flask import Flask, render_template, jsonify, request, abort
from itsdangerous import JSONWebSignatureSerializer, Serializer
import json
import boto3
import rsa
import binascii

# load the key
# NOTE: There must be a json file called aws_key that contains the key. This is deliberately left out of the repo
aws_key = json.load(open("aws_key.json"))
aws_access_key_id, aws_secret_access_key = aws_key["aws_access_key_id"], aws_key["aws_secret_access_key"]

# initialize the dynamodb session
session = boto3.session.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
dynamodb = session.resource('dynamodb')
table = dynamodb.Table('mechwolf_resolver')

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    '''renders the homepage'''
    return render_template("index.html")

@app.route("/v1/register", methods=["POST"])
def register():
    '''accepts hub registrations'''
    if not request.form.get("hub_id"):
        return "failure: must provide 'hub_id' field"
    elif not request.form.get("hub_address"):
        return "failure: must provide 'hub_address' field"
    elif not request.form.get("hub_public_key"):
        return "failure: must provide 'hub_public_key' field"
    elif not request.form.get("hub_address_signature"):
        return "failure: must provide 'hub_address_signature' field"

    signature = binascii.unhexlify(request.form.get("hub_address_signature"))

    # verify given signature is valid for address
    try:
        hub_public_key = rsa.PublicKey.load_pkcs1(binascii.unhexlify(request.form["hub_public_key"]))
        rsa.verify(request.form.get("hub_address").encode(),
                   signature,
                   hub_public_key)
    except:
        return "failure: signature provided does not match address"

    # verify that the public key on record matches the one we just verified
    try:
        hub_data = table.get_item(Key={'hub_id': request.form["hub_id"]})['Item']
        assert hub_public_key == rsa.PublicKey.load_pkcs1(binascii.unhexlify(hub_data["hub_public_key"]))
        table.update_item(
            Key={'hub_id': request.form["hub_id"]},
            UpdateExpression='SET hub_address = :val1',
            ExpressionAttributeValues={':val1': request.form["hub_address"]})

    except KeyError:
        # create new entry if KeyError, indicating that there is no item with the hub_id
        table.update_item(
            Key={'hub_id': request.form["hub_id"]},
            UpdateExpression='SET hub_address = :val1, hub_public_key = :val2',
            ExpressionAttributeValues={':val1': request.form["hub_address"],
                                       ':val2': request.form["hub_public_key"]})
    except AssertionError:
        return "failure: signature on record does not match one provided"

    except:
        return "failure: unknown reason"

    return "success"

@app.route("/v1/get_hub")
def get_hub():
    '''returns hub data as a json'''
    if not request.args.get("hub_id"):
        return "failure: must provide 'hub_id' field"
    try:
        response = table.get_item(Key={'hub_id': request.args["hub_id"]})
        item = response['Item']
        return jsonify(item)
    except Exception:
        return "failure: unable to locate"

if __name__ == '__main__':
    app.run(debug=True)
