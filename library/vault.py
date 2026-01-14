#!/usr/bin/python3
from ansible.module_utils.basic import *
from ansible.module_utils import urls
from urllib.parse import urljoin


def main():
    fields = {
        'vault_token': {'required': True, 'type': 'str'},
        'vault_addr': {'required': True, 'type': 'str'},
        'path': {'required': True, 'type': 'str'},
    }
    module = AnsibleModule(argument_spec=fields)

    vault_token = module.params['vault_token']
    vault_addr = module.params['vault_addr']

    if not vault_token:
        module.fail_json(msg='You must provide environment variable VAULT_TOKEN!')
    if not vault_addr:
        module.fail_json(msg='You must provide an address to Vault server '
                             'via the VAULT_ADDR environment variable or as a module parameter!')

    status_message_map = {
        204: 'The request is successful, but nothing has been returned.',
        400: 'Invalid request, missing or invalid data.',
        403: 'Forbidden, your authentication details are either incorrect or you don\'t have access to this feature.',
        404: 'Invalid path. This can both mean that the path truly doesn\'t exist or '
             'that you don\'t have permission to view a specific path.',
        429: 'Default return code for health status of standby nodes, indicating a warning.',
        500: 'Internal server error. An internal error has occurred, try again later.'
             'If the error persists, report a bug.',
        503: ' Vault is down for maintenance or is currently sealed. Try again later.',
    }

    headers = {'X-Vault-Token': vault_token}
    url = urljoin(vault_addr, '/v1/')
    url = urljoin(url, module.params['path'])
    response, info = urls.fetch_url(module, url, headers=headers)

    if info['status'] in status_message_map:
        module.fail_json(msg=status_message_map[info['status']])

    content = response.read()
    data = json.loads(content)

    if 'data' not in data:
        module.fail_json(msg='Key data was not found in response! Response: %s' % response)

    module.exit_json(**data['data'])


if __name__ == '__main__':
    main()
