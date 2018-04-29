Resolver API
============

.. warning::
    This API is not exposed directly to users. It is included for reference purposes. Here be dragons.

.. http:post:: mechwolf.io/v1/register

        Accepts registrations of a ``hub_id`` and its associated address.

        :form hub_id: The unique identifier of the hub as chosen by the user.
        :form hub_address: The signed address of the hub at which components will be able to contact it.
        :form hub_address_signature: An RSA signature of ``hub_address``.
        :form hub_public_key: The RSA public key to verify ``hub_address_signature`` in PEM format encoded in hexadecimal.

        :resheader Content-Type: text/html.

        **Example response (registration accepted)**:

        .. code-block:: text

            success

        **Example response (registration rejected due to invalid signature)**:

        .. code-block:: text

            failure: signature provided does not match address

        **Example response (registration rejected due to missing field)**:

        .. code-block:: text

            failure: must provide 'FIELD_NAME' field

        **Example response (registration rejected due to signature mismatch)**:

        .. code-block:: text

            failure: signature on record does not match one provided


.. http:get:: mechwolf.io/v1/get_hub

    Returns hub address.

    :arg hub_id: The ``hub_id`` whose address is being requested.

    :resheader Content-Type: application/json if success else text/html.

    **Example response (success)**:

    .. code-block:: json

        {
            "hub_address": "18.189.45.48.qht-gc9v1gpswY3YBICZe1MfQ9Y",
            "hub_id": "test",
            "hub_public_key": "2d2d2d2d2d424547494e20525341205055424c4943204b45592d2d2d2d2d0a4d49494243674b434151454171464c68645953447976592b525556527a6d48504233532b4a7355766936694677523368425367324b76476458335438374776470a6438457776503261315651464d42626c554f4b2f53544e31554d696e7a38504e3467514c7a6d72433571386973467a75633066447173466e6a66627a626a50770a43576559714d495552656838756b356a45764446764a43344e54664a70596b6c3642437a454b75727177546a506536444d57723777584e77327078715a4767390a6c346f5545464c3148786946566f6f35684e4e386a5676717258344359464b446358413673316f7a4b44576a3536734d716a536346486348374d3637584264300a643777534e4b78344b535436384145646e74666a5065566d4676476c6c4f76764b7431794979596a6379725373305173754a526d52776b564d704b452f6547520a45496854543745594f6d6f7170485a30303546485454526f6d636a653232567573514944415141420a2d2d2d2d2d454e4420525341205055424c4943204b45592d2d2d2d2d0a"
        }

    **Example response (no record found)**:

    .. code-block:: text

        failure: unable to locate

    **Example response (search failed due to missing field)**:

    .. code-block:: text

        failure: must provide 'hub_id' field
