import base64
from collections import namedtuple
import copy
import json
import os
import shlex
import subprocess
import uuid

"""A Python wrapper around the "bw" (Bitwarden) CLI tool."""

# Bitwarden CLI documentation: https://bitwarden.com/help/cli/

__author__ = "Dirk Henrici"
__license__ = "MIT"
__email__ = "towalink.bwinterface@henrici.name"


class BWInterface():

    result_tuple = namedtuple('bwresult', ['rc', 'out', 'err', 'data'])
    session = None
    _organizations = None
    _collections_asdictbyid = None
    _collections_asdictbyname = None
    _collections_organization = None
    _items_asdictbyid = None
    _items_asdictbyname = None
    _items_organization = None
    
    def __init__(self, bw_cli='/opt/bitwarden/bw', show_bwcommands=True, sparse_output=False, suppressoutput=True, suppresserrors=False):
        """Initialize instance"""
        self.bw_cli = bw_cli
        self.show_bwcommands = show_bwcommands
        self.sparse_output = sparse_output
        self.suppressoutput = suppressoutput
        self.suppresserrors = suppresserrors

    def invalidate_organization_cache(self):
        """Clears the organization cache"""
        self._organizations = None

    def invalidate_collection_cache(self):
        """Clears the collection cache"""
        self._collections_asdictbyid = None
        self._collections_asdictbyname = None
        self._collections_organization = None

    def invalidate_item_cache(self):
        """Clears the item cache"""
        self._items_asdictbyid = None
        self._items_asdictbyname = None
        self._items_organization = None

    def update_collection_cache(self, data, organization):
        """Updates the collection cache with the new or updated collection in case organization matches"""
        if self._collections_organization == organization:
            assert data.get('object') == 'org-collection'
            if self._collections_asdictbyid is not None:
                self._collections_asdictbyid[data.get('id')] = data
            if self._collections_asdictbyname is not None:
                self._collections_asdictbyname[data.get('name')] = data

    def update_item_cache(self, data, organization):
        """Updates the item cache with the new or updated item in case organization matches"""
        if self._items_organization == organization:
            assert data.get('object') == 'item'
            if self._items_asdictbyid is not None:
                self._items_asdictbyid[data.get('id')] = data
            if self._items_asdictbyname is not None:
                self._items_asdictbyname[data.get('name')] = data

    def run_process(self, command, env=None):
        """Execute a command and return result"""
        if self.show_bwcommands:
            print(command)
        args = shlex.split(command)
        if env is not None:
            newenv = os.environ.copy()
            newenv.update(env)
        else:
            newenv=None
        cpe = subprocess.run(args, env=newenv, capture_output=True)
        out = cpe.stdout.decode('utf8')
        err = cpe.stderr.decode('utf8')
        if not self.suppresserrors and (len(err) > 0):
            print(err.strip())
        if not self.suppressoutput and (len(out) > 0):
            print(out.strip())
        return cpe.returncode, out, err

    def execute(self, command, env=None, datadict=None, nojson=False, sparse_output=None, pretty=None):
        """Execute a bw command and return result"""
        if self.session is not None:
            if env is None:
                env = dict()
            env['BW_SESSION'] = self.session
        if sparse_output is None:
            sparse_output = self.sparse_output
        if sparse_output and (' --raw' not in command):
            command += ' --raw'            
        if pretty:
            command += ' --pretty'            
        if datadict is not None:
            command += ' ' + self.dict2base64(datadict)
        rc, out, err = self.run_process(f'{self.bw_cli} {command}', env=env) 
        data = list()
        if (rc == 0) and (out.startswith('[') or out.startswith('{') and not nojson):
            data = json.loads(out)
        return self.result_tuple(rc, out, err, data)

    def set_config_server(self, server):
        """Configures the server to use"""
        result = self.execute('config server ' + server)
        return (result.rc == 0)

    def check_login(self):
        """Checks whether we are logged in"""
        result = self.execute('login --check')
        return (result.rc == 0)

    def login_apikey(self, clientid, clientsecret):
        """Logs in using the provided API credentials"""
        env = dict()
        env['BW_CLIENTID'] = clientid
        env['BW_CLIENTSECRET'] = clientsecret
        result = self.execute('login --apikey', env)
        # returncode 1 is used for anything - overwrite to become more specific
        if result.rc == 1:
            if result.err. startswith('You are already logged in'):
                result.rc = -1
        return result

    def logout(self):
        """Logout from vault"""
        return self.execute('logout')

    def unlock(self, pwd):
        """Unlocks the vault with the provided password"""
        env = dict()
        env['BW_PASSWORD'] = pwd
        result = self.execute('unlock --passwordenv BW_PASSWORD --raw', env)
        self.session = result.out if (result.rc == 0) else None
        return result

    def sync(self):
        """Gets updates from the remote vault"""
        return self.execute('sync')

    def generate(self, uppercase=None, lowercase=None, number=None, special=None, passphrase=None, length=None, words=None, min_number=None, min_special=None, separator=None, capitalize=None, include_number=None, avoid_ambiguous=None):
        """Generates a new password/passphrase"""
        command = 'generate'
        if uppercase == True:
            command += ' --uppercase'
        if lowercase == True:
            command += ' --lowercase'
        if number == True:
            command += ' --number'
        if special == True:
            command += ' --special'
        if (passphrase == True) or ((words is not None) and (passphrase is None)):
            command += ' --passphrase'
        if length is not None:
            command += f' --length {length}'
        if words is not None:
            command += f' --words {words}'
        if min_number is not None:
            command += f' --min_number {min_number}'
        if min_special is not None:
            command += f' --min_special {min_special}'
        if separator is not None:
            if separator == '':
                separator = 'empty'
            if separator == ' ':
                separator = 'space'
            command += f' --separator {separator}'
        if words is not None:
            command += f' --words {words}'
        if capitalize == True:
            command += ' --capitalize'
        if include_number == True:
            command += ' --include_number'
        if avoid_ambiguous == True:
            command += ' --ambiguous'
        return self.execute(command)

    def generate_password(self, uppercase=None, lowercase=None, number=None, special=None, passphrase=None, length=None, words=None, min_number=None, min_special=None, separator=None, capitalize=None, include_number=None, avoid_ambiguous=None):
        """Returns a new password/passphrase"""
        result = self.generate(uppercase=uppercase, lowercase=lowercase, number=number, special=special, passphrase=passphrase, length=length, words=words, min_number=min_number, min_special=min_special, separator=separator, capitalize=capitalize, include_number=include_number, avoid_ambiguous=avoid_ambiguous)
        if result.rc != 0:
            return None
        return result.out

    def get_status(self):
        """Gets status information"""
        return self.execute('status')

    def get_organizations(self):
        """Gets a list of organizations"""
        result = self.execute('list organizations')
        if result.rc == 0:
            self._organizations = result.data
        return result

    def get_collections(self, organization=None):
        """Gets a list of collections, optionally filtered"""
        filter = ''
        if organization is not None:
            filter += ' --organizationid ' + self.get_organizationid(organization)
        return self.execute('list collections' + filter)

    def get_collections_aslist(self, organization=None):
        """Gets a list of collections, optionally filtered; always returns a list (empty list on invalid filters)"""
        try:
            return self.get_collections(organization).data
        except ValueError:
            return []

    def get_collections_asdictbyid(self, organization=None, use_cache=True):
        """Dictionary of collections with identifiers as keys, optionally filtered"""
        if use_cache and (self._collections_asdictbyid is not None) and (self._collections_organization == organization):
            return self._collections_asdictbyid
        result = { item.get('id'): item for item in self.get_collections_aslist(organization) }
        # Populate collection cache
        if result is not None:
            if self._collections_organization != organization:
                self.invalidate_collection_cache()
            self._collections_asdictbyid = result
            self._collections_organization = organization
        return result

    def get_collections_asdictbyname(self, organization=None, use_cache=True):
        """Dictionary of collections with names as keys, optionally filtered"""
        if use_cache and (self._collections_asdictbyname is not None) and (self._collections_organization == organization):
            return self._collections_asdictbyname
        result = { item.get('name'): item for item in self.get_collections_aslist(organization) }
        # Populate item cache
        if result is not None:
            if self._collections_organization != organization:
                self.invalidate_collection_cache()
            self._collections_asdictbyname = result
            self._collections_organization = organization
        return result

    def get_items(self, organization=None, collection=None, folder=None):
        """Gets a list of items, optionally filtered"""
        filter = ''
        if organization is not None:
            filter += ' --organizationid ' + self.get_organizationid(organization)
        if collection is not None:
            filter += ' --collectionid ' + self.get_collectionid(collection)
        if folder is not None:
            filter += ' --folderid ' + self.get_folderid(folder)
        return self.execute('list items' + filter)

    def get_items_aslist(self, organization=None, collection=None, folder=None):
        """Gets a list of items, optionally filtered; always returns a list (empty list on invalid filters)"""
        try:
            return self.get_items(organization, collection, folder).data
        except ValueError:
            return []

    def get_items_asdict(self, organization=None, collection=None, folder=None, byname=False):
        """Dictionary of items, uncached, optionally filtered"""
        items = self.get_items_aslist(organization, collection, folder)
        items_byid = { item.get('id'): item for item in items }
        items_byname = { item.get('name'): item for item in items }
        # Populate item cache
        if (items is not None) and (collection is None) and (folder is None):
            if self._items_organization != organization:
                self.invalidate_item_cache()
            self._items_asdictbyid = items_byid
            self._items_asdictbyname = items_byname
            self._items_organization = organization
        # Return dictionary as chosen
        if byname:
            return items_byname
        else:
            return items_byid

    def get_items_asdictbyid(self, organization=None, collection=None, folder=None, use_cache=True):
        """Dictionary of items with identifiers as keys, optionally filtered"""
        if use_cache and (self._items_asdictbyid is not None) and (self._items_organization == organization) and (collection is None) and (folder is None):
            return self._items_asdictbyid
        return self.get_items_asdict(organization=organization, collection=collection, folder=folder, byname=False)

    def get_items_asdictbyname(self, organization=None, collection=None, folder=None, use_cache=True):
        """Dictionary of items with names as keys, optionally filtered"""
        if use_cache and (self._items_asdictbyname is not None) and (self._items_organization == organization) and (collection is None) and (folder is None):
            return self._items_asdictbyname
        return self.get_items_asdict(organization=organization, collection=collection, folder=folder, byname=True)

    def get_item(self, itemid):
        """Get item with the provided identifier"""
        # Note: it is possible to enter a search term (use double quotes) instead of an item id
        return self.execute(f'get item {itemid}')

    def get_item_notes(self, itemid):
        """Get notes of item with the provided identifier (result is provided in 'out')"""
        return self.execute(f'get notes {itemid}', nojson=True)

    def create_collection(self, name, organization=None, external_id=None, otherfields=None):
        """Create a collection with the given data"""
        # Collection template ("bw get template org-collection --pretty"):
        # {
        # "organizationId": "00000000-0000-0000-0000-000000000000",
        # "name": "Collection name",
        # "externalId": null,
        # "groups": [
             #{
             #"id": "00000000-0000-0000-0000-000000000000",
             #"readOnly": false,
             #"hidePasswords": false,
             #"manage": false
             #},
             #{
             #"id": "00000000-0000-0000-0000-000000000000",
             #"readOnly": false,
             #"hidePasswords": false,
             #"manage": false
             #}
        # ],
        # "users": [
             #{
             #"id": "00000000-0000-0000-0000-000000000000",
             #"readOnly": false,
             #"hidePasswords": false,
             #"manage": false
             #},
             #{
             #"id": "00000000-0000-0000-0000-000000000000",
             #"readOnly": false,
             #"hidePasswords": false,
             #"manage": false
             #}
        # ]
        # }
        data = otherfields.copy() if otherfields is not None else dict()
        if organization is not None:
            data['organizationId'] = self.get_organizationid(organization)
        data['name'] = name
        data['externalId'] = external_id
        if 'groups' not in data:
            data['groups'] = []
        if 'users' not in data:
            data['users'] = []
        result = self.execute(f'create org-collection --organizationid {data['organizationId']}', datadict=data)
        if result.rc == 0:
            self.update_collection_cache(result.data, organization=organization)
        return result

    def create_item(self, name, username, password, organization=None, collection=None, folder=None, totp=None, uris=None, type=1, notes=None, favorite=False, fields=None, otherfields=None):
        """Create an item with the given data"""
        # Item template:
        # {
        #   "passwordHistory": [],
        #   "revisionDate": null,
        #   "creationDate": null,
        #   "deletedDate": null,
        #   "organizationId": null,
        #   "collectionIds": null,
        #   "folderId": null,
        #   "type": 1,
        #   "name": "Item name",
        #   "notes": "Some notes about this item.",
        #   "favorite": false,
        #   "fields": [],
        #   "login": null,
        #   "secureNote": null,
        #   "card": null,
        #   "identity": null,
        #   "reprompt": 0
        # }
        # with login as
        # {
        # "fido2Credentials": [
             #{
             #"credentialId": "keyId",
             #"keyType": "keyType",
             #"keyAlgorithm": "keyAlgorithm",
             #"keyCurve": "keyCurve",
             #"keyValue": "keyValue",
             #"rpId": "rpId",
             #"userHandle": "userHandle",
             #"userName": "userName",
             #"counter": "counter",
             #"rpName": "rpName",
             #"userDisplayName": "userDisplayName",
             #"discoverable": "false",
             #"creationDate": null
             #}
        # ],
        # "uris": [],
        # "username": "jdoe",
        # "password": "myp@ssword123",
        # "totp": "JBSWY3DPEHPK3PXP"
        # }
        data = otherfields.copy() if otherfields is not None else dict()
        if organization is not None:
            data['organizationId'] = self.get_organizationid(organization)
        if collection is not None:
            data['collectionIds'] = [ self.get_collectionid(collection, organization=organization) ]
        if folder is not None:
            data['folderId'] = self.get_folderid(folder)
        if type is not None:
            data['type'] = type
        else:
            data['type'] = 1
        if name is not None:
            data['name'] = name
        if notes is not None:
            data['notes'] = notes
        if favorite is not None:
            data['favorite'] = favorite
        if fields is not None:
            data['fields'] = fields
        login_data = dict()
        if username is not None:
            login_data['username'] = username
        if password is not None:
            login_data['password'] = password
        if totp is not None:
            login_data['totp'] = password
        if uris is not None:
            login_data['uris'] = uris
        data['login'] = login_data
        result = self.execute('create item', datadict=data)
        if result.rc == 0:
            self.update_item_cache(result.data, organization=organization)
        return result

    def edit_item(self, itemid, name=None, username=None, password=None, organization=None, collection=None, folder=None, totp=None, uris=None, type=None, notes=None, favorite=None, fields=None, otherfields=None, create_if_not_exists=False, use_cache=True):
        """Update an item with the given data"""
        if use_cache:
            if self.is_uuid(itemid):
                data = self.get_items_asdictbyid(organization=organization, use_cache=True)
            else:
                data = self.get_items_asdictbyname(organization=organization, use_cache=True)
            data = copy.deepcopy(data.get(itemid))
            if (data is None) and not create_if_not_exists:
                return self.result_tuple(1, '', 'Not found.', None)
        else:
            result = self.get_item(itemid)
            if result.rc != 0:
                if create_if_not_exists and result.err == 'Not found.':
                    data = None
                else:
                    return result
            data = result.data
        if data is None:
            if name is None:
                name = itemid
            return self.create_item(name=name, username=username, password=password, organization=organization, collection=collection, folder=folder, totp=totp, uris=uris, type=type, notes=notes, favorite=favorite, fields=fields, otherfields=otherfields)
        itemid = data.get('id')
        if otherfields is not None:
            data.update(otherfields)
        if organization is not None:
            data['organizationId'] = self.get_organizationid(organization)
        if collection is not None:
            data['collectionIds'] = [ self.get_collectionid(collection) ]
        if folder is not None:
            data['folderId'] = self.get_folderid(folder)
        if type is not None:
            data['type'] = type
        if name is not None:
            data['name'] = name
        if notes is not None:
            data['notes'] = notes
        if favorite is not None:
            data['favorite'] = favorite
        if fields is not None:
            data['fields'] = fields
        if username is not None:
            data['login']['username'] = username
        if password is not None:
            data['login']['password'] = password
        if totp is not None:
            data['login']['totp'] = password
        if uris is not None:
            data['login']['uris'] = uris
        result = self.execute(f'edit item {itemid}', datadict=data)
        if result.rc == 0:
            self.update_item_cache(result.data, organization=organization)
        return result

    def delete_collection(self, collection, organization, permanent=False):
        """Delete collection with the provided identifier ('permanent' does not use trash)"""
        organizationid = self.get_organizationid(organization)
        collectionid = self.get_collectionid(collection, organization=organization)
        return self.execute(f'delete org-collection {collectionid} --organizationid {organizationid}' + (' --permanent' if permanent else ''))

    def delete_item(self, itemid, permanent=False):
        """Delete item with the provided identifier ('permanent' does not use trash)"""
        return self.execute(f'delete item {itemid}' + (' --permanent' if permanent else ''))

    def is_uuid(self, s):
        """Checks whether the given string is a valid UUID"""
        try:
            uuid.UUID(s)
            return True
        except ValueError:
            return False

    def dict2base64(self, datadict):
        """Encodes a dictionary into a base64-encoded JSON notation"""
        data = json.dumps(datadict)
        
        print(data)
        
        data = bytes(data, 'utf-8')
        data = base64.b64encode(data)
        return data.decode('utf-8')

    def get_organizationid(self, organization):
        """Converts a string identifying an organization into the organization's UUID"""
        if organization == '':
            return 'null'
        if organization in ['null', 'notnull']:
            return organization
        organizationid = organization
        if not self.is_uuid(organizationid):
            organizationid = self.organizations_asdictbyname.get(organization, dict()).get('id')
            if organizationid is None:
                raise ValueError(f'Unknown organization name [{organization}] given')
        assert self.is_uuid(organizationid)
        return organizationid

    def get_collectionid(self, collection, organization=None, use_cache=True):
        """Converts a string identifying a collection into the collection's UUID"""
        if collection == '':
            return 'null'
        if collection in ['null', 'notnull']:
            return collection
        collectionid = collection
        if not self.is_uuid(collectionid):
            collectionid = self.get_collections_asdictbyname(organization=organization, use_cache=use_cache).get(collection, dict()).get('id')
            if collectionid is None:
                raise ValueError(f'Unknown collection name [{collection}] given')
        assert self.is_uuid(collectionid)
        return collectionid

    def get_folderid(self, folder):
        """Converts a string identifying a folder into the folder's UUID"""
        if folder == '':
            return 'null'
        if folder in ['null', 'notnull']:
            return folder
        folderid = folder
        if not self.is_uuid(folderid):
            raise NotImplementedError('not needed so far and thus not implemented')
            folderid = self.get_folders_asdictbyname().get(folder, dict()).get('id')
            if folderid is None:
                raise ValueError(f'Unknown folder name [{folder}] given')
        assert self.is_uuid(folderid)
        return folderid

    @property
    def organizations(self):
        """Cached list of organizations as returned by bw"""
        if self._organizations is None:
            self.get_organizations()
        return self._organizations

    @property
    def organizations_asdictbyid(self):
        """Dictionary of (cached) organizations with organization identifiers as keys"""
        return { item.get('id'): item for item in self.organizations }

    @property
    def organizations_asdictbyname(self):
        """Dictionary of (cached) organizations with organization names as keys"""
        return { item.get('name'): item for item in self.organizations }
