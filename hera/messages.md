# Message specification

In this document we specify a message format for the communication between the
furhat (Group 1) and the module management / hera reasoner (Group 2).

## Message format
The idea is, to send messages via a socket where the messages have the following
json format:

```json
{
    "id": <MESSAGE ID>,
    "type": <MESSAGE TYPE>,
    "query": <QUERY>
}
```

The `id` of a message is a unique integer type identifier. `type` can either be
`"request"` or `"reply"`. The structure of the `query` field depends on the type
of the message.

### Request messages
Structure of `<QUERY>` for messages of type `"request"`:
```json
{
    "field": <FIELD NAME>,
    "method": <METHOD NAME>,
    "arguments": <ARGUMENTS>
}
```

Requests are sent by the furhat to manipulate or request the state of the model.
Request messages trigger methods of the model to be executed. See
[Model methods](#model-methods) for a list of all possible parameters.

### Reply messages
Structure of `<QUERY>` for messages of type `"reply"`:
```json
{
    "reply_to": <ID>,
    "result": <RESULT>
}
```

Reply messages are generated for every request message. If the request triggered
a `GET` method, the `"result"` field of the reply contains the return value of
this method. Otherwise, the `"result"` field contains a boolean value which
informs about the success of a request.

## Model methods<a name="model-methods"></a>
The request messages trigger the respective methods of a model. A overwiew over
all possible methods is given in the table below.

|  Field      | Method | Argument type | Argument example             |
|-------------|--------|---------------|------------------------------|
| module      | RESET  | None          | `None`                       |
| description | SET    | string        | `"description"`              |
|             | GET    | None          | `None`                       |
| action      | ADD    | list          | `["A1", "A2", ...]`          |
|             | REMOVE | list          | `["A1", "A2", ...]`          |
|             | RENAME | dict          | `{"old": "A1", "new": "A3"}` |
|             | GET    | None          | `None`                       |
| background  | ADD    | list          | `["B1", "B2", ...]`          |
|             | REMOVE | list          | `["B1", "B2", ...]`          |
|             | RENAME | dict          | `{"old": "B1", "new": "B3"}` |
|             | GET    | None          | `None`                       |
| consequence | ADD    | list          | `["C1", "C2", ...]`          |
|             | REMOVE | list          | `["C1", "C2", ...]`          |
|             | RENAME | dict          | `{"old": "C1", "new": "C3"}` |
|             | GET    | None          | `None`                       |
| mechanism   | ADD    | dict          | `{"consequence": "C1", "variables": ["A1", "B1", ...]}` |
|             | REMOVE | dict          | `{"consequence": "C1", "variables": ["A1", "B1", ...]}` |
|             | GET    | None          | `None`                       |
| utility     | SET    | dict          | `{"consequence": "C1", "value": 42, "affirmation": True}` |
|             | REMOVE | dict          | `{"consequence": "C1", "affirmation": True}` |
|             | GET    | None          | `None`                       |
| intention   | ADD    | dict          | `{"action": "A1", "consequences": ["C1", "C2", ...]}` |
|             | REMOVE | dict          | `{"action": "A1", "consequences": ["C1", "C2", ...]}` |
|             | GET    | None          | `None`                       |

