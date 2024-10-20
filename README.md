# bwinterface

A Python wrapper around the "bw" (Bitwarden) CLI tool

The "bw" command line utility is used for accessing Bitwarden vaults or Vaultwarden vaults. At time of writing, there is no stable official module for accessing such vaults using Python. Therefore, this module provides a low-level Python wrapper around the "bw" CLI utility. A bunch of higher-level methods and facilities are provided for increased convenience, too.

---

## Features

- Provide a low-level wrapper around the "bw" CLI utility.
- Parse the "bw" tool output into Python data structures.
- Provide certain results in more convenient data structures.
- Caches certain results for increased performance in practical applications.
- Provide convenience methods to access the "bw" functionality in a simple manner.
- No other external libraries are needed, i.e. no dependencies except the "bw" utility.

---

## Installation

Install using PyPi:

```shell
pip3 install bwinterface
```

---

## Quickstart

### Accessing the bw CLI using bwinterface

The following code snippets provide examples on how `bwinterface` is used:

```python
import bwinterface

# Instantiate a wrapper object while providing the path to the "bw" CLI
bw = bwinterface.BWInterface(bw_cli='/opt/bw')

# Execute any bw command using "execute"
result = bw.execute('--help')
print(result)

# Login using API key
if not bw.check_login():
    print(bw.set_config_server('https://vaultwarden.mydomain.local'))
    result = bw.login_apikey(clientid='user.aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee', clientsecret='ffffffffffffffffffffffffffffff')
    print(result)

# Unlock the local vault
result = bw.unlock('MyMasterPassword')
print(result)

# There are useful properties
print(bw.organizations_asdictbyid)
print(bw.organizations_asdictbyname)

# There are get methods with filtering capabilities. Examples:
print(bw.get_collections('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee').data)
print(bw.get_collections('MyCollection').data)
print(bw.get_collections_asdictbyid('MyCollection'))
print(bw.get_collections_asdictbyname('MyCollection'))
print(bw.get_collectionid('MyCollection'))
print(bw.get_item('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'))
print(bw.get_item('"MyItem"'))
print(bw.get_item('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee').data.get('notes'))
print(bw.get_item_notes('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'))
print(bw.get_items_asdictbyid(organization=''))  # default organization
print(bw.get_items_asdictbyname(organization='MyOrganization'))

# You may create, change and delete objects. Examples:
print(bw.create_item('MyNewItem', 'myuser', 'mypassword', notes='This is a note'))
print(bw.edit_item('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee', password='MyNewPassword'))
print(bw.delete_item('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee', permanent=True))

# And there are many other convenience methods. Examples:
print(bw.sync())
print(bw.get_status())
print(bw.generate_password(uppercase=True, lowercase=True, number=True, special=True, passphrase=None, length=20, words=None, min_number=None, min_special=None, separator=None, capitalize=None, include_number=None, avoid_ambiguous=True))
```

Please see the section below for full API documentation.

---

## Detailed API description

### Properties

#### organizations

*Returns a cached list of organizations as returned by "bw"*

#### organizations_asdictbyid

*Returns a dictionary of (cached) organizations with organization identifiers as keys*

Note: This just differently formats the data provided by the `organization` property.

#### organizations_asdictbyname

*Returns a dictionary of (cached) organizations with organization names as keys*

Note: This just differently formats the data provided by the `organization` property.

### Methods for interaction (in alphabetical order)

#### `__init__(bw_cli='/opt/bitwarden/bw', print_bwcommands=True, print_resultdata=False, print_indent=None, sparse_output=False, suppress_output=True, suppress_errors=False)`

*Initializes the instance*

Parameters:
* "bw_cli" (str, optional, default: "/opt/bitwarden/bw"): Path to the "bw" command line utility
    The bwinterface module depends on the "bw" CLI utility for its operation. Provide the full path to the tool that shall be used.
* "print_bwcommands" (boolean, optional, default: True): Echo "bw" commands
    If True, each "bw" command executed is printed to stdout to show what is going on. JSON data is shown without encoding.
* "print_resultdata" (boolean, optional, default: True): Echo "bw" commands
    If True, the JSON data returned by each "bw" is printed to stdout.
* "print_indent" (boolean, optional, default: None): Indentation for JSON pretty printing
    If provided, JSON data is printed prettily with the specified indentation (try 2).
* "sparse_output" (boolean, optional, default: False): Reduce amount of output
    If True, "--raw" output of "bw" ise provided only.
* "suppress_output" (boolean, optional, default: True): Don't show output of "bw" utility
    If True, the full output to stdout of the "bw" utility is printed.
* "suppress_errors" (boolean, optional, default: False): Don't show error output of "bw" utility
    If True, the full output to stderr of the "bw" utility is printed.

Examples:
* `bw = bwinterface.BWInterface(bw_cli='/opt/bw')`
* `bw = bwinterface.BWInterface(bw_cli='/opt/bw', suppressoutput=False)`

#### `check_login()`

