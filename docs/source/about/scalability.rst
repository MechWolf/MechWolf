Scalability
===========

The MechWolf resolver is built to be as scalable as possible. The website uses
AWS Lambda for its computing needs. This allows the amount of compute resources
to be dynamically allocated based on demand. So, for example, if no one is
sending requests to the resolver then that means that we are not paying for idle
resources. Conversely, spikes in demand are handled seamlessly.

Similarly, our database is built on AWS DynamoDB, which allows us to scale
easily. Due to the minimal amount of data that we store, we can be confident
that the expenses of data storage and backup will remain correspondingly
low.

Additionally, the hub and client code is designed to keep the number of requests
to the resolver as low as possible, relying on cached versions whenever it can.
The reasons for this choice are twofold: first, it increases MechWolf's
performance on slow networks and, second, it reduces the amount of expense as
both AWS Lambda and DynamoDB resources are involved in answering requests.
