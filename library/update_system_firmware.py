#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2022-2023 Hewlett Packard Enterprise, Inc. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: update_system_firmware
short_description: Updates CrayXD components using Redfish APIs
version_added: #6.6.0
description:
  - Builds Redfish URIs locally and sends them to remote OOB controllers to
    perform an action.
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
extends_documentation_fragment:
  - community.general.attributes
options:
  category:
    required: true
    description:
      - Category to Update the components of CrayXD.
    type: str
    choices: ['Update']
  command:
    required: true
    description:
      - List of commands to execute on the CrayXD.
    type: list
    elements: str
  baseuri:
    required: true
    description:
      - Base URI of OOB controller.
    type: str
  username:
    required: false
    description:
      - Username for authenticating to CrayXD.
    type: str
  password:
    required: false
    description:
      - Password for authenticating to CrayXD.
    type: str
  auth_token:  #confirm this
    required: false
    description:
      - Security token for authenticating to CratXD.
    type: str
  timeout:
    required: false
    description:
      - Timeout in seconds for HTTP requests to CrayXD.
    default: 60
    type: int
author:
  - ##Varni H P (@varini-hp)
'''

EXAMPLES = '''
    - name: Running Firmware Update for Cray XD Servers
      update_system_firmware:
        category: Update
        command: SystemFirmwareUpdate
        baseuri: "{{ baseuri }}"
        username: "{{ bmc_username }}"
        password: "{{ bmc_password }}"
'''

RETURN = '''
update_system_firmware:
    description: Update the components of the CrayXD.
    type: dict
    contains:
        update_system_firmware
            description: Updates the CrayXD components using Redfish API's.
            type: dict
            contains:
                ret:
                    description: Return True/False based on whether the operation was performed successfully.
                    type: bool
                msg:
                    description: Status of the operation performed on the iLO.
                    type: str
    returned: always
'''


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.system_firmware_utils import CrayRedfishUtils
from ansible.module_utils.common.text.converters import to_native


# More will be added as module features are expanded
category_commands = {
    "Update": ["SystemFirmwareUpdate"],
}

def main():
    result = {}
    return_values = {}
    module = AnsibleModule(
        argument_spec=dict(
            category=dict(required=True),
            command=dict(required=True, type='list', elements='str'),
            baseuri=dict(required=True),
            username=dict(),
            password=dict(no_log=True),
            auth_token=dict(no_log=True),
            session_uri=dict(),
            timeout=dict(type='int', default=60),
            update_image_type = dict(type='str', default='HPM'),
            resource_id=dict(type='list',elements='str',default=[],required=False),
            update_target=dict(),
            power_state=dict(),
            update_image_path_xd220v=dict(type='str', default=''),
            update_image_path_xd225v=dict(type='str', default=''),
            update_image_path_xd295v=dict(type='str', default=''),
            update_image_path_xd665=dict(type='str', default=''),
            update_image_path_xd670=dict(type='str', default=''),
            output_file_name=dict(type='str', default=''),
        ),
        supports_check_mode=False
    )

    category = module.params['category']
    command_list = module.params['command']

    # admin credentials used for authentication
    creds = {'user': module.params['username'],
             'pswd': module.params['password'],
             'token': module.params['auth_token']}


    timeout = module.params['timeout']
    # Build root URI
    root_uri = "https://" + module.params['baseuri']
    update_uri = "/redfish/v1/UpdateService"
    rf_utils = CrayRedfishUtils(creds, root_uri, timeout, module, data_modification=True)

    # Check that Category is valid
    if category not in category_commands:
        module.fail_json(msg=to_native("Invalid Category '%s'. Valid Categories = %s" % (category, list(category_commands.keys()))))

    # Check that all commands are valid
    for cmd in command_list:
        # Fail if even one command given is invalid
        if cmd not in category_commands[category]:
            module.fail_json(msg=to_native("Invalid Command '%s'. Valid Commands = %s" % (cmd, category_commands[category])))

          
    if category == "Update":
        for command in command_list:
            if command == "SystemFirmwareUpdate":
                result = rf_utils.system_fw_update({
                'baseuri': module.params['baseuri'],
                'username': module.params['username'],
                'password': module.params['password'],
                'update_image_type' : module.params['update_image_type'],
                'update_target' : module.params['update_target'],
                'power_state' : module.params['power_state'],
                'update_image_path_xd220v' : module.params['update_image_path_xd220v'],
                'update_image_path_xd225v' : module.params['update_image_path_xd225v'],
                'update_image_path_xd295v' : module.params['update_image_path_xd295v'],
                'update_image_path_xd665' : module.params['update_image_path_xd665'],
                'update_image_path_xd670' : module.params['update_image_path_xd670'],
                'output_file_name': module.params['output_file_name'],
                })
                if result['ret']:
                    msg = result.get('msg', False)
                    module.exit_json(msg=msg)
                else:
                    module.fail_json(msg=to_native(result))
      

if __name__ == '__main__':
    main()