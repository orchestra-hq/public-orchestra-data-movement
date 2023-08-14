# data-movement

This repository builds a simple API in Python using FastAPI that allows the movement of data between sources and sinks.

Unlike modern architectures, this application takes full advantage of building an API integration framework to allow users to treat sources and sinks as the same type of resource. Rather than classify a given API as a source or a sink (not both), it assumes that doing both is intrinsically possible.

This makes sense because it reflects the nature of third-party APIs.

For example, it's straightforward to use the Snowflake Python Connector to push data to snowflake (treating it like a "sink") using an insert statement. However, it's also straightforward to use the connector to pull data from snowflake.

The same is true of third party SaaS tools outside the data sphere which are relevant to data teams, such as Hubspot.

