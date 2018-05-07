Database Serialization CLI
==========================

.. command-output: mechwolf convert --help

Converting a .db file into JSON
-------------------------------

Converting a .db file into JSON is easy::

    $ sudo mechwolf convert --output=json a75c0c70-522a-11e8-b1ce-acbc32c766d9.db
    {
        "protocol": {
            "test_1": [
                {
                    "params": {
                        "active": true
                    },
                    "time": 1.0
                },
                {
                    "params": {
                        "active": false
                    },
                    "time": 3.0
                },
                {
                    "params": {
                        "active": true
                    },
                    "time": 4.0
                },
                {
                    "params": {
                        "active": false
                    },
                    "time": 4.5
                }
            ]
        },
        "log": [
            {
                "protocol_id": "a75c0c70-522a-11e8-b1ce-acbc32c766d9",
                "device_id": "test_1",
                "timestamp": 1525720393.5929658,
                "success": true,
                "procedure": {
                    "params": {
                        "active": true
                    },
                    "time": 1.0
                }
            },
            {
                "protocol_id": "a75c0c70-522a-11e8-b1ce-acbc32c766d9",
                "device_id": "test_1",
                "timestamp": 1525720395.591344,
                "success": true,
                "procedure": {
                    "params": {
                        "active": false
                    },
                    "time": 3.0
                }
            },
            {
                "protocol_id": "a75c0c70-522a-11e8-b1ce-acbc32c766d9",
                "device_id": "test_1",
                "timestamp": 1525720396.5913658,
                "success": true,
                "procedure": {
                    "params": {
                        "active": true
                    },
                    "time": 4.0
                }
            },
            {
                "protocol_id": "a75c0c70-522a-11e8-b1ce-acbc32c766d9",
                "device_id": "test_1",
                "timestamp": 1525720397.0920599,
                "success": true,
                "procedure": {
                    "params": {
                        "active": false
                    },
                    "time": 4.5
                }
            }
        ],
        "protocol_submit_time": 1525720378.485722
    }

Converting a .db file into YAML
-------------------------------
The output of the YAML option is *much* easier to read::

    $ sudo mechwolf convert --output=yaml a75c0c70-522a-11e8-b1ce-acbc32c766d9.db
    log:
    - device_id: test_1
      procedure:
        params:
          active: true
        time: 1.0
      protocol_id: a75c0c70-522a-11e8-b1ce-acbc32c766d9
      success: true
      timestamp: 1525720393.5929658
    - device_id: test_1
      procedure:
        params:
          active: false
        time: 3.0
      protocol_id: a75c0c70-522a-11e8-b1ce-acbc32c766d9
      success: true
      timestamp: 1525720395.591344
    - device_id: test_1
      procedure:
        params:
          active: true
        time: 4.0
      protocol_id: a75c0c70-522a-11e8-b1ce-acbc32c766d9
      success: true
      timestamp: 1525720396.5913658
    - device_id: test_1
      procedure:
        params:
          active: false
        time: 4.5
      protocol_id: a75c0c70-522a-11e8-b1ce-acbc32c766d9
      success: true
      timestamp: 1525720397.0920599
    protocol:
      test_1:
      - params:
          active: true
        time: 1.0
      - params:
          active: false
        time: 3.0
      - params:
          active: true
        time: 4.0
      - params:
          active: false
        time: 4.5
    protocol_submit_time: 1525720378.485722

Saving a converted db to a file
-------------------------------

To save a converted database into a file, use the ``>`` symbol followed by the
name of the file you want to create. For example, to save the data that we've
been looking at in the previous examples into a new file called ``data.yml``,
run this command::

    $ sudo mechwolf convert --output=yaml a75c0c70-522a-11e8-b1ce-acbc32c766d9.db > data.yml
