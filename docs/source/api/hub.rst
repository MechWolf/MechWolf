Hub API
=======

.. warning::
    This API is not exposed directly to users. It is included for reference purposes. Here be dragons.

.. http:post:: /submit_protocol

        Accepts a protocol posted as JSON. Returns signed unique ID of the protocol execution.

        :form protocol: The protocol to be executed by the hub. Must be signed by the security key, specifically by a :class:`~itsdangerous.URLSafeTimedSerializer`.

        :resheader Content-Type: text/html.

        **Example response (protocol accepted)**:

        .. code-block:: text

            d65b1ac6-473b-11e8-b15b-acbc32c766d9.Db_fFw.4ieNlMKkwOr6q6cWtXWqShJeVOo

        **Example response (protocol rejected)**:

        .. code-block:: text

            protocol rejected: invalid signature.Db_jfQ.zkw2KF_NZeGdbf3oxXhKsk_Js5M

.. http:get:: /protocol

    Returns protocols, if available.

    :arg device_id: The device id of the device requesting the protocol.

    .. note::
        A device may not get a protocol a second time.

    :resheader Content-Type: text/html or application/json.

    **Example response (no protocol submitted)**:

    .. code-block:: text

        no protocol.Db_ljg.9aboQrlISgzucDxTzmfR2HDfqGM

    **Example response (protocol submitted)**:

    .. code-block:: json

        {
            "protocol": ".eJxTqo7JUwCCGKWyxJyy1BglK4VoiAgIVCOYEEUFiUWJucUgVWhSEOni1JKSzLx0kLwRqnytDrpRJZm5YOsM9AwQUsjKKLDckHjLTaluuTGxlhsOpM8NUXwOYcbG5NUqAQDFQ3aC.Db_fFw.TmjtNCwz4iFeT3c-BtwdErpB6nM",
            "protocol_id": "d65b1ac6-473b-11e8-b15b-acbc32c766d9"
        }

.. http:get:: /start_time

    Returns start time, if available. If no start time is determined but all of the devices have received the protocol, the start time will be set as five seconds in the future.

    :arg device_id: The device id of the device requesting the protocol.

    .. note::
        A device may not get a start time a second time.

    :resheader Content-Type: text/html.

    **Example response (no start time)**:

    .. code-block:: text

        no start time.Db_oBg.9fd95Z16qEtYfSxfbRfHQH4OF4A

    **Example response (protocol aborted)**:

    .. code-block:: text

        abort.Db_oQQ.LPxBlTzHnAWwUycIqJsGk1KiSAE

    **Example response (start time determined)**:

    .. code-block:: text

        1524520767.31533.Db_oug.DYaz3ZxOELhgYE2fM0gSil-7JHA