*Checks whether we are logged in*

#### `create_collection(name, organization=None, external_id=None, otherfields=None)`

*Create a collection with the given data*

#### `create_item(name, username, password, organization=None, collection=None, folder=None, totp=None, uris=None, type=1, notes=None, favorite=False, fields=None, otherfields=None)`

*Create an item with the given data*

#### `delete_collection(collection, organization, permanent=False)`

*Delete collection with the provided identifier ('permanent' does not use trash)*

#### `delete_item(itemid, permanent=False)`

*Delete item with the provided identifier ('permanent' does not use trash)*

#### `dict2base64(datadict)`

*Encodes a dictionary into a base64-encoded JSON notation*

#### `edit_item(itemid, name=None, username=None, password=None, organization=None, collection=None, folder=None, totp=None, uris=None, type=None, notes=None, favorite=None, fields=None, otherfields=None, create_if_not_exists=False, use_cache=True)`

*Update an item with the given data*

#### `execute(command, env=None, datadict=None, nojson=False, sparse_output=None, pretty=None)`

*Execute a bw command and return result*

#### `generate(uppercase=None, lowercase=None, number=None, special=None, passphrase=None, length=None, words=None, min_number=None, min_special=None, separator=None, capitalize=None, include_number=None, avoid_ambiguous=None)`

*Generates a new password/passphrase*

#### `generate_password(uppercase=None, lowercase=None, number=None, special=None, passphrase=None, length=None, words=None, min_number=None, min_special=None, separator=None, capitalize=None, include_number=None, avoid_ambiguous=None)`

*Returns a new password/passphrase*

#### `get_collectionid(collection, organization=None, use_cache=True)`

*Converts a string identifying a collection into the collection's UUID*

#### `get_collections(organization=None)`

*Gets a list of collections, optionally filtered*

#### `get_collections_aslist(organization=None)`

*Gets a list of collections, optionally filtered; always returns a list (empty list on invalid filters)*

#### `get_collections_asdictbyid(organization=None, use_cache=True)`

*Dictionary of collections with identifiers as keys, optionally filtered*

#### `get_collections_asdictbyname(organization=None, use_cache=True)`

*Dictionary of collections with names as keys, optionally filtered*

#### `get_folderid(folder)`

*Converts a string identifying a folder into the folder's UUID*

#### `get_item(itemid)`

*Get item with the provided identifier*

Note: it is possible to enter a search term (use double quotes) instead of an item id

#### `get_item_notes(itemid)`

*Get notes of item with the provided identifier (result is provided in 'out')*

#### `get_items(organization=None, collection=None, folder=None)`

*Gets a list of items, optionally filtered*

#### `get_items_asdict(organization=None, collection=None, folder=None, byname=False)`

*Dictionary of items, uncached, optionally filtered*

#### `get_items_asdictbyid(organization=None, collection=None, folder=None, use_cache=True)`

*Dictionary of items with identifiers as keys, optionally filtered*

#### `get_items_asdictbyname(organization=None, collection=None, folder=None, use_cache=True)`

*Dictionary of items with names as keys, optionally filtered*

#### `get_items_aslist(organization=None, collection=None, folder=None)`

*Gets a list of items, optionally filtered; always returns a list (empty list on invalid filters)*

#### `get_organizationid(organization)`

*Converts a string identifying an organization into the organization's UUID*

#### `get_organizations()`

*Gets a list of organizations*

#### `get_status()`

*Gets status information*

#### `invalidate_collection_cache()`

*Clears the collection cache*

#### `invalidate_item_cache()`

*Clears the item cache*

#### `invalidate_organization_cache()`

*Clears the organization cache*

#### `is_uuid(s)`

*Checks whether the given string is a valid UUID*

#### `login_apikey(clientid, clientsecret)`

*Logs in using the provided API credentials*

#### `logout()`

*Logout from vault*

#### `run_process(command, env=None)`

*Execute a command and return result*

#### `set_config_server(server)`

*Configures the server to use*

#### `sync()`

*Gets updates from the remote vault*

#### `unlock(pwd)`

*Unlocks the vault with the provided password*

#### `update_collection_cache(data, organization)`

*Updates the collection cache with the new or updated collection in case organization matches*

#### `update_item_cache(data, organization)`

*Updates the item cache with the new or updated item in case organization matches*

---

## Reporting bugs

In case you encounter any bugs, please report the expected behavior and the actual behavior so that the issue can be reproduced and fixed.

---
## Developers

### Clone repository

Clone this repo to your local machine using `https://github.com/towalink/bwinterface.git`

Install the module temporarily to make it available in your Python installation:
```shell
pip3 install -e <path to root of "src" directory>
```

---

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](https://opensource.org/licenses/MIT)

- **[MIT license](https://opensource.org/licenses/MIT)**
- Copyright 2024 © <a href="https://github.com/towalink/bwinterface" target="_blank">Dirk Henrici</a>.
- This project is not associated with Bitwarden or Vaultwarden.
