"""AWS Version 4 signing Python module.
    
    Implements the signing algorithm as described here:
    http://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html
    
    However: 
      - specific to the AWS-IOT service; service is hardcoded: 'iotdata'
      - specific to micropython; uses micropython modules
    """

try:
    from uhashlib import sha256 as _sha256
except ImportError:
    print("Warning: not using uhashlib")
    from hashlib import sha256 as _sha256

import hmac_ltd as _hmac
import ubinascii as _ubinascii


def request_gen(endpt_prefix, shadow_id, access_key, secret_key, date_time_stamp, method='GET', region='us-east-1', body=''):
    service = 'iotdata'
    request_type = 'aws4_request'
    algorithm = 'AWS4-HMAC-SHA256'

    date_stamp = date_time_stamp[:8]
    
    return_dict = {}
    return_dict["host"] = endpt_prefix + '.' + 'iot' + '.' + region + '.' + 'amazonaws.com'
    return_dict["uri"] = '/things/' + shadow_id + '/shadow'

    # make the signing key from date, region, service and request_type
    # in micropython, the key has to be a byte array
    key = bytearray()
    key.extend(('AWS4' + secret_key).encode())
    kDate = _hmac.new(key, date_stamp, _sha256).digest()
    #print("request_gen: kDate: {}".format(kDate))
    # kDate, kRegion, kService & kSigning are binary byte arrays
    kRegion = _hmac.new(kDate, region, _sha256).digest()
    #print("request_gen: kRegion: {}".format(kRegion))
    kService = _hmac.new(kRegion, service, _sha256).digest()
    signing_key = _hmac.new(kService, request_type, _sha256).digest()

    # make the string to sign
    canonical_querystring = '' #no request params for shadows
    canonical_headers = 'host:' + return_dict["host"] + '\n' + 'x-amz-date:' + date_time_stamp + '\n'
    signed_headers = 'host;x-amz-date'
    payload_hash = _ubinascii.hexlify(_sha256(body).digest()).decode("utf-8")
    
    canonical_request = method + '\n' + return_dict["uri"] + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash
    #print('\n === canonical_request: \n' + canonical_request + '\n =========== end of canonical_request')
    
    credential_scope = date_stamp + '/' + region + '/' + service + '/' + request_type
    string_to_sign = algorithm + '\n' +  date_time_stamp + '\n' +  credential_scope + '\n' + _ubinascii.hexlify(_sha256(canonical_request).digest()).decode("utf-8")
    #print('\n === string_to_sign: \n' + string_to_sign + '\n =========== end of string_to_sign')
    #print('signing_key: ' + str(_ubinascii.hexlify(signing_key)))

    # generate the signature:
    signature = _ubinascii.hexlify(_hmac.new(signing_key, string_to_sign, _sha256).digest()).decode("utf-8")

    authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' +  'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature

    return_dict["headers"] = {'x-amz-date':date_time_stamp, 'Authorization':authorization_header}
    return return_dict
